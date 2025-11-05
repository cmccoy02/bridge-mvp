const form = document.getElementById('analyze-form');
const repoInput = document.getElementById('repo');
const errorEl = document.getElementById('error');
const summaryEl = document.getElementById('summary');
const langsEl = document.getElementById('languages');

let commitsChart;

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove('hidden');
}

function clearError() {
  errorEl.textContent = '';
  errorEl.classList.add('hidden');
}

function card(label, value) {
  return `
    <div class="bg-white shadow rounded-lg p-4">
      <div class="text-xs uppercase text-gray-500">${label}</div>
      <div class="text-xl font-semibold">${value}</div>
    </div>
  `;
}

function renderSummary(s) {
  summaryEl.innerHTML = [
    card('name', s.name ?? 'N/A'),
    card('age', s.age_days == null ? 'N/A' : `${s.age_days} days`),
    card('open issues', s.open_issues == null ? 'N/A' : s.open_issues),
    card('commits', s.commits ?? 0),
    card('churn (30d)', `${s.churn_30d?.commits ?? 0} commits, ${s.churn_30d?.files ?? 0} files`),
    card('complexity', `avg ${s.complexity?.avg ?? 0}, p90 ${s.complexity?.p90 ?? 0}`),
    card('size', `${s.size_loc ?? 0} lines of code`),
    card('contributors', s.health?.contributors ?? 0),
    card('bus factor', s.health?.bus_factor ?? 0),
    card('releases/yr', s.health?.releases_per_year ?? 0),
  ].join('');

  langsEl.innerHTML = (s.languages ?? [])
    .slice(0, 8)
    .map(([lang, pct]) => `<li><span class="font-mono">${lang}</span> — ${pct}%</li>`)
    .join('');

  const weekly = (s.churn_30d?.weekly ?? []).slice(-12);
  const labels = weekly.map(w => w.week_start);
  const data = weekly.map(w => w.commits);

  const ctx = document.getElementById('commitsChart').getContext('2d');
  if (commitsChart) commitsChart.destroy();
  commitsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Commits',
        data,
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.2)',
        tension: 0.25,
        fill: true,
        pointRadius: 2,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { x: { display: false }, y: { beginAtZero: true, ticks: { precision: 0 } } }
    }
  });
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearError();
  summaryEl.innerHTML = '';
  langsEl.innerHTML = '';
  const repo = repoInput.value.trim();
  if (!repo) return showError('Please enter a repository reference.');
  try {
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo })
    });
    if (!res.ok) {
      const j = await res.json().catch(() => ({}));
      throw new Error(j.detail || `Request failed (${res.status})`);
    }
    const json = await res.json();
    renderSummary(json.summary);
  } catch (err) {
    showError(err.message || String(err));
  }
});



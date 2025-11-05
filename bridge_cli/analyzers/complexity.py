"""Calculates cyclomatic complexity and maintainability insights."""

import os
import heapq
from typing import Dict, List, Tuple
from radon.visitors import ComplexityVisitor
from radon.metrics import mi_visit

def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * p
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return float(values[int(k)])
    d0 = values[f] * (c - k)
    d1 = values[c] * (k - f)
    return float(d0 + d1)


def calculate_complexity(path: str) -> dict:
    """
    Calculates the average cyclomatic complexity and finds the most complex functions.

    Args:
        path (str): The path to the directory to analyze.

    Returns:
        dict: A dictionary containing the average complexity and a list of the
              top 5 most complex functions.
    """
    total_complexity: float = 0.0
    function_count = 0
    top_functions: List[Tuple[float, str]] = []
    complexities: List[float] = []

    file_stats: Dict[str, Dict[str, float]] = {}
    mi_per_file: Dict[str, float] = {}

    for root, _, files in os.walk(path):
        for file in files:
            if not file.endswith(".py"):
                continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            try:
                visitor = ComplexityVisitor.from_code(content)
            except Exception:
                continue

            # Maintainability Index per file
            try:
                mi_val = float(mi_visit(content, False))
                mi_per_file[file_path] = mi_val
            except Exception:
                pass

            file_total = 0.0
            file_count = 0

            for func in visitor.functions:
                total_complexity += func.complexity
                function_count += 1
                file_total += func.complexity
                file_count += 1
                complexities.append(func.complexity)

                loc = f"{file_path}:{func.lineno} - {func.name}"
                if len(top_functions) < 5:
                    heapq.heappush(top_functions, (func.complexity, loc))
                else:
                    heapq.heappushpop(top_functions, (func.complexity, loc))

            if file_count:
                s = file_stats.setdefault(file_path, {"total": 0.0, "count": 0.0})
                s["total"] += file_total
                s["count"] += file_count

    average_complexity = total_complexity / function_count if function_count > 0 else 0.0
    p90 = _percentile(complexities, 0.90)

    worst_files = sorted(
        (
            {
                "file": fp,
                "total_complexity": round(stats["total"], 2),
                "avg_complexity": round(stats["total"] / stats["count"], 2) if stats["count"] else 0.0,
            }
            for fp, stats in file_stats.items()
        ),
        key=lambda x: (x["total_complexity"], x["avg_complexity"]),
        reverse=True,
    )[:5]

    mi_items = [{"file": fp, "mi": round(mi, 1)} for fp, mi in mi_per_file.items()]
    worst_mi = sorted(mi_items, key=lambda x: x["mi"])[:5]
    avg_mi = round(sum(mi for _, mi in mi_per_file.items()) / len(mi_per_file), 1) if mi_per_file else 0.0

    sorted_top_functions = sorted(top_functions, key=lambda x: x[0], reverse=True)

    return {
        "average_complexity": round(average_complexity, 2),
        "function_count": function_count,
        "p90_complexity": round(p90, 2),
        "top_complex_functions": [
            {"complexity": score, "location": location} for score, location in sorted_top_functions
        ],
        "worst_files_by_complexity": worst_files,
        "maintainability": {
            "average_mi": avg_mi,
            "worst_files_by_mi": worst_mi,
        },
    }
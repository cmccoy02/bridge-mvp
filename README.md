# Bridge CLI

A command-line tool for analyzing technical debt in GitHub repositories.

## Features

- Calculate code complexity using radon
- Analyze open issues and their types
- Scan for security vulnerabilities using bandit
- Generate a technical debt score (0-100)
- Rich terminal output with detailed metrics
- Optional JSON output for integration with other tools

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bridge-cli.git
cd bridge-cli
```

2. Install the package:
```bash
pip install -e .
```

3. Set up your GitHub token:
```bash
# Create a .env file
echo "GITHUB_TOKEN=your_github_token" > .env
```

You can generate a GitHub token by going to GitHub Settings > Developer Settings > Personal Access Tokens.

## Usage

### Test GitHub Token Configuration

```bash
bridge test-token
```

### Analyze a Repository

```bash
bridge analyze owner/repository
```

For example:
```bash
bridge analyze facebook/react
```

### JSON Output

To get results in JSON format:
```bash
bridge analyze owner/repository --json
```

## Technical Debt Score

The technical debt score is calculated using the following weights:
- Code Complexity: 50%
- Open Issues: 30%
- Security Issues: 20%

A score of 0 indicates minimal technical debt, while 100 indicates critical levels of technical debt.

## Development

### Running Tests

```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License 
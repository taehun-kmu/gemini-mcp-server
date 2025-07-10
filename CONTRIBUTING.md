# Contributing to Gemini MCP Server

Thank you for your interest in contributing to Gemini MCP Server! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/gemini-mcp-server
   cd gemini-mcp-server
   ```

2. Create a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   uv pip install -e ".[dev]"
   ```

## Code Style

We use several tools to maintain code quality:

- **Ruff**: LCode formatting & inting
- **MyPy**: Type checking

Before submitting, ensure your code passes all checks:

```bash
ruff check gemini_mcp
mypy gemini_mcp
```

## Testing

Add tests for any new functionality:

```bash
pytest tests/ -v
```

Ensure test coverage remains high:

```bash
pytest tests/ --cov=gemini_mcp --cov-report=html
```

## Pull Request Process

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit with clear messages:
   ```bash
   git commit -m "feat: Add new feature"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request with:
   - Clear title and description
   - Reference to any related issues
   - Screenshots/examples if applicable

## Commit Message Convention

We follow conventional commits:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `chore:` Maintenance tasks
- `test:` Test additions/changes
- `ci:` CI/CD changes

## Reporting Issues

When reporting issues, please include:

1. Python version
2. OS and version
3. Steps to reproduce
4. Expected vs actual behavior
5. Error messages/logs

## Questions?

Feel free to open an issue for any questions about contributing!

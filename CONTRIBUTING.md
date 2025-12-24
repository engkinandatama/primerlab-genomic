# Contributing to PrimerLab

Thank you for your interest in contributing to **PrimerLab**! 🧬

## Quick Start

1. **Fork & Clone** the repository
2. **Read** the development guidelines below
3. **Create** a feature branch
4. **Submit** a Pull Request

## Development Guidelines

PrimerLab follows strict architecture and coding standards. Before contributing, please review:

### Required Reading

| Document | Description |
|----------|-------------|
| [Development Rules](.dev/Development%20Rules/) | Coding style, naming, error handling |
| [Architecture](.dev/High-Level%20Documentation/architecture.md) | Project structure |
| [Blueprints](.dev/Blueprint%20Files/) | System design documents |

### Key Principles

- **Deterministic outputs** — Same input = same output, always
- **No cross-layer imports** — Respect module boundaries
- **Explicit error handling** — Use project error codes
- **Comprehensive testing** — All new features need tests

## Development Setup

```bash
# Clone
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic

# Virtual environment (Linux/WSL recommended)
python3 -m venv ~/primerlab_venv
source ~/primerlab_venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v
```

## Pull Request Checklist

- [ ] Code follows [coding-style.md](.dev/Development%20Rules/coding-style.md)
- [ ] Tests added/updated
- [ ] All tests pass locally (`pytest -v`)
- [ ] Documentation updated if needed
- [ ] No breaking changes to public API

## For AI Contributors

If you're using AI coding assistants, please also review:

- [AI Helper Rules](.dev/AI%20Helper%20Files/ai-helper-rules.md)
- [AI Prompts](.dev/AI%20Helper%20Files/ai-prompts.md)

## Questions?

Open an [issue](https://github.com/engkinandatama/primerlab-genomic/issues) or check the [troubleshooting guide](docs/troubleshooting.md).

---

© 2025 — PrimerLab Contributors

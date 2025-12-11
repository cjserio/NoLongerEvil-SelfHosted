# Contributing to NoLongerEvil Self-Hosted

Thank you for your interest in contributing to NoLongerEvil Self-Hosted! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all experience levels.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git

### Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/codykociemba/NoLongerEvil-SelfHosted.git
   cd NoLongerEvil-SelfHosted
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Set up pre-commit hooks (optional but recommended):
   ```bash
   pre-commit install
   ```

## Development Workflow

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring

Example: `feature/add-humidity-sensor`

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=nolongerevil --cov-report=html

# Run specific test file
pytest tests/test_mqtt_helpers.py

# Run tests matching a pattern
pytest -k "mqtt"
```

### Code Quality

Before submitting a PR, ensure your code passes all checks:

```bash
# Linting
ruff check src/

# Formatting
ruff format src/

# Type checking
mypy src/nolongerevil
```

### Commit Messages

Write clear, concise commit messages:

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Fix bug" not "Fixes bug")
- Reference issues when applicable ("Fix #123")

Examples:
```
Add RSSI sensor to Home Assistant discovery
Fix battery voltage to percentage conversion
Update README with correct repository URLs
```

## Submitting Changes

### Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request against `main`

### Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure all CI checks pass
- Update documentation if needed
- Add tests for new functionality

### PR Title Format

Use a descriptive title that summarizes the change:
- `feat: Add new sensor type for filter status`
- `fix: Correct temperature conversion for Fahrenheit`
- `docs: Update installation instructions`
- `refactor: Simplify MQTT message handling`

## Testing Guidelines

- Write tests for new functionality
- Maintain or improve code coverage
- Use descriptive test names
- Group related tests in classes

Example:
```python
class TestBatteryVoltageToPercent:
    def test_full_battery(self):
        assert battery_voltage_to_percent(4.0) == 100

    def test_empty_battery(self):
        assert battery_voltage_to_percent(3.5) == 0
```

## Adding New Sensors

When adding new Home Assistant sensors:

1. Add the discovery payload builder in `home_assistant_discovery.py`
2. Add state publishing logic in `mqtt_integration.py`
3. Register the sensor in `get_all_discovery_configs()`
4. Add the removal topic in `get_discovery_removal_topics()`
5. Write tests for the new functionality

## Reporting Issues

### Bug Reports

Include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs or error messages

### Feature Requests

Include:
- Clear description of the feature
- Use case / motivation
- Proposed implementation (optional)

## Questions?

Open a [GitHub Discussion](https://github.com/codykociemba/NoLongerEvil-SelfHosted/discussions) for questions or ideas.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

# Contributing to AdventureGame

Thank you for your interest in contributing to AdventureGame! This document provides guidelines for contributing to the codebase.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Quality Standards](#code-quality-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Adding New Features](#adding-new-features)

## Getting Started

AdventureGame is an Interactive Fiction/Text Adventure game built for the clemgame benchmarking framework. Before contributing, familiarize yourself with:

- The [README.md](README.md) for project overview
- The [CLAUDE.md](CLAUDE.md) for detailed architecture and development commands
- The [docs/](docs/) directory for specific guides on architecture, PDDL, and development

### Prerequisites

- Python 3.10 or higher (required for match/case statement support)
- Git
- Basic understanding of PDDL (Planning Domain Definition Language)
- Familiarity with Clingo ASP solver (for adventure generation)

## Code Quality Standards

### Logging Guidelines

**Use Logging, Not Print**

Always use the `logging` module instead of `print()` statements for all output:

```python
import logging
logger = logging.getLogger(__name__)

# Good
logger.debug("Processing action: %s", action_name)
logger.info("Generated %d adventures", count)
logger.warning("Using default value for %s", param_name)
logger.error("Failed to parse file: %s", filename)

# Bad
print("Processing action:", action_name)
print(f"Generated {count} adventures")
```

### Choosing Log Levels

- **DEBUG**: Detailed diagnostic information for debugging
  - Variable dumps, loop iterations, intermediate states
  - Example: `logger.debug("Current state: %s", state_dict)`

- **INFO**: General progress and status information
  - Major steps completed, configuration loaded, generation progress
  - Example: `logger.info("Generated %d room layouts", layout_count)`

- **WARNING**: Unexpected but recoverable situations
  - Missing optional config, fallback values used, deprecated features
  - Example: `logger.warning("Config file not found, using defaults")`

- **ERROR**: Error conditions that impact functionality
  - File not found, parse errors, invalid state
  - Example: `logger.error("Failed to parse PDDL file: %s", filename)`

- **CRITICAL**: Critical errors requiring immediate attention
  - Unrecoverable state, system failures
  - Example: `logger.critical("Cannot initialize game engine")`

### String Formatting in Logs

Use lazy evaluation with `%` formatting for performance:

```python
# Good - formatting only happens if log level is enabled
logger.debug("State: %s, count: %d", state, count)

# Better - condition check before expensive operations
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Expensive dump: %s", expensive_function())

# Bad - always formats string even if debug is disabled
logger.debug(f"State: {state}, count: {count}")
```

## Development Setup

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AdventureClemGame
   ```

2. Install runtime dependencies:
   ```bash
   pip install -r adventuregame/requirements.txt
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Verify Installation

Run the test suite to verify your setup:
```bash
pytest tests/ -v
```

### Code Quality Tools

The project uses several tools to maintain code quality:

- **Black**: Code formatter (line length: 100)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking
- **pytest**: Testing framework

Run all checks before committing:
```bash
pre-commit run --all-files
```

Or run individual tools:
```bash
black adventuregame/          # Format code
isort adventuregame/          # Sort imports
flake8 adventuregame/         # Lint code
mypy adventuregame/           # Type check
pytest tests/                 # Run tests
```

### Configuration

Logging is configured in `adventuregame/config.json`:

```json
{
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": null,
    "console": true
  }
}
```

To change logging verbosity during development, modify the `level` field to `"DEBUG"`.

### Testing Changes

Before committing changes:

1. **Run tests** (if applicable):
   ```bash
   python3 -m pytest adventuregame/tests/
   ```

2. **Verify logging output**:
   - Test with `INFO` level for normal operation
   - Test with `DEBUG` level to ensure debug logs are helpful
   - Ensure no sensitive information is logged

3. **Check for remaining print statements**:
   ```bash
   grep -r "^\s*print(" adventuregame/ --exclude-dir=experiments
   ```

## Code Style

### General Principles

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and under 50 lines when possible
- Use type hints where appropriate

### Function Documentation

```python
def generate_adventure(layout: dict, goal_count: int) -> dict:
    """
    Generate an adventure from a room layout and goal count.

    Args:
        layout: Dictionary containing room layout information
        goal_count: Number of goals to generate

    Returns:
        Dictionary containing complete adventure definition

    Raises:
        ValueError: If goal_count is less than 1
    """
    logger.info("Generating adventure with %d goals", goal_count)
    # Implementation here
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=adventuregame --cov-report=html

# Run specific test file
pytest tests/test_if_wrapper.py -v

# Run tests matching a pattern
pytest tests/ -k "test_action"
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_<module>.py`
- Name test functions `test_<functionality>`
- Use pytest fixtures for common setup (see `tests/conftest.py`)
- Aim for >80% code coverage for new code

Example test:
```python
def test_action_parsing():
    """Test basic action parsing functionality."""
    interpreter = AdventureIFInterpreter(game_instance)
    result = interpreter.parse_action_input("take orange")

    assert result["valid"] is True
    assert result["action_name"] == "take"
    assert "orange" in result["parameters"]
```

## Adding New Features

### Adding New Adventure Types

See [docs/adding_actions.md](docs/adding_actions.md) for detailed instructions. Quick overview:

1. Define adventure type in `resources/definitions/adventure_types.json`
2. Create room, entity, and action definitions in `resources/definitions/`
3. Update `resources/clingo_adventures2-2.py` to handle new type
4. Generate adventures: `python3 clingo_adventures2-2.py`
5. Generate instances: `python3 instancegenerator.py`
6. Add tests for new adventure type

### Modifying Action Definitions

1. Edit PDDL action in `resources/definitions/basic_actions_*.json`
2. Ensure grammar in `pddl_actions.lark` supports syntax
3. Update ASP encoding in `resources/pddl_to_asp.py` if needed
4. Regenerate adventures and instances
5. Test with sample game runs

## Git Workflow

### Commit Messages

Write clear, descriptive commit messages:

```
Phase 2.3: Replace print statements with logging in master.py

- Add logging import and logger initialization
- Replace progress prints with logger.info()
- Replace debug prints with logger.debug()
- Replace error prints with logger.error()

Improves debugging capabilities and enables configurable output verbosity.
```

### Branch Naming

Use descriptive branch names:
- `feature/add-new-adventure-type`
- `fix/parsing-error-in-pddl`
- `refactor/simplify-goal-generation`
- `docs/update-readme`

## Pull Request Process

1. **Create a descriptive PR title**: Summarize the changes in one line
2. **Provide context**: Explain why the changes are needed
3. **List changes**: Bullet points of what was modified
4. **Test plan**: Describe how you tested the changes
5. **Breaking changes**: Clearly mark any breaking changes

## Questions or Issues?

- Check existing documentation in `CLAUDE.md` for project structure
- Review code quality guidelines in `CODE_QUALITY_ROADMAP.md`
- Open an issue for bugs or feature requests

## License

By contributing to AdventureGame, you agree that your contributions will be licensed under the same license as the project.

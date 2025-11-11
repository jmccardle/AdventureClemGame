# Development Guide

This guide covers the development workflow, tools, and best practices for working on AdventureGame.

## Table of Contents

- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Running the Game](#running-the-game)
- [Testing](#testing)
- [Debugging](#debugging)
- [Code Quality](#code-quality)
- [Common Tasks](#common-tasks)

## Development Environment

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)
- Code editor (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd AdventureClemGame

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r adventuregame/requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Verify installation
pytest tests/ -v
```

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

#### PyCharm

- Settings → Tools → Python Integrated Tools → Default test runner: pytest
- Settings → Editor → Code Style → Python → Line length: 100
- Settings → Tools → Black → Enable Black formatter
- Settings → Tools → Actions on Save → Reformat code, Optimize imports

## Project Structure

```
AdventureClemGame/
├── adventuregame/           # Main package
│   ├── master.py            # Game master & scoring
│   ├── if_wrapper.py        # IF interpreter (4K lines)
│   ├── instancegenerator.py # Instance generation
│   ├── config_loader.py     # Configuration singleton
│   ├── exceptions.py        # Custom exceptions
│   ├── config.json          # Configuration file
│   ├── requirements.txt     # Runtime dependencies
│   ├── in/                  # Game instances
│   │   └── instances.json   # Main instance file
│   └── resources/           # Game resources
│       ├── definitions/     # JSON definitions
│       ├── initial_prompts/ # Jinja2 templates
│       ├── clingo_adventures2-2.py  # Adventure generator
│       └── pddl_*.lark      # PDDL grammars
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_if_wrapper.py   # IF interpreter tests
│   ├── test_master.py       # Game master tests
│   └── ...
├── docs/                    # Documentation
│   ├── architecture.md      # System architecture
│   ├── pddl_guide.md        # PDDL syntax guide
│   ├── adding_actions.md    # How to add actions
│   ├── instance_format.md   # Instance file format
│   └── development.md       # This file
├── experiments/             # Experimental code (gitignored)
├── .github/workflows/       # CI/CD configuration
├── pyproject.toml           # Tool configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
├── CONTRIBUTING.md          # Contribution guidelines
├── CLAUDE.md                # Project overview for AI
└── CODE_QUALITY_ROADMAP.md  # Improvement plan
```

## Development Workflow

### Feature Development

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Run Quality Checks**
   ```bash
   # Format code
   black adventuregame/
   isort adventuregame/

   # Lint
   flake8 adventuregame/

   # Type check
   mypy adventuregame/

   # Test
   pytest tests/ -v --cov=adventuregame
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

   Pre-commit hooks will run automatically.

5. **Push & PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Create pull request on GitHub.

### Bug Fix Workflow

1. **Reproduce Bug**
   - Create minimal test case
   - Document expected vs actual behavior

2. **Write Failing Test**
   ```python
   def test_bug_description():
       # Setup that triggers bug
       result = function_with_bug()
       # Assertion that fails
       assert result == expected
   ```

3. **Fix Bug**
   - Implement fix
   - Verify test now passes
   - Check for similar issues

4. **Verify Fix**
   ```bash
   pytest tests/test_module.py::test_bug_description -v
   ```

5. **Document Fix**
   - Update docstrings if needed
   - Add comments explaining tricky parts
   - Update CHANGELOG if applicable

## Running the Game

### Within clemgame Framework

AdventureGame runs within the clemgame framework:

```bash
# From clemgame root directory
python3 scripts/cli.py run -g adventuregame -m gpt-3.5-turbo

# Run specific instances
python3 scripts/cli.py run -g adventuregame -m gpt-3.5-turbo --instances 0,1,2

# Run single experiment
python3 scripts/cli.py run -g adventuregame -m gpt-3.5-turbo --experiments basic_easy
```

### Standalone Testing

For quick iteration without full framework:

```python
# test_runner.py
from adventuregame.master import AdventureGameMaster
from adventuregame.if_wrapper import AdventureIFInterpreter
import json

# Load instance
with open('adventuregame/in/instances.json') as f:
    data = json.load(f)
    instance = data['experiments'][0]['game_instances'][0]

# Create interpreter
interpreter = AdventureIFInterpreter(instance)

# Test actions
actions = ["take orange", "go north", "drop orange"]
for action in actions:
    result = interpreter.process_action(action)
    print(f"Action: {action}")
    print(f"Success: {result['success']}")
    print(f"Feedback: {result['feedback']}")
    print()
```

Run:
```bash
python test_runner.py
```

### Interactive Mode

Create an interactive REPL:

```python
# interactive.py
from adventuregame.if_wrapper import AdventureIFInterpreter
import json

with open('adventuregame/in/instances.json') as f:
    data = json.load(f)
    instance = data['experiments'][0]['game_instances'][0]

interpreter = AdventureIFInterpreter(instance)
print(interpreter.get_full_room_desc())

while True:
    action = input("> ")
    if action.lower() in ['quit', 'exit']:
        break
    
    result = interpreter.process_action(action)
    print(result['feedback'])
    
    if result.get('goal_achieved'):
        print("You won!")
        break
```

Run:
```bash
python interactive.py
```

## Testing

### Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=adventuregame --cov-report=html

# Specific test file
pytest tests/test_if_wrapper.py -v

# Specific test function
pytest tests/test_if_wrapper.py::test_action_parsing -v

# With debug output
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x

# Run tests matching pattern
pytest tests/ -k "action" -v

# Run in parallel (if pytest-xdist installed)
pytest tests/ -n auto
```

### Writing Tests

See `tests/conftest.py` for available fixtures:

```python
def test_something(test_game_instance, test_interpreter):
    """Test description."""
    # Use fixtures
    interpreter = test_interpreter
    result = interpreter.process_action("take orange")
    
    # Assertions
    assert result['success'] is True
    assert "take" in result['feedback'].lower()
    assert ('in', 'orange', 'inventory') in interpreter.world_state
```

### Test Coverage

View coverage report:
```bash
pytest tests/ --cov=adventuregame --cov-report=html
open htmlcov/index.html  # View in browser
```

Current coverage: ~65%

## Debugging

### Logging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or configure in `config.json`:
```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

### Debug Action Resolution

```python
import logging
from adventuregame.if_wrapper import AdventureIFInterpreter

logging.getLogger("adventuregame.if_wrapper").setLevel(logging.DEBUG)

interpreter = AdventureIFInterpreter(instance)
result = interpreter.process_action("take orange")
```

Output shows:
- Precondition evaluation
- Variable binding
- Effect application
- State changes

### Interactive Debugger

```python
# In code
import pdb; pdb.set_trace()

# Or with ipdb (better interface)
import ipdb; ipdb.set_trace()
```

Useful commands:
- `n`: Next line
- `s`: Step into function
- `c`: Continue execution
- `p variable`: Print variable
- `pp variable`: Pretty print variable
- `l`: Show current location
- `w`: Show stack trace

### VS Code Debugging

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

## Code Quality

### Pre-commit Hooks

Hooks run automatically on `git commit`:
- Black formatting
- isort import sorting
- flake8 linting
- Trailing whitespace removal
- YAML validation

Run manually:
```bash
pre-commit run --all-files
```

### Manual Checks

```bash
# Format
black adventuregame/ tests/
isort adventuregame/ tests/

# Lint
flake8 adventuregame/ tests/

# Type check
mypy adventuregame/

# Complexity analysis
radon cc adventuregame/ -a -s
radon mi adventuregame/ -s
```

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Type hints added
- [ ] Docstrings updated
- [ ] No commented-out code
- [ ] No print statements (use logging)
- [ ] Error handling appropriate
- [ ] Documentation updated

## Common Tasks

### Generate New Adventures

```bash
cd adventuregame/resources
python3 clingo_adventures2-2.py

# Output: adventures_*.json files
```

### Create Game Instances

```bash
cd adventuregame
python3 instancegenerator.py

# Output: in/instances.json
```

### Add New Action

See [Adding Actions Guide](adding_actions.md) for detailed steps.

Quick summary:
1. Define PDDL action in `resources/definitions/`
2. Update grammar if needed
3. Regenerate adventures
4. Create instances
5. Test

### Modify Prompts

Edit Jinja2 templates in `resources/initial_prompts/`:
- `basic_initial_prompt.j2`
- `plan_initial_prompt.j2`
- `invlimit_initial_prompt.j2`

Then regenerate instances.

### Update Configuration

Edit `adventuregame/config.json`:
- Entity IDs
- Predicate lists
- Message templates
- Logging settings

Changes take effect immediately (singleton pattern).

### Run Benchmarks

```bash
# From clemgame root
python3 scripts/cli.py run -g adventuregame -m gpt-3.5-turbo

# Results in: results/adventuregame/gpt-3.5-turbo/
```

### Analyze Results

```bash
# Generate metrics
python3 scripts/cli.py score -g adventuregame -m gpt-3.5-turbo

# Open Jupyter notebook
jupyter notebook adventuregame_eval_2_3.ipynb
```

### Extract Episode Logs

```bash
# From clembench logs
python3 clem_log_adv_extract.py clembench.log output.json
```

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
interpreter.process_action("take orange")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Memory Profiling

```bash
pip install memory_profiler

python -m memory_profiler script.py
```

### Optimization Tips

- Use sets for state storage (O(1) lookup)
- Cache parsed grammars
- Avoid repeated string formatting
- Use lazy evaluation where possible
- Profile before optimizing

## Troubleshooting

### Import Errors

```
ModuleNotFoundError: No module named 'clemcore'
```

**Solution**: Ensure clemcore is installed or you're in the right environment.

### Clingo Errors

```
clingo: command not found
```

**Solution**: Install clingo: `pip install clingo==5.7.1`

### Grammar Parse Errors

```
LarkError: Unexpected token
```

**Solution**: Check `.lark` grammar files match your PDDL syntax.

### Test Failures

```
AssertionError: expected True but got False
```

**Solution**: Run with `-v -s` to see detailed output, check test assumptions.

### Performance Issues

**Solution**: Profile code, check for N^2 algorithms, cache expensive operations.

## Best Practices

1. **Write tests first** (TDD when possible)
2. **Use logging** instead of print
3. **Type hint everything** (new code)
4. **Document as you go** (don't defer)
5. **Keep functions small** (<50 lines)
6. **Use meaningful names** (no `x`, `tmp`, `data`)
7. **Handle errors explicitly** (no bare except)
8. **Review your own code** before submitting
9. **Run full test suite** before pushing
10. **Update docs** with code changes

## Resources

- [CLAUDE.md](../CLAUDE.md) - Project overview
- [Architecture](architecture.md) - System design
- [PDDL Guide](pddl_guide.md) - PDDL syntax
- [Adding Actions](adding_actions.md) - Action creation
- [Instance Format](instance_format.md) - Instance structure
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines

## Getting Help

- Check documentation first
- Search existing issues on GitHub
- Ask in project discussions
- Create detailed bug reports with:
  - Python version
  - Steps to reproduce
  - Expected vs actual behavior
  - Relevant logs

Happy developing! 🎮

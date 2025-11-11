# AdventureGame

[![CI](https://github.com/YOUR_USERNAME/AdventureClemGame/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/AdventureClemGame/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An Interactive Fiction (IF) text adventure game implementation for the clemgame benchmarking framework. Evaluates language models' ability to understand and navigate text-based adventure games by completing goals through action commands.

## Features

- **PDDL-Based Action System**: Declarative action definitions with preconditions and effects
- **Multiple Game Variants**: Basic, planning, inventory-limited, and pre-exploration modes
- **Answer Set Programming**: Uses Clingo to generate solvable adventures with optimal solutions
- **Comprehensive Metrics**: Action success rates, goal achievement, planning adherence, exploration tracking
- **Reactive Events**: Dynamic world responses to player actions
- **Type-Safe**: Extensive type hints throughout codebase
- **Well-Tested**: ~65% test coverage with unit and integration tests

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd AdventureClemGame

# Install dependencies
pip install -r adventuregame/requirements.txt

# For development
pip install -r requirements-dev.txt
pre-commit install
```

### Running the Game

Within the clemgame framework:

```bash
# From clemgame root directory
python3 scripts/cli.py run -g adventuregame -m <model_name>

# Examples
python3 scripts/cli.py run -g adventuregame -m gpt-3.5-turbo
python3 scripts/cli.py run -g adventuregame -m claude-3 --instances 0,1,2
```

### Running Tests

```bash
pytest tests/ -v

# With coverage
pytest tests/ --cov=adventuregame --cov-report=html
```

> **Note on clemcore Dependency**: This project depends on `clemcore==3.1.0` from the clemgame framework, which is not available on PyPI. Full test execution requires running within the clemgame framework environment. The CI pipeline runs code quality checks and framework-independent tests only. For complete local testing, install from the [clemgame repository](https://github.com/clembench/clemgame).

## Architecture Overview

```
┌─────────────────────────────────────┐
│       clemgame Framework            │
│    (Orchestration & Metrics)        │
└────────────┬────────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│      AdventureGameMaster           │
│    (Episode Management)            │
└────────────┬───────────────────────┘
             │
             ▼
┌────────────────────────────────────┐
│   AdventureIFInterpreter           │
│   (Core Game Engine)               │
│                                    │
│  • PDDL Parsing (Lark)             │
│  • State Management                │
│  • Action Resolution               │
│  • Event Processing                │
└────────────────────────────────────┘
```

## Game Variants

- **basic**: Single action per turn (`> take orange`)
- **plan**: Action + future plans (`> take orange\nNext actions: go north, drop orange`)
- **invlimit**: Inventory capacity constraints
- **preexplore**: Pre-exploration phase before main task
- **new-words**: Novel action verb learning

## Project Structure

```
AdventureClemGame/
├── adventuregame/          # Main package
│   ├── master.py           # Game master & scoring
│   ├── if_wrapper.py       # IF interpreter engine
│   ├── instancegenerator.py # Instance generation
│   ├── config_loader.py    # Configuration
│   ├── exceptions.py       # Custom exceptions
│   ├── in/                 # Game instances
│   └── resources/          # PDDL definitions & generators
├── tests/                  # Test suite
├── docs/                   # Documentation
│   ├── architecture.md     # System architecture
│   ├── pddl_guide.md       # PDDL syntax reference
│   ├── adding_actions.md   # How to add actions
│   ├── instance_format.md  # Instance file format
│   └── development.md      # Development guide
├── .github/workflows/      # CI/CD
└── pyproject.toml          # Tool configuration
```

## Documentation

### For Users

- **[CLAUDE.md](CLAUDE.md)**: Project overview and common workflows
- **[Instance Format](docs/instance_format.md)**: Game instance structure
- **[PDDL Guide](docs/pddl_guide.md)**: PDDL syntax and usage

### For Developers

- **[Development Guide](docs/development.md)**: Setup, workflow, debugging
- **[Architecture](docs/architecture.md)**: System design and components
- **[Adding Actions](docs/adding_actions.md)**: Step-by-step action creation
- **[Contributing](CONTRIBUTING.md)**: Contribution guidelines and standards

## Development

### Quick Commands

```bash
# Format code
black adventuregame/ tests/
isort adventuregame/ tests/

# Lint
flake8 adventuregame/ tests/

# Type check
mypy adventuregame/

# Run all quality checks
pre-commit run --all-files

# Generate adventures
cd adventuregame/resources
python3 clingo_adventures2-2.py

# Generate instances
cd adventuregame
python3 instancegenerator.py
```

### Code Quality Standards

- **Formatting**: Black (100 char line length)
- **Import Sorting**: isort
- **Linting**: flake8
- **Type Checking**: mypy
- **Testing**: pytest (target: >80% coverage)
- **Logging**: Use `logging` module, not `print()`

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Key Technologies

- **Python 3.8+**: Core language
- **Lark**: PDDL parsing
- **Clingo 5.7.1**: Answer Set Programming solver for adventure generation
- **clemcore 3.1.0**: Benchmarking framework
- **pytest**: Testing framework

## Adventure Types

Defined in `resources/definitions/adventure_types.json`:

- **home_deliver_three**: Deliver objects to target locations
- **potion_brewing**: Potion crafting with special actions (stir, wave, dump)
- **new-words**: Tests novel action understanding

## Metrics

Episode-level metrics computed by `AdventureGameScorer`:

- `BENCH_SCORE`: Binary success (100 if finished, 0 otherwise)
- `achieved_goal_ratio`: Ratio of achieved goals to total goals
- `turns_over_par`: Efficiency compared to optimal solution
- `turn_ratio`: Normalized turn efficiency
- Action failures by phase (parsing/resolution) and type
- Plan following metrics (for 'plan' variant)
- Exploration metrics (epistemic/pragmatic actions)

## Examples

### Simple Episode

```python
from adventuregame.if_wrapper import AdventureIFInterpreter
import json

# Load instance
with open('adventuregame/in/instances.json') as f:
    instance = json.load(f)['experiments'][0]['game_instances'][0]

# Create interpreter
interpreter = AdventureIFInterpreter(instance)

# Play actions
print(interpreter.get_full_room_desc())
result = interpreter.process_action("take orange")
print(result['feedback'])

result = interpreter.process_action("go north")
print(result['feedback'])

result = interpreter.process_action("drop orange")
print(result['feedback'])
print(f"Goal achieved: {result['goal_achieved']}")
```

### Adding a New Action

See [Adding Actions Guide](docs/adding_actions.md) for complete walkthrough.

Quick steps:
1. Define PDDL action in `resources/definitions/`
2. Update grammar if needed (`pddl_actions.lark`)
3. Regenerate adventures and instances
4. Test with sample scenarios

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Code style guidelines
- Testing requirements
- Pull request process
- Development workflow

### Quick Contribution Checklist

- [ ] Code formatted with Black
- [ ] Imports sorted with isort
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Type hints added
- [ ] Docstrings updated
- [ ] Documentation updated

## Troubleshooting

### Common Issues

**Import Error: No module named 'clemcore'**
```bash
pip install -r adventuregame/requirements.txt
```

**Parse Error: Unexpected token**
- Check PDDL syntax against grammar files
- Enable debug logging: `logging.getLogger("adventuregame").setLevel(logging.DEBUG)`

**Test Failures**
```bash
# Run with verbose output
pytest tests/ -v -s

# Run specific failing test
pytest tests/test_module.py::test_name -v
```

See [Development Guide](docs/development.md) for more troubleshooting tips.

## Citation

If you use AdventureGame in your research, please cite:

```bibtex
@software{adventuregame,
  title={AdventureGame: Interactive Fiction for Language Model Evaluation},
  author={Your Name},
  year={2024},
  url={https://github.com/YOUR_USERNAME/AdventureClemGame}
}
```

## License

[MIT License](LICENSE)

## Acknowledgments

- Built on the [clemgame](https://github.com/clembench/clemgame) benchmarking framework
- Uses [Clingo](https://potassco.org/clingo/) for Answer Set Programming
- PDDL parsing with [Lark](https://github.com/lark-parser/lark)

## Contact

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/AdventureClemGame/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/AdventureClemGame/discussions)

---

Made with ❤️ for advancing language model evaluation

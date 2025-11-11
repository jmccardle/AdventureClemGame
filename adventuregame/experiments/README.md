# Experiments Directory

This directory contains experimental and legacy code files that are not part of the production codebase but are kept for reference and historical purposes.

## Files

### PDDL Experiments

- **pddl_experiments.py** - Initial PDDL parsing experiments
- **pddl_experiments2.py** - Second iteration of PDDL parsing experiments (contains syntax errors)
- **pddl_experiments3.py** - Third iteration of PDDL parsing experiments
- **pddl_experiments4.py** - Fourth iteration of PDDL parsing experiments
- **pddl_experiments5.py** - Fifth iteration of PDDL parsing experiments

These files were used during the development of the PDDL parsing system. They contain experimental code for testing different approaches to parsing PDDL action definitions, domain definitions, and event definitions.

### Legacy Versions

- **if_wrapper_v1.py** - Legacy version of the Interactive Fiction interpreter
  - Contains older implementation of the IF interpreter before major refactoring
  - Kept for reference when understanding design decisions

- **master_old.py** - Legacy version of the game master
  - Contains older implementation of the benchmark orchestration code
  - Kept for reference when understanding design decisions

## Purpose

These files are preserved for:

1. **Historical Reference** - Understanding the evolution of the codebase
2. **Design Decision Documentation** - Seeing what approaches were tried and why they were changed
3. **Recovery** - In case specific functionality needs to be recovered or understood

## Usage

These files are **NOT** intended for production use. They are excluded from:

- Code formatting (Black, isort)
- Linting (flake8)
- Type checking (mypy)
- Pre-commit hooks
- Test coverage

If you need to reference or run code from these files, please:

1. Extract the specific functionality you need
2. Update it to match current code standards
3. Add it to the appropriate production module
4. Include tests for the functionality

## Maintenance

These files are not actively maintained and may not work with the current codebase. They may:

- Contain syntax errors
- Use deprecated APIs
- Have import errors
- Lack proper documentation

If specific functionality is needed from these files, create a new implementation in the production codebase rather than trying to fix the experimental code.

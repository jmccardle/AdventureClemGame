# Code Quality Enhancement Roadmap
## AdventureGame Repository

**Created:** 2025-11-11
**Status:** Proposed
**Estimated Total Effort:** 6-8 weeks

---

## Overview

This roadmap outlines a systematic approach to improving code quality, readability, and maintainability of the AdventureGame codebase. The work is organized into 4 phases, each building on the previous phase's improvements.

---

## Phase 1: Foundation & Tooling (Week 1-2)
**Goal:** Establish automated code quality infrastructure

### 1.1 Linting & Formatting Setup (3 days)

**Tasks:**
- [ ] Create `pyproject.toml` with Black, isort, and mypy configuration
- [ ] Create `.flake8` or integrate flake8 into pyproject.toml
- [ ] Add `.pre-commit-config.yaml` with hooks for:
  - Black (code formatting)
  - isort (import sorting)
  - flake8 (linting)
  - trailing-whitespace removal
  - end-of-file fixer
- [ ] Install pre-commit: `pip install pre-commit && pre-commit install`
- [ ] Run formatters on entire codebase: `black .` and `isort .`
- [ ] Address critical flake8 violations

**Deliverables:**
- `pyproject.toml`
- `.pre-commit-config.yaml`
- `requirements-dev.txt` with dev dependencies
- Formatted codebase

**Acceptance Criteria:**
- All files formatted with Black
- Pre-commit hooks run successfully
- Flake8 violations reduced by >80%

---

### 1.2 Testing Infrastructure (4 days)

**Tasks:**
- [ ] Install pytest, pytest-cov: `pip install pytest pytest-cov`
- [ ] Create `tests/` directory structure:
  ```
  tests/
  ├── __init__.py
  ├── conftest.py
  ├── test_if_wrapper.py
  ├── test_master.py
  ├── test_config_loader.py
  ├── test_pddl_util.py
  └── test_instancegenerator.py
  ```
- [ ] Add pytest configuration to `pyproject.toml`
- [ ] Write initial smoke tests for each major module
- [ ] Set up coverage reporting
- [ ] Document test running in README.md

**Initial Test Targets (aim for 20+ tests):**
- `ConfigLoader` singleton behavior
- PDDL parsing (action, domain, event)
- Action input parsing
- Condition checking
- Simple state transitions
- Instance generation basics

**Deliverables:**
- `tests/` directory with 20+ initial tests
- pytest configuration
- Coverage report showing >30% coverage

**Acceptance Criteria:**
- `pytest` runs successfully
- Coverage report generated
- All tests pass

---

### 1.3 Cleanup Experimental Code (2 days)

**Tasks:**
- [ ] Create `experiments/` directory
- [ ] Move experimental files:
  - `pddl_experiments.py` → `experiments/`
  - `pddl_experiments2.py` → `experiments/`
  - `pddl_experiments3.py` → `experiments/`
  - `pddl_experiments4.py` → `experiments/`
  - `pddl_experiments5.py` → `experiments/`
  - `if_wrapper_v1.py` → `experiments/`
  - `master_old.py` → `experiments/`
- [ ] Add `experiments/README.md` explaining these files
- [ ] Update any imports if needed
- [ ] Update `.gitignore` to ignore `experiments/__pycache__`

**Deliverables:**
- Clean main directory
- Organized `experiments/` directory
- Updated documentation

**Acceptance Criteria:**
- Main directory contains only production code
- All imports still work
- Game still runs correctly

---

## Phase 2: Code Refactoring (Week 3-4)
**Goal:** Improve code structure and reduce complexity

### 2.1 Extract Utility Modules (3 days)

**Tasks:**
- [ ] Create `adventuregame/utils/` directory:
  ```
  utils/
  ├── __init__.py
  ├── string_utils.py
  ├── pddl_transformers.py
  └── validation_utils.py
  ```

- [ ] **string_utils.py** - Extract common patterns:
  ```python
  def strip_trailing_digits(text: str) -> str:
      """Remove trailing digits from a string."""
      return text.rstrip('0123456789')

  def normalize_entity_name(name: str) -> str:
      """Normalize entity name by removing trailing digits."""
      return strip_trailing_digits(name)

  def format_predicate_list(predicates: list[tuple]) -> str:
      """Format list of predicates for display."""
      # Extract from repeated logic
  ```

- [ ] **pddl_transformers.py** - Consolidate transformers:
  - Merge duplicate `PDDLActionTransformer` classes
  - Merge duplicate `PDDLDomainTransformer` classes
  - Share common transformation logic

- [ ] **validation_utils.py** - Extract validation logic:
  - Condition validation
  - Effect validation
  - State validation

- [ ] Update imports in main files
- [ ] Add unit tests for utility functions

**Deliverables:**
- `utils/` module with 3 new files
- Updated imports throughout codebase
- 15+ tests for utility functions

**Acceptance Criteria:**
- Code duplication reduced by >50%
- All tests pass
- Game functionality unchanged

---

### 2.2 Refactor Large Functions (5 days)

**Priority Functions to Refactor:**

#### 2.2.1 `if_wrapper.py::resolve_action()` (362 lines → ~80 lines)

**Extract to:**
```python
def resolve_action(self, action_dict, ...):
    """Main action resolution orchestrator."""
    if not self._validate_action_structure(action_dict):
        return self._create_error_response()

    if not self._check_action_preconditions(action_dict):
        return self._create_precondition_failure_response()

    effects = self._apply_action_effects(action_dict)
    feedback = self._generate_action_feedback(action_dict, effects)

    return feedback

def _validate_action_structure(self, action_dict) -> bool:
    """Validate action dictionary structure."""
    # Extract validation logic

def _check_action_preconditions(self, action_dict) -> bool:
    """Check if action preconditions are satisfied."""
    # Extract from lines 2400-2500

def _apply_action_effects(self, action_dict) -> list:
    """Apply action effects to world state."""
    # Extract from lines 2500-2600

def _generate_action_feedback(self, action_dict, effects) -> dict:
    """Generate player feedback for action."""
    # Extract from lines 2600-2700
```

#### 2.2.2 `master.py::compute_scores()` (282 lines → ~60 lines)

**Extract to:**
```python
def compute_scores(self, episode_interactions):
    """Compute all episode scores and metrics."""
    turn_metrics = self._compute_turn_metrics(episode_interactions)
    episode_metrics = self._compute_episode_metrics(episode_interactions)
    planning_metrics = self._compute_planning_metrics(episode_interactions)
    exploration_metrics = self._compute_exploration_metrics(episode_interactions)

    return self._combine_metrics(turn_metrics, episode_metrics,
                                  planning_metrics, exploration_metrics)

def _compute_turn_metrics(self, interactions) -> dict:
    """Compute per-turn metrics."""
    # Extract turn-level calculations

def _compute_episode_metrics(self, interactions) -> dict:
    """Compute episode-level metrics."""
    # Extract episode-level calculations

def _compute_planning_metrics(self, interactions) -> dict:
    """Compute planning-specific metrics."""
    # Extract planning calculations

def _compute_exploration_metrics(self, interactions) -> dict:
    """Compute exploration metrics."""
    # Extract exploration calculations
```

#### 2.2.3 Other Large Functions

- [ ] `if_wrapper.py::run_events()` (262 lines) → extract event handlers
- [ ] `if_wrapper.py::check_conditions()` (260 lines) → extract condition types
- [ ] `if_wrapper.py::get_entity_desc()` (163 lines) → extract description builders
- [ ] `clingo_adventures2-2.py::generate_adventures()` (485 lines) → extract generation steps

**Deliverables:**
- Refactored functions with <50 lines each
- Extracted helper methods with clear names
- Updated tests for all refactored code
- Coverage maintained or improved

**Acceptance Criteria:**
- No functions >100 lines in main files
- All tests pass
- Game behavior unchanged

---

### 2.3 Replace Print Statements (2 days)

**Tasks:**
- [ ] Audit all 1,303 print statements
- [ ] Categorize by purpose:
  - Debug output → `logger.debug()`
  - Status updates → `logger.info()`
  - Warnings → `logger.warning()`
  - Errors → `logger.error()`
  - Should be removed entirely

- [ ] Replace systematically, file by file:
  1. `if_wrapper.py` (largest file)
  2. `master.py`
  3. `instancegenerator.py`
  4. `clingo_adventures2-2.py`
  5. `pddl_util.py`
  6. Other files

- [ ] Update logging configuration if needed
- [ ] Add logging level configuration to `config.json`

**Example Transformation:**
```python
# Before
print("self.new_word_iterate_idx before new assigned:", self.new_word_iterate_idx)
print("replacement_dict:", replacement_dict)

# After
logger.debug("new_word_iterate_idx before new assigned: %s", self.new_word_iterate_idx)
logger.debug("replacement_dict: %s", replacement_dict)
```

**Deliverables:**
- <50 print statements remaining (only if absolutely necessary)
- Consistent logging levels throughout
- Updated logging configuration

**Acceptance Criteria:**
- >95% of print statements replaced
- Logging output is informative and well-formatted
- No regression in debugging capability

---

## Phase 3: Type Safety & Documentation (Week 5-6)
**Goal:** Improve type safety and code documentation

### 3.1 Comprehensive Type Hints (5 days)

**Tasks:**
- [ ] Run mypy baseline: `mypy . --ignore-missing-imports`
- [ ] Add type hints to all function signatures in:
  - `if_wrapper.py`
  - `master.py`
  - `instancegenerator.py`
  - `config_loader.py` (already good, verify completeness)
  - `pddl_util.py`

- [ ] Add type hints to class attributes:
  ```python
  class AdventureIFInterpreter:
      entity_types: dict[str, dict]
      entity_states: dict[str, set[tuple]]
      current_room: str
      inventory: set[str]
      action_parser: Lark
  ```

- [ ] Fix mypy errors incrementally
- [ ] Add type stubs for external dependencies if needed
- [ ] Update `pyproject.toml` mypy config for stricter checking

**Example Transformation:**
```python
# Before
def get_entity_desc(self, entity_id):
    """Get entity description."""
    ...

# After
def get_entity_desc(self, entity_id: str) -> str:
    """Get entity description.

    Args:
        entity_id: The entity identifier

    Returns:
        Formatted description string
    """
    ...
```

**Deliverables:**
- 100% function signature type coverage
- >80% attribute type coverage
- Clean mypy run with minimal ignores

**Acceptance Criteria:**
- mypy passes with <20 errors
- Type hints improve IDE autocomplete
- No runtime regressions

---

### 3.2 Docstring Enhancement (4 days)

**Tasks:**
- [ ] Choose docstring style (Google or NumPy) - recommend Google
- [ ] Add docstrings to all public methods
- [ ] Add docstrings to all classes
- [ ] Document complex algorithms with examples

**Priority Areas:**
1. **Public API methods** (master.py, if_wrapper.py public methods)
2. **Complex algorithms** (condition checking, effect resolution)
3. **Transformer classes** (PDDL parsers)
4. **Utility functions** (newly extracted utils)

**Google Style Template:**
```python
def parse_action_input(self, action_input: str) -> dict[str, Any]:
    """Parse player action input string into structured dictionary.

    This method uses Lark parser to transform natural language commands
    into actionable dictionaries that can be processed by the IF interpreter.

    Args:
        action_input: Raw player input string (e.g., "open cupboard")

    Returns:
        Parsed action dictionary with keys:
            - action_name: str, normalized action name
            - parameters: list[str], entity parameters
            - valid: bool, whether parse succeeded

    Raises:
        LarkError: If input cannot be parsed by grammar

    Example:
        >>> interpreter.parse_action_input("take orange")
        {'action_name': 'take', 'parameters': ['orange'], 'valid': True}
    """
```

**Deliverables:**
- Docstrings for all public methods
- Docstrings for all classes
- Examples in complex function docstrings
- Updated documentation standards in CONTRIBUTING.md

**Acceptance Criteria:**
- >90% public method docstring coverage
- Docstrings follow consistent style
- Examples provided for non-trivial functions

---

### 3.3 Error Handling Improvements (2 days)

**Tasks:**
- [ ] Audit all try/except blocks
- [ ] Replace broad `except Exception` with specific exceptions
- [ ] Create custom exception classes:
  ```python
  # adventuregame/exceptions.py
  class AdventureGameError(Exception):
      """Base exception for AdventureGame."""

  class PDDLParseError(AdventureGameError):
      """PDDL parsing failed."""

  class ActionResolutionError(AdventureGameError):
      """Action could not be resolved."""

  class InvalidStateError(AdventureGameError):
      """Game state is invalid."""
  ```

- [ ] Update error handling to use specific exceptions
- [ ] Add error context and messages
- [ ] Log errors appropriately

**Example Transformation:**
```python
# Before
try:
    parsed = self.action_parser.parse(action_input)
except Exception as exception:
    logger.error(f"Parse failed: {exception}")
    return None

# After
try:
    parsed = self.action_parser.parse(action_input)
except lark.exceptions.LarkError as e:
    logger.error("Failed to parse action input '%s': %s", action_input, e)
    raise PDDLParseError(f"Cannot parse '{action_input}'") from e
```

**Deliverables:**
- `exceptions.py` with custom exception hierarchy
- Specific exception handling throughout
- Better error messages

**Acceptance Criteria:**
- No bare `except Exception` blocks
- Errors provide actionable information
- Exception hierarchy is logical

---

## Phase 4: Architecture & Polish (Week 7-8)
**Goal:** Improve overall architecture and finalize improvements

### 4.1 Split Large Modules (5 days)

**Priority: `if_wrapper.py` (4,102 lines)**

**Proposed Structure:**
```
adventuregame/interpreter/
├── __init__.py
├── core.py              # Main AdventureIFInterpreter class (~800 lines)
├── action_resolver.py   # Action resolution logic (~600 lines)
├── condition_checker.py # Condition checking (~400 lines)
├── effect_applier.py    # Effect application (~400 lines)
├── event_handler.py     # Event processing (~400 lines)
├── state_manager.py     # State initialization/management (~600 lines)
├── description_builder.py # Entity descriptions (~400 lines)
└── parsers.py          # Parsing utilities (~500 lines)
```

**Tasks:**
- [ ] Create `interpreter/` package
- [ ] Extract classes/functions to appropriate modules
- [ ] Maintain backward compatibility with imports:
  ```python
  # if_wrapper.py becomes a facade
  from .interpreter.core import AdventureIFInterpreter
  from .interpreter.parsers import IFTransformer, PDDLBaseTransformer

  __all__ = ['AdventureIFInterpreter', 'IFTransformer', 'PDDLBaseTransformer']
  ```
- [ ] Update tests to test individual modules
- [ ] Ensure all integration tests still pass

**Deliverables:**
- `interpreter/` package with 8 modules
- No single module >1000 lines
- Backward compatible imports
- Updated tests

**Acceptance Criteria:**
- Game runs identically
- All tests pass
- Code is more navigable
- Clear separation of concerns

---

### 4.2 Address TODOs (2 days)

**19 TODOs to address:**

**High Priority:**
- [ ] `master.py:384` - Update scoring to clemcore 3.0.2
- [ ] `if_wrapper.py:1518` - De-hardcode mutable predicates tracking

**Medium Priority:**
- [ ] `instancegenerator.py:133` - De-hardcode domain difference
- [ ] `if_wrapper.py:765` - Make event handling more robust
- [ ] `if_wrapper.py:1109` - Retrace why entity lookup can fail
- [ ] `if_wrapper.py:1232` - De-hardcode strings, anticipate localization

**Low Priority / Consider Removing:**
- [ ] Review remaining TODOs
- [ ] Create GitHub issues for future work
- [ ] Remove obsolete TODOs

**Deliverables:**
- ≤5 TODOs remaining
- GitHub issues for deferred work
- Updated code for addressed TODOs

**Acceptance Criteria:**
- High priority TODOs resolved
- Remaining TODOs documented in issues

---

### 4.3 CI/CD Setup (3 days)

**Tasks:**
- [ ] Create `.github/workflows/ci.yml`:
  ```yaml
  name: CI

  on: [push, pull_request]

  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
          with:
            python-version: '3.9'
        - run: pip install -r requirements.txt -r requirements-dev.txt
        - run: black --check .
        - run: isort --check .
        - run: flake8 .
        - run: mypy .
        - run: pytest --cov=adventuregame --cov-report=xml
        - uses: codecov/codecov-action@v3
  ```

- [ ] Add status badges to README.md
- [ ] Set up code coverage tracking (Codecov or similar)
- [ ] Configure branch protection rules

**Deliverables:**
- GitHub Actions CI workflow
- Status badges in README
- Automated quality checks

**Acceptance Criteria:**
- CI runs on all PRs
- All checks pass on main branch
- Coverage reporting works

---

### 4.4 Developer Documentation (2 days)

**Tasks:**
- [ ] Create `CONTRIBUTING.md`:
  - Code style guidelines
  - How to run tests
  - How to add new adventure types
  - Pull request process

- [ ] Create `docs/` directory:
  ```
  docs/
  ├── architecture.md     # System architecture
  ├── pddl_guide.md      # PDDL syntax guide
  ├── adding_actions.md  # How to add new actions
  ├── instance_format.md # Instance file format
  └── development.md     # Development setup
  ```

- [ ] Update README.md with:
  - Development setup instructions
  - Link to CONTRIBUTING.md
  - Link to docs/

- [ ] Add architecture diagrams (optional)

**Deliverables:**
- CONTRIBUTING.md
- docs/ directory with 5 guides
- Updated README.md

**Acceptance Criteria:**
- New contributors can get started from docs
- Architecture is clearly explained
- Code standards are documented

---

## Success Metrics

### Code Quality Metrics

**Before Roadmap:**
- Functions >100 lines: 15+
- Print statements: 1,303
- Test coverage: 0%
- Linting config: None
- Type hint coverage: ~50%
- Docstring coverage: ~20%

**After Roadmap (Targets):**
- Functions >100 lines: 0
- Print statements: <50
- Test coverage: >60%
- Linting config: Complete
- Type hint coverage: >90%
- Docstring coverage: >85%

### Developer Experience Metrics

- Time to onboard new contributor: <2 hours (with docs)
- Time to run full test suite: <5 minutes
- Time to add new adventure type: <4 hours (down from ~8+)
- Code review time: Reduced by 40% (clearer code)

---

## Risk Mitigation

### Potential Risks

1. **Breaking Changes**
   - **Mitigation:** Extensive testing at each phase
   - **Mitigation:** Maintain backward compatibility where possible
   - **Mitigation:** Use feature flags for major changes

2. **Scope Creep**
   - **Mitigation:** Strict phase boundaries
   - **Mitigation:** Defer non-critical items to future phases
   - **Mitigation:** Regular progress reviews

3. **Integration with clemgame Framework**
   - **Mitigation:** Test within framework after each phase
   - **Mitigation:** Keep clemgame team informed
   - **Mitigation:** Document any framework-specific requirements

4. **Time Overruns**
   - **Mitigation:** Buffer time in estimates (20% added)
   - **Mitigation:** Can skip Phase 4.1 (module splitting) if needed
   - **Mitigation:** Prioritize critical improvements

---

## Alternative Approaches

### Incremental vs. Big Bang

**Chosen:** Incremental (4 phases)
**Reasoning:** Allows testing and validation at each step, reduces risk

**Alternative:** Could do "big refactor" all at once
**Rejected:** Too risky, harder to debug issues

### Test-First vs. Test-After

**Chosen:** Test infrastructure first (Phase 1), then improve coverage
**Reasoning:** Need tests to verify refactoring doesn't break functionality

**Alternative:** Write tests for each function before refactoring
**Rejected:** Would slow down initial phases significantly

---

## Dependencies & Prerequisites

### Required Skills/Knowledge
- Python 3.8+
- pytest, unittest
- Black, isort, flake8, mypy
- Git and GitHub
- PDDL (basic understanding)
- Clingo ASP (basic understanding)

### Tools Required
- Python 3.8+
- Git
- Text editor or IDE with Python support
- GitHub account (for CI/CD)

### External Dependencies
- clemgame framework (for integration testing)
- Clingo solver
- Lark parser

---

## Maintenance Plan

### After Roadmap Completion

**Weekly:**
- Monitor CI/CD status
- Review and merge dependabot PRs
- Address new issues

**Monthly:**
- Review code quality metrics
- Update dependencies
- Refactor high-complexity functions

**Quarterly:**
- Review test coverage
- Update documentation
- Performance profiling

**Annually:**
- Major dependency updates
- Architecture review
- Roadmap for next improvements

---

## Appendix: Quick Reference Commands

### Development Setup
```bash
# Clone and setup
git clone <repo>
cd AdventureClemGame
pip install -r adventuregame/requirements.txt
pip install -r adventuregame/requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=adventuregame --cov-report=html

# Run specific test file
pytest tests/test_if_wrapper.py

# Run with verbose output
pytest -v
```

### Code Quality Checks
```bash
# Format code
black adventuregame/
isort adventuregame/

# Lint code
flake8 adventuregame/

# Type check
mypy adventuregame/

# Run all pre-commit hooks
pre-commit run --all-files
```

### Generating Instances
```bash
cd adventuregame
python3 instancegenerator.py
```

### Running Game
```bash
# From clemgame framework root
python3 scripts/cli.py run -g adventuregame -m <model_name>
```

---

## Contact & Support

**Questions or suggestions about this roadmap?**
- Create a GitHub issue
- Tag with `code-quality` label
- Reference this roadmap in discussion

**Progress Tracking:**
- Create GitHub project board
- Link issues to roadmap phases
- Update weekly status

---

**End of Roadmap**

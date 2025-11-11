# Phase 2.3: Print Statement Replacement - Detailed Plan

**Status:** Partially Complete (Main Files Done)
**Priority:** Medium
**Estimated Effort:** 2 days
**Dependencies:** None

---

## Overview

This document provides a detailed plan for replacing all remaining print statements with proper logging throughout the AdventureGame codebase. The goal is to improve debugging capabilities, enable configurable output verbosity, and follow Python logging best practices.

---

## Current Status

### ✅ Completed (Phase 2.3a)
- **if_wrapper.py**: 2 active print statements → logging ✅
- **master.py**: 1 active print statement → logging ✅

### 🔄 Remaining Work

**Active Print Statements by File:**
```
clingo_adventures2-2.py:        49 active print statements
pddl_util.py:                   15 active print statements
clingo_adventures.py:           38 active print statements
new_word_definitions.py:        12 active print statements
new_word_util.py:                8 active print statements
potion_adventures.py:           22 active print statements
clingo_tests.py:                18 active print statements
augment_curated_adventures.py:  10 active print statements
clingo_adventure_solve_checker: 14 active print statements
instances_bug_checks.py:         7 active print statements
readable_instances.py:           5 active print statements
Other files:                    ~20 active print statements

TOTAL REMAINING:                ~218 active print statements
```

**Commented Print Statements:**
```
if_wrapper.py:                  210 commented print statements
pddl_util.py:                    35 commented print statements
Other files:                    ~100 commented print statements

TOTAL COMMENTED:                ~345 print statements
```

---

## Success Criteria

### Primary Goals:
- ✅ <50 active print statements in entire codebase
- ✅ No print statements in production runtime code
- ✅ Appropriate logging levels (debug, info, warning, error)
- ✅ Consistent logging format across all modules
- ✅ Configurable logging verbosity

### Secondary Goals:
- ✅ Remove or document commented-out print statements
- ✅ Add logging configuration to config.json
- ✅ Update development documentation with logging guidelines
- ✅ No regression in debugging capability

---

## Logging Level Guidelines

### When to Use Each Level:

```python
logger.debug()    # Detailed diagnostic info for debugging
                  # Examples: variable values, intermediate states, loop iterations
                  # Only visible with DEBUG logging level

logger.info()     # General informational messages
                  # Examples: major steps completed, configuration loaded, game started
                  # Visible by default in INFO level

logger.warning()  # Something unexpected but recoverable
                  # Examples: missing optional config, fallback used, deprecated feature
                  # Should be investigated but doesn't stop execution

logger.error()    # Error condition, functionality impaired
                  # Examples: file not found, parse error, invalid state
                  # Should be fixed but program can continue

logger.critical() # Critical error, program may need to stop
                  # Examples: configuration fatal error, unrecoverable state
                  # Rare - usually followed by program exit
```

### Categorization Strategy:

For each print statement, ask:

1. **Is this debugging output?** → `logger.debug()`
   - Variable dumps, intermediate values, loop iterations
   - "Verbose mode" output

2. **Is this progress/status information?** → `logger.info()`
   - "Starting generation", "Completed step X", "Loaded config"
   - User-facing status updates

3. **Is this a potential problem?** → `logger.warning()`
   - "Using default value", "Could not find optional file"
   - Recoverable issues

4. **Is this an error?** → `logger.error()`
   - "Parse failed", "Invalid input", "Expected file not found"
   - Actual errors that impact functionality

5. **Should this be removed?** → Delete it
   - Obsolete debugging output, duplicate information
   - Output that serves no purpose

---

## File-by-File Replacement Plan

### Priority 1: Production Runtime Files

#### 1. `resources/pddl_util.py` (15 print statements)

**File Purpose:** PDDL parsing utilities used at runtime

**Print Statement Analysis:**
```bash
$ grep -n "^\s*print(" adventuregame/resources/pddl_util.py
```

**Categorization:**
- Debug output (variable dumps) → `logger.debug()`
- Parse errors → `logger.error()`
- Status messages → `logger.info()`

**Replacement Strategy:**
```python
# Add logger at top of file
import logging
logger = logging.getLogger(__name__)

# Example replacements:
# Before:
print("Parsing action:", action_name)
print("Action parameters:", parameters)

# After:
logger.debug("Parsing action: %s", action_name)
logger.debug("Action parameters: %s", parameters)
```

**Estimated Time:** 1 hour

---

#### 2. `instances_bug_checks.py` (7 print statements)

**File Purpose:** Validation checks for instances

**Print Statement Analysis:**
```bash
$ grep -n "^\s*print(" adventuregame/instances_bug_checks.py
```

**Categorization:**
- Validation results → `logger.info()` or `logger.warning()`
- Bug detection → `logger.error()`

**Replacement Strategy:**
```python
# Before:
print(f"Bug found in instance {instance_id}: {bug_description}")
print(f"Checked {num_instances} instances")

# After:
logger.error("Bug found in instance %s: %s", instance_id, bug_description)
logger.info("Checked %d instances", num_instances)
```

**Estimated Time:** 30 minutes

---

#### 3. `readable_instances.py` (5 print statements)

**File Purpose:** Convert instances to human-readable format

**Categorization:**
- Output formatting → May keep some for stdout output
- Debug info → `logger.debug()`

**Special Consideration:** This might be a CLI tool that *should* use print for output

**Estimated Time:** 30 minutes

---

### Priority 2: Development/Generation Tools

#### 4. `resources/clingo_adventures2-2.py` (49 print statements)

**File Purpose:** Main adventure generation script using Clingo

**This is the LARGEST remaining source of print statements**

**Print Statement Analysis:**
```bash
$ grep -n "^\s*print(" adventuregame/resources/clingo_adventures2-2.py | head -20
```

**Categorization:**
- Generation progress → `logger.info()`
- Clingo output → `logger.debug()`
- Solution validation → `logger.info()` or `logger.warning()`
- Error conditions → `logger.error()`
- Statistics/results → `logger.info()`

**Replacement Strategy:**
```python
# Add logger
import logging
logger = logging.getLogger(__name__)

# Progress updates:
# Before:
print(f"Generating adventure {i+1}/{total}")
print("Running Clingo solver...")
print(f"Solution found in {time_taken}s")

# After:
logger.info("Generating adventure %d/%d", i+1, total)
logger.info("Running Clingo solver...")
logger.info("Solution found in %.2fs", time_taken)

# Debug output:
# Before:
print("Initial state:", initial_state)
print("Goal facts:", goal_facts)

# After:
logger.debug("Initial state: %s", initial_state)
logger.debug("Goal facts: %s", goal_facts)

# Errors:
# Before:
print("ERROR: No solution found!")

# After:
logger.error("No solution found for adventure %d", adventure_idx)
```

**Special Considerations:**
- May want to keep some print statements for CLI output (progress bars, summaries)
- Consider adding a `--verbose` flag to control logging level
- Statistics output might be better as structured data (JSON) rather than logs

**Estimated Time:** 3 hours

---

#### 5. `resources/clingo_adventures.py` (38 print statements)

**File Purpose:** Legacy adventure generation script

**Note:** This appears to be superseded by `clingo_adventures2-2.py`

**Options:**
1. **Replace all prints with logging** (consistent with rest of codebase)
2. **Add deprecation notice and minimal changes** (if truly legacy)
3. **Move to experiments/** (if no longer used)

**Recommended:** Option 3 (move to experiments) or Option 2 (deprecation)

**Estimated Time:** 2 hours (if full replacement) OR 30 minutes (if deprecation notice)

---

#### 6. `resources/potion_adventures.py` (22 print statements)

**File Purpose:** Potion brewing adventure generation

**Categorization:**
- Generation progress → `logger.info()`
- Debug info → `logger.debug()`
- Validation → `logger.warning()` or `logger.error()`

**Replacement Strategy:** Similar to clingo_adventures2-2.py

**Estimated Time:** 1.5 hours

---

#### 7. `resources/new_word_generation/new_word_definitions.py` (12 print statements)

**File Purpose:** Generate new-word action definitions

**Categorization:**
- Word generation progress → `logger.info()`
- Generated definitions → `logger.debug()`

**Estimated Time:** 1 hour

---

#### 8. `resources/new_word_generation/new_word_util.py` (8 print statements)

**File Purpose:** Utilities for new-word generation

**Categorization:**
- Utility function debug output → `logger.debug()`

**Estimated Time:** 30 minutes

---

### Priority 3: Testing/Validation Tools

#### 9. `clingo_adventure_solve_checker.py` (14 print statements)

**File Purpose:** Validate adventure solutions

**Categorization:**
- Validation results → `logger.info()`
- Issues found → `logger.warning()` or `logger.error()`
- Debug info → `logger.debug()`

**Special Consideration:** May want structured output (JSON) for automated validation

**Estimated Time:** 1 hour

---

#### 10. `resources/clingo_tests.py` (18 print statements)

**File Purpose:** Tests for Clingo generation

**Categorization:**
- Test results → Consider using `unittest` framework output
- Test debug info → `logger.debug()`
- Test failures → `logger.error()`

**Recommendation:** Consider restructuring as proper unit tests if not already

**Estimated Time:** 1.5 hours

---

#### 11. `resources/augment_curated_adventures.py` (10 print statements)

**File Purpose:** Augment manually curated adventures

**Categorization:**
- Augmentation progress → `logger.info()`
- Changes made → `logger.debug()`

**Estimated Time:** 45 minutes

---

### Priority 4: Commented Print Statements

#### 12. `if_wrapper.py` (210 commented print statements)

**File Purpose:** IF interpreter - main game logic

**Options:**
1. **Remove all commented prints** (clean slate approach)
2. **Convert to logger.debug() and comment out** (preserve for reference)
3. **Leave as-is** (document as "debug reference")

**Recommendation:** Option 1 (remove) - the code is version controlled, can always be retrieved

**Alternative:** Option 2 for particularly complex sections

**Example:**
```python
# Before:
# print("condition check:", condition)
# print("bindings:", bindings)

# Option 1 (remove):
# [deleted]

# Option 2 (convert and comment):
# logger.debug("condition check: %s", condition)
# logger.debug("bindings: %s", bindings)
```

**Estimated Time:** 2 hours (automated find/replace with manual review)

---

#### 13. Other Files with Commented Prints (~135 statements)

**Files:**
- `pddl_util.py`: 35 commented
- Various other files: ~100 commented

**Recommendation:** Remove all during this phase

**Estimated Time:** 1 hour (automated with review)

---

## Implementation Checklist

### Phase 1: Setup (30 minutes)

- [ ] Review current logging configuration in codebase
- [ ] Add logging configuration section to `config.json` if not present:
  ```json
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": null,
    "console": true
  }
  ```
- [ ] Create helper script for bulk replacements (optional)
- [ ] Set up testing environment

### Phase 2: Priority 1 Files (2-3 hours)

- [ ] `pddl_util.py` (15 statements) - 1 hour
- [ ] `instances_bug_checks.py` (7 statements) - 30 min
- [ ] `readable_instances.py` (5 statements) - 30 min
- [ ] Test runtime behavior after changes
- [ ] Commit: "Phase 2.3b: Replace print statements in runtime utility files"

### Phase 3: Priority 2 Files (6-8 hours)

- [ ] `clingo_adventures2-2.py` (49 statements) - 3 hours
- [ ] `potion_adventures.py` (22 statements) - 1.5 hours
- [ ] `new_word_definitions.py` (12 statements) - 1 hour
- [ ] `new_word_util.py` (8 statements) - 30 min
- [ ] Decide on `clingo_adventures.py` (deprecate or move) - 30 min
- [ ] Test generation tools
- [ ] Commit: "Phase 2.3c: Replace print statements in generation tools"

### Phase 4: Priority 3 Files (3-4 hours)

- [ ] `clingo_adventure_solve_checker.py` (14 statements) - 1 hour
- [ ] `clingo_tests.py` (18 statements) - 1.5 hours
- [ ] `augment_curated_adventures.py` (10 statements) - 45 min
- [ ] Test validation tools
- [ ] Commit: "Phase 2.3d: Replace print statements in testing/validation tools"

### Phase 5: Cleanup (2-3 hours)

- [ ] Remove commented print statements from `if_wrapper.py` - 2 hours
- [ ] Remove commented print statements from other files - 1 hour
- [ ] Final verification that no active prints remain (except intentional)
- [ ] Update `.flake8` or `pyproject.toml` to flag print statements
- [ ] Commit: "Phase 2.3e: Remove commented print statements"

### Phase 6: Documentation & Configuration (1 hour)

- [ ] Update `CONTRIBUTING.md` with logging guidelines
- [ ] Document logging levels in README
- [ ] Add logging configuration examples
- [ ] Test logging configuration changes
- [ ] Commit: "Phase 2.3f: Add logging documentation and configuration"

---

## Automation Opportunities

### Script 1: Print Statement Finder

```python
#!/usr/bin/env python3
"""Find and categorize print statements."""
import os
import re
from pathlib import Path

def find_print_statements(directory, exclude_patterns=None):
    """Find all print statements in Python files."""
    if exclude_patterns is None:
        exclude_patterns = ['experiments/', '__pycache__/', '.git/']

    results = []
    for py_file in Path(directory).rglob('*.py'):
        # Skip excluded paths
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue

        with open(py_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                # Find active print statements
                if re.match(r'^\s*print\(', line):
                    results.append({
                        'file': str(py_file),
                        'line': line_num,
                        'content': line.strip(),
                        'type': 'active'
                    })
                # Find commented print statements
                elif re.match(r'^\s*#\s*print\(', line):
                    results.append({
                        'file': str(py_file),
                        'line': line_num,
                        'content': line.strip(),
                        'type': 'commented'
                    })

    return results

if __name__ == '__main__':
    results = find_print_statements('adventuregame')

    # Group by file
    by_file = {}
    for result in results:
        file_name = result['file']
        if file_name not in by_file:
            by_file[file_name] = {'active': 0, 'commented': 0}
        by_file[file_name][result['type']] += 1

    # Print report
    print("Print Statement Report")
    print("=" * 60)
    for file_name, counts in sorted(by_file.items()):
        print(f"{file_name}:")
        print(f"  Active: {counts['active']}, Commented: {counts['commented']}")
```

### Script 2: Bulk Replacement Helper

```python
#!/usr/bin/env python3
"""Helper script to replace print statements with logging."""
import re
import sys

def suggest_replacement(print_line):
    """Suggest logging replacement for a print statement."""
    # Extract content from print()
    match = re.search(r'print\((.*)\)', print_line)
    if not match:
        return None

    content = match.group(1)

    # Determine logging level based on keywords
    content_lower = content.lower()
    if any(word in content_lower for word in ['error', 'fail', 'exception']):
        level = 'error'
    elif any(word in content_lower for word in ['warn', 'warning']):
        level = 'warning'
    elif any(word in content_lower for word in ['debug', 'dump', 'detail']):
        level = 'debug'
    else:
        level = 'info'

    # Convert f-string to % formatting
    # This is simplified - may need manual adjustment
    converted = content.replace('f"', '"').replace("f'", "'")

    return f"logger.{level}({converted})"

# Interactive mode
if __name__ == '__main__':
    print("Print Statement Replacement Helper")
    print("Enter print statements (Ctrl-D to exit):")
    for line in sys.stdin:
        suggestion = suggest_replacement(line.strip())
        if suggestion:
            print(f"Suggestion: {suggestion}")
        else:
            print("Could not parse print statement")
```

---

## Testing Strategy

### Before Replacement:
1. **Capture baseline output:** Run tools with all print statements and save output
2. **Document expected behavior:** Note what information is useful
3. **Identify critical messages:** Mark which prints are essential

### During Replacement:
1. **Replace in small batches:** One file or section at a time
2. **Test after each batch:** Verify functionality unchanged
3. **Compare output:** Ensure logging provides same information
4. **Adjust levels:** If too verbose/quiet, adjust logger levels

### After Replacement:
1. **Smoke test all tools:** Run generation, validation, testing scripts
2. **Verify logging levels:** Check DEBUG, INFO, WARNING, ERROR all work
3. **Test configuration:** Verify logging config controls output
4. **Performance check:** Ensure no significant slowdown
5. **Documentation review:** Confirm logging guidelines are clear

---

## Logging Configuration

### Recommended Setup in `config_loader.py`:

```python
import logging
import sys

def setup_logging(config):
    """Configure logging based on config settings."""
    log_config = config.get('logging', {})

    # Get logging level
    level_name = log_config.get('level', 'INFO')
    level = getattr(logging, level_name.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    if log_config.get('console', True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler (optional)
    log_file = log_config.get('file')
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger
```

### Update `config.json`:

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

### CLI Flag Support:

```python
# In main scripts, support --verbose flag:
if args.verbose:
    logging.getLogger().setLevel(logging.DEBUG)
```

---

## Quality Checks

### Flake8 Configuration

Add to `.flake8` or `pyproject.toml`:

```ini
[flake8]
# ... other settings ...

# Disallow print statements (use logging instead)
# T001 = print found
extend-ignore = T001
```

Or use `flake8-print` plugin:

```bash
pip install flake8-print
```

Then print statements will be flagged as violations.

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  # ... other repos ...

  - repo: https://github.com/pre-commit/pygrep-hooks
    rev: v1.10.0
    hooks:
      - id: python-no-log-warn  # Prefer logger.warning over logger.warn
      - id: python-check-blanket-noqa

  # Custom hook to check for print statements
  - repo: local
    hooks:
      - id: no-print-statements
        name: Check for print statements
        entry: 'grep -r "^\s*print(" adventuregame/ --exclude-dir=experiments'
        language: system
        pass_filenames: false
        # This will fail if print found - adjust as needed
```

---

## Documentation Updates

### CONTRIBUTING.md Section:

```markdown
## Logging Guidelines

### Use Logging, Not Print

Always use the `logging` module instead of `print()` statements:

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

- **DEBUG**: Detailed diagnostic information (variable dumps, loop iterations)
- **INFO**: General progress/status information
- **WARNING**: Unexpected but recoverable situations
- **ERROR**: Error conditions that impact functionality
- **CRITICAL**: Critical errors requiring immediate attention

### Performance Considerations

For expensive string formatting in debug logs, use lazy evaluation:

```python
# Good - formatting only happens if DEBUG enabled
logger.debug("State: %s", expensive_state_dump())

# Better - condition check before expensive operation
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("State: %s", expensive_state_dump())
```
```

---

## Expected Outcomes

### Metrics Before:

- Active print statements: **~225**
- Commented print statements: **~345**
- Logging usage: **Minimal** (only recent additions)
- Log level control: **None**
- Debugging capability: **Medium** (relies on prints)

### Metrics After:

- Active print statements: **<10** (only CLI tools if needed)
- Commented print statements: **0**
- Logging usage: **Comprehensive**
- Log level control: **Configurable via config.json**
- Debugging capability: **High** (proper logging levels)

### Quality Improvements:

- ✅ Configurable verbosity without code changes
- ✅ Consistent logging format across all modules
- ✅ Ability to log to files for debugging
- ✅ Better control over output in production vs. development
- ✅ Easier to filter and search logs
- ✅ Professional logging practices

---

## Timeline

### Optimistic: 1.5 days
- Experienced with codebase
- Using automation scripts
- Minimal testing required

### Realistic: 2 days
- Normal pace
- Manual categorization and testing
- Thorough verification

### Conservative: 3 days
- Extra testing time
- Unexpected issues with tools
- Additional documentation

**Recommended: Allocate 2 days (16 hours)**

---

## Risks and Mitigation

### Risk 1: Breaking CLI Tools
**Impact:** Medium
**Mitigation:** Keep strategic prints in CLI tools, or replace with proper CLI output (not logging)

### Risk 2: Losing Important Debug Info
**Impact:** Low
**Mitigation:** Review all prints before removing, convert to logger.debug() if useful

### Risk 3: Performance Impact
**Impact:** Very Low
**Mitigation:** Logging is typically very fast; use lazy evaluation for expensive formatting

### Risk 4: Configuration Issues
**Impact:** Low
**Mitigation:** Test logging config thoroughly, provide good defaults

---

## Success Criteria Checklist

Phase 2.3 is complete when:

- [ ] <50 active print statements remain in entire codebase
- [ ] Any remaining prints are documented and justified (CLI output)
- [ ] All production runtime code uses logging
- [ ] All generation tools use logging
- [ ] Commented prints removed or documented
- [ ] Logging configuration added to config.json
- [ ] Documentation updated with logging guidelines
- [ ] All tests pass
- [ ] No loss of debugging capability
- [ ] Team review completed

---

## References

- Original Roadmap: `CODE_QUALITY_ROADMAP.md` (lines 259-301)
- Python Logging Documentation: https://docs.python.org/3/library/logging.html
- Python Logging Best Practices: https://docs.python-guide.org/writing/logging/
- Phase 2.1 Completion: Commit 8cd4080
- Phase 2.3a Completion: Commit fe0860d

---

**Document Version:** 1.0
**Created:** 2025-11-11
**Author:** Claude Code
**Status:** Partially Complete - Awaiting Full Implementation
**Completion:** ~13% (3/226 active prints replaced)

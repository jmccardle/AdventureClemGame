# Pre-commit Setup Guide

**Purpose**: Automatically run code quality checks before committing to prevent CI/CD failures.

## Why Pre-commit Hooks?

Currently, CI/CD breaks on almost every commit because linters don't run automatically. Pre-commit hooks solve this by running checks **locally before you commit**, catching issues early.

## Quick Setup

### 1. Install Development Dependencies

```bash
# From repository root
pip install -r requirements-dev.txt
```

This installs:
- `pre-commit` - Hook framework
- `black` - Code formatter
- `isort` - Import sorter
- `flake8` - Linter
- `mypy` - Type checker
- `pytest` - Test runner

### 2. Install Pre-commit Hooks

```bash
pre-commit install
```

This creates `.git/hooks/pre-commit` which runs automatically on `git commit`.

### 3. Test It Works

```bash
# Run on all files
pre-commit run --all-files

# Or just on staged files
pre-commit run
```

## What Gets Checked

The hooks are configured in `.pre-commit-config.yaml`:

1. **Trailing whitespace** - Removes extra spaces at line ends
2. **End of files** - Ensures files end with newline
3. **YAML/JSON/TOML validation** - Checks syntax
4. **Large files** - Warns about files >1MB
5. **Merge conflicts** - Detects conflict markers
6. **Debug statements** - Catches leftover breakpoints
7. **Black** - Formats Python code (100 char lines)
8. **isort** - Sorts imports alphabetically
9. **flake8** - Linting (style, unused imports, docstrings)
10. **mypy** - Type checking

## Usage Workflow

### Normal Commit (Hooks Run Automatically)

```bash
git add file.py
git commit -m "Add feature"

# Pre-commit runs automatically:
# - If checks pass → commit succeeds
# - If checks fail → commit blocked, files auto-fixed where possible
```

### Auto-fix Workflow

If hooks modify files (black, isort):

```bash
$ git commit -m "Add feature"
black....................................................................Failed
isort....................................................................Failed

# Files were auto-formatted! Just re-add and commit:
$ git add file.py
$ git commit -m "Add feature"
```

### Skip Hooks (Emergency Only)

```bash
# Skip ALL hooks (not recommended)
git commit --no-verify -m "Emergency fix"
```

## Common Issues

### Issue: Hooks are slow on first run

**Cause**: Pre-commit downloads and caches tool environments.

**Solution**: First run takes ~2 minutes, subsequent runs are fast (<5s).

```bash
# Warm up the cache
pre-commit run --all-files
```

### Issue: Mypy errors in existing code

**Cause**: `if_wrapper.py` has existing type errors.

**Temporary solutions**:

1. **Skip mypy for specific commits**:
   ```bash
   SKIP=mypy git commit -m "Fix formatting"
   ```

2. **Disable mypy in pre-commit** (edit `.pre-commit-config.yaml`):
   ```yaml
   - repo: https://github.com/pre-commit/mirrors-mypy
     rev: v1.8.0
     hooks:
       - id: mypy
         exclude: (experiments/|if_wrapper\.py)  # Skip problematic files
   ```

3. **Fix type errors incrementally** (recommended long-term)

### Issue: Flake8 docstring errors

**Error**: `D401 First line should be in imperative mood`

**Fix**: Change docstrings to imperative:
```python
# Bad
def load_data():
    """Loads data from file."""

# Good
def load_data():
    """Load data from file."""
```

### Issue: Import order errors

**Cause**: isort expects specific ordering.

**Fix**: Let isort fix it automatically:
```bash
isort adventuregame/
```

Or configure in `pyproject.toml`:
```toml
[tool.isort]
profile = "black"
line_length = 100
```

## Manual Code Quality Checks

Run checks manually without committing:

```bash
# Format code
black adventuregame/ tests/

# Sort imports
isort adventuregame/ tests/

# Lint
flake8 adventuregame/ tests/

# Type check
mypy adventuregame/

# Run tests
pytest tests/ -v

# All quality checks
pre-commit run --all-files
```

## CI/CD Integration

The CI workflow (`.github/workflows/python-app.yml`) runs the same checks:

```yaml
- name: Format check
  run: black --check adventuregame/

- name: Import check
  run: isort --check-only adventuregame/

- name: Lint
  run: flake8 adventuregame/

- name: Type check
  run: mypy adventuregame/

- name: Test
  run: pytest tests/
```

**Local pre-commit hooks ensure CI passes!**

## Updating Hooks

Keep hooks up to date:

```bash
# Update to latest versions
pre-commit autoupdate

# Commit the updated .pre-commit-config.yaml
git add .pre-commit-config.yaml
git commit -m "Update pre-commit hooks"
```

## Configuration Files

### `.pre-commit-config.yaml`
Defines which hooks to run and their settings.

### `pyproject.toml`
Tool-specific configuration:
```toml
[tool.black]
line-length = 100
target-version = ['py310']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
ignore_missing_imports = true
```

### `.flake8`
Flake8-specific config (if needed):
```ini
[flake8]
max-line-length = 100
exclude = experiments/
```

## Best Practices

### 1. Run Pre-commit Before Pushing

```bash
# Before pushing
pre-commit run --all-files

# If errors, fix and commit
git add .
git commit -m "Fix linting issues"
git push
```

### 2. Keep Commits Focused

If pre-commit makes large formatting changes:

```bash
# Option 1: Separate formatting commit
git add -p  # Selectively stage your changes
git commit -m "Add feature X"

# Then commit formatting separately
git add .
git commit -m "Apply black formatting"

# Option 2: Run formatters first
black adventuregame/file.py
isort adventuregame/file.py
# Make your changes
# Commit everything together
```

### 3. Fix Issues Early

Don't accumulate technical debt:
- Fix linting issues as you code
- Run formatters regularly
- Address type errors incrementally

## For New Developers

Add to onboarding docs:

```bash
# Setup
git clone <repo>
cd AdventureClemGame
pip install -r requirements-dev.txt
pre-commit install

# Verify setup
pre-commit run --all-files
pytest tests/

# You're ready to contribute!
```

## Troubleshooting

### Pre-commit doesn't run

**Check**: Hook installed?
```bash
ls .git/hooks/pre-commit
```

**Fix**: Reinstall
```bash
pre-commit install
```

### Hooks hang/timeout

**Check**: Internet connection (first run downloads tools)

**Fix**: Wait or run offline
```bash
pre-commit run --all-files --hook-stage manual
```

### Can't commit due to errors

**Debug**: See what failed
```bash
pre-commit run --verbose
```

**Quick fix**: Auto-fix what you can
```bash
black adventuregame/
isort adventuregame/
flake8 adventuregame/  # Manual fixes needed
```

## Summary

| Command | Purpose |
|---------|---------|
| `pre-commit install` | Set up hooks (once) |
| `pre-commit run` | Check staged files |
| `pre-commit run --all-files` | Check entire repo |
| `SKIP=mypy git commit` | Skip specific hook |
| `git commit --no-verify` | Skip all hooks (emergency) |
| `pre-commit autoupdate` | Update hook versions |

**Result**: No more CI failures from formatting issues! 🎉

---

**See also**:
- [Pre-commit documentation](https://pre-commit.com/)
- [Black documentation](https://black.readthedocs.io/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)

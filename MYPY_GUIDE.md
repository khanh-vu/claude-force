# Type Checking with mypy (ARCH-04)

## Overview

Type checking is enabled using `mypy` with a gradual typing approach. The configuration is in `pyproject.toml`.

## Running Type Checks

```bash
# Check all files
mypy claude_force/

# Check specific files
mypy claude_force/orchestrator.py

# Install type stubs when prompted
mypy claude_force/ --install-types --non-interactive

# Show error codes
mypy claude_force/ --show-error-codes
```

## Current Status

**Configuration:** `pyproject.toml` [tool.mypy]

- Python version: 3.9+ (mypy requirement)
- Mode: Gradual typing (permissive for now)
- `ignore_missing_imports = true` (third-party packages)
- `disallow_untyped_defs = false` (will enable incrementally)

**Known Issues (P2/P3 work):**

- `semantic_selector.py`: Needs numpy type stubs
- `skills_manager.py`: `any` vs `Any` type confusion
- `quick_start.py`: Complex nested types
- `performance_tracker.py`: Dict annotations needed
- `orchestrator.py`: Return type annotations needed

## Gradual Adoption Strategy

### Phase 1 (P1 - Current)
- ✅ Enable mypy with permissive config
- ✅ Fix critical type errors blocking CI
- ✅ Document usage

### Phase 2 (Future)
- Enable `check_untyped_defs = true`
- Add annotations to core modules
- Fix existing type errors

### Phase 3 (Future)
- Enable `disallow_untyped_defs = true`
- Achieve 100% type coverage
- Add to CI/CD pipeline

## Adding Type Hints

### Example: Function annotations

```python
# Before
def process_data(data):
    return data.upper()

# After
def process_data(data: str) -> str:
    return data.upper()
```

### Example: Class properties

```python
from typing import Optional, Dict, List

class MyClass:
    def __init__(self):
        self.data: Dict[str, List[int]] = {}
        self.optional_value: Optional[str] = None
```

## Common Type Errors

### 1. Missing annotation

```python
# Error: Need type annotation for "items"
items = []

# Fix
items: List[str] = []
```

### 2. Optional attribute access

```python
# Error: Item "None" of "Optional[str]" has no attribute "encode"
value: Optional[str] = get_value()
encoded = value.encode()  # Error!

# Fix
if value is not None:
    encoded = value.encode()
```

### 3. Incompatible types

```python
# Error: Incompatible types in assignment
result: List[str] = None  # Error!

# Fix
result: Optional[List[str]] = None
```

## CI/CD Integration (Future)

When ready to enforce in CI:

```yaml
# .github/workflows/ci.yml
- name: Type Check
  run: |
    pip install mypy types-PyYAML
    mypy claude_force/ --strict
```

## Resources

- [mypy Documentation](https://mypy.readthedocs.io/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [PEP 484](https://www.python.org/dev/peps/pep-0484/) - Type Hints spec

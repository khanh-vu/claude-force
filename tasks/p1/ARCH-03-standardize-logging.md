# ARCH-03: Standardize Logging

**Priority**: P1 - High  
**Estimated Effort**: 2-3 hours  
**Impact**: MEDIUM - Better production debugging  
**Category**: Architecture

## Problem

Inconsistent logging:
- Mix of `print()` and `logger` calls  
- Hard to control log levels  
- Can't redirect to file in production  
- No structured logging

## Solution

Replace all `print()` with `logger` calls.

## Implementation

```python
import logging

logger = logging.getLogger(__name__)

# Before
print(f"Running agent {agent_name}")
print(f"Error: {error}")

# After
logger.info(f"Running agent {agent_name}")
logger.error(f"Error occurred: {error}")
```

## Configuration

```python
# claude_force/logging_config.py
import logging
import os

def setup_logging():
    level = os.getenv('CLAUDE_LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

## Acceptance Criteria

- [ ] All `print()` replaced with `logger` calls  
- [ ] Log levels used correctly (DEBUG/INFO/WARNING/ERROR)  
- [ ] Configurable via environment variable  
- [ ] No regressions in output

**Status**: Not Started  
**Due Date**: Week 2

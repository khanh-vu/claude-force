# SEC-01: Enforce Cache Secret in Production

**Priority**: P1 - High  
**Estimated Effort**: 1 hour  
**Impact**: HIGH - Prevents production security issue  
**Category**: Security

## Problem

Default cache secret allowed in production:
- Security risk (cache poisoning)  
- No warning or error  
- Users may deploy with default secret

**File**: `claude_force/response_cache.py`

## Solution

Raise error if default secret used in production.

## Implementation

```python
class ResponseCache:
    def __init__(self, cache_secret: Optional[str] = None):
        self.cache_secret = cache_secret or os.getenv(
            "CLAUDE_CACHE_SECRET",
            "default_secret_change_in_production"
        )

        # Enforce secure secret in production
        if (os.getenv("CLAUDE_ENV") == "production" and
            self.cache_secret == "default_secret_change_in_production"):
            raise ValueError(
                "SECURITY ERROR: Must set CLAUDE_CACHE_SECRET in production.\n"
                "Generate secure secret with:\n"
                "  python -c 'import secrets; print(secrets.token_hex(32))'"
            )
```

## Documentation Update

```markdown
## Production Deployment

**IMPORTANT**: Set a unique cache secret:

\`\`\`bash
# Generate secret
export CLAUDE_CACHE_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Add to .env
echo "CLAUDE_CACHE_SECRET=$CLAUDE_CACHE_SECRET" >> .env
\`\`\`
```

## Acceptance Criteria

- [ ] Error raised when default secret in production  
- [ ] Clear error message with instructions  
- [ ] Development still works with default  
- [ ] Documentation updated  
- [ ] Tests verify behavior

**Status**: Not Started  
**Due Date**: Week 2

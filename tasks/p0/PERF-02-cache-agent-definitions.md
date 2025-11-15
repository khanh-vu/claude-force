# PERF-02: Cache Agent Definition Files

**Priority**: P0 - Critical  
**Estimated Effort**: 1-2 hours  
**Impact**: HIGH - 50-100% faster for repeated executions  
**Category**: Performance

## Problem

Agent definitions loaded from disk on every execution:
- 1-2ms I/O overhead per execution  
- Unnecessary file reads for repeated agent calls  
- No caching of agent definition files

**File**: `claude_force/orchestrator.py`

## Solution

Add LRU cache for agent definitions using `functools.lru_cache`.

## Implementation

```python
from functools import lru_cache

class AgentOrchestrator:
    @lru_cache(maxlen=128)
    def _load_agent_definition(self, agent_name: str) -> str:
        """Load and cache agent definition (LRU cached)."""
        agent_path = self.config['agents'][agent_name]['file']
        with open(agent_path, 'r') as f:
            return f.read()
            
    def run_agent(self, agent_name: str, task: str) -> AgentResult:
        """Use cached agent definition."""
        agent_definition = self._load_agent_definition(agent_name)
        # ... rest of execution
```

## Testing

```python
def test_agent_definition_cached():
    """Agent definitions are cached after first load."""
    orchestrator = AgentOrchestrator()
    
    # First call - loads from disk
    result1 = orchestrator.run_agent('code-reviewer', task='test')
    
    # Second call - uses cache (no disk I/O)  
    result2 = orchestrator.run_agent('code-reviewer', task='test2')
    
    # Verify both succeeded
    assert result1.success
    assert result2.success
```

## Acceptance Criteria

- [ ] LRU cache implemented  
- [ ] Cache size configurable (default 128)  
- [ ] 50-100% faster for repeated agent calls  
- [ ] Tests verify caching behavior  
- [ ] No breaking changes

**Status**: Not Started  
**Due Date**: Week 1

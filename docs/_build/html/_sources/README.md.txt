# Claude-Force Documentation

This directory contains the complete documentation for claude-force, built with Sphinx.

## Documentation Structure

```
docs/
├── index.md                    # Main documentation index
├── installation.md             # Installation guide
├── quickstart.md              # Quick start guide (TODO)
├── conf.py                    # Sphinx configuration
├── requirements.txt           # Documentation build dependencies
├── api-reference/             # API documentation
│   ├── index.md              # API reference index
│   ├── orchestrator.md       # AgentOrchestrator API
│   ├── semantic-selector.md  # Semantic selection (TODO)
│   ├── hybrid-orchestrator.md # Hybrid orchestration (TODO)
│   ├── performance-tracker.md # Performance tracking (TODO)
│   ├── marketplace.md        # Marketplace API (TODO)
│   └── cli.md                # CLI reference (TODO)
├── guides/                    # In-depth guides
│   ├── index.md              # Guides index (TODO)
│   ├── workflows.md          # Workflow guide (TODO)
│   ├── marketplace.md        # Marketplace guide (TODO)
│   └── performance.md        # Performance optimization (TODO)
└── examples/                  # Real-world examples
    └── index.md              # Examples index (TODO)
```

## Building Documentation

### Prerequisites

Install documentation dependencies:

```bash
pip install -r docs/requirements.txt
```

### Build HTML Documentation

```bash
cd docs
sphinx-build -b html . _build/html
```

Then open `_build/html/index.html` in your browser.

### Live Reload (Development)

For live rebuilding during documentation development:

```bash
pip install sphinx-autobuild
cd docs
sphinx-autobuild . _build/html
```

Then visit http://localhost:8000

## Documentation Status

### ✅ Completed

- [x] Main index page (index.md)
- [x] Installation guide (installation.md)
- [x] API Reference index (api-reference/index.md)
- [x] AgentOrchestrator API documentation (api-reference/orchestrator.md)
- [x] Sphinx configuration (conf.py)
- [x] Build requirements (requirements.txt)

### ⏳ In Progress / TODO

- [ ] Quick Start guide (quickstart.md)
- [ ] API documentation for remaining classes:
  - [ ] SemanticAgentSelector
  - [ ] HybridOrchestrator
  - [ ] PerformanceTracker
  - [ ] WorkflowComposer
  - [ ] AgentMarketplace
  - [ ] CLI commands reference
- [ ] Guides:
  - [ ] Workflow composition
  - [ ] Performance optimization
  - [ ] Semantic selection
  - [ ] Marketplace usage
  - [ ] Architecture overview
  - [ ] Contributing guide
  - [ ] Testing guide
- [ ] Examples:
  - [ ] Real-world usage examples
  - [ ] Integration patterns
  - [ ] Advanced scenarios

## Documentation Guidelines

### Writing Style

- Use clear, concise language
- Include code examples for all features
- Provide real-world use cases
- Link to related documentation
- Use consistent formatting

### Code Examples

All code examples should be:
- Complete and runnable
- Include necessary imports
- Show expected output
- Follow best practices

Example:
```python
from claude_force.orchestrator import AgentOrchestrator

# Initialize
orchestrator = AgentOrchestrator()

# Run agent
result = orchestrator.run_agent(
    "code-reviewer",
    "Review this code"
)

# Output:
# Success: True
# Output: Code review results...
```

### API Documentation Format

Each API doc should include:
1. Overview and purpose
2. Class/function signature
3. Parameter descriptions
4. Return value description
5. Raises (exceptions)
6. Examples
7. Related documentation links

### Markdown vs RST

We use Markdown (.md) for better readability and easier contribution. Sphinx supports Markdown through myst-parser.

## Publishing

### ReadTheDocs

The documentation is configured for ReadTheDocs:

1. Connect repository to ReadTheDocs
2. ReadTheDocs automatically builds on each commit
3. Documentation published at: https://claude-force.readthedocs.io

### Manual HTML Build

To build and publish HTML manually:

```bash
# Build
cd docs
sphinx-build -b html . _build/html

# The _build/html directory can be deployed to:
# - GitHub Pages
# - Netlify
# - Vercel
# - Any static hosting
```

## Contributing to Documentation

1. Write documentation in Markdown (.md)
2. Follow existing structure and style
3. Include code examples
4. Test build locally before committing
5. Submit PR with documentation changes

## Need Help?

- See Sphinx documentation: https://www.sphinx-doc.org/
- See MyST Parser docs: https://myst-parser.readthedocs.io/
- Open an issue: https://github.com/khanh-vu/claude-force/issues

---

**Status**: P1 Task - In Progress
**Target**: Complete all API documentation
**Progress**: ~30% complete (core framework + AgentOrchestrator done)

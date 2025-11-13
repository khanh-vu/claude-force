# Claude Multi-Agent System

A professional multi-agent orchestration system for Claude, designed to handle complex development workflows through specialized agents with clear contracts, governance, and quality gates.

## 🎯 Purpose

This system enables you to:
- Break complex tasks into specialized agent workflows
- Maintain clear separation of concerns between different technical domains
- Enforce quality gates and governance automatically
- Track progress and context across multi-step projects
- Integrate with Claude's built-in skills system

## 📁 Directory Structure

```
.claude/
├── README.md                 # This file
├── claude.json              # Agent router configuration
├── task.md                  # Current task specification
├── work.md                  # Agent output artifacts
├── scorecard.md             # Quality checklist template
├── commands.md              # Common commands reference
├── workflows.md             # Multi-agent workflow patterns
│
├── agents/                  # Agent definitions
│   ├── frontend-architect.md
│   ├── backend-architect.md
│   ├── python-expert.md
│   ├── database-architect.md
│   ├── ui-components-expert.md
│   ├── deployment-integration-expert.md
│   ├── devops-architect.md
│   ├── google-cloud-expert.md
│   ├── qc-automation-expert.md
│   ├── document-writer-expert.md
│   ├── api-documenter.md
│   └── frontend-developer.md
│
├── contracts/               # Agent contracts (one per agent)
│   └── [agent-name].contract
│
├── hooks/                   # Governance system
│   ├── README.md
│   ├── pre-run.md           # Pre-execution checks
│   ├── post-run.md          # Post-execution validation
│   └── validators/
│       ├── scorecard-validator.md
│       ├── write-zone-guard.md
│       ├── secret-scan.md
│       ├── diff-discipline.md
│       ├── format-lint.md
│       └── hierarchy-governance.md
│
├── macros/                  # Reusable instruction blocks
│   └── boot.md              # Agent initialization
│
├── tasks/                   # Task context tracking
│   └── context_session_1.md
│
└── skills/                  # Claude skills integration
    ├── README.md
    └── [skill-name]/
```

## 🚀 Quick Start

### 1. Define Your Task

Edit `.claude/task.md` with your objective:

```markdown
# Task: Build Product Catalog UI

## Objective
Create a server-side rendered product catalog with filtering and search.

## Requirements
- Next.js 14+ App Router
- TypeScript
- Tailwind CSS
- PostgreSQL backend

## Acceptance Criteria
- [ ] Products display in grid layout
- [ ] Filters work for category/price
- [ ] Search returns relevant results
- [ ] Page loads < 2s
```

### 2. Select Agent

Choose the appropriate agent from `.claude/agents/` or use the router:

```bash
# Manual selection
"Run the frontend-architect agent on this task"

# Auto-routing (if implemented)
"Route and execute this task"
```

### 3. Review Output

Check `.claude/work.md` for the agent's deliverables and validate against the scorecard.

### 4. Iterate

Update `task.md` and run the next agent in the workflow.

## 🤖 Available Agents

| Agent | Purpose | Outputs |
|-------|---------|---------|
| **frontend-architect** | App structure, routing, data flow | Architecture brief, component hierarchy |
| **backend-architect** | API design, service architecture | OpenAPI spec, error taxonomy |
| **python-expert** | Python utilities, CLI tools, scripts | Python modules, tests, CLI |
| **database-architect** | Schema design, migrations, indexing | DDL, ERD, query optimization |
| **ui-components-expert** | React components, design system | TSX components, prop types, examples |
| **deployment-integration-expert** | Deployment config, CI/CD | vercel.json, .env.example, deploy docs |
| **devops-architect** | Infrastructure, containerization | Dockerfiles, k8s manifests, IaC |
| **google-cloud-expert** | GCP services integration | Cloud Run, Firestore, IAM configs |
| **qc-automation-expert** | Testing strategy, automation | Test plans, Playwright/Jest specs |
| **document-writer-expert** | Technical documentation | Markdown docs, API references |
| **api-documenter** | API documentation | OpenAPI/Swagger docs |
| **frontend-developer** | Feature implementation | React/Next.js code, tests |

## 📋 Agent Workflow

Each agent follows this pattern:

1. **Load hooks** - Read governance rules from `.claude/hooks/`
2. **Read task** - Parse `.claude/task.md` and context from `tasks/context_session_1.md`
3. **Execute** - Generate artifacts following agent's template
4. **Write output** - Save to `.claude/work.md`
5. **Update context** - Append summary to Write Zone in `context_session_1.md`
6. **Validate** - Self-check against scorecard

## 🔒 Governance & Quality

The hooks system enforces:

- **Pre-run**: Tool/file scope restrictions, task.md existence
- **Post-run**: Scorecard validation, write zone updates, secret scanning
- **Validators**: Atomic checks for specific requirements

### Quality Gates

Every agent output must pass:

- ✅ Scorecard items all PASS or justified FAIL
- ✅ Acceptance checklist completed
- ✅ No secrets in code/examples
- ✅ Minimal diffs (no wide rewrites)
- ✅ Format matches agent specification
- ✅ Write Zone updated with summary

## 🔗 Skills Integration

The system integrates with Claude's native skills:

- **docx**: Document creation/editing
- **xlsx**: Spreadsheet operations
- **pptx**: Presentation generation
- **pdf**: PDF manipulation
- **Custom skills**: User-defined capabilities

Skills are referenced in agent definitions where appropriate.

## 📝 Example Workflow

**Goal**: Build a product catalog for a flower shop

1. **frontend-architect** → Architecture brief, routes, data boundaries
2. **database-architect** → Schema (Product, Category, Image), indexes
3. **backend-architect** → API spec (GET /products), error handling
4. **python-expert** → Image import/ETL script with tests
5. **ui-components-expert** → ProductCard, FilterBar, SearchBox components
6. **frontend-developer** → Implement catalog page with components
7. **qc-automation-expert** → E2E tests for catalog flows
8. **deployment-integration-expert** → Vercel config, env vars

## 🛠️ Advanced Usage

### Contracts

Each agent has a contract in `.claude/contracts/` defining:
- Scope of authority (what decisions it owns)
- Tools available
- Read/write permissions
- Dependencies on other agents
- Change approval requirements

### Write Zones

In `tasks/context_session_1.md`, each agent has a dedicated zone:
- Prevents write conflicts
- Tracks agent progress
- Maintains conversation continuity
- Enables context sharing

### Overlaps

When agent responsibilities overlap:
1. Agent files an Overlap Request
2. Controlling agent approves/denies
3. Decision logged in Write Zone
4. Work proceeds with documented authorization

## Workflows

The system supports multi-agent workflows where multiple agents collaborate on complex tasks:

### Available Workflows

1. **full-stack-feature**: Complete feature from architecture to deployment
   - Frontend Architect → Database Architect → Backend Architect → Python Expert → UI Components Expert → Frontend Developer → QC Automation Expert → Deployment Integration Expert

2. **frontend-only**: Frontend-focused workflows
   - Frontend Architect → UI Components Expert → Frontend Developer → QC Automation Expert

3. **backend-only**: Backend-focused workflows  
   - Backend Architect → Database Architect → Python Expert → QC Automation Expert

4. **documentation**: Documentation workflows
   - Document Writer Expert → API Documenter

See `workflows.md` for detailed workflow patterns and orchestration strategies.

## 🧪 Testing

The system includes:

- **Unit tests** for governance validators
- **Integration tests** for multi-agent workflows
- **Contract tests** to verify agent boundaries
- **Example tasks** with expected outputs

Run tests:

```bash
cd tests/
pytest -v
```

## 📊 Benchmarks & Demo

The system includes comprehensive benchmarks to demonstrate capabilities and measure performance:

### Quick Start

```bash
# Run all benchmarks
python3 benchmarks/scripts/run_all.py

# Generate interactive dashboard
python3 benchmarks/scripts/generate_dashboard.py

# View dashboard
open benchmarks/reports/dashboard/index.html
```

### What's Included

1. **Real-World Scenarios** (`benchmarks/scenarios/`)
   - **Simple**: Add API endpoint, fix bugs, update docs (3 scenarios)
   - **Medium**: User authentication, multi-agent features (1 scenario)
   - **Complex**: Full-stack applications (coming soon)

2. **Performance Metrics** (`benchmarks/metrics/`)
   - Agent selection speed and accuracy
   - Task completion times
   - Quality scores (test coverage, security, code quality)

3. **Interactive Dashboard** (`benchmarks/reports/dashboard/`)
   - Visual performance metrics
   - Accuracy distribution
   - Scenario catalog
   - Detailed test results

### Example Results

Recent benchmark run (15 agents, 6 workflows, 9 skills):
- **Agent Selection Accuracy**: 75% average
- **Selection Time**: 0.01ms average
- **Scenarios Available**: 4 (3 simple, 1 medium)
- **System Coverage**: 100% agents in workflows

See `benchmarks/README.md` for detailed documentation.

## 📚 Documentation

- **commands.md**: Common operations and shortcuts
- **workflows.md**: Multi-agent orchestration patterns
- **Agent files**: Each agent documents its own capabilities
- **Contracts**: Formal authority and boundary definitions

## 🤝 Contributing

To add a new agent:

1. Create `.claude/agents/new-agent.md` with the template
2. Define contract in `.claude/contracts/new-agent.contract`
3. Add to router in `claude.json`
4. Write tests in `tests/test_new_agent.py`
5. Update this README

## 📄 License

This system is designed for use with Claude by Anthropic. Adapt as needed for your projects.

## 🆘 Support

Issues? Check:
1. Hooks validators for failures
2. Agent Write Zones for error context
3. Scorecard for quality gate failures
4. Commands.md for common operations

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Maintained By**: Your Team

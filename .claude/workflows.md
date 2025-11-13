# Multi-Agent Workflows

Proven patterns for orchestrating multiple agents to accomplish complex tasks.

---

## Workflow Structure

Each workflow defines:
- **Goal**: What the workflow achieves
- **Agents**: Ordered list of agents to run
- **Handoffs**: What each agent provides to the next
- **Success Criteria**: When the workflow is complete

---

## Core Workflows

### 1. Full Stack Feature Development

**Goal**: Build a complete feature from architecture to deployment.

**Use Case**: Adding a new user-facing feature that requires frontend, backend, and database work.

**Agents & Order**:

1. **frontend-architect**
   - Defines routes, components structure, data flow
   - **Hands off**: Architecture brief, component contracts

2. **database-architect**
   - Designs schema, migrations, indexes
   - **Hands off**: DDL, ERD, query patterns

3. **backend-architect**
   - Designs API endpoints, services, authentication
   - **Hands off**: OpenAPI spec, error taxonomy

4. **python-expert**
   - Creates utilities, data processing, ETL scripts
   - **Hands off**: Python modules, CLI tools, tests

5. **ui-components-expert**
   - Builds reusable React components
   - **Hands off**: TSX components, props, examples

6. **frontend-developer**
   - Implements feature using components and API
   - **Hands off**: Feature implementation, integration tests

7. **qc-automation-expert**
   - Creates automated tests for the feature
   - **Hands off**: Test suites, coverage reports

8. **deployment-integration-expert**
   - Configures deployment and CI/CD
   - **Hands off**: Deploy configs, environment setup

**Duration**: 8 agent runs  
**Output**: Production-ready feature

---

### 2. Frontend-Only Feature

**Goal**: Build a client-side feature without backend changes.

**Use Case**: Adding a new UI component, improving UX, client-side functionality.

**Agents & Order**:

1. **frontend-architect**
   - Component architecture, state management
   - **Hands off**: Architecture decisions, contracts

2. **ui-components-expert**
   - Builds the components
   - **Hands off**: TSX files, props, styling

3. **frontend-developer**
   - Integrates components into application
   - **Hands off**: Feature implementation

4. **qc-automation-expert**
   - Creates component tests and E2E tests
   - **Hands off**: Test suites

**Duration**: 4 agent runs  
**Output**: Tested frontend feature

---

### 3. Backend-Only API Development

**Goal**: Create new API endpoints and services.

**Use Case**: Adding new backend functionality, third-party integrations, data processing.

**Agents & Order**:

1. **backend-architect**
   - API design, authentication, error handling
   - **Hands off**: OpenAPI spec, architecture decisions

2. **database-architect**
   - Schema changes, migrations, performance tuning
   - **Hands off**: DDL, indexes, query patterns

3. **python-expert**
   - Implements business logic, services, utilities
   - **Hands off**: Python code, CLI, tests

4. **qc-automation-expert**
   - Creates API tests, integration tests
   - **Hands off**: Test suites, test data

**Duration**: 4 agent runs  
**Output**: Tested API endpoints

---

### 4. Infrastructure & Deployment

**Goal**: Set up infrastructure, containerization, and deployment pipeline.

**Use Case**: New project setup, infrastructure migration, deployment optimization.

**Agents & Order**:

1. **devops-architect**
   - Infrastructure design, containerization strategy
   - **Hands off**: Architecture, IaC approach

2. **deployment-integration-expert**
   - Platform-specific configuration (Vercel, AWS, etc.)
   - **Hands off**: Deploy configs, environment variables

3. **google-cloud-expert** (if using GCP)
   - GCP services configuration
   - **Hands off**: Cloud Run, Firestore, IAM configs

4. **qc-automation-expert**
   - Smoke tests, deployment verification
   - **Hands off**: Deployment test suite

**Duration**: 3-4 agent runs  
**Output**: Deployment pipeline ready

---

### 5. Documentation Creation

**Goal**: Create comprehensive documentation for a project or feature.

**Use Case**: New project launch, API documentation, user guides.

**Agents & Order**:

1. **document-writer-expert**
   - Technical documentation, guides, README
   - **Hands off**: Markdown docs

2. **api-documenter**
   - API reference documentation
   - **Hands off**: OpenAPI/Swagger docs, examples

**Duration**: 2 agent runs  
**Output**: Complete documentation

---

### 6. Testing & Quality Assurance

**Goal**: Comprehensive test coverage for existing code.

**Use Case**: Adding tests to legacy code, improving coverage, preparing for refactor.

**Agents & Order**:

1. **qc-automation-expert**
   - Test strategy, test plans, automation setup
   - **Hands off**: Test framework setup, test plans

2. **python-expert** or **frontend-developer**
   - Implement test fixtures, test utilities
   - **Hands off**: Test helpers, mock data

3. **qc-automation-expert**
   - Execute tests, generate coverage reports
   - **Hands off**: Test results, CI/CD integration

**Duration**: 2-3 agent runs  
**Output**: Test suite with coverage

---

## Advanced Workflows

### 7. Microservices Creation

**Goal**: Design and implement a new microservice.

**Agents & Order**:

1. **backend-architect** - Service boundaries, API contracts
2. **database-architect** - Service-specific database design
3. **python-expert** - Service implementation
4. **devops-architect** - Containerization, service mesh
5. **deployment-integration-expert** - Kubernetes manifests
6. **qc-automation-expert** - Service tests, contract tests
7. **api-documenter** - Service documentation

**Duration**: 7 agent runs  
**Output**: Deployed microservice

---

### 8. Database Migration

**Goal**: Migrate database schema or data.

**Agents & Order**:

1. **database-architect** - Migration strategy, new schema design
2. **python-expert** - Data migration scripts, validation
3. **backend-architect** - API compatibility layer during migration
4. **qc-automation-expert** - Migration testing, rollback tests
5. **document-writer-expert** - Migration runbook

**Duration**: 5 agent runs  
**Output**: Safe migration path

---

### 9. Performance Optimization

**Goal**: Improve application performance.

**Agents & Order**:

1. **backend-architect** or **frontend-architect** - Identify bottlenecks, optimization strategy
2. **database-architect** - Query optimization, indexing
3. **python-expert** or **frontend-developer** - Implement optimizations
4. **qc-automation-expert** - Performance testing, benchmarks
5. **document-writer-expert** - Performance analysis report

**Duration**: 5 agent runs  
**Output**: Optimized application

---

### 10. Security Hardening

**Goal**: Improve application security.

**Agents & Order**:

1. **backend-architect** - Security assessment, threat model
2. **database-architect** - Data encryption, access controls
3. **python-expert** or **frontend-developer** - Implement security measures
4. **devops-architect** - Infrastructure security
5. **qc-automation-expert** - Security testing, penetration tests
6. **document-writer-expert** - Security documentation

**Duration**: 6 agent runs  
**Output**: Hardened application

---

## Workflow Coordination

### Sequential Execution

Run agents one at a time, reviewing output before proceeding:

```
1. Run agent A
2. Review work.md
3. Validate with scorecard
4. Update task.md if needed
5. Run agent B
6. ...
```

**Pros**: Maximum control, can adjust course  
**Cons**: Slower, requires human review at each step

---

### Batch Execution

Run multiple agents with predefined stopping points:

```
1. Run agents A, B, C in sequence
2. Review accumulated output
3. Validate and proceed or adjust
4. Run agents D, E, F
5. Final review
```

**Pros**: Faster for well-understood workflows  
**Cons**: May need backtracking if issues arise

---

### Parallel Execution (Advanced)

Some agents can run in parallel if they don't have dependencies:

```
Parallel:
- Agent A (frontend work)
- Agent B (backend work)
- Agent C (documentation)

Then sequential:
- Agent D (integration)
- Agent E (testing)
```

**Pros**: Maximum speed  
**Cons**: Requires careful dependency management

---

## Workflow Decision Tree

```
New Feature?
├─ Requires Backend?
│  ├─ Yes → Full Stack Workflow
│  └─ No → Frontend-Only Workflow
│
New Project?
├─ Infrastructure First?
│  ├─ Yes → Infrastructure → Full Stack
│  └─ No → Full Stack → Infrastructure
│
Existing Code?
├─ Bug Fix? → Single Agent (relevant expert)
├─ Refactor? → Architecture Agent → Implementation Agent → QA
├─ Testing? → QA Workflow
└─ Documentation? → Documentation Workflow
```

---

## Workflow Customization

### Creating Custom Workflows

1. **Identify the goal**: What needs to be accomplished?
2. **List required capabilities**: What skills are needed?
3. **Map to agents**: Which agents provide those capabilities?
4. **Order by dependencies**: What information does each agent need from previous agents?
5. **Define handoffs**: What artifacts pass between agents?
6. **Set success criteria**: When is the workflow complete?

### Example: Adding AI Image Generation

**Goal**: Add AI image generation feature to app

**Custom Workflow**:
1. **backend-architect** - API for image generation service
2. **python-expert** - Integration with OpenAI/Stability AI
3. **frontend-architect** - UI for image generation
4. **ui-components-expert** - Image generation components
5. **frontend-developer** - Feature integration
6. **qc-automation-expert** - Test image generation flows
7. **deployment-integration-expert** - Configure API keys, rate limits

---

## Workflow Templates

### Template: Data Processing Pipeline

```markdown
## Goal
Build a data processing pipeline

## Agents
1. backend-architect - Pipeline architecture
2. database-architect - Data storage design
3. python-expert - ETL scripts, processing logic
4. qc-automation-expert - Data validation tests

## Success Criteria
- [ ] Data ingestion working
- [ ] Transformations validated
- [ ] Output format correct
- [ ] Error handling robust
- [ ] Tests passing
```

### Template: API-First Development

```markdown
## Goal
Build feature starting with API design

## Agents
1. api-documenter - OpenAPI specification
2. backend-architect - Implementation architecture
3. python-expert - API implementation
4. qc-automation-expert - API contract tests
5. frontend-architect - Frontend integration design
6. frontend-developer - UI implementation

## Success Criteria
- [ ] API spec complete
- [ ] Backend implemented
- [ ] Tests passing
- [ ] Frontend integrated
- [ ] Documentation complete
```

---

## Workflow Monitoring

Track workflow progress in `context_session_1.md`:

```markdown
## Workflow: Full Stack Feature - Product Catalog

**Started**: 2025-11-13
**Status**: In Progress (4/8 agents complete)

### Completed
- [x] frontend-architect (2025-11-13 10:00)
- [x] database-architect (2025-11-13 11:30)
- [x] backend-architect (2025-11-13 13:00)
- [x] python-expert (2025-11-13 14:30)

### Current
- [ ] ui-components-expert (in progress)

### Remaining
- [ ] frontend-developer
- [ ] qc-automation-expert
- [ ] deployment-integration-expert

### Blockers
None

### Notes
Database schema approved. API spec reviewed and validated.
```

---

## Workflow Optimization Tips

1. **Front-load architecture**: Architecture agents first prevent rework
2. **Parallel when possible**: Independent work can happen simultaneously
3. **Batch similar work**: Group related agent executions
4. **Validate early**: Catch issues before they propagate
5. **Document decisions**: Clear Write Zones prevent confusion
6. **Plan handoffs**: Define exactly what each agent provides
7. **Set checkpoints**: Review after major milestones
8. **Allow iteration**: Workflows aren't always linear

---

## Common Workflow Issues

### Issue: Agent Blocked
**Symptom**: Agent can't proceed due to missing information  
**Solution**: Run prerequisite agents first, or update task.md with needed context

### Issue: Conflicting Output
**Symptom**: Later agents contradict earlier agents  
**Solution**: Review contracts, file overlap request, or adjust agent order

### Issue: Incomplete Handoff
**Symptom**: Next agent doesn't have required artifacts  
**Solution**: Previous agent must update Write Zone with complete handoff

### Issue: Quality Gate Failure
**Symptom**: Scorecard shows multiple FAILs  
**Solution**: Agent must address issues before workflow continues

---

**Version**: 1.0.0  
**Last Updated**: November 2025

---

## Next Steps

After defining your workflow:
1. Create `.claude/task.md` with clear objectives
2. Initialize `.claude/tasks/context_session_1.md`
3. Execute agents in order
4. Review output after each agent
5. Validate with scorecard
6. Proceed to next agent
7. Compile final artifacts when complete

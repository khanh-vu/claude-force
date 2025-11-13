# Agent Skills Matrix

**Purpose**: Quick reference guide for selecting the right agent based on required skills and expertise.

**Last Updated**: 2025-11-13
**Version**: 1.0.0

---

## 📋 Quick Agent Selector

### By Task Type

| Task Type | Primary Agent | Supporting Agents | Skills Needed |
|-----------|--------------|-------------------|---------------|
| **New Feature Architecture** | frontend-architect, backend-architect | database-architect, security-specialist | Architecture design, System design, API design |
| **Feature Implementation** | frontend-developer, python-expert | ui-components-expert | Coding, Framework knowledge, Testing |
| **Bug Investigation** | bug-investigator | code-reviewer | Debugging, Log analysis, Root cause analysis |
| **Code Review** | code-reviewer | security-specialist, performance-optimizer | Code quality, Best practices, Security |
| **Security Audit** | security-specialist | code-reviewer | OWASP, Authentication, Vulnerability scanning |
| **Performance Issues** | performance-optimizer | database-architect, devops-architect | Profiling, Optimization, Caching |
| **Database Design** | database-architect | backend-architect | SQL, NoSQL, Schema design, Indexing |
| **API Design** | backend-architect | api-documenter | REST, GraphQL, OpenAPI, Authentication |
| **UI/UX Components** | ui-components-expert | frontend-developer | React, Design systems, Accessibility |
| **Testing** | qc-automation-expert | code-reviewer | Test automation, E2E testing, Unit testing |
| **Deployment** | deployment-integration-expert | devops-architect | CI/CD, Cloud platforms, Containers |
| **Infrastructure** | devops-architect | deployment-integration-expert | Docker, Kubernetes, IaC, Monitoring |
| **Documentation** | document-writer-expert | api-documenter | Technical writing, Markdown, Diagrams |
| **Refactoring** | refactoring-expert | code-reviewer | Design patterns, SOLID, Code smells |
| **Requirements** | requirements-analyst | tech-lead-mentor | Requirements engineering, User stories |
| **Mobile Development** | mobile-developer | ui-components-expert | React Native, iOS, Android |

---

## 🎯 Agent Skills Breakdown

### 1. frontend-architect

**Role**: Senior Frontend Architect
**Priority**: 1 (Critical)

#### Core Skills
- **Frameworks**: Next.js 13/14, React 18+, Remix, Astro
- **Languages**: TypeScript (advanced), JavaScript (ES2023+)
- **Styling**: Tailwind CSS, CSS-in-JS, CSS Modules, Sass/SCSS
- **State**: React Server Components, Zustand, Jotai, TanStack Query
- **Build Tools**: Vite, Turbopack, Webpack, esbuild

#### Specialized Skills
- Architecture patterns (MVC, MVVM, Atomic Design)
- Micro-frontends, Monorepo strategies
- SSR, SSG, ISR, Streaming SSR
- Core Web Vitals optimization
- SEO & Accessibility (WCAG 2.1 AA)

#### Best For
✅ Application architecture design
✅ Technology stack selection
✅ Routing and navigation strategy
✅ Performance optimization planning
✅ Component hierarchy design

#### Avoid For
❌ Component implementation (use ui-components-expert)
❌ Backend logic (use backend-architect)
❌ Bug fixes (use bug-investigator)

---

### 2. backend-architect

**Role**: Senior Backend Architect
**Priority**: 1 (Critical)

#### Core Skills
- **Languages**: Node.js, Python, Go, Java
- **Frameworks**: Express, Fastify, FastAPI, Django, Spring Boot
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **APIs**: REST, GraphQL, gRPC, WebSockets
- **Authentication**: JWT, OAuth 2.0, SAML, Session-based

#### Specialized Skills
- Microservices architecture
- Event-driven architecture (Kafka, RabbitMQ)
- CQRS and Event Sourcing
- API gateway patterns
- Service mesh (Istio, Linkerd)
- Distributed systems

#### Best For
✅ API design and architecture
✅ Microservices design
✅ Data flow architecture
✅ Authentication/authorization strategy
✅ Service integration patterns

#### Avoid For
❌ Frontend design (use frontend-architect)
❌ Database schema (use database-architect)
❌ Implementation (use python-expert)

---

### 3. database-architect

**Role**: Database Architect / DBA
**Priority**: 1 (Critical)

#### Core Skills
- **SQL Databases**: PostgreSQL, MySQL, Oracle, SQL Server
- **NoSQL**: MongoDB, Cassandra, DynamoDB, Redis
- **Search**: Elasticsearch, Apache Solr
- **Graph**: Neo4j, Amazon Neptune
- **Time-series**: InfluxDB, TimescaleDB

#### Specialized Skills
- Schema design and normalization
- Indexing strategies
- Query optimization
- Sharding and partitioning
- Replication and high availability
- Migration strategies
- Data modeling (ERD, Dimensional)

#### Best For
✅ Database schema design
✅ Query optimization
✅ Index strategy
✅ Data migration planning
✅ Database technology selection

#### Avoid For
❌ API design (use backend-architect)
❌ Frontend data flow (use frontend-architect)
❌ Data analysis (use data-engineer if available)

---

### 4. python-expert

**Role**: Python Developer / Automation Expert
**Priority**: 2 (High)

#### Core Skills
- **Languages**: Python 3.10+, Type hints
- **Frameworks**: FastAPI, Django, Flask, Celery
- **Libraries**: Pandas, NumPy, Requests, SQLAlchemy
- **Testing**: pytest, unittest, hypothesis
- **CLI**: Click, Typer, argparse

#### Specialized Skills
- Async/await patterns
- Data processing and ETL
- API development (FastAPI)
- Automation scripts
- CLI tool development
- Background job processing

#### Best For
✅ Backend API implementation
✅ Data processing scripts
✅ Automation tools
✅ CLI applications
✅ Background job processors

#### Avoid For
❌ Frontend code (use frontend-developer)
❌ Mobile apps (use mobile-developer)
❌ Database design (use database-architect)

---

### 5. ui-components-expert

**Role**: UI Component Library Developer
**Priority**: 2 (High)

#### Core Skills
- **Frameworks**: React, Vue, Svelte
- **Languages**: TypeScript, JavaScript
- **Styling**: Tailwind, CSS Modules, Styled Components
- **Design Systems**: Storybook, Figma integration
- **Accessibility**: ARIA, WCAG, Screen readers

#### Specialized Skills
- Component API design
- Design token systems
- Responsive design
- Animation (Framer Motion, React Spring)
- Component documentation
- Atomic design methodology

#### Best For
✅ Reusable component development
✅ Design system implementation
✅ Component library creation
✅ Accessibility implementation
✅ UI patterns and widgets

#### Avoid For
❌ Application architecture (use frontend-architect)
❌ Page-level implementation (use frontend-developer)
❌ Backend components (use backend developer)

---

### 6. frontend-developer

**Role**: Frontend Feature Developer
**Priority**: 2 (High)

#### Core Skills
- **Frameworks**: Next.js, React, Vue, Angular
- **Languages**: TypeScript, JavaScript
- **Styling**: Tailwind, CSS, Sass
- **State**: Redux, Context API, Zustand
- **APIs**: REST, GraphQL, fetch, axios

#### Specialized Skills
- Page and feature implementation
- Form handling and validation
- API integration
- Client-side routing
- Data fetching and caching
- Error handling

#### Best For
✅ Feature implementation
✅ Page development
✅ API integration
✅ Form and data handling
✅ Client-side logic

#### Avoid For
❌ Architecture decisions (use frontend-architect)
❌ Component library design (use ui-components-expert)
❌ Backend logic (use python-expert)

---

### 7. deployment-integration-expert

**Role**: Deployment Engineer
**Priority**: 3 (Medium)

#### Core Skills
- **Platforms**: Vercel, Netlify, AWS Amplify, Heroku
- **CI/CD**: GitHub Actions, GitLab CI, CircleCI
- **Cloud**: AWS, Google Cloud, Azure basics
- **Containers**: Docker basics
- **Monitoring**: Basic logging and monitoring

#### Specialized Skills
- Deployment configuration
- Environment variable management
- Build optimization
- Edge computing setup
- Serverless deployment
- Static site generation

#### Best For
✅ Application deployment configuration
✅ CI/CD pipeline setup
✅ Environment management
✅ Build process optimization
✅ Platform-specific configuration

#### Avoid For
❌ Infrastructure design (use devops-architect)
❌ Complex orchestration (use devops-architect)
❌ Production incident response (use devops-architect)

---

### 8. devops-architect

**Role**: DevOps Engineer / SRE
**Priority**: 2 (High)

#### Core Skills
- **Containers**: Docker, Kubernetes, Docker Compose
- **IaC**: Terraform, CloudFormation, Pulumi
- **CI/CD**: Jenkins, GitHub Actions, ArgoCD
- **Cloud**: AWS, GCP, Azure (advanced)
- **Monitoring**: Prometheus, Grafana, ELK Stack

#### Specialized Skills
- Kubernetes orchestration
- Infrastructure as Code
- Service mesh configuration
- Monitoring and observability
- Incident response
- Disaster recovery
- High availability design

#### Best For
✅ Infrastructure architecture
✅ Kubernetes setup
✅ Monitoring and alerting
✅ Disaster recovery planning
✅ High availability design

#### Avoid For
❌ Application code (use developers)
❌ Simple deployments (use deployment-integration-expert)
❌ Frontend infrastructure (use frontend-architect)

---

### 9. google-cloud-expert

**Role**: Google Cloud Platform Specialist
**Priority**: 2 (High)

#### Core Skills
- **Compute**: Cloud Run, GKE, App Engine, Cloud Functions
- **Storage**: Cloud Storage, Firestore, Cloud SQL, BigQuery
- **Networking**: VPC, Load Balancing, Cloud CDN
- **Security**: IAM, Secret Manager, Cloud Armor
- **Data**: BigQuery, Dataflow, Pub/Sub

#### Specialized Skills
- GCP architecture design
- Serverless patterns on GCP
- Firebase integration
- Cloud Native applications
- Cost optimization
- GCP security best practices

#### Best For
✅ GCP-specific architecture
✅ Firebase integration
✅ Cloud Run deployment
✅ BigQuery data warehousing
✅ GCP cost optimization

#### Avoid For
❌ AWS-specific tasks (generalize or request AWS expert)
❌ Application logic (use developers)
❌ Frontend design (use frontend-architect)

---

### 10. qc-automation-expert

**Role**: QA Engineer / Test Automation Engineer
**Priority**: 3 (Medium)

#### Core Skills
- **E2E Testing**: Playwright, Cypress, Selenium
- **Unit Testing**: Jest, Vitest, pytest, JUnit
- **API Testing**: Postman, REST Assured, Supertest
- **Performance**: k6, JMeter, Lighthouse
- **Visual Regression**: Percy, Chromatic, BackstopJS

#### Specialized Skills
- Test strategy planning
- Test automation frameworks
- CI/CD integration
- Test data management
- Coverage analysis
- Mutation testing
- Exploratory testing guidance

#### Best For
✅ Test strategy creation
✅ E2E test automation
✅ Unit test creation
✅ API testing
✅ Performance testing setup

#### Avoid For
❌ Application development (use developers)
❌ Manual QA only (needs automation focus)
❌ Security testing (use security-specialist)

---

### 11. document-writer-expert

**Role**: Technical Writer
**Priority**: 3 (Medium)

#### Core Skills
- **Formats**: Markdown, AsciiDoc, reStructuredText
- **Tools**: MkDocs, Docusaurus, GitBook
- **Diagrams**: Mermaid, PlantUML, Draw.io
- **Skills**: DOCX generation (via Claude skills)
- **Version Control**: Git, docs-as-code

#### Specialized Skills
- Technical documentation structure
- User guide creation
- Tutorial writing
- README optimization
- Documentation site setup
- Information architecture
- Style guide adherence

#### Best For
✅ Technical documentation
✅ User guides and tutorials
✅ README files
✅ Architecture documentation
✅ Developer onboarding docs

#### Avoid For
❌ API documentation (use api-documenter)
❌ Code comments (use code-reviewer)
❌ Marketing copy (out of scope)

---

### 12. api-documenter

**Role**: API Documentation Specialist
**Priority**: 3 (Medium)

#### Core Skills
- **Formats**: OpenAPI 3.0/3.1, Swagger, AsyncAPI
- **Tools**: Swagger UI, Redoc, Postman
- **Languages**: YAML, JSON
- **APIs**: REST, GraphQL, gRPC, WebSockets
- **Standards**: JSON Schema, API Blueprint

#### Specialized Skills
- OpenAPI specification writing
- API design documentation
- Interactive API documentation
- Code generation from specs
- API versioning documentation
- Authentication documentation
- SDK documentation

#### Best For
✅ OpenAPI/Swagger specs
✅ API reference documentation
✅ API integration guides
✅ Postman collections
✅ GraphQL schema documentation

#### Avoid For
❌ General documentation (use document-writer-expert)
❌ API implementation (use backend-architect)
❌ User guides (use document-writer-expert)

---

## 🆕 Recommended New Agents

### code-reviewer (CRITICAL)

**Role**: Senior Code Reviewer
**Priority**: 1 (Critical)

#### Core Skills (Planned)
- **Languages**: TypeScript, JavaScript, Python, Go, Java
- **Patterns**: SOLID, Design Patterns, Anti-patterns
- **Security**: OWASP Top 10, Common vulnerabilities
- **Performance**: Complexity analysis, Memory leaks
- **Quality**: Code smells, Technical debt

#### Specialized Skills (Planned)
- Static code analysis
- Security vulnerability detection
- Performance bottleneck identification
- Best practices enforcement
- Refactoring suggestions
- Test coverage analysis
- Code complexity metrics

#### Best For (Planned)
✅ Pre-commit code review
✅ Pull request review
✅ Security vulnerability scan
✅ Code quality assessment
✅ Refactoring recommendations

---

### security-specialist (CRITICAL)

**Role**: Security Engineer / AppSec
**Priority**: 1 (Critical)

#### Core Skills (Planned)
- **Security**: OWASP Top 10, CWE, CVE
- **Authentication**: OAuth, SAML, JWT, MFA
- **Encryption**: TLS, AES, RSA, Key management
- **Standards**: PCI-DSS, GDPR, SOC 2, HIPAA
- **Tools**: Security scanners, SAST, DAST

#### Specialized Skills (Planned)
- Threat modeling
- Vulnerability assessment
- Penetration testing guidance
- Security architecture review
- Compliance checking
- Incident response planning
- Security code review

#### Best For (Planned)
✅ Security architecture review
✅ Vulnerability scanning
✅ Authentication/authorization design
✅ Compliance checking
✅ Security best practices

---

### bug-investigator (CRITICAL)

**Role**: Senior Debugger / Bug Detective
**Priority**: 1 (Critical)

#### Core Skills (Planned)
- **Debugging**: GDB, LLDB, Chrome DevTools, pdb
- **Log Analysis**: ELK, Splunk, CloudWatch Logs
- **Profiling**: Performance profilers, Memory profilers
- **Tracing**: OpenTelemetry, Jaeger, Zipkin
- **Error Tracking**: Sentry, Rollbar, Bugsnag

#### Specialized Skills (Planned)
- Root cause analysis
- Stack trace interpretation
- Memory leak detection
- Race condition identification
- Hypothesis testing
- Reproduction step creation
- Fix verification

#### Best For (Planned)
✅ Bug investigation
✅ Log analysis
✅ Root cause identification
✅ Performance debugging
✅ Memory leak detection

---

### performance-optimizer (HIGH)

**Role**: Performance Engineer
**Priority**: 2 (High)

#### Core Skills (Planned)
- **Profiling**: Chrome DevTools, Python profilers, Go profiler
- **Monitoring**: New Relic, Datadog, Application Insights
- **Databases**: Query optimization, Index tuning
- **Caching**: Redis, Memcached, CDN
- **Frontend**: Core Web Vitals, Bundle optimization

#### Specialized Skills (Planned)
- Performance profiling
- Bottleneck identification
- Load testing (k6, JMeter, Gatling)
- Database query optimization
- Caching strategy design
- CDN optimization
- Code-level optimization

#### Best For (Planned)
✅ Performance profiling
✅ Bottleneck identification
✅ Database optimization
✅ Frontend performance
✅ Load testing

---

### requirements-analyst (HIGH)

**Role**: Business Analyst / Requirements Engineer
**Priority**: 2 (High)

#### Core Skills (Planned)
- **Methods**: User stories, Use cases, BDD
- **Tools**: JIRA, Confluence, Miro, Figma
- **Techniques**: Requirement elicitation, Prioritization
- **Modeling**: Process flows, User flows, Wireframes
- **Documentation**: Requirements specs, Acceptance criteria

#### Specialized Skills (Planned)
- Requirement clarification
- Stakeholder management
- Edge case identification
- Acceptance criteria definition
- Risk identification
- Scope management
- Feasibility analysis

#### Best For (Planned)
✅ Requirement clarification
✅ User story refinement
✅ Edge case identification
✅ Acceptance criteria definition
✅ Scope definition

---

### tech-lead-mentor (HIGH)

**Role**: Technical Lead / Engineering Mentor
**Priority**: 2 (High)

#### Core Skills (Planned)
- **Leadership**: Technical leadership, Decision-making
- **Architecture**: System design, Trade-off analysis
- **Best Practices**: Code quality, Design patterns
- **Mentoring**: Code review, Knowledge sharing
- **Communication**: Documentation, Presentations

#### Specialized Skills (Planned)
- Architecture decision guidance
- Technology selection
- Best practices recommendations
- Technical debt management
- Team coordination
- Career development guidance
- Learning path creation

#### Best For (Planned)
✅ Architecture decisions
✅ Technology selection
✅ Best practices guidance
✅ Technical debt assessment
✅ Trade-off analysis

---

### refactoring-expert (HIGH)

**Role**: Refactoring Specialist
**Priority**: 2 (High)

#### Core Skills (Planned)
- **Patterns**: Design patterns, Refactoring patterns
- **Principles**: SOLID, DRY, KISS, YAGNI
- **Techniques**: Extract method, Rename, Move
- **Testing**: Refactoring with tests, Test coverage
- **Tools**: IDE refactoring, AST manipulation

#### Specialized Skills (Planned)
- Code smell detection
- Refactoring strategy planning
- Safe refactoring steps
- Test-driven refactoring
- Legacy code modernization
- Performance refactoring
- Design pattern application

#### Best For (Planned)
✅ Code smell identification
✅ Refactoring planning
✅ Legacy code improvement
✅ Design pattern application
✅ Technical debt reduction

---

### mobile-developer (HIGH)

**Role**: Mobile App Developer
**Priority**: 2 (High)

#### Core Skills (Planned)
- **Cross-platform**: React Native, Flutter, Expo
- **iOS**: Swift, SwiftUI, UIKit, Xcode
- **Android**: Kotlin, Jetpack Compose, Android Studio
- **State**: Redux, MobX, Provider, Bloc
- **Navigation**: React Navigation, Flutter Navigator

#### Specialized Skills (Planned)
- Native module integration
- Platform-specific features
- App store deployment
- Push notifications
- Offline functionality
- Mobile performance optimization
- Deep linking

#### Best For (Planned)
✅ Mobile app development
✅ React Native apps
✅ iOS native development
✅ Android native development
✅ Mobile UI/UX implementation

---

## 📊 Skills Comparison Matrix

### By Technology Stack

| Technology | Agents with Expertise | Proficiency Level |
|------------|----------------------|-------------------|
| **TypeScript** | frontend-architect, frontend-developer, ui-components-expert, code-reviewer* | Advanced / High / High / Advanced |
| **React** | frontend-architect, frontend-developer, ui-components-expert, mobile-developer* | Advanced / Advanced / Expert / High |
| **Next.js** | frontend-architect, frontend-developer | Expert / Advanced |
| **Node.js** | backend-architect, python-expert (secondary) | Advanced / Medium |
| **Python** | python-expert, backend-architect (secondary), data-engineer* | Expert / Medium / Advanced |
| **PostgreSQL** | database-architect, backend-architect | Expert / Advanced |
| **MongoDB** | database-architect, backend-architect | Advanced / Advanced |
| **Docker** | devops-architect, deployment-integration-expert | Expert / Medium |
| **Kubernetes** | devops-architect, google-cloud-expert | Expert / Advanced |
| **AWS** | devops-architect, deployment-integration-expert | Advanced / Medium |
| **GCP** | google-cloud-expert, devops-architect | Expert / Advanced |
| **Testing** | qc-automation-expert, code-reviewer* | Expert / Advanced |
| **Security** | security-specialist*, code-reviewer* | Expert / Advanced |

*Planned/Recommended agent

---

## 🎯 Agent Selection Decision Tree

```
START: What do you need?
│
├─ 🏗️ Architecture/Design
│  ├─ Frontend? → frontend-architect
│  ├─ Backend? → backend-architect
│  ├─ Database? → database-architect
│  ├─ Full System? → solution-architect*
│  └─ Mobile? → mobile-developer*
│
├─ 💻 Implementation
│  ├─ Frontend pages? → frontend-developer
│  ├─ UI components? → ui-components-expert
│  ├─ Backend/Python? → python-expert
│  ├─ Mobile app? → mobile-developer*
│  └─ Data pipeline? → data-engineer*
│
├─ 🐛 Issues/Problems
│  ├─ Bug investigation? → bug-investigator*
│  ├─ Performance issues? → performance-optimizer*
│  ├─ Security issues? → security-specialist*
│  └─ Code quality? → code-reviewer*
│
├─ 🔍 Review/Audit
│  ├─ Code review? → code-reviewer*
│  ├─ Security audit? → security-specialist*
│  ├─ Performance audit? → performance-optimizer*
│  └─ Architecture review? → tech-lead-mentor*
│
├─ 🔧 Improvement
│  ├─ Refactoring? → refactoring-expert*
│  ├─ Performance optimization? → performance-optimizer*
│  ├─ Technical debt? → tech-lead-mentor*
│  └─ Code quality? → code-reviewer*
│
├─ 🧪 Testing
│  ├─ Test strategy? → qc-automation-expert
│  ├─ E2E tests? → qc-automation-expert
│  ├─ Unit tests? → qc-automation-expert
│  └─ Security tests? → security-specialist*
│
├─ 🚀 Deployment/Ops
│  ├─ Simple deployment? → deployment-integration-expert
│  ├─ Complex infrastructure? → devops-architect
│  ├─ GCP-specific? → google-cloud-expert
│  └─ Monitoring? → devops-architect
│
├─ 📝 Documentation
│  ├─ General docs? → document-writer-expert
│  ├─ API docs? → api-documenter
│  └─ Architecture docs? → [relevant-architect] + document-writer-expert
│
└─ 🤔 Guidance/Planning
   ├─ Requirements unclear? → requirements-analyst*
   ├─ Technology choice? → tech-lead-mentor*
   ├─ Architecture decision? → tech-lead-mentor*
   └─ Best practices? → tech-lead-mentor*
```

*Planned/Recommended agent

---

## 💡 Usage Tips

### 1. **Start with Architecture**
Always begin with architecture agents before implementation:
```
requirements-analyst* → [architect agents] → [implementation agents]
```

### 2. **Layer Your Reviews**
Apply multiple review layers for quality:
```
[implementation] → code-reviewer* → security-specialist* → performance-optimizer*
```

### 3. **Specialize for Efficiency**
Use the most specialized agent for the task:
- ❌ Don't use frontend-architect for component implementation
- ✅ Use ui-components-expert for components
- ✅ Use frontend-architect for architecture decisions

### 4. **Combine Agents for Complex Tasks**
Complex tasks need multiple agents:
```
Full-stack feature = frontend-architect + backend-architect + database-architect +
                     security-specialist* + developers + qc-automation-expert
```

### 5. **Review Before Commit**
Always review before committing:
```
[write code] → code-reviewer* → [fix issues] → security-specialist* → [commit]
```

---

## 📈 Skill Coverage Analysis

### Current System (12 agents)

| Skill Category | Coverage | Strong Agents | Gap Areas |
|----------------|----------|---------------|-----------|
| **Frontend** | 95% | 3 agents | Mobile apps |
| **Backend** | 80% | 2 agents | Microservices, Message queues |
| **Database** | 85% | 1 agent | NoSQL advanced patterns |
| **DevOps** | 75% | 2 agents | Service mesh, Advanced monitoring |
| **Testing** | 70% | 1 agent | Security testing, Load testing |
| **Documentation** | 90% | 2 agents | Interactive docs |
| **Security** | 30% | 0 agents | **CRITICAL GAP** |
| **Code Quality** | 40% | 0 agents | **CRITICAL GAP** |
| **Performance** | 45% | 0 agents | **HIGH PRIORITY GAP** |
| **Requirements** | 20% | 0 agents | **HIGH PRIORITY GAP** |
| **Debugging** | 25% | 0 agents | **CRITICAL GAP** |
| **Mobile** | 10% | 0 agents | **HIGH PRIORITY GAP** |

### With Recommended Agents (20 agents)

| Skill Category | Coverage | Strong Agents | Remaining Gaps |
|----------------|----------|---------------|----------------|
| **Frontend** | 95% | 3 agents | None major |
| **Backend** | 85% | 2 agents | Advanced patterns |
| **Database** | 90% | 1 agent | Graph databases |
| **DevOps** | 80% | 2 agents | Multi-cloud |
| **Testing** | 85% | 1 agent | Visual testing |
| **Documentation** | 95% | 2 agents | None major |
| **Security** | 95% | 1 agent | **✅ FILLED** |
| **Code Quality** | 95% | 2 agents | **✅ FILLED** |
| **Performance** | 90% | 1 agent | **✅ FILLED** |
| **Requirements** | 85% | 1 agent | **✅ FILLED** |
| **Debugging** | 90% | 1 agent | **✅ FILLED** |
| **Mobile** | 85% | 1 agent | **✅ FILLED** |

---

## 🔄 Updating This Document

When adding new agents:

1. Add agent to "Agent Skills Breakdown" section
2. Update "Skills Comparison Matrix"
3. Update "Agent Selection Decision Tree"
4. Update "Skill Coverage Analysis"
5. Update agent count in document header

When agents are enhanced:
1. Update skills list for that agent
2. Update comparison matrix if new technologies added
3. Update "Best For" / "Avoid For" sections

---

## 📞 Questions?

- **Which agent for X task?** - Use the decision tree above
- **Agent A vs Agent B?** - Check "Skills Comparison Matrix"
- **What can agent X do?** - See "Agent Skills Breakdown"
- **Coverage gaps?** - See "Skill Coverage Analysis"

---

**Document Status**: Production Ready
**Maintenance**: Update when agents added/modified
**Owner**: System Administrator

---

*This document provides a comprehensive view of all agent capabilities.
Use it as your primary reference for agent selection.*

# 🚀 Cryptocurrency Trading Bot - Step-by-Step Implementation Tasks

**Project**: Add Cryptocurrency Trading Bot Workflow Template to Claude Force
**Branch**: `claude/add-workflow-template-01Ya4j2rCwYdrS6X28wunag8`
**Estimated Total Time**: 8-12 hours of implementation work

---

## 📋 OVERVIEW

This document breaks down the implementation into clear, manageable tasks organized by priority and dependencies.

### Implementation Phases

```
Phase 1: Agent Definitions (10 agents)          → 3-4 hours
Phase 2: Skill Definitions (9 skills)           → 2-3 hours
Phase 3: Workflow Configuration                 → 1 hour
Phase 4: Template Definition                    → 1 hour
Phase 5: Documentation & Examples               → 1-2 hours
Phase 6: Testing & Validation                   → 1 hour
```

**Total Estimated Time**: 9-12 hours

---

## 🎯 PHASE 1: CREATE AGENT DEFINITIONS

### Task 1.1: Create Risk Engine Architect Agent
**Priority**: 🔴 CRITICAL
**Estimated Time**: 30-40 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/agents/risk-engine-architect.md
.claude/contracts/risk-engine-architect.contract
```

**Agent Capabilities**:
- Real-time portfolio risk calculations (VaR, CVaR)
- Pre-trade validation checks
- Position concentration limits
- Liquidation monitoring
- Exchange counterparty risk
- Correlation-adjusted exposure

**Deliverables**:
- [ ] Create agent definition file (`.claude/agents/risk-engine-architect.md`)
- [ ] Create contract file (`.claude/contracts/risk-engine-architect.contract`)
- [ ] Define risk limit hierarchies
- [ ] Document pre-trade validation rules
- [ ] Specify risk monitoring thresholds

---

### Task 1.2: Create Exchange Integration Specialist Agent
**Priority**: 🔴 CRITICAL
**Estimated Time**: 30-40 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/agents/exchange-integration-specialist.md
.claude/contracts/exchange-integration-specialist.contract
```

**Agent Capabilities**:
- Exchange-specific API integration
- Rate limit optimization
- WebSocket reconnection strategies
- Exchange API versioning
- Order book precision handling
- Exchange-specific error handling

**Deliverables**:
- [ ] Create agent definition file
- [ ] Create contract file
- [ ] Document Binance-specific patterns
- [ ] Document Coinbase Pro patterns
- [ ] Document Kraken patterns
- [ ] Define rate limiting strategies

---

### Task 1.3: Create Execution Optimization Expert Agent
**Priority**: 🟠 HIGH
**Estimated Time**: 25-35 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/agents/execution-optimization-expert.md
.claude/contracts/execution-optimization-expert.contract
```

**Agent Capabilities**:
- TWAP/VWAP execution algorithms
- Smart order routing
- Iceberg orders and order splitting
- Execution cost analysis (TCA)
- Market impact modeling

**Deliverables**:
- [ ] Create agent definition file
- [ ] Create contract file
- [ ] Define TWAP/VWAP algorithms
- [ ] Document order splitting strategies
- [ ] Specify slippage reduction techniques

---

### Task 1.4: Create Liquidation Monitor Agent
**Priority**: 🔴 CRITICAL
**Estimated Time**: 25-35 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/agents/liquidation-monitor.md
.claude/contracts/liquidation-monitor.contract
```

**Agent Capabilities**:
- Margin health monitoring
- Liquidation price tracking
- Auto-deleverage triggers
- Funding rate impact analysis
- Emergency position closure

**Deliverables**:
- [ ] Create agent definition file
- [ ] Create contract file
- [ ] Define margin thresholds (75%, 80%, 85%)
- [ ] Document auto-deleverage procedures
- [ ] Specify emergency protocols

---

### Task 1.5: Create Infrastructure Reliability Expert Agent
**Priority**: 🔴 CRITICAL
**Estimated Time**: 30-40 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/agents/infrastructure-reliability-expert.md
.claude/contracts/infrastructure-reliability-expert.contract
```

**Agent Capabilities**:
- High-availability architectures
- Leader election and failover
- Circuit breaker patterns
- State reconciliation
- Disaster recovery

**Deliverables**:
- [ ] Create agent definition file
- [ ] Create contract file
- [ ] Define HA architecture patterns
- [ ] Document failover procedures
- [ ] Specify state reconciliation logic

---

### Task 1.6: Update Crypto Trading Architect Agent
**Priority**: 🟠 HIGH
**Estimated Time**: 20-30 minutes
**Dependencies**: None

**Files to Update**:
```
.claude/agents/crypto-trading-architect.md (NEW)
.claude/contracts/crypto-trading-architect.contract (NEW)
```

**Agent Capabilities**:
- Trading bot architecture patterns
- Event-driven design
- Real-time data pipeline design
- Order execution systems
- Multi-database hybrid architecture

**Deliverables**:
- [ ] Create agent definition file
- [ ] Create contract file
- [ ] Document asyncio architecture
- [ ] Define data flow patterns
- [ ] Specify system components

---

### Task 1.7: Update Trading Strategy Expert Agent
**Priority**: 🟠 HIGH
**Estimated Time**: 20-30 minutes
**Dependencies**: None

**Files to Update**:
```
.claude/agents/trading-strategy-expert.md (NEW)
.claude/contracts/trading-strategy-expert.contract (NEW)
```

**Agent Capabilities**:
- Algorithmic trading strategies
- Technical analysis indicators
- Backtesting methodology
- Position sizing algorithms
- Strategy optimization

**Deliverables**:
- [ ] Create agent definition file
- [ ] Create contract file
- [ ] Document funding rate arbitrage
- [ ] Document statistical arbitrage
- [ ] Define strategy evaluation criteria

---

### Task 1.8: Update Crypto Data Engineer Agent
**Priority**: 🟠 HIGH
**Estimated Time**: 20-30 minutes
**Dependencies**: None

**Files to Update**:
```
.claude/agents/crypto-data-engineer.md (NEW)
.claude/contracts/crypto-data-engineer.contract (NEW)
```

**Agent Capabilities**:
- OHLCV data collection
- Real-time streaming pipelines
- Multi-database architecture
- Data quality validation
- Historical data management

**Deliverables**:
- [ ] Create agent definition file
- [ ] Create contract file
- [ ] Document QuestDB setup
- [ ] Document ClickHouse integration
- [ ] Define data retention policies

---

### Task 1.9: Update Telegram Bot Specialist Agent
**Priority**: 🟡 MEDIUM
**Estimated Time**: 15-20 minutes
**Dependencies**: None

**Files to Update**:
```
.claude/agents/telegram-bot-specialist.md (NEW)
.claude/contracts/telegram-bot-specialist.contract (NEW)
```

**Agent Capabilities**:
- python-telegram-bot integration
- Command handler design
- Interactive keyboards
- User authentication
- Notification system

**Deliverables**:
- [ ] Create agent definition file
- [ ] Create contract file
- [ ] Document command patterns
- [ ] Define security requirements
- [ ] Specify notification types

---

### Task 1.10: Update Crypto Security Auditor Agent
**Priority**: 🔴 CRITICAL
**Estimated Time**: 25-35 minutes
**Dependencies**: None

**Files to Update**:
```
.claude/agents/crypto-security-auditor.md (NEW)
.claude/contracts/crypto-security-auditor.contract (NEW)
```

**Agent Capabilities**:
- API key management security
- Wallet security architecture
- Transaction signing security
- Secrets management
- Compliance requirements

**Deliverables**:
- [ ] Create agent definition file
- [ ] Create contract file
- [ ] Document CloudHSM integration
- [ ] Define 3-tier wallet architecture
- [ ] Specify audit logging requirements

---

## 🛠️ PHASE 2: CREATE SKILL DEFINITIONS

### Task 2.1: Create Crypto Trading Patterns Skill
**Priority**: 🔴 CRITICAL
**Estimated Time**: 30-40 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/skills/crypto-trading-patterns/SKILL.md
```

**Skill Contents**:
- Common trading bot architectures
- Exchange API integration patterns
- Order management system design
- Risk management implementations
- Event-driven patterns

**Deliverables**:
- [ ] Create skill directory
- [ ] Create SKILL.md with code examples
- [ ] Include position sizing algorithms
- [ ] Include order state machine patterns
- [ ] Include circuit breaker examples

---

### Task 2.2: Create Telegram Bot Patterns Skill
**Priority**: 🟡 MEDIUM
**Estimated Time**: 20-30 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/skills/telegram-bot-patterns/SKILL.md
```

**Skill Contents**:
- Telegram bot command structures
- Interactive keyboard layouts
- Message formatting
- Authentication patterns
- Notification system design

**Deliverables**:
- [ ] Create skill directory
- [ ] Create SKILL.md with examples
- [ ] Include command handler patterns
- [ ] Include security examples
- [ ] Include notification templates

---

### Task 2.3: Create Crypto Backtesting Skill
**Priority**: 🟠 HIGH
**Estimated Time**: 25-35 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/skills/crypto-backtesting/SKILL.md
```

**Skill Contents**:
- Backtesting framework design
- Performance metrics calculation
- Walk-forward optimization
- Monte Carlo simulation
- Avoiding common biases

**Deliverables**:
- [ ] Create skill directory
- [ ] Create SKILL.md with examples
- [ ] Include backtesting engine code
- [ ] Include metrics calculation
- [ ] Include bias prevention patterns

---

### Task 2.4: Create Exchange API Integration Skill
**Priority**: 🔴 CRITICAL
**Estimated Time**: 30-40 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/skills/exchange-api-integration/SKILL.md
```

**Skill Contents**:
- CCXT library best practices
- Exchange-specific quirks
- Rate limiting strategies
- Error handling patterns
- WebSocket implementation

**Deliverables**:
- [ ] Create skill directory
- [ ] Create SKILL.md with examples
- [ ] Include CCXT Pro examples
- [ ] Include WebSocket reconnection
- [ ] Include rate limiting code

---

### Task 2.5: Create Risk Management Framework Skill
**Priority**: 🔴 CRITICAL
**Estimated Time**: 30-40 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/skills/risk-management-framework/SKILL.md
```

**Skill Contents**:
- Pre-trade validation patterns
- Position sizing algorithms
- Risk limit hierarchies
- VaR/CVaR calculations
- Circuit breaker implementations

**Deliverables**:
- [ ] Create skill directory
- [ ] Create SKILL.md with examples
- [ ] Include pre-trade validators
- [ ] Include position sizing code
- [ ] Include risk limit enforcement

---

### Task 2.6: Create High Availability Patterns Skill
**Priority**: 🔴 CRITICAL
**Estimated Time**: 25-35 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/skills/high-availability-patterns/SKILL.md
```

**Skill Contents**:
- Active-passive architectures
- Leader election algorithms
- Split-brain prevention
- State synchronization
- Failover procedures

**Deliverables**:
- [ ] Create skill directory
- [ ] Create SKILL.md with examples
- [ ] Include Redis leader election
- [ ] Include failover patterns
- [ ] Include health check code

---

### Task 2.7: Create Order Execution Patterns Skill
**Priority**: 🟠 HIGH
**Estimated Time**: 20-30 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/skills/order-execution-patterns/SKILL.md
```

**Skill Contents**:
- TWAP/VWAP algorithms
- Order slicing strategies
- Iceberg order patterns
- Smart order routing
- Fill quality monitoring

**Deliverables**:
- [ ] Create skill directory
- [ ] Create SKILL.md with examples
- [ ] Include TWAP implementation
- [ ] Include VWAP implementation
- [ ] Include order splitting logic

---

### Task 2.8: Create State Management Patterns Skill
**Priority**: 🔴 CRITICAL
**Estimated Time**: 25-35 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/skills/state-management-patterns/SKILL.md
```

**Skill Contents**:
- Position reconciliation
- Order state machines
- Idempotency patterns
- State recovery procedures
- Consistency guarantees

**Deliverables**:
- [ ] Create skill directory
- [ ] Create SKILL.md with examples
- [ ] Include reconciliation code
- [ ] Include state machine patterns
- [ ] Include idempotency examples

---

### Task 2.9: Create Secrets Management Production Skill
**Priority**: 🔴 CRITICAL
**Estimated Time**: 25-35 minutes
**Dependencies**: None

**Files to Create**:
```
.claude/skills/secrets-management-production/SKILL.md
```

**Skill Contents**:
- AWS Secrets Manager integration
- KMS + CloudHSM usage
- Secrets rotation automation
- API key lifecycle management
- HSM-based transaction signing

**Deliverables**:
- [ ] Create skill directory
- [ ] Create SKILL.md with examples
- [ ] Include Secrets Manager code
- [ ] Include rotation examples
- [ ] Include CloudHSM integration

---

## ⚙️ PHASE 3: UPDATE WORKFLOW CONFIGURATION

### Task 3.1: Add Crypto Trading Bot Workflow to claude.json
**Priority**: 🔴 CRITICAL
**Estimated Time**: 30-40 minutes
**Dependencies**: Phase 1 (all agents created)

**Files to Update**:
```
.claude/claude.json
```

**Workflow Definition**:
```json
"workflows": {
  "crypto-trading-bot": [
    "crypto-trading-architect",
    "crypto-data-engineer",
    "database-architect",
    "trading-strategy-expert",
    "backend-architect",
    "python-expert",
    "telegram-bot-specialist",
    "crypto-security-auditor",
    "risk-engine-architect",
    "exchange-integration-specialist",
    "execution-optimization-expert",
    "liquidation-monitor",
    "infrastructure-reliability-expert",
    "qc-automation-expert",
    "code-reviewer",
    "deployment-integration-expert"
  ]
}
```

**Deliverables**:
- [ ] Add workflow to `claude.json`
- [ ] Define agent execution order
- [ ] Specify agent priorities
- [ ] Add agent domain mappings
- [ ] Update skills integration section

---

### Task 3.2: Update Agent Configurations in claude.json
**Priority**: 🔴 CRITICAL
**Estimated Time**: 20-30 minutes
**Dependencies**: Task 3.1

**Configuration Updates**:
```json
"agents": {
  "crypto-trading-architect": {
    "file": "agents/crypto-trading-architect.md",
    "contract": "contracts/crypto-trading-architect.contract",
    "domains": ["crypto", "trading", "architecture", "real-time"],
    "priority": 1
  },
  "risk-engine-architect": {
    "file": "agents/risk-engine-architect.md",
    "contract": "contracts/risk-engine-architect.contract",
    "domains": ["risk", "finance", "compliance", "monitoring"],
    "priority": 1
  },
  // ... (repeat for all 10 agents)
}
```

**Deliverables**:
- [ ] Add all 10 agent configurations
- [ ] Set appropriate priorities
- [ ] Define domain mappings
- [ ] Verify file paths
- [ ] Validate JSON syntax

---

### Task 3.3: Update Skills Integration in claude.json
**Priority**: 🟠 HIGH
**Estimated Time**: 15-20 minutes
**Dependencies**: Phase 2 (all skills created)

**Skills Configuration**:
```json
"skills_integration": {
  "enabled": true,
  "skills_path": "skills/",
  "available_skills": [
    "crypto-trading-patterns",
    "telegram-bot-patterns",
    "crypto-backtesting",
    "exchange-api-integration",
    "risk-management-framework",
    "high-availability-patterns",
    "order-execution-patterns",
    "state-management-patterns",
    "secrets-management-production",
    "test-generation",
    "code-review",
    "api-design",
    "dockerfile",
    "git-workflow"
  ]
}
```

**Deliverables**:
- [ ] Add all 9 new skills to configuration
- [ ] Verify skill paths
- [ ] Enable skills integration
- [ ] Validate JSON syntax

---

## 📝 PHASE 4: CREATE TEMPLATE DEFINITION

### Task 4.1: Add Crypto Trading Bot Template to templates.yaml
**Priority**: 🔴 CRITICAL
**Estimated Time**: 40-50 minutes
**Dependencies**: Phase 3 (workflow configured)

**Files to Update**:
```
claude_force/templates/definitions/templates.yaml
```

**Template Definition**:
```yaml
- id: crypto-trading-bot
  name: "Cryptocurrency Trading Bot"
  description: "Automated trading bot with multi-exchange support, risk management, backtesting, and Telegram integration"
  category: finance-ai
  difficulty: advanced
  estimated_setup_time: "20-30 minutes"

  agents:
    - crypto-trading-architect
    - crypto-data-engineer
    - database-architect
    - trading-strategy-expert
    - backend-architect
    - python-expert
    - telegram-bot-specialist
    - crypto-security-auditor
    - risk-engine-architect
    - exchange-integration-specialist
    - execution-optimization-expert
    - liquidation-monitor
    - infrastructure-reliability-expert
    - qc-automation-expert
    - code-reviewer
    - deployment-integration-expert

  workflows:
    - crypto-trading-bot

  skills:
    - crypto-trading-patterns
    - telegram-bot-patterns
    - crypto-backtesting
    - exchange-api-integration
    - risk-management-framework
    - high-availability-patterns
    - order-execution-patterns
    - state-management-patterns
    - secrets-management-production
    - api-design
    - test-generation
    - code-review
    - git-workflow
    - dockerfile

  keywords:
    - crypto
    - cryptocurrency
    - trading
    - bot
    - bitcoin
    - ethereum
    - binance
    - coinbase
    - telegram
    - api
    - backtesting
    - risk-management
    - automation
    - algorithmic-trading
    - quantitative-finance

  tech_stack:
    language: ["Python 3.11+"]
    framework: ["asyncio", "FastAPI"]
    exchanges: ["Binance", "Coinbase Pro", "Kraken"]
    data_stack:
      - "QuestDB (hot data)"
      - "ClickHouse (analytics)"
      - "PostgreSQL (transactional)"
      - "Redis (caching)"
      - "Parquet/S3 (archive)"
    libraries:
      - "CCXT Pro"
      - "python-telegram-bot"
      - "pandas-ta"
      - "VectorBT Pro"
    deployment: ["Docker", "Kubernetes", "AWS"]
    security: ["AWS Secrets Manager", "CloudHSM", "KMS"]

  use_cases:
    - "Automated cryptocurrency trading"
    - "Algorithmic trading strategies"
    - "Portfolio management bots"
    - "DCA (Dollar Cost Averaging) bots"
    - "Arbitrage trading"
    - "Market making"
    - "Funding rate arbitrage"
    - "Statistical arbitrage"

  features:
    core:
      - "Multi-exchange support (Binance, Coinbase, Kraken)"
      - "Real-time market data processing"
      - "Advanced order execution (TWAP, VWAP, iceberg)"
      - "Comprehensive risk management"
      - "Paper trading mode"

    strategies:
      - "Funding rate arbitrage"
      - "Statistical arbitrage (pairs trading)"
      - "Grid trading with trend filters"
      - "ML-enhanced strategies (XGBoost)"
      - "Custom strategy framework"

    data:
      - "Multi-database hybrid architecture"
      - "Real-time data pipeline (Redis Streams)"
      - "Historical data management"
      - "Backtesting engine with walk-forward analysis"
      - "Performance attribution"

    security:
      - "3-tier wallet architecture (cold/warm/hot)"
      - "CloudHSM for API key storage"
      - "Comprehensive audit logging"
      - "IP whitelisting"
      - "MFA for sensitive operations"

    reliability:
      - "High-availability (active-passive)"
      - "Leader election and failover"
      - "Circuit breaker patterns"
      - "State reconciliation"
      - "Disaster recovery"

    monitoring:
      - "Prometheus metrics"
      - "Grafana dashboards"
      - "PagerDuty alerting"
      - "Real-time P&L tracking"
      - "Liquidation monitoring"

    integration:
      - "Telegram bot for control and notifications"
      - "Interactive command interface"
      - "Real-time alerts"
      - "Portfolio status reports"

  architecture:
    pattern: "Event-driven microservices"
    data_flow: "WebSocket → Redis Streams → QuestDB → ClickHouse → Parquet"
    deployment: "Active-passive with leader election"
    scaling: "Horizontal (Kubernetes) + Vertical (larger instances)"

  estimated_costs:
    infrastructure_monthly: "$800-2,100"
    development_time: "9-12 months to production"
    minimum_capital: "$10,000 (testing), $50,000+ (production)"

  prerequisites:
    - "Exchange accounts (Binance, Coinbase, Kraken)"
    - "API keys with trading permissions (NO withdrawal)"
    - "AWS account (for Secrets Manager, CloudHSM, S3)"
    - "Telegram Bot Token"
    - "Basic understanding of trading concepts"

  security_requirements:
    critical:
      - "NEVER store API keys in code or .env files"
      - "Use AWS Secrets Manager + CloudHSM for production"
      - "Enable IP whitelisting on all exchanges"
      - "Bot should NEVER have withdrawal permissions"
      - "Implement 3-tier wallet architecture"
      - "Enable comprehensive audit logging"

    recommended:
      - "Use hardware wallets for cold storage"
      - "Implement multi-sig for operational wallet"
      - "Enable 2FA on exchange accounts"
      - "Set up PagerDuty for critical alerts"
      - "Regular security audits"

  performance_targets:
    latency: "Order execution <200ms (p95)"
    uptime: "99.99% (<52 min downtime/year)"
    query_performance: "Latest price <10ms"
    data_freshness: "<5 seconds lag"

  risk_management:
    limits:
      - "Max position size: 2% of capital"
      - "Max loss per trade: 1%"
      - "Max daily loss: 5%"
      - "Max drawdown: 20%"
      - "Max leverage: 3x"
      - "Max concentration: 20% in single asset"

  metrics:
    performance:
      - "Annual Return: 15-60% (strategy dependent)"
      - "Sharpe Ratio: >1.5 target"
      - "Max Drawdown: <20%"
      - "Win Rate: >50%"

    technical:
      - "Order execution latency: p95 <200ms"
      - "System uptime: >99.99%"
      - "API error rate: <0.1%"
      - "Test coverage: >80%"

  roadmap:
    phase_0: "Critical Foundations (2-4 weeks)"
    phase_1: "Core Trading Engine (5-12 weeks)"
    phase_2: "Strategies & Backtesting (13-20 weeks)"
    phase_3: "Production Hardening (21-28 weeks)"
    phase_4: "Paper Trading Validation (29-36 weeks)"
    phase_5: "Live Trading Gradual Rollout (37+ weeks)"

  references:
    - "Expert Review: Crypto Trading & Quant Finance"
    - "Expert Review: Python Backend Architecture"
    - "Expert Review: Cybersecurity"
    - "Expert Review: Data Engineering"
    - "Expert Review: DevOps & SRE"

  documentation:
    - "CRYPTO_TRADING_BOT_UPDATED_PLAN.md"
    - "CRYPTO_TRADING_BOT_DEVOPS_REVIEW.md"

  warnings:
    - "⚠️ CRITICAL: Never use python-dotenv in production"
    - "⚠️ CRITICAL: Bot should NEVER have direct wallet access"
    - "⚠️ CRITICAL: API keys must have NO withdrawal permissions"
    - "⚠️ CRITICAL: CloudHSM required for production ($1,200/mo)"
    - "⚠️ Only trade with capital you can afford to lose"
    - "⚠️ Cryptocurrency trading is high risk"
    - "⚠️ Past performance does not guarantee future results"
```

**Deliverables**:
- [ ] Add complete template definition
- [ ] Verify all agent references
- [ ] Verify all skill references
- [ ] Validate YAML syntax
- [ ] Add comprehensive metadata
- [ ] Include security warnings
- [ ] Specify cost estimates
- [ ] Define performance targets

---

### Task 4.2: Add Finance-AI Category (if needed)
**Priority**: 🟡 MEDIUM
**Estimated Time**: 5-10 minutes
**Dependencies**: Task 4.1

**Category Definition**:
```yaml
categories:
  - id: finance-ai
    name: "Finance & AI Trading"
    description: "Trading bots, financial analysis, and automated investment systems"
    icon: "💰"
```

**Deliverables**:
- [ ] Check if finance-ai category exists
- [ ] Add category if needed
- [ ] Validate YAML syntax

---

## 📚 PHASE 5: DOCUMENTATION & EXAMPLES

### Task 5.1: Create Template README
**Priority**: 🟠 HIGH
**Estimated Time**: 30-40 minutes
**Dependencies**: Phase 4 (template created)

**Files to Create**:
```
claude_force/templates/crypto-trading-bot/README.md
```

**README Contents**:
- Overview and introduction
- Quick start guide
- Architecture diagram
- Security best practices
- Configuration instructions
- Deployment guide
- Troubleshooting
- FAQ

**Deliverables**:
- [ ] Create template directory
- [ ] Write comprehensive README
- [ ] Include architecture diagrams (ASCII art)
- [ ] Add configuration examples
- [ ] Include security checklist
- [ ] Add troubleshooting section

---

### Task 5.2: Create Example Configuration Files
**Priority**: 🟡 MEDIUM
**Estimated Time**: 20-30 minutes
**Dependencies**: Task 5.1

**Files to Create**:
```
claude_force/templates/crypto-trading-bot/examples/config.example.yaml
claude_force/templates/crypto-trading-bot/examples/risk-limits.example.yaml
claude_force/templates/crypto-trading-bot/examples/strategy.example.yaml
claude_force/templates/crypto-trading-bot/examples/.env.example
```

**Deliverables**:
- [ ] Create examples directory
- [ ] Create config.example.yaml
- [ ] Create risk-limits.example.yaml
- [ ] Create strategy.example.yaml
- [ ] Create .env.example (with warnings)
- [ ] Add inline documentation

---

### Task 5.3: Create Quick Start Guide
**Priority**: 🟠 HIGH
**Estimated Time**: 20-30 minutes
**Dependencies**: Task 5.1

**Files to Create**:
```
claude_force/templates/crypto-trading-bot/QUICKSTART.md
```

**Guide Contents**:
- Prerequisites checklist
- Step-by-step setup instructions
- Exchange account setup
- API key configuration
- First strategy deployment
- Paper trading validation

**Deliverables**:
- [ ] Create QUICKSTART.md
- [ ] Include step-by-step instructions
- [ ] Add screenshots/diagrams
- [ ] Include security warnings
- [ ] Add verification steps

---

### Task 5.4: Create Security Guide
**Priority**: 🔴 CRITICAL
**Estimated Time**: 25-35 minutes
**Dependencies**: Task 5.1

**Files to Create**:
```
claude_force/templates/crypto-trading-bot/SECURITY.md
```

**Security Guide Contents**:
- 3-tier wallet architecture setup
- AWS Secrets Manager configuration
- CloudHSM setup (production)
- IP whitelisting configuration
- API key security checklist
- Incident response procedures

**Deliverables**:
- [ ] Create SECURITY.md
- [ ] Document wallet architecture
- [ ] Include AWS setup instructions
- [ ] Add security checklists
- [ ] Document incident response
- [ ] Include audit logging setup

---

## ✅ PHASE 6: TESTING & VALIDATION

### Task 6.1: Validate All Agent Files
**Priority**: 🔴 CRITICAL
**Estimated Time**: 15-20 minutes
**Dependencies**: Phase 1 (all agents created)

**Validation Checklist**:
- [ ] All agent .md files exist
- [ ] All contract files exist
- [ ] Markdown syntax is valid
- [ ] No broken references
- [ ] Consistent formatting
- [ ] Complete metadata

**Deliverables**:
- [ ] Run validation script
- [ ] Fix any syntax errors
- [ ] Verify file permissions
- [ ] Check file encoding (UTF-8)

---

### Task 6.2: Validate All Skill Files
**Priority**: 🔴 CRITICAL
**Estimated Time**: 15-20 minutes
**Dependencies**: Phase 2 (all skills created)

**Validation Checklist**:
- [ ] All skill directories exist
- [ ] All SKILL.md files exist
- [ ] Code examples are syntactically correct
- [ ] No broken references
- [ ] Consistent formatting
- [ ] Complete documentation

**Deliverables**:
- [ ] Run validation script
- [ ] Test code examples
- [ ] Fix any syntax errors
- [ ] Verify file permissions

---

### Task 6.3: Validate Configuration Files
**Priority**: 🔴 CRITICAL
**Estimated Time**: 15-20 minutes
**Dependencies**: Phase 3 (workflow configured)

**Validation Checklist**:
- [ ] claude.json is valid JSON
- [ ] templates.yaml is valid YAML
- [ ] All agent references are correct
- [ ] All skill references are correct
- [ ] No duplicate entries
- [ ] File paths are correct

**Deliverables**:
- [ ] Validate JSON syntax
- [ ] Validate YAML syntax
- [ ] Check all file references
- [ ] Run template discovery test

---

### Task 6.4: Test Template Discovery
**Priority**: 🟠 HIGH
**Estimated Time**: 10-15 minutes
**Dependencies**: All previous phases

**Test Cases**:
- [ ] Template appears in gallery
- [ ] Template metadata is correct
- [ ] All agents are listed
- [ ] All skills are listed
- [ ] Category is correct
- [ ] Keywords work for search

**Deliverables**:
- [ ] Run template gallery
- [ ] Verify template appears
- [ ] Test search functionality
- [ ] Verify all metadata

---

## 📦 FINAL COMMIT & PUSH

### Task 7.1: Create Comprehensive Commit
**Priority**: 🔴 CRITICAL
**Estimated Time**: 10-15 minutes
**Dependencies**: All phases complete

**Commit Message**:
```
feat: add cryptocurrency trading bot workflow template

Add comprehensive crypto trading bot template with 10 specialized agents,
9 custom skills, and production-ready architecture.

Features:
- Multi-exchange support (Binance, Coinbase, Kraken)
- Multi-database hybrid (QuestDB, ClickHouse, PostgreSQL)
- High-availability with leader election
- Comprehensive risk management
- Production security (CloudHSM, 3-tier wallet)
- Telegram integration
- Advanced strategies (arbitrage, ML-enhanced)

Agents (10 total):
- crypto-trading-architect
- trading-strategy-expert
- crypto-data-engineer
- telegram-bot-specialist
- crypto-security-auditor
- risk-engine-architect (NEW)
- exchange-integration-specialist (NEW)
- execution-optimization-expert (NEW)
- liquidation-monitor (NEW)
- infrastructure-reliability-expert (NEW)

Skills (9 new):
- crypto-trading-patterns
- telegram-bot-patterns
- crypto-backtesting
- exchange-api-integration
- risk-management-framework
- high-availability-patterns
- order-execution-patterns
- state-management-patterns
- secrets-management-production

Estimated costs: $800-2,100/month infrastructure
Timeline: 9-12 months to production
Documentation: Complete with expert reviews
```

**Deliverables**:
- [ ] Stage all files
- [ ] Create comprehensive commit message
- [ ] Commit changes
- [ ] Push to remote branch

---

## 📊 IMPLEMENTATION SUMMARY

### Files to Create/Update

**Agent Definitions** (10 files × 2 = 20 files):
- 10 agent .md files
- 10 contract files

**Skill Definitions** (9 files):
- 9 SKILL.md files in separate directories

**Configuration Files** (2 files):
- .claude/claude.json (update)
- claude_force/templates/definitions/templates.yaml (update)

**Documentation** (5+ files):
- Template README
- QUICKSTART guide
- SECURITY guide
- Example configuration files (4+)

**Total Files**: ~45-50 files

---

## ⏱️ TIME ESTIMATES

| Phase | Tasks | Estimated Time | Priority |
|-------|-------|----------------|----------|
| Phase 1: Agents | 10 tasks | 3-4 hours | 🔴 CRITICAL |
| Phase 2: Skills | 9 tasks | 2-3 hours | 🔴 CRITICAL |
| Phase 3: Workflow | 3 tasks | 1 hour | 🔴 CRITICAL |
| Phase 4: Template | 2 tasks | 45-60 min | 🔴 CRITICAL |
| Phase 5: Documentation | 4 tasks | 1.5-2 hours | 🟠 HIGH |
| Phase 6: Testing | 4 tasks | 1 hour | 🔴 CRITICAL |
| Phase 7: Commit | 1 task | 15 min | 🔴 CRITICAL |

**Total Estimated Time**: 9-12 hours

---

## 🎯 RECOMMENDED IMPLEMENTATION APPROACH

### Option A: Complete Implementation (All Phases)
**Time**: 9-12 hours
**Result**: Fully functional template ready for production use

### Option B: Phased Implementation
**Phase 1-3 Only**: 5-6 hours (Core agents, skills, workflow)
**Phase 4-6 Later**: 3-4 hours (Template, documentation, testing)

### Option C: Parallel Implementation
**Agent Team**: Focus on Phase 1
**Skill Team**: Focus on Phase 2
**Config Team**: Focus on Phase 3-4
**Time**: 4-6 hours (if working in parallel)

---

## ❓ NEXT STEPS

Please review this task breakdown and let me know:

1. **Which implementation approach do you prefer?**
   - A) Complete implementation (all phases)
   - B) Phased implementation (core first)
   - C) Parallel implementation (faster)

2. **Do you want me to proceed immediately, or would you like to:**
   - Review specific tasks in more detail?
   - Adjust priorities or scope?
   - Modify any specific components?

3. **Any specific concerns or requirements?**
   - Time constraints?
   - Specific features to prioritize?
   - Additional validation needed?

I'm ready to start implementation as soon as you give the go-ahead! 🚀

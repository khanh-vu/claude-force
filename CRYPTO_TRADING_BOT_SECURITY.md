# Cryptocurrency Trading Bot - Production Security Guide

## Overview

This guide covers **production-grade security** for deploying a cryptocurrency trading bot. Following these practices is **CRITICAL** to prevent loss of funds.

## Table of Contents

1. [Secrets Management](#secrets-management)
2. [Exchange API Security](#exchange-api-security)
3. [Wallet Architecture](#wallet-architecture)
4. [Network Security](#network-security)
5. [Monitoring & Alerting](#monitoring--alerting)
6. [Audit Logging](#audit-logging)
7. [Incident Response](#incident-response)

---

## 1. Secrets Management

### Production: AWS Secrets Manager + CloudHSM

❌ **NEVER in Production:**
- `.env` files
- Environment variables
- Hardcoded secrets
- `python-dotenv`
- Plaintext configuration files

✅ **ALWAYS in Production:**
- AWS Secrets Manager for API keys
- AWS KMS for encryption
- AWS CloudHSM for cold wallet keys ($1,200/month)
- Secrets rotation every 90 days

### Implementation

```python
# ✅ CORRECT - Production secrets management
from claude_force.crypto_trading.secrets import SecretsManager

secrets = SecretsManager(region_name='us-east-1')

# Fetch exchange credentials
binance_creds = await secrets.get_exchange_credentials('binance')
exchange = ccxt.binance({
    'apiKey': binance_creds['api_key'],
    'secret': binance_creds['secret'],
    'enableRateLimit': True
})

# Fetch database credentials
db_creds = await secrets.get_database_credentials()

# Fetch Telegram token
telegram_token = await secrets.get_telegram_token()
```

### Secrets Structure in AWS Secrets Manager

```json
{
  "name": "trading-bot/binance/credentials",
  "value": {
    "api_key": "...",
    "secret": "...",
    "ip_whitelist": ["52.1.2.3", "52.1.2.4"],
    "permissions": {
      "read": true,
      "trade": true,
      "withdraw": false,
      "transfer": false
    },
    "created_at": "2025-01-15T00:00:00Z",
    "rotation_date": "2025-04-15T00:00:00Z"
  }
}
```

### Automatic Secrets Rotation

```python
from claude_force.crypto_trading.secrets import SecretsRotationManager

rotation_manager = SecretsRotationManager(
    secrets_manager=secrets,
    rotation_interval_days=90
)

# Schedule automatic rotation check
async def check_rotation_daily():
    for exchange in ['binance', 'okx', 'bybit']:
        if await rotation_manager.check_rotation_needed(exchange):
            # Alert operations team
            await send_alert(
                f"Credentials rotation needed for {exchange}",
                severity='warning'
            )
```

---

## 2. Exchange API Security

### API Key Configuration Checklist

#### ✅ MUST DO:

1. **Disable Withdrawal Permissions**
   ```
   Trading bot API key MUST NEVER have:
   - Withdrawal permissions
   - Transfer permissions
   - Subaccount transfer permissions
   ```

2. **IP Whitelisting**
   ```
   Add ONLY your server IPs:
   - Production server 1: 52.1.2.3
   - Production server 2: 52.1.2.4 (HA failover)
   - NO wildcards (0.0.0.0/0)
   - NO VPN IPs
   ```

3. **Read-Only for Monitoring Keys**
   ```
   Separate API keys:
   - Trading key: read + trade permissions
   - Monitoring key: read only
   - NEVER use same key for both
   ```

4. **Daily Withdrawal Limit**
   ```
   Set daily withdrawal limit to: $0
   Even if permissions are disabled, set limit to zero
   ```

#### Security Validation Script

```python
from claude_force.crypto_trading.security import ExchangeSecurityAuditor

auditor = ExchangeSecurityAuditor()

# Audit API key security
async def audit_exchange_security():
    for exchange_id in ['binance', 'okx', 'bybit']:
        # Get API key info from exchange
        api_key_info = await exchange.fetch_api_key_info()

        # Run security audit
        warnings = auditor.audit_api_key_security(
            exchange_id,
            api_key_info
        )

        if warnings:
            for warning in warnings:
                logger.critical(f"[{exchange_id}] {warning}")
                await send_critical_alert(warning)
```

### Example Security Audit Output

```
🚨 CRITICAL: Withdrawal permission enabled on Binance! Disable immediately.
⚠️  WARNING: No IP whitelist configured on OKX. Add server IPs.
✅ OK: Bybit API key properly configured.
```

---

## 3. Wallet Architecture

### 3-Tier Wallet System

#### Cold Wallet (80% of funds)
- **Storage**: Hardware wallets (Ledger, Trezor)
- **Location**: Physical safe, bank vault
- **Access**: Multi-signature (3-of-5)
- **Purpose**: Long-term storage, NOT used by bot

#### Warm Wallet (19% of funds)
- **Storage**: Exchange wallets
- **Permissions**: NO withdrawal permissions on API keys
- **Purpose**: Trading capital
- **Access**: Manual withdrawal only (via exchange UI with 2FA)

#### Hot Wallet (1% of funds)
- **Storage**: Bot-controlled wallet (if needed)
- **Permissions**: Multi-sig (3-of-5)
- **Purpose**: Immediate liquidity (rare)
- **Access**: Bot has 1 of 5 keys, NOT enough to sign alone

### Critical Rules

❌ **BOT MUST NEVER:**
- Have access to cold wallet keys
- Have withdrawal permissions on warm wallet
- Have sole signing authority on hot wallet
- Store private keys in database
- Transmit private keys over network

✅ **BOT SHOULD:**
- Only trade with exchange balance
- Alert when balance is low
- Request manual rebalancing
- Operate with read + trade permissions only

### Fund Rebalancing Procedure

```
1. Bot detects low balance (< $5,000)
2. Bot sends Telegram alert to operator
3. Operator manually transfers from cold → warm wallet
4. Operator confirms transfer via exchange UI (with 2FA)
5. Bot confirms balance increase
6. Bot resumes trading
```

**NEVER automate cold/warm wallet transfers!**

---

## 4. Network Security

### Infrastructure Hardening

#### Firewall Rules

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH (from bastion only)
ufw allow 443/tcp   # HTTPS (from load balancer)
ufw allow 6379/tcp  # Redis (from localhost only)
ufw allow 5432/tcp  # PostgreSQL (from localhost only)

# Block everything else
ufw default deny incoming
ufw default allow outgoing
ufw enable
```

#### SSH Hardening

```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers trading-bot-admin
```

#### VPC Configuration (AWS)

```
VPC: 10.0.0.0/16
  - Public subnet: 10.0.1.0/24 (NAT Gateway, Bastion)
  - Private subnet: 10.0.2.0/24 (Trading bot servers)

Security Groups:
  - Trading bot: Allow 22 from bastion, 443 from ALB
  - Database: Allow 5432 from trading bot only
  - Redis: Allow 6379 from trading bot only
```

### SSL/TLS Everywhere

```python
# Database connections
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"

# Redis connections
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    ssl=True,
    ssl_cert_reqs='required'
)

# Exchange API (CCXT handles this automatically)
# All HTTPS connections verified
```

---

## 5. Monitoring & Alerting

### Metrics to Monitor

#### Trading Metrics
```
- Order execution latency (< 200ms)
- WebSocket connection status
- Exchange API error rate (< 1%)
- Order fill rate (> 95%)
- Position reconciliation errors
```

#### Risk Metrics
```
- Current portfolio value
- Daily P&L vs. limit (-5%)
- Max drawdown vs. limit (20%)
- Position concentration (< 20% per asset)
- Margin health (> 30% buffer)
- Leverage (< 3x)
```

#### System Metrics
```
- CPU usage (< 80%)
- Memory usage (< 85%)
- Disk space (> 20% free)
- Database connections (< max)
- Leader election status
```

### Alert Thresholds

| Alert Level | Condition | Response Time |
|------------|-----------|---------------|
| 🚨 **CRITICAL** | Circuit breaker triggered | Immediate (< 5 min) |
| 🚨 **CRITICAL** | Daily loss limit hit (-5%) | Immediate (< 5 min) |
| 🚨 **CRITICAL** | Unauthorized API access | Immediate (< 5 min) |
| 🚨 **CRITICAL** | Failover occurred | Immediate (< 15 min) |
| ⚠️ **WARNING** | Margin health < 40% | 1 hour |
| ⚠️ **WARNING** | High latency (> 500ms) | 1 hour |
| ℹ️ **INFO** | Daily report | 24 hours |

### Prometheus Metrics

```python
from prometheus_client import Counter, Gauge, Histogram

# Trading metrics
orders_placed = Counter('trading_orders_placed_total', 'Total orders placed', ['exchange', 'symbol'])
order_latency = Histogram('trading_order_latency_seconds', 'Order execution latency')
portfolio_value = Gauge('trading_portfolio_value_usd', 'Current portfolio value')

# Risk metrics
daily_pnl_pct = Gauge('trading_daily_pnl_percent', 'Daily P&L percentage')
margin_health = Gauge('trading_margin_health_percent', 'Margin health percentage')
```

---

## 6. Audit Logging

### Comprehensive Logging Requirements

All sensitive operations MUST be logged:

```python
from claude_force.crypto_trading.audit import AuditLogger

audit_logger = AuditLogger(s3_bucket='trading-bot-audit-logs')

# Log order placement
await audit_logger.log_order_placed(
    order_id='12345',
    exchange='binance',
    symbol='BTC/USDT',
    side='buy',
    amount=0.1,
    price=50000,
    user='bot',
    ip_address='52.1.2.3'
)

# Log configuration changes
await audit_logger.log_config_change(
    parameter='max_position_size_pct',
    old_value='0.02',
    new_value='0.03',
    changed_by='admin',
    reason='Risk limit adjustment'
)

# Log secret access
await audit_logger.log_secret_access(
    secret_name='binance/credentials',
    accessed_by='trading-bot',
    ip_address='52.1.2.3',
    success=True
)
```

### S3 WORM Storage (Write Once Read Many)

```python
# Upload logs to S3 with object lock
s3.put_object(
    Bucket='trading-bot-audit-logs',
    Key=f'logs/{date}/audit.jsonl',
    Body=log_data,
    ServerSideEncryption='AES256',
    ObjectLockMode='COMPLIANCE',
    ObjectLockRetainUntilDate=datetime.utcnow() + timedelta(days=2555)  # 7 years
)
```

### Log Retention

```
- Audit logs: 7 years (S3 WORM, compliance)
- Trading logs: 2 years (S3 Standard)
- Debug logs: 90 days (S3 Standard)
- Metrics: 1 year (Prometheus)
```

---

## 7. Incident Response

### Incident Response Plan

#### Phase 1: Detection (0-5 minutes)
```
1. Alert triggers (Telegram, PagerDuty, email)
2. On-call engineer acknowledges
3. Verify incident is real (not false positive)
```

#### Phase 2: Containment (5-15 minutes)
```
1. Emergency stop trading (/stop command)
2. Cancel all open orders
3. Assess damage (positions, losses)
4. Isolate affected systems
```

#### Phase 3: Investigation (15 minutes - 2 hours)
```
1. Review audit logs
2. Check for unauthorized access
3. Verify API key security
4. Check for code bugs
5. Review trade history
```

#### Phase 4: Recovery (2-24 hours)
```
1. Fix root cause
2. Rotate compromised credentials
3. Reconcile positions and balances
4. Resume trading (if safe)
5. Post-mortem report
```

### Emergency Stop Procedures

#### 1. Telegram Kill Switch
```
/stop - Immediately stops all trading
```

#### 2. API Key Revocation
```
1. Log into exchange
2. Delete/disable API key
3. Bot automatically stops (401 errors)
```

#### 3. AWS Secrets Manager Deletion
```bash
aws secretsmanager delete-secret \
  --secret-id trading-bot/binance/credentials \
  --force-delete-without-recovery
```

#### 4. Circuit Breaker Manual Trigger
```python
circuit_breaker.force_open(reason="Manual trigger by admin")
```

### Incident Severity Levels

| Severity | Definition | Example |
|----------|-----------|---------|
| **SEV-1** | Fund loss or critical security breach | Unauthorized withdrawal, API key compromised |
| **SEV-2** | Trading halted, no fund loss | Exchange outage, database failure |
| **SEV-3** | Degraded performance | High latency, partial failures |
| **SEV-4** | Minor issue, no impact | Warning threshold exceeded |

### Post-Incident Review

After every SEV-1 or SEV-2 incident:

```markdown
# Incident Report Template

## Incident Summary
- **Date**: 2025-01-15
- **Severity**: SEV-1
- **Duration**: 2 hours
- **Impact**: $5,000 loss

## Timeline
- 14:00 UTC: Alert triggered
- 14:05 UTC: Acknowledged
- 14:10 UTC: Trading stopped
- 14:30 UTC: Root cause identified
- 16:00 UTC: Resolved

## Root Cause
[Detailed analysis]

## Actions Taken
1. Emergency stop
2. Revoked API key
3. Fixed bug in risk engine

## Prevention
1. Add additional validation
2. Improve monitoring
3. Update runbooks

## Lessons Learned
[Key takeaways]
```

---

## Security Checklist for Production

Before going live, verify **ALL** items:

### Secrets Management
- [ ] AWS Secrets Manager configured
- [ ] All secrets migrated from .env
- [ ] Secrets rotation schedule set (90 days)
- [ ] CloudHSM configured for cold wallets
- [ ] No secrets in code or config files

### Exchange Security
- [ ] API keys have NO withdrawal permissions
- [ ] API keys have NO transfer permissions
- [ ] IP whitelist configured (server IPs only)
- [ ] Daily withdrawal limit set to $0
- [ ] Separate keys for trading vs. monitoring

### Wallet Security
- [ ] Cold wallet (80%) in hardware wallet
- [ ] Warm wallet (19%) on exchange, no withdrawal perms
- [ ] Hot wallet (1%) multi-sig configured
- [ ] Bot NEVER has access to private keys
- [ ] Manual rebalancing procedure documented

### Network Security
- [ ] Firewall rules configured
- [ ] SSH key-only authentication
- [ ] VPC with private subnets
- [ ] SSL/TLS for all connections
- [ ] Bastion host for SSH access

### Monitoring
- [ ] Prometheus metrics configured
- [ ] Grafana dashboards created
- [ ] PagerDuty/alerting configured
- [ ] Telegram alerts enabled
- [ ] Health checks running

### Audit Logging
- [ ] S3 WORM bucket created
- [ ] Audit logging enabled
- [ ] Log retention policy set (7 years)
- [ ] Log monitoring configured

### Incident Response
- [ ] Runbooks created
- [ ] On-call rotation configured
- [ ] Emergency stop procedure tested
- [ ] Incident response plan documented

---

## Compliance Considerations

### Financial Regulations

Depending on jurisdiction, you may need:
- Money transmitter license
- Securities dealer registration
- AML/KYC procedures
- Transaction reporting

**Consult legal counsel before trading with client funds.**

### Data Privacy

If storing user data:
- GDPR compliance (EU)
- CCPA compliance (California)
- SOC 2 certification (enterprise)

---

## Cost Estimates

### Security Infrastructure Costs

```
AWS Secrets Manager:   $0.40/secret/month × 10 = $4/month
AWS KMS:              $1/key/month × 5 = $5/month
CloudHSM:             $1,200/month (optional, cold wallets)
VPC NAT Gateway:      $32/month
Application Load Balancer: $16/month
CloudWatch Logs:      ~$10/month
S3 Storage (logs):    ~$5/month

Total (without CloudHSM): ~$72/month
Total (with CloudHSM):    ~$1,272/month
```

### Recommended for Different Scales

| Scale | Monthly Budget | Security Stack |
|-------|---------------|----------------|
| **Hobbyist** | < $100 | Secrets Manager, KMS, basic monitoring |
| **Semi-Pro** | $100-$500 | + HA setup, enhanced monitoring |
| **Professional** | $500-$2,000 | + CloudHSM, SOC 2, compliance |
| **Institutional** | $2,000+ | Full enterprise security, dedicated SecOps |

---

## Support & Resources

- **AWS Secrets Manager**: https://aws.amazon.com/secrets-manager/
- **CloudHSM**: https://aws.amazon.com/cloudhsm/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Crypto Security Best Practices**: https://www.cisa.gov/cryptocurrency-security

---

## Final Warning

⚠️ **CRITICAL REMINDER**:

1. **Start small** - Test with small amounts first
2. **Never rush** - Production security cannot be skipped
3. **Monitor 24/7** - Crypto markets never sleep
4. **Have backups** - Always have emergency procedures
5. **Stay updated** - Security threats evolve constantly

**The cost of cutting corners on security can be catastrophic.**

**If in doubt, consult security professionals before going to production.**

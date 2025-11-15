# Cryptocurrency Trading Bot - Configuration Examples

## Overview

This document provides real-world configuration examples for various trading strategies and deployment scenarios.

## Table of Contents

1. [Strategy Configurations](#strategy-configurations)
2. [Risk Management Configurations](#risk-management-configurations)
3. [Exchange Configurations](#exchange-configurations)
4. [Database Configurations](#database-configurations)
5. [Deployment Configurations](#deployment-configurations)

---

## 1. Strategy Configurations

### Grid Trading Strategy

#### Conservative Grid (Low Risk)

```yaml
# config/strategies/grid_conservative.yaml
strategy:
  type: grid_trading
  name: "BTC Conservative Grid"

  parameters:
    symbol: "BTC/USDT"
    grid_levels: 20
    grid_spacing_pct: 0.5  # 0.5% between levels
    grid_range:
      lower: 40000  # $40k
      upper: 60000  # $60k
    position_size_per_level: 100  # $100 per grid level

  risk_management:
    max_total_exposure: 2000  # $2000 total
    stop_loss_pct: 0.15  # 15% stop loss
    take_profit_pct: 0.10  # 10% take profit on full grid

  execution:
    order_type: "limit"  # Use limit orders
    post_only: true  # Maker orders only (get rebates)

  conditions:
    min_volatility: 0.02  # Min 2% daily volatility
    max_volatility: 0.10  # Max 10% daily volatility
    market_hours_only: false  # Trade 24/7
```

#### Aggressive Grid (Higher Risk)

```yaml
# config/strategies/grid_aggressive.yaml
strategy:
  type: grid_trading
  name: "ETH Aggressive Grid"

  parameters:
    symbol: "ETH/USDT"
    grid_levels: 50
    grid_spacing_pct: 0.2  # 0.2% between levels (tighter)
    grid_range:
      lower: 2000  # $2k
      upper: 4000  # $4k
    position_size_per_level: 200  # $200 per level

  risk_management:
    max_total_exposure: 10000  # $10k total
    stop_loss_pct: 0.20  # 20% stop loss
    take_profit_pct: 0.15  # 15% take profit

  execution:
    order_type: "limit"
    post_only: false  # Allow taker orders if needed
    timeout_seconds: 60  # Cancel after 60s if not filled
```

### Funding Rate Arbitrage

```yaml
# config/strategies/funding_arbitrage.yaml
strategy:
  type: funding_rate_arbitrage
  name: "Multi-Exchange Funding Arb"

  parameters:
    symbol: "BTC/USDT"
    exchanges: ["binance", "okx", "bybit"]

    # Enter when funding rate differential > threshold
    entry_threshold: 0.03  # 0.03% funding rate difference
    exit_threshold: 0.01   # Exit when diff < 0.01%

    position_size_usd: 10000  # $10k per side

  hedging:
    # Long on exchange with negative funding
    # Short on exchange with positive funding
    hedge_ratio: 1.0  # 1:1 hedge
    rebalance_threshold: 0.02  # Rebalance if > 2% imbalance

  risk_management:
    max_basis_risk: 0.005  # Max 0.5% basis risk
    max_positions: 3  # Max 3 concurrent arb positions
```

### Statistical Arbitrage (Pairs Trading)

```yaml
# config/strategies/stat_arb.yaml
strategy:
  type: statistical_arbitrage
  name: "BTC-ETH Pairs Trading"

  parameters:
    pair: ["BTC/USDT", "ETH/USDT"]
    lookback_period: 60  # 60 days for cointegration

    # Z-score thresholds
    entry_zscore: 2.0  # Enter when spread > 2 std devs
    exit_zscore: 0.5   # Exit when spread < 0.5 std devs
    stop_zscore: 3.0   # Stop loss at 3 std devs

    position_size_usd: 5000  # $5k per side

  cointegration:
    test: "engle_granger"  # Cointegration test
    significance: 0.05  # 5% significance level
    recompute_interval: "1d"  # Recompute daily

  execution:
    entry_type: "market"  # Market orders for entry
    exit_type: "limit"    # Limit orders for exit
```

---

## 2. Risk Management Configurations

### Conservative Risk Profile

```yaml
# config/risk/conservative.yaml
risk_management:
  name: "Conservative Risk Profile"

  position_limits:
    max_position_size_pct: 0.01  # 1% per position
    max_concentration_pct: 0.10  # 10% max in single asset
    max_correlation_exposure: 0.30  # 30% in correlated assets
    max_leverage: 1.0  # No leverage

  portfolio_limits:
    max_daily_loss_pct: 0.02  # 2% daily loss limit
    max_drawdown_pct: 0.10  # 10% max drawdown
    max_open_positions: 5

  per_trade_limits:
    max_trade_size_usd: 1000
    min_trade_size_usd: 50

  circuit_breakers:
    daily_loss_trigger: 0.02  # Trigger at 2% loss
    consecutive_losses: 5  # Trigger after 5 losses
    high_volatility_threshold: 0.15  # Pause if volatility > 15%
```

### Moderate Risk Profile

```yaml
# config/risk/moderate.yaml
risk_management:
  name: "Moderate Risk Profile"

  position_limits:
    max_position_size_pct: 0.02  # 2% per position
    max_concentration_pct: 0.20  # 20% max in single asset
    max_correlation_exposure: 0.40  # 40% in correlated assets
    max_leverage: 2.0  # 2x max leverage

  portfolio_limits:
    max_daily_loss_pct: 0.05  # 5% daily loss limit
    max_drawdown_pct: 0.20  # 20% max drawdown
    max_open_positions: 10

  per_trade_limits:
    max_trade_size_usd: 5000
    min_trade_size_usd: 100
```

### Aggressive Risk Profile

```yaml
# config/risk/aggressive.yaml
risk_management:
  name: "Aggressive Risk Profile"

  position_limits:
    max_position_size_pct: 0.05  # 5% per position
    max_concentration_pct: 0.30  # 30% max in single asset
    max_correlation_exposure: 0.50  # 50% in correlated assets
    max_leverage: 3.0  # 3x max leverage

  portfolio_limits:
    max_daily_loss_pct: 0.10  # 10% daily loss limit
    max_drawdown_pct: 0.30  # 30% max drawdown
    max_open_positions: 20

  per_trade_limits:
    max_trade_size_usd: 10000
    min_trade_size_usd: 200
```

---

## 3. Exchange Configurations

### Binance Configuration

```yaml
# config/exchanges/binance.yaml
exchange:
  id: binance
  name: "Binance"

  api:
    # Credentials loaded from AWS Secrets Manager
    secret_name: "trading-bot/binance/credentials"
    testnet: false

  options:
    defaultType: "future"  # spot, future, margin
    enableRateLimit: true  # CRITICAL!
    adjustForTimeDifference: true
    recvWindow: 10000

  rate_limits:
    requests_per_minute: 1200
    orders_per_minute: 300

  websockets:
    enabled: true
    reconnect_timeout: 5
    ping_interval: 30

  symbols:
    - "BTC/USDT"
    - "ETH/USDT"
    - "BNB/USDT"
    - "SOL/USDT"

  fees:
    maker: 0.0002  # 0.02%
    taker: 0.0004  # 0.04%
    discount: 0.25  # 25% if using BNB
```

### Multi-Exchange Configuration

```yaml
# config/exchanges/multi_exchange.yaml
exchanges:
  - id: binance
    weight: 50  # 50% of volume
    config: !include binance.yaml

  - id: okx
    weight: 30  # 30% of volume
    config: !include okx.yaml

  - id: bybit
    weight: 20  # 20% of volume
    config: !include bybit.yaml

routing:
  strategy: "smart"  # smart, round_robin, lowest_fee

  smart_routing:
    factors:
      - name: "liquidity"
        weight: 0.4
      - name: "fees"
        weight: 0.3
      - name: "latency"
        weight: 0.3
```

---

## 4. Database Configurations

### QuestDB Configuration

```yaml
# config/database/questdb.yaml
questdb:
  host: "localhost"
  http_port: 9000
  ilp_port: 9009  # InfluxDB Line Protocol
  pg_port: 8812   # PostgreSQL wire protocol

  tables:
    tickers:
      partitioning: "DAY"
      retention_days: 7  # Keep 7 days in hot storage

    orderbook_snapshots:
      partitioning: "HOUR"
      retention_days: 2  # Keep 2 days

    trades:
      partitioning: "DAY"
      retention_days: 7

  performance:
    commit_lag: 1000  # 1 second commit lag
    max_uncommitted_rows: 100000

  archival:
    enabled: true
    archive_to: "clickhouse"  # Archive to ClickHouse after 7 days
```

### ClickHouse Configuration

```yaml
# config/database/clickhouse.yaml
clickhouse:
  host: "localhost"
  http_port: 8123
  native_port: 9000

  database: "trading_analytics"

  tables:
    historical_tickers:
      engine: "MergeTree"
      partition_by: "toYYYYMM(timestamp)"
      order_by: "(symbol, timestamp)"
      ttl: "timestamp + INTERVAL 365 DAY"  # Keep 1 year

    aggregated_ohlcv:
      engine: "AggregatingMergeTree"
      partition_by: "toYYYYMM(timestamp)"
      order_by: "(symbol, timeframe, timestamp)"

  materialized_views:
    - name: "ohlcv_1m"
      interval: "1 MINUTE"
      source: "historical_tickers"

    - name: "ohlcv_5m"
      interval: "5 MINUTE"

    - name: "ohlcv_1h"
      interval: "1 HOUR"
```

### PostgreSQL Configuration

```yaml
# config/database/postgresql.yaml
postgresql:
  host: "localhost"
  port: 5432
  database: "trading_bot"

  # Credentials from AWS Secrets Manager
  secret_name: "trading-bot/database/credentials"

  connection_pool:
    min_size: 5
    max_size: 20
    timeout: 30

  tables:
    orders:
      indexes:
        - "symbol"
        - "status"
        - "created_at"
      partitioning: "created_at"  # Partition by month

    trades:
      indexes:
        - "order_id"
        - "symbol"
        - "executed_at"

    positions:
      indexes:
        - "symbol"
        - "status"
```

---

## 5. Deployment Configurations

### Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  trading-bot:
    build: .
    environment:
      - ENV=development
      - LOG_LEVEL=DEBUG
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
      - questdb
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: trading_bot
      POSTGRES_USER: trading_bot
      POSTGRES_PASSWORD: dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  questdb:
    image: questdb/questdb:latest
    ports:
      - "9000:9000"  # HTTP
      - "9009:9009"  # ILP
      - "8812:8812"  # PostgreSQL wire
    volumes:
      - questdb_data:/var/lib/questdb
    environment:
      QDB_CAIRO_COMMIT_LAG: 1000

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "8123:8123"
      - "9002:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse

volumes:
  postgres_data:
  redis_data:
  questdb_data:
  clickhouse_data:
```

### Kubernetes (Production)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-bot
  namespace: trading
spec:
  replicas: 2  # Active-passive HA
  selector:
    matchLabels:
      app: trading-bot
  template:
    metadata:
      labels:
        app: trading-bot
    spec:
      containers:
      - name: trading-bot
        image: trading-bot:latest
        env:
        - name: ENV
          value: "production"
        - name: AWS_REGION
          value: "us-east-1"
        - name: REDIS_HOST
          value: "redis-service"
        - name: POSTGRES_HOST
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: host
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: trading-bot-service
spec:
  selector:
    app: trading-bot
  ports:
  - port: 8080
    targetPort: 8080
```

### systemd Service (VPS Deployment)

```ini
# /etc/systemd/system/trading-bot.service
[Unit]
Description=Cryptocurrency Trading Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=trading-bot
WorkingDirectory=/opt/trading-bot
Environment="ENV=production"
Environment="AWS_REGION=us-east-1"

ExecStart=/opt/trading-bot/venv/bin/python -m claude_force.crypto_trading.main \
  --config /opt/trading-bot/config/production.yaml

Restart=always
RestartSec=10

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/trading-bot/logs

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

### Monitoring Stack

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    environment:
      GF_SECURITY_ADMIN_PASSWORD: changeme
      GF_USERS_ALLOW_SIGN_UP: false

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
```

---

## Example Backtest Configuration

```yaml
# config/backtest/grid_backtest.yaml
backtest:
  name: "BTC Grid Trading Backtest"

  data:
    source: "csv"  # csv, database, ccxt
    file: "data/BTCUSDT_1h_2024.csv"
    start_date: "2024-01-01"
    end_date: "2024-12-31"

  strategy:
    config: !include ../strategies/grid_conservative.yaml

  initial_capital: 10000  # $10k

  execution:
    slippage_pct: 0.001  # 0.1% slippage
    fees:
      maker: 0.0002  # 0.02%
      taker: 0.0004  # 0.04%

  analysis:
    metrics:
      - total_return
      - sharpe_ratio
      - max_drawdown
      - win_rate
      - profit_factor
      - number_of_trades

    plots:
      - portfolio_value
      - drawdown_curve
      - trade_distribution
      - pnl_heatmap

  optimization:
    enabled: true
    method: "grid_search"  # grid_search, random, bayesian

    parameters:
      grid_spacing_pct: [0.3, 0.5, 0.7, 1.0]
      grid_levels: [10, 20, 30, 50]

    metric: "sharpe_ratio"  # Optimize for Sharpe ratio
```

---

## Telegram Bot Configuration

```yaml
# config/telegram/bot.yaml
telegram:
  # Token from AWS Secrets Manager
  secret_name: "trading-bot/telegram/token"

  security:
    allowed_users:
      - 123456789  # Your user ID
      - 987654321  # Team member

    mfa_required_commands:
      - "/execute_trade"
      - "/close_all_positions"
      - "/update_risk_limits"

    mfa_secret_name: "trading-bot/telegram/mfa"

  commands:
    - command: "start"
      description: "Initialize bot"

    - command: "status"
      description: "View trading status"
      auto_refresh: 60  # Auto-refresh every 60s

    - command: "portfolio"
      description: "Portfolio overview"

    - command: "pnl"
      description: "P&L report"
      timeframes: ["1h", "24h", "7d", "30d"]

    - command: "stop"
      description: "Emergency stop (kill switch)"
      confirmation_required: true

  notifications:
    order_filled: true
    position_opened: true
    position_closed: true
    daily_report: true
    daily_report_time: "00:00 UTC"

    alerts:
      - type: "daily_loss_limit"
        threshold: 0.05
        severity: "critical"

      - type: "circuit_breaker"
        severity: "critical"

      - type: "low_balance"
        threshold: 5000
        severity: "warning"
```

---

## Complete Production Configuration

```yaml
# config/production.yaml
environment: production

logging:
  level: INFO
  format: json
  destinations:
    - console
    - file: /var/log/trading-bot/app.log
    - cloudwatch: trading-bot-logs

secrets:
  provider: aws_secrets_manager
  region: us-east-1

exchanges: !include exchanges/multi_exchange.yaml

database:
  questdb: !include database/questdb.yaml
  clickhouse: !include database/clickhouse.yaml
  postgresql: !include database/postgresql.yaml
  redis:
    host: redis-cluster.trading.local
    port: 6379
    ssl: true

strategy: !include strategies/grid_conservative.yaml

risk_management: !include risk/moderate.yaml

high_availability:
  enabled: true
  mode: active_passive
  leader_election:
    backend: redis
    ttl_seconds: 10
    instance_id: "${HOSTNAME}"

monitoring:
  prometheus:
    enabled: true
    port: 9090
    metrics_path: /metrics

  health_checks:
    enabled: true
    interval_seconds: 30

telegram: !include telegram/bot.yaml

audit_logging:
  enabled: true
  destination: s3
  bucket: trading-bot-audit-logs
  retention_days: 2555  # 7 years
```

---

## Usage Examples

### Running with Configuration

```bash
# Development
python -m claude_force.crypto_trading.main \
  --config config/development.yaml \
  --mode paper

# Production
python -m claude_force.crypto_trading.main \
  --config config/production.yaml \
  --mode live
```

### Backtesting

```bash
python -m claude_force.crypto_trading.backtest \
  --config config/backtest/grid_backtest.yaml \
  --output results/grid_backtest_2024.json
```

### Configuration Validation

```bash
python -m claude_force.crypto_trading.validate \
  --config config/production.yaml
```

---

These examples provide a solid foundation for configuring and deploying your cryptocurrency trading bot. Adjust parameters based on your risk tolerance, capital, and trading goals.

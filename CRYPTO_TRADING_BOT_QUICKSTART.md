# Cryptocurrency Trading Bot - Quick Start Guide

## Overview

This quick start guide will help you initialize a cryptocurrency trading bot project using the Claude Force crypto-trading-bot template.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Redis (for leader election and caching)
- PostgreSQL (for transactional data)
- Exchange API keys (Binance, OKX, Bybit, etc.)
- Telegram bot token (optional, for notifications)
- AWS account (for production secrets management)

## Step 1: Initialize Project with Template

```bash
# Using Claude Force CLI
claude-force init --template crypto-trading-bot my-trading-bot

cd my-trading-bot
```

## Step 2: Set Up Development Environment

### Install Dependencies

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install ccxt ccxt[pro] python-telegram-bot asyncio aiohttp
pip install psycopg[binary] redis questdb-client clickhouse-driver
pip install tenacity pydantic python-dotenv
pip install pytest pytest-asyncio pytest-mock

# Install development dependencies
pip install black ruff mypy pre-commit
```

### Environment Configuration (Development Only)

⚠️ **WARNING**: NEVER use .env files in production! Use AWS Secrets Manager.

Create `.env` file for **local development only**:

```bash
# Exchange Credentials (Development/Testnet)
BINANCE_API_KEY=your_testnet_api_key
BINANCE_SECRET=your_testnet_secret
BINANCE_TESTNET=true

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=trading_bot
POSTGRES_PASSWORD=dev_password_change_me
POSTGRES_DB=trading_bot

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# QuestDB Configuration
QUESTDB_HOST=localhost
QUESTDB_ILP_PORT=9009
QUESTDB_HTTP_PORT=9000

# Telegram Configuration (Optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ALLOWED_USERS=123456789,987654321

# Risk Management (Conservative defaults)
MAX_POSITION_SIZE_PCT=0.02  # 2%
MAX_DAILY_LOSS_PCT=0.05     # 5%
MAX_LEVERAGE=3.0
```

## Step 3: Start Infrastructure with Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: trading_bot
      POSTGRES_PASSWORD: dev_password_change_me
      POSTGRES_DB: trading_bot
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  questdb:
    image: questdb/questdb:latest
    ports:
      - "9000:9000"  # HTTP/REST
      - "9009:9009"  # ILP (InfluxDB Line Protocol)
      - "8812:8812"  # PostgreSQL wire protocol
    volumes:
      - questdb_data:/var/lib/questdb
    environment:
      QDB_CAIRO_COMMIT_LAG: 1000

  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "8123:8123"  # HTTP
      - "9002:9000"  # Native
    volumes:
      - clickhouse_data:/var/lib/clickhouse
    ulimits:
      nofile:
        soft: 262144
        hard: 262144

volumes:
  postgres_data:
  redis_data:
  questdb_data:
  clickhouse_data:
```

Start infrastructure:

```bash
docker-compose up -d
```

## Step 4: Initialize Database Schema

```bash
# Run database migrations
python scripts/init_database.py

# This creates:
# - PostgreSQL tables (orders, trades, positions, balances)
# - QuestDB tables (tickers, orderbook_snapshots, trades)
# - ClickHouse tables (analytics views)
```

## Step 5: Configure Exchange API Keys

### Security Checklist for Exchange API Keys

✅ **DO:**
- Use testnet/sandbox environments for development
- Enable IP whitelisting
- Restrict to trading permissions only
- Set daily withdrawal limit to $0

❌ **DON'T:**
- Enable withdrawal permissions
- Enable transfer permissions
- Use production keys in development
- Share API keys in version control

### Create Exchange API Keys

1. **Binance Testnet**: https://testnet.binance.vision/
2. **OKX Demo**: https://www.okx.com/demo-trading
3. **Bybit Testnet**: https://testnet.bybit.com/

Required permissions:
- ✅ Read account info
- ✅ Spot & Futures trading
- ❌ Withdrawal (MUST be disabled)
- ❌ Transfer (MUST be disabled)

## Step 6: Test Exchange Connection

```python
# test_connection.py
import asyncio
import ccxt.async_support as ccxt

async def test_exchange_connection():
    exchange = ccxt.binance({
        'apiKey': 'your_testnet_key',
        'secret': 'your_testnet_secret',
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
            'testnet': True
        }
    })

    try:
        # Test connection
        balance = await exchange.fetch_balance()
        print(f"✅ Connected successfully!")
        print(f"Balance: {balance['total']}")

        # Test market data
        ticker = await exchange.fetch_ticker('BTC/USDT')
        print(f"BTC/USDT: ${ticker['last']}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

    finally:
        await exchange.close()

if __name__ == '__main__':
    asyncio.run(test_exchange_connection())
```

Run test:
```bash
python test_connection.py
```

## Step 7: Configure Telegram Bot (Optional)

1. Create bot with @BotFather on Telegram
2. Get bot token
3. Get your Telegram user ID (use @userinfobot)
4. Add to `.env`:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALLOWED_USERS=123456789  # Your user ID
```

## Step 8: Run Your First Backtest

```python
# backtest_simple_strategy.py
from claude_force.crypto_trading.backtesting import Backtester
from claude_force.crypto_trading.strategies import GridTradingStrategy
import pandas as pd

# Load historical data
data = pd.read_csv('data/BTCUSDT_1h.csv', parse_dates=['timestamp'])

# Configure strategy
strategy = GridTradingStrategy(
    grid_levels=10,
    grid_spacing_pct=0.5,  # 0.5% between levels
    grid_range=(30000, 50000)  # $30k - $50k
)

# Run backtest
backtester = Backtester(
    strategy=strategy,
    data=data,
    initial_capital=10000
)

result = backtester.run()

print(f"""
Backtest Results:
-----------------
Total Return: {result.total_return:.2%}
Sharpe Ratio: {result.sharpe_ratio:.2f}
Max Drawdown: {result.max_drawdown:.2%}
Win Rate: {result.win_rate:.2%}
Number of Trades: {result.num_trades}
""")
```

## Step 9: Run Trading Bot (Paper Trading)

```bash
# Start in paper trading mode (no real orders)
python -m claude_force.crypto_trading.main \
    --mode paper \
    --strategy grid_trading \
    --config config/grid_trading.yaml
```

Monitor in another terminal:
```bash
# Watch logs
tail -f logs/trading_bot.log

# Monitor PostgreSQL
psql -h localhost -U trading_bot -d trading_bot
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;

# Monitor QuestDB
curl "http://localhost:9000/exec?query=SELECT * FROM tickers LATEST ON timestamp PARTITION BY symbol"
```

## Step 10: Telegram Bot Commands

Once bot is running, use these Telegram commands:

```
/start       - Initialize bot
/status      - View current status
/portfolio   - Portfolio overview
/pnl         - Profit & Loss report
/positions   - Open positions
/orders      - Active orders
/strategy    - Current strategy info
/pause       - Pause trading
/resume      - Resume trading
/stop        - Emergency stop (kill switch)
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Trading Bot System                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │  Exchange    │    │   Telegram   │    │   Risk    │ │
│  │  Connector   │◄───┤     Bot      │◄───┤  Engine   │ │
│  └──────┬───────┘    └──────────────┘    └─────┬─────┘ │
│         │                                        │       │
│         ▼                                        ▼       │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Core Trading Engine (asyncio)          │  │
│  │  - Order Management  - Strategy Execution        │  │
│  │  - Position Tracking - Event Loop                │  │
│  └───────────┬──────────────────────────────────────┘  │
│              │                                           │
│              ▼                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Data Layer                          │   │
│  │  - QuestDB (hot)    - ClickHouse (analytics)    │   │
│  │  - PostgreSQL (txn) - Redis (cache)             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Review Documentation**:
   - `CRYPTO_TRADING_BOT_SECURITY.md` - Production security
   - `CRYPTO_TRADING_BOT_EXAMPLES.md` - Configuration examples
   - `CRYPTO_TRADING_BOT_UPDATED_PLAN.md` - Full architecture

2. **Implement Trading Strategies**:
   - Start with simple strategies (grid trading, DCA)
   - Backtest thoroughly before live trading
   - Paper trade for at least 1 month

3. **Set Up Monitoring**:
   - Prometheus metrics
   - Grafana dashboards
   - Telegram alerts

4. **Production Deployment**:
   - Follow security guide
   - Set up AWS Secrets Manager
   - Configure HA with leader election
   - Enable comprehensive logging

## Common Issues & Troubleshooting

### Exchange API Errors

**"Invalid API key"**
- Verify API key and secret are correct
- Check if testnet mode is enabled for testnet keys
- Ensure IP is whitelisted

**"Rate limit exceeded"**
- Always use `enableRateLimit: True` in CCXT
- Reduce request frequency
- Implement exponential backoff

### Database Connection Issues

**"Connection refused"**
```bash
# Check if containers are running
docker-compose ps

# Check logs
docker-compose logs postgres
docker-compose logs questdb
```

### WebSocket Disconnections

- Normal behavior, bot auto-reconnects
- Check internet stability
- Review exchange status page

## Support & Resources

- **Documentation**: See all `CRYPTO_TRADING_BOT_*.md` files
- **Agent Help**: Use `/run-agent crypto-trading-architect` for guidance
- **Skills**: Access patterns via skills (crypto-trading-patterns, etc.)
- **Community**: Join trading bot development discussions

## Safety Reminders

⚠️ **CRITICAL**:
- Start with testnet/paper trading
- Never risk more than you can afford to lose
- Test extensively before live trading
- Always use stop losses and risk limits
- Monitor bot 24/7 during live trading
- Have emergency stop procedures

---

**Happy Trading! Remember: Past performance does not guarantee future results.**

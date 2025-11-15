# Exchange API Integration

Best practices for robust CCXT-based exchange integrations.

## Robust Exchange Connector

```python
import ccxt
from tenacity import retry, stop_after_attempt, wait_exponential

class ExchangeConnector:
    def __init__(self, exchange_id: str, api_key: str, secret: str):
        exchange_class = getattr(ccxt, exchange_id)
        self.exchange = exchange_class({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,  # CRITICAL!
            'options': {'adjustForTimeDifference': True}
        })

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def fetch_ticker(self, symbol: str):
        """Fetch ticker with automatic retries"""
        try:
            return await self.exchange.fetch_ticker(symbol)
        except ccxt.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise
        except ccxt.ExchangeError as e:
            logger.error(f"Exchange error: {e}")
            raise
```

## WebSocket Reconnection

```python
async def websocket_with_reconnection(exchange_id: str, symbol: str):
    """WebSocket connection with exponential backoff reconnection"""
    exchange = getattr(ccxt.pro, exchange_id)()
    attempt = 0

    while True:
        try:
            while True:
                ticker = await exchange.watch_ticker(symbol)
                attempt = 0  # Reset on success
                yield ticker
        except Exception as e:
            wait_time = min(2 ** attempt, 60)
            logger.warning(f"WebSocket error, reconnecting in {wait_time}s: {e}")
            await asyncio.sleep(wait_time)
            attempt += 1
```

## Rate Limiting

```python
# ✅ CORRECT - CCXT handles rate limiting
exchange = ccxt.binance({
    'enableRateLimit': True  # ALWAYS enable this!
})

# ❌ WRONG - No rate limiting
exchange = ccxt.binance()  # Will get banned!
```

---
**Always use `enableRateLimit: True`** to prevent exchange bans.

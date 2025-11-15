# Order Execution Patterns

Advanced order execution algorithms to minimize slippage and optimize fill quality.

## TWAP (Time-Weighted Average Price) Execution

```python
import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict

class TWAPExecutor:
    """
    Time-Weighted Average Price execution
    Splits large order evenly over time to minimize market impact
    """

    def __init__(self, exchange_connector):
        self.exchange = exchange_connector
        self.active_executions = {}

    async def execute_twap(
        self,
        symbol: str,
        side: str,  # 'buy' or 'sell'
        total_amount: Decimal,
        duration_minutes: int,
        num_slices: int = None
    ) -> Dict:
        """
        Execute TWAP order

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            side: 'buy' or 'sell'
            total_amount: Total quantity to trade
            duration_minutes: Time window for execution
            num_slices: Number of slices (default: duration_minutes)

        Returns:
            Execution report with fills, average price, slippage
        """
        if num_slices is None:
            num_slices = duration_minutes

        slice_amount = total_amount / num_slices
        interval_seconds = (duration_minutes * 60) / num_slices

        execution_id = f"twap_{symbol}_{datetime.utcnow().timestamp()}"
        self.active_executions[execution_id] = {
            'symbol': symbol,
            'side': side,
            'total_amount': total_amount,
            'fills': [],
            'start_time': datetime.utcnow(),
            'status': 'active'
        }

        logger.info(
            f"Starting TWAP execution: {total_amount} {symbol} "
            f"over {duration_minutes}m in {num_slices} slices"
        )

        try:
            for slice_num in range(num_slices):
                # Get current mid price
                ticker = await self.exchange.fetch_ticker(symbol)
                mid_price = (ticker['bid'] + ticker['ask']) / 2

                # Place limit order at mid price (passive execution)
                order = await self.exchange.create_limit_order(
                    symbol=symbol,
                    side=side,
                    amount=float(slice_amount),
                    price=float(mid_price)
                )

                # Wait for partial fill or timeout
                fill = await self._wait_for_fill(
                    order['id'],
                    timeout_seconds=interval_seconds * 0.8  # 80% of interval
                )

                self.active_executions[execution_id]['fills'].append(fill)

                # If not fully filled, cancel and use market order for remainder
                if fill['filled'] < slice_amount:
                    await self.exchange.cancel_order(order['id'])
                    remainder = slice_amount - fill['filled']

                    if remainder > 0:
                        market_fill = await self.exchange.create_market_order(
                            symbol=symbol,
                            side=side,
                            amount=float(remainder)
                        )
                        self.active_executions[execution_id]['fills'].append(market_fill)

                # Wait until next slice
                if slice_num < num_slices - 1:
                    await asyncio.sleep(interval_seconds)

            # Calculate execution statistics
            report = self._generate_execution_report(execution_id)
            self.active_executions[execution_id]['status'] = 'completed'

            return report

        except Exception as e:
            logger.error(f"TWAP execution failed: {e}")
            self.active_executions[execution_id]['status'] = 'failed'
            raise

    async def _wait_for_fill(
        self,
        order_id: str,
        timeout_seconds: float
    ) -> Dict:
        """Wait for order to fill or timeout"""
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            order = await self.exchange.fetch_order(order_id)

            if order['status'] in ['closed', 'filled']:
                return {
                    'filled': Decimal(str(order['filled'])),
                    'price': Decimal(str(order['average'])),
                    'timestamp': order['timestamp']
                }

            await asyncio.sleep(1)

        # Timeout - return partial fill
        order = await self.exchange.fetch_order(order_id)
        return {
            'filled': Decimal(str(order.get('filled', 0))),
            'price': Decimal(str(order.get('average', 0))),
            'timestamp': order['timestamp']
        }
```

## VWAP (Volume-Weighted Average Price) Execution

```python
import numpy as np

class VWAPExecutor:
    """
    Volume-Weighted Average Price execution
    Slices order according to historical volume distribution
    """

    def __init__(self, exchange_connector):
        self.exchange = exchange_connector

    async def execute_vwap(
        self,
        symbol: str,
        side: str,
        total_amount: Decimal,
        duration_minutes: int,
        lookback_days: int = 7
    ) -> Dict:
        """
        Execute VWAP order using historical volume profile

        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            total_amount: Total quantity to trade
            duration_minutes: Execution window
            lookback_days: Days of historical data for volume profile
        """
        # Fetch historical volume distribution
        volume_profile = await self._calculate_volume_profile(
            symbol,
            lookback_days
        )

        # Determine slice sizes based on expected volume
        slices = self._calculate_vwap_slices(
            total_amount,
            duration_minutes,
            volume_profile
        )

        logger.info(
            f"Starting VWAP execution: {total_amount} {symbol} "
            f"over {duration_minutes}m with {len(slices)} dynamic slices"
        )

        fills = []

        for slice_info in slices:
            # Wait until target time
            wait_time = (slice_info['target_time'] - datetime.utcnow()).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

            # Execute slice
            try:
                ticker = await self.exchange.fetch_ticker(symbol)
                mid_price = (ticker['bid'] + ticker['ask']) / 2

                order = await self.exchange.create_limit_order(
                    symbol=symbol,
                    side=side,
                    amount=float(slice_info['amount']),
                    price=float(mid_price)
                )

                # Wait briefly for fill
                fill = await self._wait_for_fill(order['id'], timeout_seconds=30)
                fills.append(fill)

                # Market order for remainder if needed
                if fill['filled'] < slice_info['amount']:
                    await self.exchange.cancel_order(order['id'])
                    remainder = slice_info['amount'] - fill['filled']

                    if remainder > 0:
                        market_order = await self.exchange.create_market_order(
                            symbol=symbol,
                            side=side,
                            amount=float(remainder)
                        )
                        fills.append(market_order)

            except Exception as e:
                logger.error(f"VWAP slice execution failed: {e}")
                continue

        return self._generate_vwap_report(fills, total_amount)

    async def _calculate_volume_profile(
        self,
        symbol: str,
        lookback_days: int
    ) -> Dict:
        """
        Calculate intraday volume distribution from historical data
        Returns percentage of daily volume per time bucket
        """
        # Fetch historical OHLCV data
        since = int((datetime.utcnow() - timedelta(days=lookback_days)).timestamp() * 1000)
        ohlcv = await self.exchange.fetch_ohlcv(
            symbol,
            timeframe='1h',
            since=since
        )

        # Group by hour of day
        hourly_volumes = {}
        for candle in ohlcv:
            timestamp, open_, high, low, close, volume = candle
            hour = datetime.fromtimestamp(timestamp / 1000).hour

            if hour not in hourly_volumes:
                hourly_volumes[hour] = []
            hourly_volumes[hour].append(volume)

        # Calculate average volume per hour
        volume_profile = {}
        total_volume = sum(np.mean(vols) for vols in hourly_volumes.values())

        for hour, volumes in hourly_volumes.items():
            avg_volume = np.mean(volumes)
            volume_profile[hour] = avg_volume / total_volume

        return volume_profile
```

## Iceberg Order Pattern

```python
class IcebergOrderExecutor:
    """
    Iceberg order execution - hide total order size
    Only show small portion on order book at a time
    """

    def __init__(self, exchange_connector):
        self.exchange = exchange_connector

    async def execute_iceberg(
        self,
        symbol: str,
        side: str,
        total_amount: Decimal,
        visible_amount: Decimal,  # Amount visible on order book
        price: Decimal = None     # None for market price
    ) -> Dict:
        """
        Execute iceberg order

        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            total_amount: Total order size (hidden)
            visible_amount: Visible portion on order book
            price: Limit price (None for market)
        """
        remaining = total_amount
        fills = []

        logger.info(
            f"Starting iceberg order: {total_amount} {symbol} "
            f"with {visible_amount} visible per slice"
        )

        while remaining > 0:
            # Determine current slice size
            slice_size = min(visible_amount, remaining)

            # Place order
            if price:
                order = await self.exchange.create_limit_order(
                    symbol=symbol,
                    side=side,
                    amount=float(slice_size),
                    price=float(price)
                )
            else:
                # Dynamic pricing at mid price
                ticker = await self.exchange.fetch_ticker(symbol)
                mid_price = (ticker['bid'] + ticker['ask']) / 2

                order = await self.exchange.create_limit_order(
                    symbol=symbol,
                    side=side,
                    amount=float(slice_size),
                    price=float(mid_price)
                )

            # Wait for full fill
            fill = await self._wait_for_full_fill(order['id'], timeout_seconds=300)
            fills.append(fill)

            remaining -= fill['filled']

            logger.info(f"Iceberg slice filled: {fill['filled']} @ {fill['price']}, remaining: {remaining}")

            # Small delay before next slice
            await asyncio.sleep(2)

        return self._generate_iceberg_report(fills, total_amount)
```

## Smart Order Router (SOR)

```python
class SmartOrderRouter:
    """
    Route orders across multiple exchanges for best execution
    """

    def __init__(self, exchange_connectors: Dict[str, 'ExchangeConnector']):
        self.exchanges = exchange_connectors

    async def route_order(
        self,
        symbol: str,
        side: str,
        amount: Decimal
    ) -> Dict:
        """
        Route order to exchange(s) with best liquidity and price

        Strategy:
        1. Fetch order books from all exchanges
        2. Calculate effective price for full amount on each exchange
        3. Optionally split order across multiple exchanges
        """
        # Fetch order books from all exchanges
        order_books = await self._fetch_all_order_books(symbol)

        # Calculate execution cost on each exchange
        execution_analysis = {}

        for exchange_name, order_book in order_books.items():
            analysis = self._analyze_execution_cost(
                order_book,
                side,
                amount
            )
            execution_analysis[exchange_name] = analysis

        # Find best single-exchange execution
        best_exchange = min(
            execution_analysis.items(),
            key=lambda x: x[1]['total_cost']
        )[0]

        logger.info(
            f"Smart routing: Best execution for {amount} {symbol} "
            f"on {best_exchange} at avg price {execution_analysis[best_exchange]['avg_price']}"
        )

        # Execute on best exchange
        order = await self.exchanges[best_exchange].create_market_order(
            symbol=symbol,
            side=side,
            amount=float(amount)
        )

        return {
            'exchange': best_exchange,
            'order': order,
            'execution_analysis': execution_analysis
        }

    def _analyze_execution_cost(
        self,
        order_book: Dict,
        side: str,
        amount: Decimal
    ) -> Dict:
        """Calculate total cost and average price for execution"""
        levels = order_book['asks'] if side == 'buy' else order_book['bids']

        remaining = amount
        total_cost = Decimal('0')
        total_filled = Decimal('0')

        for price, size in levels:
            price = Decimal(str(price))
            size = Decimal(str(size))

            fill_amount = min(remaining, size)
            total_cost += fill_amount * price
            total_filled += fill_amount
            remaining -= fill_amount

            if remaining <= 0:
                break

        if remaining > 0:
            # Insufficient liquidity
            return {
                'avg_price': None,
                'total_cost': Decimal('inf'),
                'liquidity_sufficient': False
            }

        return {
            'avg_price': total_cost / total_filled,
            'total_cost': total_cost,
            'liquidity_sufficient': True
        }
```

---
**Use these execution algorithms** to minimize slippage and improve fill quality for large orders.

# State Management Patterns

Robust state management for distributed cryptocurrency trading systems.

## Position Reconciliation

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class Position:
    symbol: str
    amount: Decimal
    entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    leverage: Decimal
    liquidation_price: Optional[Decimal]
    last_updated: datetime

class PositionReconciliation:
    """
    Reconcile positions between exchange, database, and in-memory state
    Critical for preventing duplicate orders and state drift
    """

    def __init__(self, exchange_connector, database, cache):
        self.exchange = exchange_connector
        self.db = database
        self.cache = cache

    async def reconcile_positions(self) -> Dict[str, Position]:
        """
        Full position reconciliation across all data sources
        Returns: Reconciled positions (source of truth)
        """
        logger.info("Starting position reconciliation...")

        # Fetch positions from all sources
        exchange_positions = await self._fetch_exchange_positions()
        db_positions = await self.db.get_positions()
        cache_positions = await self.cache.get_positions()

        # Build position map keyed by symbol
        reconciled = {}

        # Use exchange as source of truth
        for symbol, exchange_pos in exchange_positions.items():
            db_pos = db_positions.get(symbol)
            cache_pos = cache_positions.get(symbol)

            # Detect discrepancies
            discrepancies = []

            if db_pos and abs(db_pos.amount - exchange_pos.amount) > Decimal('0.0001'):
                discrepancies.append(
                    f"DB amount mismatch: {db_pos.amount} vs exchange {exchange_pos.amount}"
                )

            if cache_pos and abs(cache_pos.amount - exchange_pos.amount) > Decimal('0.0001'):
                discrepancies.append(
                    f"Cache amount mismatch: {cache_pos.amount} vs exchange {exchange_pos.amount}"
                )

            # Update DB and cache to match exchange
            if discrepancies:
                logger.warning(
                    f"Position discrepancy for {symbol}: {', '.join(discrepancies)}"
                )

                await self.db.update_position(exchange_pos)
                await self.cache.set_position(symbol, exchange_pos)

            reconciled[symbol] = exchange_pos

        # Check for positions in DB/cache but not on exchange (stale data)
        all_symbols = set(exchange_positions.keys()) | set(db_positions.keys()) | set(cache_positions.keys())

        for symbol in all_symbols:
            if symbol not in exchange_positions:
                if symbol in db_positions or symbol in cache_positions:
                    logger.warning(f"Found stale position for {symbol} - removing from DB/cache")
                    await self.db.delete_position(symbol)
                    await self.cache.delete_position(symbol)

        logger.info(f"Position reconciliation complete: {len(reconciled)} positions")

        return reconciled

    async def _fetch_exchange_positions(self) -> Dict[str, Position]:
        """Fetch positions from exchange and convert to Position objects"""
        raw_positions = await self.exchange.fetch_positions()

        positions = {}
        for pos in raw_positions:
            if pos['contracts'] == 0:
                continue  # Skip closed positions

            position = Position(
                symbol=pos['symbol'],
                amount=Decimal(str(pos['contracts'])),
                entry_price=Decimal(str(pos['entryPrice'])),
                current_price=Decimal(str(pos['markPrice'])),
                unrealized_pnl=Decimal(str(pos['unrealizedPnl'])),
                realized_pnl=Decimal(str(pos.get('realizedPnl', 0))),
                leverage=Decimal(str(pos.get('leverage', 1))),
                liquidation_price=Decimal(str(pos['liquidationPrice'])) if pos.get('liquidationPrice') else None,
                last_updated=datetime.utcnow()
            )

            positions[pos['symbol']] = position

        return positions
```

## Idempotency Pattern for Orders

```python
import hashlib
import uuid

class IdempotentOrderManager:
    """
    Ensure orders are only placed once, even with retries or duplicate requests
    Uses idempotency keys to prevent duplicate order submission
    """

    def __init__(self, exchange_connector, cache):
        self.exchange = exchange_connector
        self.cache = cache
        self.idempotency_ttl = 86400  # 24 hours

    async def place_order_idempotent(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: Decimal,
        price: Optional[Decimal] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict:
        """
        Place order with idempotency guarantee

        If called multiple times with same idempotency_key,
        returns the original order without placing duplicate
        """
        # Generate idempotency key if not provided
        if not idempotency_key:
            idempotency_key = self._generate_idempotency_key(
                symbol, side, order_type, amount, price
            )

        # Check if order already placed with this key
        cached_order = await self.cache.get(f"order:idempotency:{idempotency_key}")

        if cached_order:
            logger.info(
                f"Idempotent order already placed: {idempotency_key} -> {cached_order['id']}"
            )
            return cached_order

        # Place order
        try:
            if order_type == 'market':
                order = await self.exchange.create_market_order(
                    symbol=symbol,
                    side=side,
                    amount=float(amount)
                )
            else:
                order = await self.exchange.create_limit_order(
                    symbol=symbol,
                    side=side,
                    amount=float(amount),
                    price=float(price)
                )

            # Cache order with idempotency key
            await self.cache.set(
                f"order:idempotency:{idempotency_key}",
                order,
                ttl=self.idempotency_ttl
            )

            logger.info(
                f"Order placed with idempotency key {idempotency_key}: {order['id']}"
            )

            return order

        except Exception as e:
            logger.error(f"Order placement failed: {e}")
            raise

    def _generate_idempotency_key(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: Decimal,
        price: Optional[Decimal],
        strategy_id: str = "default",
        signal_id: str = None
    ) -> str:
        """
        Generate deterministic idempotency key from order parameters

        CRITICAL: Does NOT include timestamp - must be deterministic across retries
        Uses strategy_id and signal_id for uniqueness instead of time
        """
        # Use signal_id if provided, otherwise generate from parameters
        if signal_id is None:
            # For manual orders, use parameter-based ID
            signal_id = f"{symbol}_{side}_{amount}_{price}"

        key_data = f"{strategy_id}:{signal_id}:{symbol}:{side}:{order_type}:{amount}:{price}"
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]

        return key_hash
```

## Event Sourcing for Trade History

```python
from enum import Enum
from typing import List
import json

class EventType(Enum):
    ORDER_PLACED = "order_placed"
    ORDER_FILLED = "order_filled"
    ORDER_PARTIALLY_FILLED = "order_partially_filled"
    ORDER_CANCELLED = "order_cancelled"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    POSITION_MODIFIED = "position_modified"

@dataclass
class Event:
    event_id: str
    event_type: EventType
    timestamp: datetime
    aggregate_id: str  # Order ID or Position ID
    data: Dict
    version: int

class EventStore:
    """
    Event sourcing for complete audit trail
    Reconstruct state from event stream
    """

    def __init__(self, database):
        self.db = database

    async def append_event(
        self,
        event_type: EventType,
        aggregate_id: str,
        data: Dict
    ) -> Event:
        """Append event to event store"""
        # Get current version for aggregate
        current_version = await self._get_aggregate_version(aggregate_id)

        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            aggregate_id=aggregate_id,
            data=data,
            version=current_version + 1
        )

        # Store event
        await self.db.insert_event({
            'event_id': event.event_id,
            'event_type': event.event_type.value,
            'timestamp': event.timestamp,
            'aggregate_id': event.aggregate_id,
            'data': json.dumps(data),
            'version': event.version
        })

        logger.debug(f"Event appended: {event.event_type.value} for {aggregate_id}")

        return event

    async def get_events(
        self,
        aggregate_id: str,
        since_version: int = 0
    ) -> List[Event]:
        """Retrieve events for aggregate"""
        rows = await self.db.query(
            """
            SELECT event_id, event_type, timestamp, aggregate_id, data, version
            FROM events
            WHERE aggregate_id = $1 AND version > $2
            ORDER BY version ASC
            """,
            aggregate_id,
            since_version
        )

        events = []
        for row in rows:
            events.append(Event(
                event_id=row['event_id'],
                event_type=EventType(row['event_type']),
                timestamp=row['timestamp'],
                aggregate_id=row['aggregate_id'],
                data=json.loads(row['data']),
                version=row['version']
            ))

        return events

    async def reconstruct_order_state(self, order_id: str) -> Dict:
        """Reconstruct current order state from event stream"""
        events = await self.get_events(order_id)

        state = {
            'order_id': order_id,
            'status': 'unknown',
            'filled': Decimal('0'),
            'remaining': Decimal('0'),
            'fills': []
        }

        for event in events:
            if event.event_type == EventType.ORDER_PLACED:
                state['status'] = 'open'
                state['remaining'] = Decimal(str(event.data['amount']))
                state['symbol'] = event.data['symbol']
                state['side'] = event.data['side']

            elif event.event_type == EventType.ORDER_FILLED:
                state['status'] = 'filled'
                state['filled'] = Decimal(str(event.data['filled_amount']))
                state['remaining'] = Decimal('0')
                state['avg_price'] = Decimal(str(event.data['avg_price']))

            elif event.event_type == EventType.ORDER_PARTIALLY_FILLED:
                fill_amount = Decimal(str(event.data['fill_amount']))
                state['filled'] += fill_amount
                state['remaining'] -= fill_amount
                state['fills'].append(event.data)

            elif event.event_type == EventType.ORDER_CANCELLED:
                state['status'] = 'cancelled'

        return state
```

## Optimistic Locking for Concurrent Updates

```python
class OptimisticLockError(Exception):
    """Raised when optimistic lock fails due to concurrent modification"""
    pass

class OptimisticLockManager:
    """
    Optimistic locking for safe concurrent updates
    Uses version numbers to detect conflicts
    """

    # Whitelist of allowed tables to prevent SQL injection
    ALLOWED_TABLES = {'orders', 'positions', 'balances', 'trades', 'strategies'}

    async def update_with_optimistic_lock(
        self,
        table: str,
        record_id: str,
        updates: Dict,
        current_version: int
    ):
        """
        Update record with optimistic locking

        Raises OptimisticLockError if version mismatch (concurrent update)
        Raises ValueError if table name is not whitelisted
        """
        # Validate table name to prevent SQL injection
        if table not in self.ALLOWED_TABLES:
            raise ValueError(
                f"Invalid table name: {table}. "
                f"Allowed tables: {', '.join(self.ALLOWED_TABLES)}"
            )

        # Attempt update with version check
        result = await self.db.execute(
            f"""
            UPDATE {table}
            SET
                {', '.join(f"{k} = ${i+2}" for i, k in enumerate(updates.keys()))},
                version = version + 1,
                updated_at = NOW()
            WHERE id = $1 AND version = ${len(updates) + 2}
            RETURNING version
            """,
            record_id,
            *updates.values(),
            current_version
        )

        if not result:
            # Version mismatch - concurrent update detected
            raise OptimisticLockError(
                f"Concurrent modification detected for {table}:{record_id}. "
                f"Expected version {current_version}, but it was modified."
            )

        new_version = result[0]['version']
        logger.debug(f"Optimistic lock success: {table}:{record_id} updated to v{new_version}")

        return new_version

    async def update_with_retry(
        self,
        table: str,
        record_id: str,
        update_func,
        max_retries: int = 3
    ):
        """
        Update with automatic retry on optimistic lock failure
        update_func receives current record and returns updates dict
        """
        for attempt in range(max_retries):
            try:
                # Fetch current record
                record = await self.db.get_record(table, record_id)

                # Generate updates
                updates = update_func(record)

                # Attempt update
                new_version = await self.update_with_optimistic_lock(
                    table,
                    record_id,
                    updates,
                    record['version']
                )

                return new_version

            except OptimisticLockError:
                if attempt == max_retries - 1:
                    raise
                logger.warning(
                    f"Optimistic lock retry {attempt + 1}/{max_retries} for {table}:{record_id}"
                )
                await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
```

---
**Critical patterns** for maintaining state consistency in distributed trading systems.

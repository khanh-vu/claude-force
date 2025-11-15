# Crypto Trading Patterns

Comprehensive patterns and best practices for building cryptocurrency trading bots.

## Position Sizing Algorithm

```python
from decimal import Decimal

def calculate_position_size(
    account_balance: Decimal,
    risk_per_trade: Decimal,  # e.g., 0.02 for 2%
    entry_price: Decimal,
    stop_loss_price: Decimal
) -> Decimal:
    """
    Calculate position size based on risk management
    Returns amount to trade in base currency
    """
    risk_amount = account_balance * risk_per_trade
    risk_per_unit = abs(entry_price - stop_loss_price)

    if risk_per_unit == 0:
        raise ValueError("Stop loss must differ from entry price")

    position_size = risk_amount / risk_per_unit
    return position_size
```

## Order State Machine

```python
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OrderStateMachine:
    """Manages order lifecycle and valid state transitions"""

    VALID_TRANSITIONS = {
        OrderStatus.PENDING: [OrderStatus.SUBMITTED, OrderStatus.REJECTED],
        OrderStatus.SUBMITTED: [OrderStatus.PARTIAL, OrderStatus.FILLED, OrderStatus.CANCELLED],
        OrderStatus.PARTIAL: [OrderStatus.FILLED, OrderStatus.CANCELLED],
        OrderStatus.FILLED: [],  # Terminal state
        OrderStatus.CANCELLED: [],  # Terminal state
        OrderStatus.REJECTED: [],  # Terminal state
    }

    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = OrderStatus.PENDING

    def transition(self, new_status: OrderStatus):
        if new_status not in self.VALID_TRANSITIONS[self.status]:
            raise ValueError(
                f"Invalid transition: {self.status} -> {new_status}"
            )
        self.status = new_status
        self._log_transition(new_status)
```

## Circuit Breaker Pattern

```python
import time

class CircuitBreaker:
    """Prevents trading during system failures"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenError("Trading halted")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = 'OPEN'
            logger.critical("Circuit breaker opened - trading halted!")

    def _on_success(self):
        self.failures = 0
        self.state = 'CLOSED'
```

---
**Use these patterns** when implementing core trading bot functionality.

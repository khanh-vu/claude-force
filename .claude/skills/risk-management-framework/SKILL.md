# Risk Management Framework

Comprehensive risk management patterns for cryptocurrency trading bots.

## Pre-Trade Validation Framework

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

@dataclass
class ValidationResult:
    passed: bool
    failed_checks: List[str]
    warnings: List[str]

class PreTradeValidator:
    """Multi-layer validation before order submission"""

    def __init__(self, config: dict):
        self.max_position_pct = config.get('max_position_pct', Decimal('0.02'))  # 2%
        self.max_concentration = config.get('max_concentration', Decimal('0.20'))  # 20%
        self.max_daily_loss_pct = config.get('max_daily_loss_pct', Decimal('0.05'))  # 5%
        self.min_margin_buffer = config.get('min_margin_buffer', Decimal('0.30'))  # 30%
        self.max_correlated_exposure = config.get('max_correlated_exposure', Decimal('0.40'))  # 40%

    def validate_order(self, order: 'Order', portfolio: 'Portfolio') -> ValidationResult:
        """Run all pre-trade validation checks"""
        failed = []
        warnings = []

        # Check 1: Position size limit (max 2% of portfolio per trade)
        if not self._check_position_size(order, portfolio):
            failed.append(f"Position size exceeds {self.max_position_pct*100}% limit")

        # Check 2: Concentration risk (max 20% in single asset)
        if not self._check_concentration(order, portfolio):
            failed.append(f"Concentration exceeds {self.max_concentration*100}% limit")

        # Check 3: Daily loss limit (max 5% daily loss)
        if not self._check_daily_loss_limit(portfolio):
            failed.append(f"Daily loss limit ({self.max_daily_loss_pct*100}%) triggered")

        # Check 4: Margin health (min 30% buffer)
        margin_check, margin_pct = self._check_margin_health(order, portfolio)
        if not margin_check:
            failed.append(f"Insufficient margin buffer: {margin_pct:.2%} < {self.min_margin_buffer:.2%}")
        elif margin_pct < Decimal('0.40'):
            warnings.append(f"Low margin buffer: {margin_pct:.2%}")

        # Check 5: Correlation exposure (max 40% in correlated assets)
        if not self._check_correlation_exposure(order, portfolio):
            failed.append(f"Correlated exposure exceeds {self.max_correlated_exposure*100}% limit")

        # Check 6: Fat finger detection
        if not self._check_fat_finger(order):
            failed.append("Order price deviates >5% from market - possible fat finger")

        return ValidationResult(
            passed=len(failed) == 0,
            failed_checks=failed,
            warnings=warnings
        )

    def _check_position_size(self, order: 'Order', portfolio: 'Portfolio') -> bool:
        position_value = order.quantity * order.price
        max_position_value = portfolio.total_value * self.max_position_pct
        return position_value <= max_position_value

    def _check_concentration(self, order: 'Order', portfolio: 'Portfolio') -> bool:
        current_exposure = portfolio.get_asset_exposure(order.symbol)
        new_exposure = current_exposure + (order.quantity * order.price)
        concentration = new_exposure / portfolio.total_value
        return concentration <= self.max_concentration
```

## Risk Limit Hierarchy

```python
from enum import Enum

class RiskLevel(Enum):
    ACCOUNT = "account"      # Highest priority
    STRATEGY = "strategy"    # Mid priority
    POSITION = "position"    # Lowest priority

class RiskLimitHierarchy:
    """Hierarchical risk limits with priority enforcement"""

    def __init__(self):
        self.limits = {
            RiskLevel.ACCOUNT: {
                'max_daily_loss_pct': Decimal('0.05'),    # 5% account-wide
                'max_drawdown_pct': Decimal('0.20'),       # 20% max drawdown
                'max_leverage': Decimal('3.0'),            # 3x max leverage
                'max_open_positions': 20,
            },
            RiskLevel.STRATEGY: {
                'max_allocation_pct': Decimal('0.30'),     # 30% per strategy
                'max_daily_trades': 100,
                'max_position_size_pct': Decimal('0.10'),  # 10% per position
            },
            RiskLevel.POSITION: {
                'max_position_value': Decimal('50000'),    # $50k per position
                'min_position_value': Decimal('100'),      # $100 minimum
                'max_holding_period_hours': 72,            # 3 days max
            }
        }

    def check_limits(self, level: RiskLevel, metric: str, value: Decimal) -> bool:
        """Check if value is within limits for given level and metric"""
        if level not in self.limits:
            return True

        if metric not in self.limits[level]:
            return True

        limit = self.limits[level][metric]
        return value <= limit

    def get_effective_limit(self, metric: str) -> Decimal:
        """Get most restrictive limit across hierarchy"""
        limits = []
        for level in RiskLevel:
            if metric in self.limits[level]:
                limits.append(self.limits[level][metric])

        return min(limits) if limits else None
```

## Value at Risk (VaR) Calculator

```python
import numpy as np
import pandas as pd

class VaRCalculator:
    """Calculate Value at Risk for portfolio risk assessment"""

    def calculate_parametric_var(
        self,
        returns: pd.Series,
        portfolio_value: Decimal,
        confidence_level: float = 0.95,
        holding_period_days: int = 1
    ) -> Decimal:
        """
        Parametric VaR (assumes normal distribution)
        VaR = portfolio_value * z_score * volatility * sqrt(holding_period)
        """
        # Calculate mean and std of returns
        mean_return = returns.mean()
        std_return = returns.std()

        # Z-score for confidence level
        z_scores = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}
        z_score = z_scores.get(confidence_level, 1.65)

        # Calculate VaR
        var = portfolio_value * z_score * std_return * np.sqrt(holding_period_days)

        return Decimal(str(var))

    def calculate_historical_var(
        self,
        returns: pd.Series,
        portfolio_value: Decimal,
        confidence_level: float = 0.95
    ) -> Decimal:
        """
        Historical VaR (uses actual distribution)
        More accurate for non-normal distributions
        """
        # Sort returns and find percentile
        sorted_returns = returns.sort_values()
        percentile_index = int((1 - confidence_level) * len(sorted_returns))
        percentile_return = sorted_returns.iloc[percentile_index]

        # Calculate VaR
        var = portfolio_value * abs(percentile_return)

        return Decimal(str(var))
```

## Circuit Breaker with Cooldown

```python
import time
from datetime import datetime, timedelta

class EnhancedCircuitBreaker:
    """Circuit breaker with cooldown period and gradual recovery"""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 300,        # 5 minutes
        cooldown_seconds: int = 1800,      # 30 minutes
        gradual_recovery: bool = True
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout_seconds
        self.cooldown = cooldown_seconds
        self.gradual_recovery = gradual_recovery

        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN, COOLDOWN
        self.failures = 0
        self.last_failure_time = None
        self.recovery_count = 0
        self.recovery_threshold = 3  # Need 3 successes to fully recover

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""

        # Check state transitions
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker OPEN - trading halted. "
                    f"Retry in {self.timeout - (time.time() - self.last_failure_time):.0f}s"
                )

        elif self.state == 'COOLDOWN':
            if time.time() - self.last_failure_time > self.cooldown:
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker exiting cooldown - entering HALF_OPEN")
            else:
                raise CircuitBreakerCooldownError(
                    f"Circuit breaker in COOLDOWN - limited operations only"
                )

        # Try to execute
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure(e)
            raise

    def _on_success(self):
        """Handle successful execution"""
        if self.state == 'HALF_OPEN':
            self.recovery_count += 1

            if self.gradual_recovery:
                if self.recovery_count >= self.recovery_threshold:
                    self.state = 'CLOSED'
                    self.failures = 0
                    self.recovery_count = 0
                    logger.info("Circuit breaker fully recovered - CLOSED")
            else:
                self.state = 'CLOSED'
                self.failures = 0
                logger.info("Circuit breaker recovered - CLOSED")

        elif self.state == 'CLOSED':
            # Reset failure count on success
            self.failures = max(0, self.failures - 1)

    def _on_failure(self, error: Exception):
        """Handle failed execution"""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = 'OPEN'
            logger.critical(
                f"Circuit breaker OPENED after {self.failures} failures! "
                f"Last error: {error}"
            )

            # Send critical alert
            self._send_alert(error)

        elif self.state == 'HALF_OPEN':
            # Failed during recovery - back to COOLDOWN
            self.state = 'COOLDOWN'
            self.recovery_count = 0
            logger.warning("Circuit breaker failed during recovery - entering COOLDOWN")
```

---
**Always implement these patterns** to prevent catastrophic losses and ensure robust risk management.

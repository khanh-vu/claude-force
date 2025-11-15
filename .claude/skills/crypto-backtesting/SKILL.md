# Crypto Backtesting

Comprehensive backtesting framework patterns and pitfalls to avoid.

## Backtesting Engine

```python
import pandas as pd
from dataclasses import dataclass

@dataclass
class BacktestResult:
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    num_trades: int

class Backtester:
    def __init__(self, strategy, data: pd.DataFrame, initial_capital: float = 10000):
        self.strategy = strategy
        self.data = data
        self.initial_capital = initial_capital
        self.portfolio_value = []
        self.trades = []

    def run(self) -> BacktestResult:
        """Execute backtest with proper order of operations"""
        capital = self.initial_capital
        position = 0

        for timestamp, row in self.data.iterrows():
            # Generate signal BEFORE knowing close price (avoid lookahead bias)
            signal = self.strategy.generate_signal(row, position)

            if signal == 'buy' and position == 0:
                # Use NEXT bar's open price (realistic execution)
                entry_price = self._get_next_open(timestamp)
                shares = capital / entry_price
                position = shares
                capital = 0
                self.trades.append(('buy', timestamp, entry_price, shares))

            elif signal == 'sell' and position > 0:
                exit_price = self._get_next_open(timestamp)
                capital = position * exit_price
                self.trades.append(('sell', timestamp, exit_price, position))
                position = 0

            # Track portfolio value
            current_value = capital + (position * row['close'])
            self.portfolio_value.append(current_value)

        return self._calculate_metrics()
```

## Walk-Forward Analysis

```python
def walk_forward_optimization(
    strategy_class,
    data: pd.DataFrame,
    train_window: int = 252,  # 1 year
    test_window: int = 63,    # 3 months
    step_size: int = 21       # 1 month
):
    """
    Walk-forward optimization to prevent overfitting
    Train on historical data, test on future data
    """
    results = []

    for i in range(0, len(data) - train_window - test_window, step_size):
        # Split data
        train_data = data.iloc[i:i+train_window]
        test_data = data.iloc[i+train_window:i+train_window+test_window]

        # Optimize on training data
        best_params = optimize_strategy(strategy_class, train_data)

        # Test on out-of-sample data
        strategy = strategy_class(**best_params)
        backtest = Backtester(strategy, test_data)
        result = backtest.run()

        results.append({
            'train_period': (train_data.index[0], train_data.index[-1]),
            'test_period': (test_data.index[0], test_data.index[-1]),
            'params': best_params,
            'result': result
        })

    return results
```

## Avoiding Lookahead Bias

```python
# ❌ WRONG - Uses close price of same bar
def wrong_strategy(row):
    if row['rsi'] < 30:
        return 'buy', row['close']  # Lookahead bias!

# ✅ CORRECT - Uses next bar's open
def correct_strategy(row, next_open):
    if row['rsi'] < 30:
        return 'buy', next_open  # Realistic execution
```

---
**Critical**: Always test strategies with walk-forward analysis and realistic slippage.

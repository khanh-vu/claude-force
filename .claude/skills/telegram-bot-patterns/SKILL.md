# Telegram Bot Patterns

Patterns for building secure, interactive Telegram bot interfaces for trading bots.

## Command Handler Pattern

```python
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

async def portfolio_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display current portfolio with interactive buttons"""

    # Fetch portfolio data
    portfolio = await get_portfolio_status()

    # Create interactive keyboard
    keyboard = [
        [InlineKeyboardButton("📊 Detailed View", callback_data='portfolio_detail')],
        [InlineKeyboardButton("💰 P&L Report", callback_data='pnl_report')],
        [InlineKeyboardButton("🔄 Refresh", callback_data='refresh')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Format message
    message = f"""
📈 **Portfolio Status**

Total Value: ${portfolio['total_value']:,.2f}
Today's P&L: ${portfolio['daily_pnl']:+,.2f} ({portfolio['daily_pnl_pct']:+.2f}%)
Open Positions: {portfolio['num_positions']}

💼 Top 3 Positions:
{format_top_positions(portfolio['positions'])}
    """

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
```

## Authentication Pattern

```python
from functools import wraps

# Whitelist of allowed user IDs
ALLOWED_USERS = {123456789, 987654321}

def restricted(func):
    """Decorator to restrict command to whitelisted users"""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id

        if user_id not in ALLOWED_USERS:
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            await update.message.reply_text(
                "⛔ Access denied. This incident has been logged."
            )
            return

        return await func(update, context, *args, **kwargs)
    return wrapped

@restricted
async def execute_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute trade - requires authorization"""
    # Trading logic here
    pass
```

## MFA Pattern for Sensitive Commands

```python
import pyotp
import redis.asyncio as redis

class TelegramMFA:
    """Multi-factor authentication for trading commands"""

    def __init__(self, secret: str, redis_client: redis.Redis):
        self.totp = pyotp.TOTP(secret)
        self.redis = redis_client
        self.mfa_ttl = 300  # 5 minutes

    async def request_mfa(self, user_id: int, command: str):
        """
        Request MFA code for sensitive command

        Stores pending command in Redis with 5-minute expiry
        Survives bot restarts
        """
        await self.redis.setex(
            f"mfa:pending:{user_id}",
            self.mfa_ttl,
            command
        )

        return (
            "🔐 **MFA Required**\n\n"
            "This is a sensitive operation.\n"
            "Please enter your 6-digit authenticator code:\n"
            "`/mfa <code>`\n"
            "(Code expires in 5 minutes)"
        )

    async def verify_mfa(self, user_id: int, code: str) -> bool:
        """
        Verify MFA code and execute pending command

        Retrieves pending command from Redis
        Deletes after successful verification to prevent replay
        """
        if self.totp.verify(code, valid_window=1):
            # Get pending command from Redis
            command = await self.redis.get(f"mfa:pending:{user_id}")

            if command:
                # Delete immediately to prevent replay attacks
                await self.redis.delete(f"mfa:pending:{user_id}")

                # Execute command
                await self.execute_pending_command(command.decode())
                return True
        return False
```

---
**Use these patterns** for secure Telegram bot development.

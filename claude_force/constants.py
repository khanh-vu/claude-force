"""
System-wide constants and configuration values.

This module centralizes all magic numbers and configuration constants
used throughout the claude-force codebase, making them easier to maintain
and modify.

ARCH-05: Created to eliminate scattered magic numbers and improve
maintainability.
"""

# =============================================================================
# TOKEN LIMITS
# =============================================================================

# Maximum token limit for tasks (100K tokens)
MAX_TOKEN_LIMIT = 100_000

# Default character-to-token conversion ratio
DEFAULT_TOKEN_ESTIMATE = 4  # 4 chars ≈ 1 token

# Typical agent prompt size in tokens
TYPICAL_AGENT_PROMPT_TOKENS = 1_000

# Typical task size in tokens for analytics
TYPICAL_TASK_TOKENS = 10_000

# Maximum characters for content preview/truncation
MAX_CONTENT_PREVIEW_CHARS = 1_000

# Maximum task characters before truncation in logs
MAX_TASK_LOG_CHARS = 100


# =============================================================================
# CACHE CONFIGURATION
# =============================================================================

# Default cache TTL in hours
DEFAULT_CACHE_TTL_HOURS = 24

# Maximum cache size in megabytes
MAX_CACHE_SIZE_MB = 100

# Default cache secret (MUST be changed in production)
DEFAULT_CACHE_SECRET = "default_secret_change_in_production"


# =============================================================================
# PERFORMANCE TRACKING
# =============================================================================

# Maximum number of metrics entries to keep in memory (ring buffer)
MAX_METRICS_IN_MEMORY = 10_000

# Default metrics export format
DEFAULT_METRICS_EXPORT_FORMAT = "jsonl"

# Default time window for performance trends (hours)
DEFAULT_TREND_INTERVAL_HOURS = 24

# Metrics data retention period (days)
METRICS_RETENTION_DAYS = 30


# =============================================================================
# RATE LIMITING
# =============================================================================

# Maximum concurrent requests
DEFAULT_MAX_CONCURRENT_REQUESTS = 3

# MCP server rate limit (requests per window)
MCP_RATE_LIMIT_REQUESTS = 100

# MCP server rate limit window (seconds)
MCP_RATE_LIMIT_WINDOW_SECONDS = 3_600  # 1 hour

# Demo mode rate limit (requests per hour)
DEMO_MODE_RATE_LIMIT = 1_000


# =============================================================================
# TIMEOUTS
# =============================================================================

# Default timeout for agent execution (seconds)
DEFAULT_TIMEOUT_SECONDS = 30

# Typical task duration for estimation (minutes)
TYPICAL_TASK_DURATION_MINUTES = 30

# Workflow duration buffer (minutes)
WORKFLOW_DURATION_BUFFER_MINUTES = 30


# =============================================================================
# INPUT VALIDATION
# =============================================================================

# Maximum task input size (bytes) - SEC-02
MAX_TASK_SIZE_MB = 10
MAX_TASK_SIZE_BYTES = MAX_TASK_SIZE_MB * 1024 * 1024

# Minimum agent definition content length (chars)
MIN_AGENT_DEFINITION_CHARS = 100


# =============================================================================
# DISPLAY AND FORMATTING
# =============================================================================

# Column widths for CLI table formatting
COL_WIDTH_NAME = 30
COL_WIDTH_PRIORITY = 10
COL_WIDTH_AGENT = 30
COL_WIDTH_RUNS = 6
COL_WIDTH_SUCCESS = 8
COL_WIDTH_TIME = 10
COL_WIDTH_COST = 10

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


# =============================================================================
# DATA RETENTION AND CLEANUP
# =============================================================================

# Agent memory session retention (days)
AGENT_MEMORY_RETENTION_DAYS = 90

# Old metrics cleanup threshold (days)
OLD_METRICS_CLEANUP_DAYS = 30

# Agent statistics default time window (days)
AGENT_STATS_DEFAULT_DAYS = 30


# =============================================================================
# TASK ROUTING
# =============================================================================

# Task complexity threshold (word count)
TASK_COMPLEXITY_WORD_THRESHOLD = 30

# Token ratio assumptions for analytics
INPUT_TOKEN_RATIO = 0.70  # 70% of tokens are typically input
OUTPUT_TOKEN_RATIO = 0.30  # 30% of tokens are typically output


# =============================================================================
# TEMPLATE GALLERY
# =============================================================================

# Default estimated time for templates
DEFAULT_TEMPLATE_TIME = "15-30 minutes"

# Time estimates by complexity
TEMPLATE_TIME_SIMPLE = "20-30 minutes"
TEMPLATE_TIME_MODERATE = "30-45 minutes"
TEMPLATE_TIME_COMPLEX = "60-90 minutes"


# =============================================================================
# CONVERSION UTILITIES
# =============================================================================


def ms_to_seconds(milliseconds: float) -> float:
    """Convert milliseconds to seconds."""
    return milliseconds / 1000


def hours_to_seconds(hours: int) -> int:
    """Convert hours to seconds."""
    return hours * 3600


def days_to_seconds(days: int) -> int:
    """Convert days to seconds."""
    return days * 86400


def percent(value: float, total: float) -> float:
    """Calculate percentage safely (handles division by zero)."""
    return (value / total * 100) if total > 0 else 0.0

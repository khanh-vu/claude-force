"""
Centralized Logging Configuration for claude-force.

Provides runtime logging configuration with support for:
- YAML-based configuration files
- CLI flag overrides (--log-level, --log-file, --log-format)
- Environment variable overrides
- Multiple output formats (text, JSON)
- Log rotation

Usage:
    # Basic setup (uses defaults)
    setup_logging()

    # With CLI overrides
    setup_logging(log_level="DEBUG", log_file="/var/log/app.log")

    # With JSON format
    setup_logging(log_format="json", log_file="/var/log/app.json")

    # With custom config file
    setup_logging(config_file="/path/to/custom/logging.yaml")
"""

import logging
import logging.config
import logging.handlers
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

# Global flag to track if logging has been configured
_LOGGING_CONFIGURED = False


def get_default_config_path() -> Path:
    """Get path to default logging configuration file."""
    current_dir = Path(__file__).parent
    return current_dir / "logging_config.yaml"


def load_config_file(config_path: Path) -> Dict[str, Any]:
    """
    Load logging configuration from YAML file.

    Args:
        config_path: Path to logging configuration YAML file

    Returns:
        Dictionary with logging configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Logging config not found: {config_path}")

    # Check file size (max 1MB for safety)
    if config_path.stat().st_size > 1024 * 1024:
        raise ValueError(f"Logging config file too large: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_default_config() -> Dict[str, Any]:
    """
    Get default logging configuration (fallback if YAML fails).

    Returns:
        Dictionary with basic logging configuration
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': 'simple',
                'level': 'INFO'
            }
        },
        'loggers': {
            'claude_force': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['console']
        }
    }


def apply_cli_overrides(
    config: Dict[str, Any],
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> Dict[str, Any]:
    """
    Apply CLI flag overrides to logging configuration.

    Args:
        config: Base logging configuration
        log_level: Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file path override
        log_format: Log format override (text, json)

    Returns:
        Modified configuration dictionary
    """
    # Apply log level override
    if log_level:
        level = log_level.upper()
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level not in valid_levels:
            raise ValueError(f"Invalid log level: {log_level}. Must be one of {valid_levels}")

        # Update all claude_force loggers
        for logger_name in config.get('loggers', {}).keys():
            if logger_name.startswith('claude_force'):
                config['loggers'][logger_name]['level'] = level

        # Also update console handler level if DEBUG
        if level == 'DEBUG' and 'handlers' in config:
            if 'console' in config['handlers']:
                config['handlers']['console']['level'] = 'DEBUG'
                config['handlers']['console']['formatter'] = 'detailed'

    # Apply log file override
    if log_file:
        # Ensure parent directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Choose handler name based on format
        handler_name = 'file_json' if log_format == 'json' else 'file'

        # Add file handler if not present
        if 'handlers' not in config:
            config['handlers'] = {}

        # Update or create file handler
        if handler_name in config['handlers']:
            config['handlers'][handler_name]['filename'] = str(log_file)
        else:
            # Create new file handler
            formatter = 'json' if log_format == 'json' else 'detailed'
            config['handlers'][handler_name] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(log_file),
                'formatter': formatter,
                'level': 'DEBUG',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }

        # Add file handler to all claude_force loggers
        for logger_name in config.get('loggers', {}).keys():
            if logger_name.startswith('claude_force'):
                handlers = config['loggers'][logger_name].get('handlers', [])
                if handler_name not in handlers:
                    handlers.append(handler_name)
                    config['loggers'][logger_name]['handlers'] = handlers

    # Apply log format override (affects console output)
    if log_format:
        if log_format not in ['text', 'json', 'simple', 'detailed']:
            raise ValueError(f"Invalid log format: {log_format}. Must be text, json, simple, or detailed")

        # Map format names to formatters
        format_map = {
            'text': 'simple',
            'simple': 'simple',
            'detailed': 'detailed',
            'json': 'json'
        }
        formatter = format_map.get(log_format, 'simple')

        # Update console handler formatter
        if 'handlers' in config and 'console' in config['handlers']:
            config['handlers']['console']['formatter'] = formatter

    return config


def apply_env_overrides(
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply environment variable overrides to logging configuration.

    Environment variables:
        CLAUDE_FORCE_LOG_LEVEL: Override log level
        CLAUDE_FORCE_LOG_FILE: Override log file path
        CLAUDE_FORCE_LOG_FORMAT: Override log format

    Args:
        config: Base logging configuration

    Returns:
        Modified configuration dictionary
    """
    env_level = os.getenv('CLAUDE_FORCE_LOG_LEVEL')
    env_file = os.getenv('CLAUDE_FORCE_LOG_FILE')
    env_format = os.getenv('CLAUDE_FORCE_LOG_FORMAT')

    return apply_cli_overrides(config, env_level, env_file, env_format)


def setup_logging(
    config_file: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    force: bool = False
) -> None:
    """
    Configure logging for claude-force.

    This function should be called once at application startup.
    Subsequent calls are ignored unless force=True.

    Args:
        config_file: Path to custom logging YAML file (optional)
        log_level: Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file path override
        log_format: Log format (text, json, simple, detailed)
        force: Force reconfiguration even if already configured

    Raises:
        FileNotFoundError: If custom config file doesn't exist
        ValueError: If invalid log level or format provided
    """
    global _LOGGING_CONFIGURED

    # Skip if already configured (unless forced)
    if _LOGGING_CONFIGURED and not force:
        return

    try:
        # Load base configuration
        if config_file:
            config_path = Path(config_file)
            config = load_config_file(config_path)
        else:
            # Try to load default config
            default_path = get_default_config_path()
            try:
                config = load_config_file(default_path)
            except (FileNotFoundError, yaml.YAMLError) as e:
                # Fall back to hardcoded default
                logging.warning(f"Could not load logging config: {e}. Using defaults.")
                config = get_default_config()

        # Apply CLI overrides (takes precedence over env)
        config = apply_cli_overrides(config, log_level, log_file, log_format)

        # Apply environment variable overrides (if no CLI overrides)
        if not any([log_level, log_file, log_format]):
            config = apply_env_overrides(config)

        # Apply configuration
        logging.config.dictConfig(config)

        _LOGGING_CONFIGURED = True

        # Log successful configuration
        logger = logging.getLogger('claude_force')
        logger.debug(f"Logging configured successfully")

    except Exception as e:
        # Fall back to basic logging on error
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.error(f"Error configuring logging: {e}. Using basic config.")
        _LOGGING_CONFIGURED = True


def reset_logging() -> None:
    """
    Reset logging configuration (mainly for testing).

    This clears the configured flag so setup_logging() can be called again.
    """
    global _LOGGING_CONFIGURED
    _LOGGING_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Ensures logging is configured before returning logger.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    if not _LOGGING_CONFIGURED:
        setup_logging()

    return logging.getLogger(name)

"""
Tests for centralized logging configuration.
"""

import unittest
import logging
import tempfile
import os
import json
from pathlib import Path

from claude_force.logging_setup import (
    setup_logging,
    reset_logging,
    get_logger,
    load_config_file,
    get_default_config,
    apply_cli_overrides,
    apply_env_overrides,
    get_default_config_path
)


class TestLoggingSetup(unittest.TestCase):
    """Test logging setup and configuration."""

    def setUp(self):
        """Reset logging before each test."""
        reset_logging()
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        cf_logger = logging.getLogger('claude_force')
        for handler in cf_logger.handlers[:]:
            cf_logger.removeHandler(handler)

    def tearDown(self):
        """Cleanup after tests."""
        reset_logging()
        # Clear environment variables
        for var in ['CLAUDE_FORCE_LOG_LEVEL', 'CLAUDE_FORCE_LOG_FILE', 'CLAUDE_FORCE_LOG_FORMAT']:
            if var in os.environ:
                del os.environ[var]

    def test_default_config_path_exists(self):
        """Test that default config file exists."""
        config_path = get_default_config_path()
        self.assertTrue(config_path.exists(), f"Default config not found: {config_path}")
        self.assertEqual(config_path.name, "logging_config.yaml")

    def test_load_config_file(self):
        """Test loading configuration from YAML file."""
        config_path = get_default_config_path()
        config = load_config_file(config_path)

        self.assertIn('version', config)
        self.assertEqual(config['version'], 1)
        self.assertIn('formatters', config)
        self.assertIn('handlers', config)
        self.assertIn('loggers', config)

    def test_load_config_file_not_found(self):
        """Test loading non-existent config file."""
        with self.assertRaises(FileNotFoundError):
            load_config_file(Path("/nonexistent/config.yaml"))

    def test_load_config_file_too_large(self):
        """Test loading excessively large config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Write >1MB of data
            f.write('x' * (1024 * 1024 + 1))
            large_file = f.name

        try:
            with self.assertRaises(ValueError) as ctx:
                load_config_file(Path(large_file))
            self.assertIn("too large", str(ctx.exception))
        finally:
            os.unlink(large_file)

    def test_get_default_config(self):
        """Test getting fallback default configuration."""
        config = get_default_config()

        self.assertEqual(config['version'], 1)
        self.assertIn('formatters', config)
        self.assertIn('simple', config['formatters'])
        self.assertIn('handlers', config)
        self.assertIn('console', config['handlers'])
        self.assertIn('loggers', config)
        self.assertIn('claude_force', config['loggers'])

    def test_setup_logging_default(self):
        """Test basic logging setup with defaults."""
        setup_logging()

        logger = logging.getLogger('claude_force')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.level, logging.INFO)

    def test_setup_logging_only_once(self):
        """Test that logging setup is only applied once."""
        setup_logging(log_level="DEBUG")
        logger1 = logging.getLogger('claude_force')
        level1 = logger1.level

        # Second call should not change anything
        setup_logging(log_level="ERROR")
        logger2 = logging.getLogger('claude_force')
        level2 = logger2.level

        self.assertEqual(level1, level2)

    def test_setup_logging_force_reconfigure(self):
        """Test forcing logging reconfiguration."""
        setup_logging(log_level="DEBUG")
        logger = logging.getLogger('claude_force')
        self.assertEqual(logger.level, logging.DEBUG)

        # Force reconfiguration
        setup_logging(log_level="ERROR", force=True)
        self.assertEqual(logger.level, logging.ERROR)

    def test_get_logger(self):
        """Test getting logger (auto-configures if needed)."""
        logger = get_logger('claude_force.test')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'claude_force.test')

    def test_apply_cli_overrides_log_level(self):
        """Test applying log level override."""
        config = get_default_config()
        modified = apply_cli_overrides(config, log_level="DEBUG")

        self.assertEqual(modified['loggers']['claude_force']['level'], 'DEBUG')

    def test_apply_cli_overrides_invalid_level(self):
        """Test applying invalid log level."""
        config = get_default_config()
        with self.assertRaises(ValueError) as ctx:
            apply_cli_overrides(config, log_level="INVALID")
        self.assertIn("Invalid log level", str(ctx.exception))

    def test_apply_cli_overrides_log_file(self):
        """Test applying log file override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            config = get_default_config()
            modified = apply_cli_overrides(config, log_file=log_file)

            # Should have file handler
            self.assertIn('file', modified['handlers'])
            self.assertEqual(modified['handlers']['file']['filename'], log_file)

            # claude_force logger should use file handler
            handlers = modified['loggers']['claude_force']['handlers']
            self.assertIn('file', handlers)

    def test_apply_cli_overrides_log_file_json(self):
        """Test applying JSON log file override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.json")
            config = get_default_config()
            modified = apply_cli_overrides(config, log_file=log_file, log_format="json")

            # Should have file_json handler
            self.assertIn('file_json', modified['handlers'])
            self.assertEqual(modified['handlers']['file_json']['filename'], log_file)
            self.assertEqual(modified['handlers']['file_json']['formatter'], 'json')

    def test_apply_cli_overrides_log_format(self):
        """Test applying log format override."""
        config = get_default_config()
        modified = apply_cli_overrides(config, log_format="json")

        # Console handler should use json formatter
        self.assertEqual(modified['handlers']['console']['formatter'], 'json')

    def test_apply_cli_overrides_invalid_format(self):
        """Test applying invalid log format."""
        config = get_default_config()
        with self.assertRaises(ValueError) as ctx:
            apply_cli_overrides(config, log_format="invalid")
        self.assertIn("Invalid log format", str(ctx.exception))

    def test_apply_env_overrides(self):
        """Test applying environment variable overrides."""
        os.environ['CLAUDE_FORCE_LOG_LEVEL'] = 'DEBUG'
        os.environ['CLAUDE_FORCE_LOG_FORMAT'] = 'json'

        config = get_default_config()
        modified = apply_env_overrides(config)

        self.assertEqual(modified['loggers']['claude_force']['level'], 'DEBUG')
        self.assertEqual(modified['handlers']['console']['formatter'], 'json')

    def test_setup_logging_with_file(self):
        """Test complete logging setup with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "app.log")

            setup_logging(log_level="DEBUG", log_file=log_file)

            logger = logging.getLogger('claude_force')
            logger.info("Test message")
            logger.debug("Debug message")

            # Verify file was created and contains messages
            self.assertTrue(os.path.exists(log_file))

            with open(log_file, 'r') as f:
                content = f.read()
                self.assertIn("Test message", content)
                self.assertIn("Debug message", content)

    def test_setup_logging_creates_parent_dirs(self):
        """Test that log file parent directories are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "subdir", "nested", "app.log")

            setup_logging(log_file=log_file)

            logger = logging.getLogger('claude_force')
            logger.info("Test message")

            # Verify nested directories were created
            self.assertTrue(os.path.exists(log_file))

    def test_logging_integration(self):
        """Test complete logging integration scenario."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "integration.log")

            # Setup with all options
            setup_logging(
                log_level="DEBUG",
                log_file=log_file,
                log_format="detailed"
            )

            # Get loggers for different modules
            logger_main = logging.getLogger('claude_force')
            logger_marketplace = logging.getLogger('claude_force.marketplace')
            logger_router = logging.getLogger('claude_force.agent_router')

            # Log messages at different levels
            logger_main.debug("Debug from main")
            logger_marketplace.info("Info from marketplace")
            logger_router.warning("Warning from router")
            logger_main.error("Error from main")

            # Read log file
            with open(log_file, 'r') as f:
                content = f.read()

            # Verify all messages present
            self.assertIn("Debug from main", content)
            self.assertIn("Info from marketplace", content)
            self.assertIn("Warning from router", content)
            self.assertIn("Error from main", content)

            # Verify detailed format (includes filename and line number)
            self.assertIn("test_logging_setup.py", content)

    def test_log_rotation_config(self):
        """Test that log rotation is configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "rotate.log")

            setup_logging(log_file=log_file)

            logger = logging.getLogger('claude_force')

            # Find the file handler
            file_handler = None
            for handler in logger.handlers:
                if isinstance(handler, logging.handlers.RotatingFileHandler):
                    file_handler = handler
                    break

            self.assertIsNotNone(file_handler, "Should have RotatingFileHandler")
            self.assertEqual(file_handler.maxBytes, 10485760)  # 10MB
            self.assertEqual(file_handler.backupCount, 5)

    def test_env_var_precedence(self):
        """Test that CLI overrides take precedence over environment variables."""
        os.environ['CLAUDE_FORCE_LOG_LEVEL'] = 'ERROR'

        # CLI override should win
        setup_logging(log_level="DEBUG")

        logger = logging.getLogger('claude_force')
        self.assertEqual(logger.level, logging.DEBUG)

    def test_fallback_on_error(self):
        """Test fallback to basic logging on configuration error."""
        # Use non-existent custom config file
        setup_logging(config_file="/nonexistent/bad.yaml")

        # Should still have logging configured (fallback)
        logger = logging.getLogger('claude_force')
        self.assertIsNotNone(logger)

        # Should be able to log without errors
        logger.info("Test message")


class TestLoggingLevels(unittest.TestCase):
    """Test different logging levels."""

    def setUp(self):
        """Reset logging before each test."""
        reset_logging()

    def tearDown(self):
        """Cleanup after tests."""
        reset_logging()

    def test_debug_level(self):
        """Test DEBUG logging level."""
        setup_logging(log_level="DEBUG")
        logger = logging.getLogger('claude_force')
        self.assertEqual(logger.level, logging.DEBUG)

    def test_info_level(self):
        """Test INFO logging level."""
        setup_logging(log_level="INFO")
        logger = logging.getLogger('claude_force')
        self.assertEqual(logger.level, logging.INFO)

    def test_warning_level(self):
        """Test WARNING logging level."""
        setup_logging(log_level="WARNING")
        logger = logging.getLogger('claude_force')
        self.assertEqual(logger.level, logging.WARNING)

    def test_error_level(self):
        """Test ERROR logging level."""
        setup_logging(log_level="ERROR")
        logger = logging.getLogger('claude_force')
        self.assertEqual(logger.level, logging.ERROR)

    def test_critical_level(self):
        """Test CRITICAL logging level."""
        setup_logging(log_level="CRITICAL")
        logger = logging.getLogger('claude_force')
        self.assertEqual(logger.level, logging.CRITICAL)


if __name__ == '__main__':
    unittest.main()

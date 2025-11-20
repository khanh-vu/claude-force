"""
Fixtures for shell tests.
"""

import pytest
from unittest.mock import Mock
from pathlib import Path
import tempfile


@pytest.fixture
def shell_instance():
    """
    Fixture for interactive shell instance.

    This is a placeholder fixture for edge cases and security tests.
    TODO: Implement actual InteractiveShell instantiation once the implementation is complete.
    """
    mock_shell = Mock()
    mock_shell.executor = Mock()
    mock_shell.executor.execute = Mock(return_value=Mock(success=True, error=""))
    mock_shell.history = []
    mock_shell.stop = Mock()
    return mock_shell


@pytest.fixture
def mock_orchestrator():
    """
    Fixture for mock orchestrator.

    This provides a mock orchestrator for testing shell interactions.
    TODO: Implement actual Orchestrator mock based on real interface.
    """
    mock = Mock()
    mock.list_agents = Mock(return_value=["code-reviewer", "test-agent"])
    mock.list_workflows = Mock(return_value=["workflow1", "workflow2"])
    return mock

"""
Error handling utilities for improved user experience.

Provides fuzzy matching, helpful suggestions, and contextual error messages.
"""

from difflib import get_close_matches
from typing import List, Optional
import sys


def suggest_agents(invalid_name: str, all_agents: List[str], n: int = 3) -> List[str]:
    """
    Suggest similar agent names using fuzzy matching.

    Args:
        invalid_name: The invalid agent name provided by user
        all_agents: List of all available agent names
        n: Maximum number of suggestions to return

    Returns:
        List of suggested agent names
    """
    suggestions = get_close_matches(invalid_name, all_agents, n=n, cutoff=0.6)
    return suggestions


def format_agent_not_found_error(invalid_name: str, all_agents: List[str]) -> str:
    """
    Format a helpful error message when an agent is not found.

    Args:
        invalid_name: The invalid agent name provided by user
        all_agents: List of all available agent names

    Returns:
        Formatted error message with suggestions
    """
    error_msg = f"Agent '{invalid_name}' not found."

    # Try fuzzy matching
    suggestions = suggest_agents(invalid_name, all_agents)

    if suggestions:
        error_msg += "\n\n💡 Did you mean?"
        for suggestion in suggestions:
            error_msg += f"\n   - {suggestion}"
        error_msg += "\n\n💡 Tip: Use 'claude-force list agents' to see all available agents"
    else:
        error_msg += f"\n\n📋 Available agents: {', '.join(sorted(all_agents[:10]))}"
        if len(all_agents) > 10:
            error_msg += f"... ({len(all_agents)} total)"
        error_msg += "\n\n💡 Tip: Use 'claude-force list agents' for the full list"

    return error_msg


def format_workflow_not_found_error(invalid_name: str, all_workflows: List[str]) -> str:
    """
    Format a helpful error message when a workflow is not found.

    Args:
        invalid_name: The invalid workflow name provided by user
        all_workflows: List of all available workflow names

    Returns:
        Formatted error message with suggestions
    """
    error_msg = f"Workflow '{invalid_name}' not found."

    # Try fuzzy matching
    suggestions = get_close_matches(invalid_name, all_workflows, n=3, cutoff=0.6)

    if suggestions:
        error_msg += "\n\n💡 Did you mean?"
        for suggestion in suggestions:
            error_msg += f"\n   - {suggestion}"
        error_msg += "\n\n💡 Tip: Use 'claude-force list workflows' to see all available workflows"
    else:
        error_msg += f"\n\n🔄 Available workflows: {', '.join(sorted(all_workflows))}"
        error_msg += "\n\n💡 Tip: Use 'claude-force list workflows' for details"

    return error_msg


def format_api_key_error() -> str:
    """
    Format a helpful error message for missing API key.

    Returns:
        Formatted error message with setup instructions
    """
    error_msg = """❌ Anthropic API key not found.

🔑 How to set up your API key:

1. Get your API key from: https://console.anthropic.com/account/keys

2. Set it as an environment variable:

   Linux/Mac:
   $ export ANTHROPIC_API_KEY='your-api-key-here'

   Windows (PowerShell):
   $ $env:ANTHROPIC_API_KEY='your-api-key-here'

   Windows (CMD):
   $ set ANTHROPIC_API_KEY=your-api-key-here

3. Or add to your shell profile (~/.bashrc, ~/.zshrc, etc.):
   export ANTHROPIC_API_KEY='your-api-key-here'

4. Verify it's set:
   $ echo $ANTHROPIC_API_KEY  (Linux/Mac)
   $ echo %ANTHROPIC_API_KEY%  (Windows CMD)

💡 Tip: Never commit your API key to version control!

📖 Full documentation: https://github.com/khanh-vu/claude-force#installation
"""
    return error_msg


def format_missing_dependency_error(package: str, install_cmd: str) -> str:
    """
    Format a helpful error message for missing dependencies.

    Args:
        package: Name of the missing package
        install_cmd: Installation command

    Returns:
        Formatted error message with installation instructions
    """
    error_msg = f"""❌ Required package '{package}' not found.

📦 To install this dependency:

   $ {install_cmd}

💡 Tip: Make sure you're in your virtual environment if using one.

🔧 If you continue to have issues:
   - Check your Python version (requires Python 3.8+)
   - Try upgrading pip: pip install --upgrade pip
   - Check the installation guide: https://github.com/khanh-vu/claude-force#installation
"""
    return error_msg


def format_config_not_found_error(config_path: str) -> str:
    """
    Format a helpful error message when configuration file is not found.

    Args:
        config_path: Path to the missing configuration file

    Returns:
        Formatted error message with setup instructions
    """
    error_msg = f"""❌ Configuration file not found: {config_path}

🚀 To set up claude-force in this directory:

   $ claude-force init

   This will create:
   - .claude/claude.json (configuration)
   - .claude/agents/ (agent definitions)
   - .claude/workflows/ (workflow definitions)

💡 Or, navigate to an existing claude-force project:

   $ cd /path/to/your/claude-force-project

📖 Documentation: https://github.com/khanh-vu/claude-force#getting-started
"""
    return error_msg


def format_tracking_not_enabled_error() -> str:
    """
    Format a helpful error message when performance tracking is not enabled.

    Returns:
        Formatted error message with instructions
    """
    error_msg = """❌ Performance tracking is not enabled.

📊 To enable performance tracking:

   When creating the orchestrator:

   ```python
   orchestrator = AgentOrchestrator(
       config_path=".claude/claude.json",
       enable_tracking=True  # Enable tracking
   )
   ```

💡 Performance tracking provides:
   - Execution time metrics
   - Token usage tracking
   - Cost analysis
   - Performance reports

📖 Learn more: https://github.com/khanh-vu/claude-force/docs/performance.md
"""
    return error_msg


def print_contextual_help(error_type: str):
    """
    Print contextual help based on the type of error.

    Args:
        error_type: Type of error that occurred
    """
    help_messages = {
        'agent_not_found': "\n💡 To list all agents: claude-force list agents",
        'workflow_not_found': "\n💡 To list all workflows: claude-force list workflows",
        'api_key': "\n💡 Get your API key: https://console.anthropic.com/account/keys",
        'config_not_found': "\n💡 Initialize a new project: claude-force init",
        'tracking_disabled': "\n💡 Enable tracking when creating the orchestrator",
        'missing_dependency': "\n💡 Install missing packages with pip",
    }

    if error_type in help_messages:
        print(help_messages[error_type], file=sys.stderr)


def enhance_error_message(error: Exception, context: Optional[dict] = None) -> str:
    """
    Enhance an error message with contextual information and helpful tips.

    Args:
        error: The original exception
        context: Optional context dictionary with additional information

    Returns:
        Enhanced error message
    """
    error_str = str(error)
    context = context or {}

    # Check for specific error patterns and enhance accordingly
    if "API key required" in error_str or "ANTHROPIC_API_KEY" in error_str:
        return format_api_key_error()

    elif "not found in configuration" in error_str and "agents" in context:
        # Extract agent name from error message
        import re
        match = re.search(r"Agent '(\w+(?:-\w+)*)' not found", error_str)
        if match:
            agent_name = match.group(1)
            return format_agent_not_found_error(agent_name, context['agents'])

    elif "Workflow" in error_str and "not found" in error_str and "workflows" in context:
        # Extract workflow name from error message
        import re
        match = re.search(r"Workflow '(\w+(?:-\w+)*)' not found", error_str)
        if match:
            workflow_name = match.group(1)
            return format_workflow_not_found_error(workflow_name, context['workflows'])

    elif "Configuration file not found" in error_str:
        if "config_path" in context:
            return format_config_not_found_error(context['config_path'])

    elif "Performance tracking not enabled" in error_str:
        return format_tracking_not_enabled_error()

    elif "package required" in error_str or "ImportError" in error.__class__.__name__:
        # Extract package name
        import re
        match = re.search(r"'?(\w+)'? package required", error_str)
        if match:
            package = match.group(1)
            install_cmd = f"pip install {package}"
            if "sentence-transformers" in error_str:
                install_cmd = "pip install sentence-transformers"
            return format_missing_dependency_error(package, install_cmd)

    # Default: return original error message
    return error_str

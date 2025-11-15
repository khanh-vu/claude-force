"""
Diagnostic utilities for troubleshooting claude-force issues.

UX-04: Comprehensive system diagnostics to reduce support time by 50%.
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DiagnosticCheck:
    """Result of a single diagnostic check."""

    def __init__(self, name: str, status: bool, message: str, details: Optional[str] = None):
        self.name = name
        self.status = status  # True = pass, False = fail
        self.message = message
        self.details = details


class SystemDiagnostics:
    """
    Run comprehensive system diagnostics for claude-force.

    Checks:
    - Python version compatibility
    - Package installation
    - API key configuration
    - Config file validity
    - Agent availability
    - Cache status
    - Network connectivity
    - File permissions
    """

    def __init__(self):
        self.checks: List[DiagnosticCheck] = []

    def run_all_checks(self) -> List[DiagnosticCheck]:
        """Run all diagnostic checks."""
        self.checks = []

        # Run checks in order
        self.check_python_version()
        self.check_package_installation()
        self.check_api_key()
        self.check_config_file()
        self.check_agents_available()
        self.check_cache_status()
        self.check_network_connectivity()
        self.check_file_permissions()

        return self.checks

    def check_python_version(self) -> DiagnosticCheck:
        """Check Python version is 3.8+."""
        try:
            version = sys.version_info
            required_major = 3
            required_minor = 8

            if version.major >= required_major and version.minor >= required_minor:
                check = DiagnosticCheck(
                    name="Python version",
                    status=True,
                    message=f"Python {version.major}.{version.minor}.{version.micro}",
                    details=f"Meets requirement: Python {required_major}.{required_minor}+",
                )
            else:
                check = DiagnosticCheck(
                    name="Python version",
                    status=False,
                    message=f"Python {version.major}.{version.minor}.{version.micro} (too old)",
                    details=f"Required: Python {required_major}.{required_minor}+",
                )
        except Exception as e:
            check = DiagnosticCheck(
                name="Python version", status=False, message="Failed to check", details=str(e)
            )

        self.checks.append(check)
        return check

    def check_package_installation(self) -> DiagnosticCheck:
        """Check claude-force package is installed."""
        try:
            import claude_force

            version = getattr(claude_force, "__version__", "unknown")

            check = DiagnosticCheck(
                name="Package installation",
                status=True,
                message=f"claude-force v{version} installed",
                details=f"Location: {claude_force.__file__}",
            )
        except ImportError as e:
            check = DiagnosticCheck(
                name="Package installation",
                status=False,
                message="claude-force not installed",
                details=str(e),
            )

        self.checks.append(check)
        return check

    def check_api_key(self) -> DiagnosticCheck:
        """Check Anthropic API key is configured."""
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key:
            # Mask key for security
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"

            check = DiagnosticCheck(
                name="API key configured",
                status=True,
                message=f"ANTHROPIC_API_KEY set ({masked_key})",
                details="Environment variable found",
            )
        else:
            # Check .env file in multiple locations (project first, then home)
            env_locations = [
                Path.cwd() / ".env",  # Current project directory
                Path.home() / ".claude" / ".env",  # Global config
            ]

            found_env = None
            for env_file in env_locations:
                if env_file.exists():
                    found_env = env_file
                    break

            if found_env:
                check = DiagnosticCheck(
                    name="API key configured",
                    status=True,
                    message="Found in .env file",
                    details=f"Location: {found_env}",
                )
            else:
                check = DiagnosticCheck(
                    name="API key configured",
                    status=False,
                    message="No API key found",
                    details="Set ANTHROPIC_API_KEY environment variable or create .env file",
                )

        self.checks.append(check)
        return check

    def check_config_file(self) -> DiagnosticCheck:
        """Check claude.json config file exists and is valid."""
        # Check config in multiple locations (project first, then home)
        config_locations = [
            Path.cwd() / ".claude" / "claude.json",  # Current project
            Path.home() / ".claude" / "claude.json",  # Global config
        ]

        config_path = None
        for path in config_locations:
            if path.exists():
                config_path = path
                break

        if not config_path:
            check = DiagnosticCheck(
                name="Config file",
                status=False,
                message="claude.json not found",
                details=f"Expected: ./.claude/claude.json or ~/.claude/claude.json",
            )
        else:
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)

                agent_count = len(config.get("agents", {}))
                workflow_count = len(config.get("workflows", {}))

                check = DiagnosticCheck(
                    name="Config file",
                    status=True,
                    message=f"Valid ({agent_count} agents, {workflow_count} workflows)",
                    details=f"Location: {config_path}",
                )
            except json.JSONDecodeError as e:
                check = DiagnosticCheck(
                    name="Config file",
                    status=False,
                    message="Invalid JSON",
                    details=f"Error at line {e.lineno}: {e.msg}",
                )
            except Exception as e:
                check = DiagnosticCheck(
                    name="Config file", status=False, message="Failed to read", details=str(e)
                )

        self.checks.append(check)
        return check

    def check_agents_available(self) -> DiagnosticCheck:
        """Check agent definition files are available."""
        try:
            from claude_force.orchestrator import AgentOrchestrator

            # Try to create orchestrator (may fail without API key, but checks config)
            try:
                orchestrator = AgentOrchestrator(api_key="test")
                agent_count = len(orchestrator.config.get("agents", {}))

                check = DiagnosticCheck(
                    name="Agents available",
                    status=True,
                    message=f"{agent_count} agents configured",
                    details="Agent definitions loaded successfully",
                )
            except Exception as e:
                # If it fails due to missing API key, that's okay
                if "API key" in str(e):
                    check = DiagnosticCheck(
                        name="Agents available",
                        status=True,
                        message="Config accessible",
                        details="Agent count unavailable (no API key)",
                    )
                else:
                    check = DiagnosticCheck(
                        name="Agents available",
                        status=False,
                        message="Failed to load agents",
                        details=str(e),
                    )

        except Exception as e:
            check = DiagnosticCheck(
                name="Agents available", status=False, message="Failed to check", details=str(e)
            )

        self.checks.append(check)
        return check

    def check_cache_status(self) -> DiagnosticCheck:
        """Check response cache directory and status."""
        cache_dir = Path.home() / ".claude" / "cache"

        try:
            if cache_dir.exists():
                # Count cache files
                cache_files = list(cache_dir.glob("*.json"))
                total_size = sum(f.stat().st_size for f in cache_files)
                size_mb = total_size / (1024 * 1024)

                check = DiagnosticCheck(
                    name="Cache status",
                    status=True,
                    message=f"{len(cache_files)} entries ({size_mb:.2f} MB)",
                    details=f"Location: {cache_dir}",
                )
            else:
                check = DiagnosticCheck(
                    name="Cache status",
                    status=True,
                    message="Not initialized (will be created on first use)",
                    details=f"Will be created at: {cache_dir}",
                )
        except Exception as e:
            check = DiagnosticCheck(
                name="Cache status", status=False, message="Failed to check", details=str(e)
            )

        self.checks.append(check)
        return check

    def check_network_connectivity(self) -> DiagnosticCheck:
        """Check network connectivity to Anthropic API."""
        try:
            import socket

            # Try to resolve Anthropic API hostname
            host = "api.anthropic.com"
            socket.gethostbyname(host)

            check = DiagnosticCheck(
                name="Network connectivity",
                status=True,
                message=f"Can resolve {host}",
                details="DNS resolution successful",
            )
        except socket.gaierror:
            check = DiagnosticCheck(
                name="Network connectivity",
                status=False,
                message="Cannot resolve api.anthropic.com",
                details="Check internet connection or DNS settings",
            )
        except Exception as e:
            check = DiagnosticCheck(
                name="Network connectivity",
                status=False,
                message="Failed to check",
                details=str(e),
            )

        self.checks.append(check)
        return check

    def check_file_permissions(self) -> DiagnosticCheck:
        """Check file permissions for .claude directory."""
        claude_dir = Path.home() / ".claude"

        try:
            # Check if directory exists
            if not claude_dir.exists():
                check = DiagnosticCheck(
                    name="File permissions",
                    status=True,
                    message="Directory will be created on first use",
                    details=f"Location: {claude_dir}",
                )
            else:
                # Check if we can write to the directory
                test_file = claude_dir / ".write_test"
                try:
                    test_file.touch()
                    test_file.unlink()

                    check = DiagnosticCheck(
                        name="File permissions",
                        status=True,
                        message="Read/write access OK",
                        details=f"Location: {claude_dir}",
                    )
                except PermissionError:
                    check = DiagnosticCheck(
                        name="File permissions",
                        status=False,
                        message="No write access",
                        details=f"Cannot write to {claude_dir}",
                    )
        except Exception as e:
            check = DiagnosticCheck(
                name="File permissions", status=False, message="Failed to check", details=str(e)
            )

        self.checks.append(check)
        return check

    def get_summary(self) -> Dict[str, int]:
        """Get summary of check results."""
        passed = sum(1 for check in self.checks if check.status)
        failed = sum(1 for check in self.checks if not check.status)

        return {"total": len(self.checks), "passed": passed, "failed": failed}

    def format_report(self, verbose: bool = False) -> str:
        """Format diagnostic report as string."""
        lines = []
        lines.append("=" * 70)
        lines.append("Claude Force System Diagnostics")
        lines.append("=" * 70)
        lines.append("")

        for check in self.checks:
            icon = "✅" if check.status else "❌"
            lines.append(f"{icon} {check.name}: {check.message}")

            if verbose and check.details:
                lines.append(f"   {check.details}")

        lines.append("")
        lines.append("-" * 70)

        summary = self.get_summary()
        lines.append(
            f"Summary: {summary['passed']}/{summary['total']} checks passed, {summary['failed']} failed"
        )

        if summary["failed"] > 0:
            lines.append("")
            lines.append("⚠️  Some checks failed. Please address the issues above.")
        else:
            lines.append("")
            lines.append("✅ All checks passed! System is ready.")

        lines.append("=" * 70)

        return "\n".join(lines)


def run_diagnostics(verbose: bool = False) -> Tuple[bool, str]:
    """
    Run system diagnostics and return results.

    Args:
        verbose: Include detailed information in output

    Returns:
        Tuple of (all_passed, formatted_report)
    """
    diagnostics = SystemDiagnostics()
    diagnostics.run_all_checks()

    summary = diagnostics.get_summary()
    all_passed = summary["failed"] == 0

    report = diagnostics.format_report(verbose=verbose)

    return all_passed, report

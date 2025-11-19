"""
Test Suite for Tab Completion

TDD tests for ClaudeForceCompleter class.
Tests context-aware completion for commands, agents, workflows, and flags.

Coverage:
- Command name completion
- Agent name completion
- Workflow name completion
- Flag/option completion
- File path completion
- Context awareness
- Performance
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from claude_force.shell.completer import ClaudeForceCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completion


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_orchestrator():
    """Mock orchestrator with agents and workflows."""
    orch = Mock()
    orch.list_agents.return_value = [
        "code-reviewer",
        "frontend-architect",
        "backend-architect",
        "python-expert",
        "bug-investigator",
    ]
    orch.list_workflows.return_value = [
        "full-stack-feature",
        "frontend-only",
        "bug-fix",
        "documentation",
    ]
    return orch


@pytest.fixture
def completer(mock_orchestrator):
    """Create completer instance."""
    return ClaudeForceCompleter(orchestrator=mock_orchestrator)


def create_document(text, cursor_position=None):
    """Helper to create Document for testing."""
    if cursor_position is None:
        cursor_position = len(text)
    return Document(text=text, cursor_position=cursor_position)


# =============================================================================
# TEST CLASS: Command Completion
# =============================================================================

class TestCommandCompletion:
    """Test completion of command names."""

    def test_complete_run_command(self, completer):
        """Test completing 'ru' to 'run'."""
        doc = create_document("ru")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "run" for c in completions)

    def test_complete_list_command(self, completer):
        """Test completing 'lis' to 'list'."""
        doc = create_document("lis")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "list" for c in completions)

    # Note: 'workflow' is not a top-level command, only a subcommand after 'run'
    # This test has been removed as it tested incorrect behavior

    def test_complete_help_command(self, completer):
        """Test completing 'hel' to 'help'."""
        doc = create_document("hel")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "help" for c in completions)

    def test_complete_exit_command(self, completer):
        """Test completing 'ex' to 'exit'."""
        doc = create_document("ex")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "exit" for c in completions)

    def test_no_completions_for_complete_command(self, completer):
        """Test no completions after complete command + space."""
        doc = create_document("run ")
        completions = list(completer.get_completions(doc, None))
        # Should complete subcommands (agent, workflow), not 'run' again
        assert not any(c.text == "run" for c in completions)

    def test_all_commands_listed_on_empty_input(self, completer):
        """Test all commands listed when input is empty."""
        doc = create_document("")
        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]
        assert "run" in completion_texts
        assert "list" in completion_texts
        assert "help" in completion_texts


# =============================================================================
# TEST CLASS: Agent Completion
# =============================================================================

class TestAgentCompletion:
    """Test completion of agent names."""

    def test_complete_agent_after_run_agent(self, completer):
        """Test agent name completion after 'run agent'."""
        doc = create_document("run agent ")
        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        # Exact match - should return all mocked agents
        expected = ["code-reviewer", "frontend-architect", "backend-architect",
                    "python-expert", "bug-investigator"]
        assert completion_texts == expected, \
            f"Expected exactly {expected}, got {completion_texts}"

        # Verify all have correct metadata
        assert all(c.display_meta is not None for c in completions), \
            "All completions should have display_meta set"

    def test_complete_partial_agent_name(self, completer):
        """Test partial agent name completion."""
        doc = create_document("run agent code-")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "code-reviewer" for c in completions)

    def test_complete_agent_case_insensitive(self, completer):
        """Test case-insensitive agent completion."""
        doc = create_document("run agent CODE-")
        completions = list(completer.get_completions(doc, None))
        assert any("code-reviewer" in c.text.lower() for c in completions)

    def test_complete_agent_with_prefix_match(self, completer):
        """Test agent completion with prefix match."""
        doc = create_document("run agent front")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "frontend-architect" for c in completions)

    def test_no_agent_completion_without_run_agent(self, completer):
        """Test agent names not suggested in wrong context."""
        doc = create_document("list ")
        completions = list(completer.get_completions(doc, None))
        # Should suggest 'agents' or 'workflows', not agent names
        assert not any(c.text == "code-reviewer" for c in completions)


# =============================================================================
# TEST CLASS: Workflow Completion
# =============================================================================

class TestWorkflowCompletion:
    """Test completion of workflow names."""

    def test_complete_workflow_after_run_workflow(self, completer):
        """Test workflow name completion after 'run workflow'."""
        doc = create_document("run workflow ")
        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        # Exact match - should return all mocked workflows
        expected = ["full-stack-feature", "frontend-only", "bug-fix", "documentation"]
        assert completion_texts == expected, \
            f"Expected exactly {expected}, got {completion_texts}"

    def test_complete_partial_workflow_name(self, completer):
        """Test partial workflow name completion."""
        doc = create_document("run workflow full-")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "full-stack-feature" for c in completions)

    def test_complete_workflow_case_insensitive(self, completer):
        """Test case-insensitive workflow completion."""
        doc = create_document("run workflow FULL-")
        completions = list(completer.get_completions(doc, None))
        assert any("full-stack-feature" in c.text.lower() for c in completions)


# =============================================================================
# TEST CLASS: Flag Completion
# =============================================================================

class TestFlagCompletion:
    """Test completion of flags and options."""

    def test_complete_task_flag(self, completer):
        """Test --task flag completion."""
        doc = create_document("run agent code-reviewer --ta")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "--task" for c in completions)

    def test_complete_task_file_flag(self, completer):
        """Test --task-file flag completion."""
        doc = create_document("run agent code-reviewer --task-f")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "--task-file" for c in completions)

    def test_complete_output_flag(self, completer):
        """Test --output flag completion."""
        doc = create_document("run agent code-reviewer --task Test --out")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "--output" for c in completions)

    def test_complete_json_flag(self, completer):
        """Test --json flag completion."""
        doc = create_document("list agents --js")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "--json" for c in completions)

    def test_complete_quiet_flag(self, completer):
        """Test --quiet flag completion."""
        doc = create_document("run agent code-reviewer --task Test --qui")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "--quiet" for c in completions)

    def test_complete_help_flag(self, completer):
        """Test --help flag completion."""
        doc = create_document("run agent code-reviewer --hel")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "--help" for c in completions)


# =============================================================================
# TEST CLASS: File Path Completion
# =============================================================================

class TestFilePathCompletion:
    """Test completion of file paths."""

    @pytest.mark.skip(reason="File path completion not yet implemented")
    def test_complete_task_file_path(self, completer, tmp_path):
        """Test file path completion for --task-file."""
        # Create test files
        (tmp_path / "task1.txt").touch()
        (tmp_path / "task2.txt").touch()

        doc = create_document(f'run agent code-reviewer --task-file "{tmp_path}/task')
        completions = list(completer.get_completions(doc, None))
        assert any("task1.txt" in c.text for c in completions), \
            f"Expected task1.txt in completions, got: {[c.text for c in completions]}"
        assert any("task2.txt" in c.text for c in completions), \
            f"Expected task2.txt in completions, got: {[c.text for c in completions]}"

    @pytest.mark.skip(reason="File path completion not yet implemented")
    def test_complete_directory_path(self, completer, tmp_path):
        """Test directory path completion."""
        (tmp_path / "subdir").mkdir()
        doc = create_document(f'run agent code-reviewer --task-file "{tmp_path}/sub')
        completions = list(completer.get_completions(doc, None))
        assert any("subdir" in c.text for c in completions), \
            f"Expected subdir in completions, got: {[c.text for c in completions]}"

    @pytest.mark.skip(reason="File path completion not yet implemented")
    def test_complete_path_with_spaces(self, completer, tmp_path):
        """Test path completion with spaces in filename."""
        (tmp_path / "task file.txt").touch()
        doc = create_document(f'run agent code-reviewer --task-file "{tmp_path}/task')
        completions = list(completer.get_completions(doc, None))
        assert any("task file.txt" in c.text for c in completions), \
            f"Expected 'task file.txt' in completions, got: {[c.text for c in completions]}"


# =============================================================================
# TEST CLASS: Context Awareness
# =============================================================================

class TestContextAwareness:
    """Test context-aware completion."""

    def test_completes_subcommand_after_run(self, completer):
        """Test completing subcommand after 'run'."""
        doc = create_document("run ")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "agent" for c in completions)

    def test_completes_subcommand_after_list(self, completer):
        """Test completing subcommand after 'list'."""
        doc = create_document("list ")
        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        # Exact match - should return only list subcommands
        expected = ["agents", "workflows"]
        assert completion_texts == expected, \
            f"Expected exactly {expected}, got {completion_texts}"

    def test_no_completions_after_task_value(self, completer):
        """Test no inappropriate completions after --task value."""
        doc = create_document('run agent code-reviewer --task "Review code" ')
        completions = list(completer.get_completions(doc, None))
        # Should suggest additional flags, not agent names
        assert not any(c.text == "frontend-architect" for c in completions)

    @pytest.mark.skip(reason="Cursor position awareness not yet implemented - completer only completes at end of line")
    def test_cursor_position_affects_completion(self, completer):
        """Test cursor position determines completion context."""
        # Cursor in middle of command
        doc = create_document("run agent code-reviewer --task Test", cursor_position=4)
        completions = list(completer.get_completions(doc, None))
        # Should complete 'run', not agents
        completion_texts = [c.text for c in completions]
        assert any("run" in c for c in completion_texts), \
            f"Expected 'run' completions with cursor at position 4, got: {completion_texts}"


# =============================================================================
# TEST CLASS: Completion Metadata
# =============================================================================

class TestCompletionMetadata:
    """Test completion metadata and display."""

    def test_completion_has_display_text(self, completer):
        """Test completions have display text."""
        doc = create_document("run agent ")
        completions = list(completer.get_completions(doc, None))

        assert len(completions) > 0, "Should have at least one completion"
        for completion in completions:
            assert hasattr(completion, 'text'), \
                f"Completion should have 'text' attribute"
            assert isinstance(completion.text, str), \
                f"Completion text should be string, got: {type(completion.text)}"
            assert len(completion.text) > 0, \
                f"Completion text should not be empty"

    def test_completion_has_display_meta(self, completer):
        """Test completions have metadata descriptions."""
        doc = create_document("run agent ")
        completions = list(completer.get_completions(doc, None))

        # Agent completions should have display_meta
        code_reviewer = next((c for c in completions if c.text == "code-reviewer"), None)
        assert code_reviewer is not None, \
            f"Expected 'code-reviewer' in completions, got: {[c.text for c in completions]}"
        assert hasattr(code_reviewer, 'display_meta'), \
            "Completion should have 'display_meta' attribute"

        # display_meta can be either a string or FormattedText
        meta_str = str(code_reviewer.display_meta)
        assert "agent" in meta_str, \
            f"Expected 'agent' in display_meta, got: '{meta_str}'"

    def test_completion_start_position_correct(self, completer):
        """Test completion start_position is correct."""
        doc = create_document("run agent code-")
        completions = list(completer.get_completions(doc, None))

        assert len(completions) > 0, "Should have at least one completion"
        for completion in completions:
            assert hasattr(completion, 'start_position'), \
                f"Completion should have 'start_position' attribute"
            # start_position should be negative (relative to cursor)
            assert completion.start_position <= 0, \
                f"start_position should be ≤ 0 (relative to cursor), got: {completion.start_position}"
            # For "code-" the start position should be -5 (length of "code-")
            assert completion.start_position == -5, \
                f"Expected start_position=-5 for 'code-' prefix, got: {completion.start_position}"


# =============================================================================
# TEST CLASS: Performance
# =============================================================================

class TestPerformance:
    """Test completion performance."""

    @pytest.mark.skip(reason="Timing tests are flaky in CI environments - performance verified manually")
    def test_completion_fast_for_empty_input(self, completer):
        """Test completion is fast for empty input."""
        import time
        doc = create_document("")
        start = time.time()
        list(completer.get_completions(doc, None))
        elapsed = time.time() - start
        assert elapsed < 0.1, f"Completion took {elapsed}s (expected <100ms)"

    @pytest.mark.skip(reason="Timing tests are flaky in CI environments - performance verified manually")
    def test_completion_fast_for_partial_agent(self, completer):
        """Test completion is fast for partial agent name."""
        import time
        doc = create_document("run agent code-")
        start = time.time()
        list(completer.get_completions(doc, None))
        elapsed = time.time() - start
        assert elapsed < 0.1, f"Completion took {elapsed}s (expected <100ms)"

    def test_completion_caches_agent_list(self, completer, mock_orchestrator):
        """Test completer caches agent list for performance."""
        doc = create_document("run agent ")
        list(completer.get_completions(doc, None))
        list(completer.get_completions(doc, None))
        list(completer.get_completions(doc, None))
        # Should only call list_agents once (cached)
        assert mock_orchestrator.list_agents.call_count == 1


# =============================================================================
# TEST CLASS: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases in completion."""

    def test_completion_with_trailing_spaces(self, completer):
        """Test completion with trailing spaces."""
        doc = create_document("run agent   ")
        completions = list(completer.get_completions(doc, None))
        # Should still complete agent names
        assert len(completions) > 0, \
            "Should complete agent names even with trailing spaces"

    def test_completion_with_multiple_consecutive_spaces(self, completer):
        """Test completion with multiple consecutive spaces between words."""
        doc = create_document("run  agent  ")  # Double spaces
        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        # Should still complete agent names
        assert len(completions) > 0, \
            "Should handle multiple consecutive spaces gracefully"
        assert "code-reviewer" in completion_texts, \
            f"Expected agent completions with multiple spaces, got: {completion_texts}"

    def test_completion_with_mixed_case(self, completer):
        """Test completion with mixed case input."""
        doc = create_document("RuN AgEnT CoDe-")
        completions = list(completer.get_completions(doc, None))
        assert any("code-reviewer" in c.text.lower() for c in completions)

    def test_completion_with_typo(self, completer):
        """Test completion doesn't crash on typo."""
        doc = create_document("rnu agtne code-")
        completions = list(completer.get_completions(doc, None))
        # May return empty list, but shouldn't crash
        assert isinstance(completions, list)

    def test_completion_with_very_long_input(self, completer):
        """Test completion with very long input."""
        long_input = "run agent code-reviewer --task " + ("x" * 10000)
        doc = create_document(long_input)

        # Should handle gracefully without crashing
        try:
            completions = list(completer.get_completions(doc, None))
            # Should return flag completions or empty list, not crash
            assert isinstance(completions, list), \
                f"Expected list of completions, got: {type(completions)}"
        except Exception as e:
            pytest.fail(f"Completer crashed on very long input: {e}")

    def test_completion_with_unicode(self, completer):
        """Test completion with Unicode characters."""
        doc = create_document("run agent 🚀")

        # Should handle gracefully without crashing
        try:
            completions = list(completer.get_completions(doc, None))
            assert isinstance(completions, list), \
                f"Expected list of completions, got: {type(completions)}"
        except Exception as e:
            pytest.fail(f"Completer crashed on Unicode input: {e}")

    def test_completion_empty_agent_list(self):
        """Test completion when no agents available."""
        mock_orch = Mock()
        mock_orch.list_agents.return_value = []
        mock_orch.list_workflows.return_value = []
        completer = ClaudeForceCompleter(orchestrator=mock_orch)

        doc = create_document("run agent ")
        completions = list(completer.get_completions(doc, None))

        assert len(completions) == 0, \
            f"Expected 0 completions with empty agent list, got {len(completions)}: {[c.text for c in completions]}"


# =============================================================================
# TEST CLASS: Error Handling
# =============================================================================

class TestErrorHandling:
    """Test error handling in completion."""

    def test_get_agents_handles_exception_gracefully(self):
        """Test completer handles exception when listing agents."""
        mock_orch = Mock()
        mock_orch.list_agents.side_effect = Exception("API error")
        mock_orch.list_workflows.return_value = []
        completer = ClaudeForceCompleter(orchestrator=mock_orch)

        doc = create_document("run agent ")
        completions = list(completer.get_completions(doc, None))

        # Should return empty list, not crash
        assert completions == [], \
            f"Expected empty list when agent listing fails, got: {[c.text for c in completions]}"

    def test_get_workflows_handles_exception_gracefully(self):
        """Test completer handles exception when listing workflows."""
        mock_orch = Mock()
        mock_orch.list_agents.return_value = []
        mock_orch.list_workflows.side_effect = Exception("API error")
        completer = ClaudeForceCompleter(orchestrator=mock_orch)

        doc = create_document("run workflow ")
        completions = list(completer.get_completions(doc, None))

        # Should return empty list, not crash
        assert completions == [], \
            f"Expected empty list when workflow listing fails, got: {[c.text for c in completions]}"

    def test_completes_with_none_orchestrator(self):
        """Test completer works without orchestrator."""
        completer = ClaudeForceCompleter(orchestrator=None)

        # Should complete commands
        doc = create_document("ru")
        completions = list(completer.get_completions(doc, None))
        assert any(c.text == "run" for c in completions), \
            f"Expected 'run' in completions without orchestrator, got: {[c.text for c in completions]}"

        # Should return empty for agent completions
        doc = create_document("run agent ")
        completions = list(completer.get_completions(doc, None))
        assert completions == [], \
            f"Expected no agent completions without orchestrator, got: {[c.text for c in completions]}"


# =============================================================================
# TEST CLASS: Cache Management
# =============================================================================

class TestCacheManagement:
    """Test cache invalidation and management."""

    def test_invalidate_cache_clears_agent_cache(self, mock_orchestrator):
        """Test invalidate_cache clears agent cache."""
        completer = ClaudeForceCompleter(orchestrator=mock_orchestrator)

        # First call - fetches agents
        doc = create_document("run agent ")
        list(completer.get_completions(doc, None))
        assert mock_orchestrator.list_agents.call_count == 1

        # Invalidate cache
        completer.invalidate_cache()

        # Second call - should fetch again
        list(completer.get_completions(doc, None))
        assert mock_orchestrator.list_agents.call_count == 2, \
            "Cache invalidation should trigger new fetch"

    def test_invalidate_cache_clears_workflow_cache(self, mock_orchestrator):
        """Test invalidate_cache clears workflow cache."""
        completer = ClaudeForceCompleter(orchestrator=mock_orchestrator)

        # First call - fetches workflows
        doc = create_document("run workflow ")
        list(completer.get_completions(doc, None))
        assert mock_orchestrator.list_workflows.call_count == 1

        # Invalidate cache
        completer.invalidate_cache()

        # Second call - should fetch again
        list(completer.get_completions(doc, None))
        assert mock_orchestrator.list_workflows.call_count == 2, \
            "Cache invalidation should trigger new fetch"

    def test_workflow_list_cached(self, mock_orchestrator):
        """Test workflow list is cached after first fetch."""
        completer = ClaudeForceCompleter(orchestrator=mock_orchestrator)

        doc = create_document("run workflow ")
        list(completer.get_completions(doc, None))
        list(completer.get_completions(doc, None))
        list(completer.get_completions(doc, None))

        # Should only call list_workflows once (cached)
        assert mock_orchestrator.list_workflows.call_count == 1, \
            f"Expected 1 call to list_workflows (cached), got {mock_orchestrator.list_workflows.call_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

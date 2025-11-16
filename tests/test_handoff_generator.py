"""
Tests for HandoffGenerator service

Ensures HandoffGenerator correctly:
- Generates session handoffs
- Captures decision context
- Prioritizes work remaining
- Detects confidence levels
- Saves and loads handoffs
- Integrates with orchestrator
"""

import pytest
from pathlib import Path
from datetime import datetime

from claude_force.models.handoff import (
    Handoff,
    SessionSummary,
    WorkflowProgress,
    WorkCompleted,
    WorkRemaining,
    ActiveContext,
    GovernanceStatus,
    PerformanceMetrics,
    ConfidenceLevel
)
from claude_force.services.handoff_generator import HandoffGenerator


class MockOrchestrator:
    """Mock orchestrator for testing"""

    def __init__(self):
        self.performance_tracker = None


class TestHandoffGenerator:
    """Test HandoffGenerator service"""

    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator"""
        return MockOrchestrator()

    @pytest.fixture
    def handoff_generator(self, mock_orchestrator):
        """Create HandoffGenerator instance"""
        return HandoffGenerator(mock_orchestrator)

    @pytest.fixture
    def sample_handoff(self):
        """Create sample Handoff object"""
        return Handoff(
            session_id="test-session-123",
            started=datetime.now(),
            duration_minutes=120,
            confidence_level=ConfidenceLevel.HIGH,
            resume_instructions="Run /run-agent frontend-developer",
            original_task="Build product catalog UI",
            session_summary=SessionSummary(
                key_decisions=["Chose PostgreSQL for better performance"],
                critical_insights=["Images need lazy loading"],
                conversation_highlights="Architecture → Implementation → Testing"
            ),
            work_completed=WorkCompleted(
                completed_items=["Database schema", "API endpoints"],
                files_modified={"src/api.py": "Added product endpoints"},
                agent_outputs=[{"agent": "backend-architect", "summary": "API design"}]
            ),
            work_remaining=WorkRemaining(
                priority_1_critical=["Complete ProductList component"],
                priority_2_high=["Add loading states"],
                priority_3_nice_to_have=["Add sorting options"]
            ),
            active_context=ActiveContext(
                most_relevant=["Use react-window for virtualization"],
                known_blockers=[{"blocker": "CDN not configured", "mitigation": "Use placeholders"}],
                open_questions=["Pre-load next page?"]
            )
        )

    def test_generate_handoff_basic(self, handoff_generator):
        """Test basic handoff generation"""
        handoff = handoff_generator.generate_handoff()

        assert handoff is not None
        assert isinstance(handoff, Handoff)
        assert handoff.session_id is not None
        assert handoff.started is not None
        assert isinstance(handoff.confidence_level, ConfidenceLevel)

    def test_handoff_to_markdown(self, sample_handoff):
        """Test handoff markdown serialization"""
        markdown = sample_handoff.to_markdown()

        # Verify key sections present
        assert "## Session Handoff" in markdown
        assert "## Session Summary" in markdown
        assert "## Next Steps" in markdown
        assert "## Active Context" in markdown
        assert "## Quality Status" in markdown
        assert "## Cost & Performance" in markdown

        # Verify emoji indicators
        assert "🟢" in markdown or "🟡" in markdown  # Confidence level
        assert "🔴" in markdown or "🟡" in markdown or "🟢" in markdown  # Priorities

    def test_save_handoff(self, handoff_generator, sample_handoff, tmp_path):
        """Test saving handoff to file"""
        output_path = tmp_path / "test-handoff.md"

        saved_path = handoff_generator.save_handoff(
            sample_handoff,
            output_path=output_path,
            also_save_to_whats_next=False
        )

        assert saved_path == output_path
        assert output_path.exists()

        # Verify content
        content = output_path.read_text()
        assert "## Session Handoff" in content
        assert sample_handoff.session_id in content

    def test_save_handoff_with_whats_next(self, handoff_generator, sample_handoff, tmp_path, monkeypatch):
        """Test saving handoff with whats-next.md creation"""
        # Change to tmp directory
        monkeypatch.chdir(tmp_path)

        # Create .claude directory
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        saved_path = handoff_generator.save_handoff(
            sample_handoff,
            also_save_to_whats_next=True
        )

        # Check whats-next.md created
        whats_next = tmp_path / ".claude" / "whats-next.md"
        assert whats_next.exists()

    def test_confidence_level_detection_high(self, handoff_generator):
        """Test high confidence detection"""
        session_data = {
            'original_task': 'Build feature',
            'work_completed': {'completed_items': ['Task 1']},
            'work_remaining': {'priority_1': ['Task 2']},
            'active_context': {'most_relevant': ['Important info']},
            'governance_status': {'validation_passed': True}
        }

        confidence = handoff_generator._detect_confidence_level(session_data)
        assert confidence == ConfidenceLevel.HIGH

    def test_confidence_level_detection_low(self, handoff_generator):
        """Test low confidence detection"""
        session_data = {
            'original_task': '',
            'work_completed': {},
            'work_remaining': {},
            'active_context': {},
            'governance_status': {'validation_passed': False}
        }

        confidence = handoff_generator._detect_confidence_level(session_data)
        assert confidence == ConfidenceLevel.LOW

    def test_confidence_level_detection_medium(self, handoff_generator):
        """Test medium confidence detection"""
        session_data = {
            'original_task': 'Build feature',
            'work_completed': {'completed_items': ['Task 1']},
            'work_remaining': {},  # Missing
            'active_context': {},  # Missing
            'governance_status': {'validation_passed': True}
        }

        confidence = handoff_generator._detect_confidence_level(session_data)
        assert confidence == ConfidenceLevel.MEDIUM

    def test_generate_resume_instructions(self, handoff_generator):
        """Test resume instructions generation"""
        session_data = {
            'work_remaining': {
                'priority_1': ['Complete ProductList component']
            },
            'workflow_progress': {
                'workflow_name': 'full-stack-feature'
            }
        }

        instructions = handoff_generator._generate_resume_instructions(session_data)

        assert isinstance(instructions, str)
        assert len(instructions) > 0
        assert "Resume" in instructions or "resume" in instructions


class TestHandoffModel:
    """Test Handoff data model"""

    def test_handoff_creation(self):
        """Test creating handoff with minimal fields"""
        handoff = Handoff(
            session_id="test-123",
            started=datetime.now(),
            duration_minutes=60,
            confidence_level=ConfidenceLevel.MEDIUM,
            resume_instructions="Continue work",
            original_task="Test task"
        )

        assert handoff.session_id == "test-123"
        assert handoff.duration_minutes == 60
        assert handoff.confidence_level == ConfidenceLevel.MEDIUM

    def test_session_summary_creation(self):
        """Test SessionSummary creation"""
        summary = SessionSummary(
            key_decisions=["Decision 1", "Decision 2"],
            critical_insights=["Insight 1"],
            conversation_highlights="Test highlights"
        )

        assert len(summary.key_decisions) == 2
        assert len(summary.critical_insights) == 1
        assert summary.conversation_highlights == "Test highlights"

    def test_workflow_progress_completion_percentage(self):
        """Test workflow progress percentage calculation"""
        progress = WorkflowProgress(
            workflow_name="test-workflow",
            total_agents=8,
            completed_agents=5,
            current_phase="Implementation"
        )

        assert progress.completion_percentage == 62.5

    def test_workflow_progress_zero_agents(self):
        """Test workflow progress with zero agents"""
        progress = WorkflowProgress(
            workflow_name="test-workflow",
            total_agents=0,
            completed_agents=0,
            current_phase="Planning"
        )

        assert progress.completion_percentage == 0.0

    def test_work_remaining_priorities(self):
        """Test WorkRemaining priorities"""
        work = WorkRemaining(
            priority_1_critical=["Critical task"],
            priority_2_high=["High task 1", "High task 2"],
            priority_3_nice_to_have=["Optional task"],
            dependencies=["Task A depends on Task B"]
        )

        assert len(work.priority_1_critical) == 1
        assert len(work.priority_2_high) == 2
        assert len(work.priority_3_nice_to_have) == 1

    def test_active_context_structure(self):
        """Test ActiveContext structure"""
        context = ActiveContext(
            most_relevant=["Info 1", "Info 2"],
            known_blockers=[
                {"blocker": "API key missing", "mitigation": "Use test key"}
            ],
            open_questions=["How to handle edge case?"]
        )

        assert len(context.most_relevant) == 2
        assert len(context.known_blockers) == 1
        assert context.known_blockers[0]["blocker"] == "API key missing"

    def test_governance_status_validation(self):
        """Test GovernanceStatus"""
        status = GovernanceStatus(
            validation_passed=True,
            scorecard_pass=12,
            scorecard_total=12,
            blockers=[],
            next_validation_checkpoint="After frontend completion"
        )

        assert status.validation_passed is True
        assert status.scorecard_pass == status.scorecard_total

    def test_performance_metrics(self):
        """Test PerformanceMetrics"""
        metrics = PerformanceMetrics(
            total_cost=2.45,
            execution_time_minutes=120,
            agents_executed=5,
            token_usage=45000,
            context_window_used_percent=35.2
        )

        assert metrics.total_cost == 2.45
        assert metrics.execution_time_minutes == 120
        assert metrics.agents_executed == 5

    def test_handoff_markdown_includes_all_sections(self):
        """Test that handoff markdown includes all expected sections"""
        handoff = Handoff(
            session_id="test-123",
            started=datetime.now(),
            duration_minutes=60,
            confidence_level=ConfidenceLevel.HIGH,
            resume_instructions="Continue",
            original_task="Test task",
            session_summary=SessionSummary(
                key_decisions=["Decision"],
                critical_insights=["Insight"]
            ),
            work_completed=WorkCompleted(
                completed_items=["Item 1"]
            ),
            work_remaining=WorkRemaining(
                priority_1_critical=["Task 1"]
            ),
            active_context=ActiveContext(
                most_relevant=["Info"]
            ),
            governance_status=GovernanceStatus(
                validation_passed=True,
                scorecard_pass=10,
                scorecard_total=10
            ),
            performance_metrics=PerformanceMetrics(
                total_cost=1.50,
                execution_time_minutes=30,
                agents_executed=2,
                token_usage=10000,
                context_window_used_percent=20.0
            ),
            technical_context=["Technical detail 1"]
        )

        markdown = handoff.to_markdown()

        # Verify all major sections
        sections = [
            "## Session Handoff",
            "## Original Task",
            "## Session Summary",
            "## Work Completed",
            "## Next Steps",
            "## Active Context",
            "## Quality Status",
            "## Cost & Performance",
            "## Technical Context",
            "## To Resume"
        ]

        for section in sections:
            assert section in markdown, f"Missing section: {section}"

    def test_handoff_repr(self):
        """Test handoff string representation"""
        handoff = Handoff(
            session_id="test-123",
            started=datetime.now(),
            duration_minutes=60,
            confidence_level=ConfidenceLevel.HIGH,
            resume_instructions="Test",
            original_task="Test"
        )

        repr_str = repr(handoff)
        assert "test-123" in repr_str
        assert "60min" in repr_str
        assert "high" in repr_str

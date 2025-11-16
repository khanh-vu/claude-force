"""
HandoffGenerator service for session continuity and context preservation.

Provides:
- Session state extraction from orchestrator
- Comprehensive handoff generation with decision context
- Priority-ordered work remaining
- Performance metrics aggregation
- Handoff archival
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
from pathlib import Path
from datetime import datetime

if TYPE_CHECKING:
    from claude_force.orchestrator import AgentOrchestrator

from ..models.handoff import (
    Handoff,
    SessionSummary,
    WorkflowProgress,
    WorkCompleted,
    WorkRemaining,
    ActiveContext,
    GovernanceStatus,
    PerformanceMetrics,
    ConfidenceLevel,
)


class HandoffGenerator:
    """
    Generates session handoffs for continuity across sessions.

    Features:
    - Extracts comprehensive session state
    - Prioritizes remaining work (P1/P2/P3)
    - Captures decision context (WHY, not just WHAT)
    - Includes governance and performance metrics
    - Archives handoffs with timestamps
    """

    def __init__(self, orchestrator: "AgentOrchestrator"):
        self.orchestrator = orchestrator

    def generate_handoff(
        self,
        session_id: Optional[str] = None,
        confidence_level: ConfidenceLevel = ConfidenceLevel.HIGH,
        auto_detect_confidence: bool = True,
    ) -> Handoff:
        """
        Generate structured handoff from current session.

        Args:
            session_id: Optional session ID (defaults to current)
            confidence_level: Manual confidence level
            auto_detect_confidence: Auto-detect confidence based on session state

        Returns:
            Handoff object with complete session context
        """
        # Get session state
        if session_id is None:
            session_id = self._get_current_session_id()

        # Extract session data
        session_data = self._extract_session_data(session_id)

        # Auto-detect confidence if requested
        if auto_detect_confidence:
            confidence_level = self._detect_confidence_level(session_data)

        # Build handoff components
        handoff = Handoff(
            session_id=session_id,
            started=session_data.get("started", datetime.now()),
            duration_minutes=session_data.get("duration_minutes", 0),
            confidence_level=confidence_level,
            resume_instructions=self._generate_resume_instructions(session_data),
            original_task=session_data.get("original_task", ""),
            session_summary=self._build_session_summary(session_data),
            workflow_progress=self._build_workflow_progress(session_data),
            work_completed=self._build_work_completed(session_data),
            work_remaining=self._build_work_remaining(session_data),
            active_context=self._build_active_context(session_data),
            technical_context=session_data.get("technical_context", []),
            governance_status=self._build_governance_status(session_data),
            performance_metrics=self._build_performance_metrics(session_data),
        )

        return handoff

    def save_handoff(
        self,
        handoff: Handoff,
        output_path: Optional[Path] = None,
        also_save_to_whats_next: bool = True,
    ) -> Path:
        """
        Save handoff to file with archival.

        Args:
            handoff: Handoff object to save
            output_path: Optional custom path
            also_save_to_whats_next: Also save to .claude/whats-next.md

        Returns:
            Path where handoff was saved
        """
        if output_path is None:
            # Default location: archived handoff
            handoff_dir = Path(".claude/handoffs")
            handoff_dir.mkdir(parents=True, exist_ok=True)

            timestamp = handoff.generated_at.strftime("%Y-%m-%d-%H%M%S")
            output_path = handoff_dir / f"handoff-{timestamp}.md"

        # Convert to markdown
        markdown = handoff.to_markdown()

        # Write to archive
        output_path.write_text(markdown)

        # Also write to whats-next.md for easy discovery
        if also_save_to_whats_next:
            whats_next = Path(".claude/whats-next.md")
            whats_next.write_text(markdown)

        return output_path

    def load_latest_handoff(self) -> Optional[Handoff]:
        """
        Load the most recent handoff.

        Returns:
            Handoff object or None if no handoffs exist
        """
        # Check whats-next.md first
        whats_next = Path(".claude/whats-next.md")
        if whats_next.exists():
            content = whats_next.read_text()
            return Handoff.from_markdown(content)

        # Otherwise check archives
        handoff_dir = Path(".claude/handoffs")
        if not handoff_dir.exists():
            return None

        # Find most recent
        handoffs = sorted(handoff_dir.glob("handoff-*.md"), reverse=True)
        if not handoffs:
            return None

        content = handoffs[0].read_text()
        return Handoff.from_markdown(content)

    # Private helper methods

    def _get_current_session_id(self) -> str:
        """Get current session ID from orchestrator"""
        # This would come from the orchestrator's session tracking
        # For now, generate a simple session ID
        return f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    def _extract_session_data(self, session_id: str) -> Dict[str, Any]:
        """
        Extract comprehensive session data from orchestrator.

        Args:
            session_id: Session to extract

        Returns:
            Dict with all session data
        """
        # This would extract from orchestrator's state
        # For now, create a template structure

        # Try to get task from .claude/task.md
        task_file = Path(".claude/task.md")
        original_task = ""
        if task_file.exists():
            original_task = task_file.read_text()

        # Get performance data from orchestrator if available
        performance_data = {}
        if hasattr(self.orchestrator, "performance_tracker"):
            try:
                performance_data = self.orchestrator.performance_tracker.get_summary()
            except Exception as e:
                import logging

                logging.getLogger(__name__).debug(f"Failed to retrieve performance metrics: {e}")

        return {
            "started": datetime.now(),
            "duration_minutes": 0,
            "original_task": original_task,
            "session_summary": {
                "key_decisions": [],
                "critical_insights": [],
                "conversation_highlights": "",
            },
            "workflow_progress": None,
            "work_completed": {
                "completed_items": [],
                "files_modified": {},
                "agent_outputs": [],
            },
            "work_remaining": {
                "priority_1": [],
                "priority_2": [],
                "priority_3": [],
                "dependencies": [],
            },
            "active_context": {
                "most_relevant": [],
                "known_blockers": [],
                "open_questions": [],
            },
            "technical_context": [],
            "governance_status": {
                "validation_passed": True,
                "scorecard_pass": 0,
                "scorecard_total": 0,
                "blockers": [],
            },
            "performance": performance_data,
        }

    def _detect_confidence_level(self, session_data: Dict[str, Any]) -> ConfidenceLevel:
        """
        Auto-detect confidence level based on session completeness.

        Args:
            session_data: Session data dict

        Returns:
            Detected confidence level
        """
        score = 0

        # Check if we have original task
        if session_data.get("original_task"):
            score += 1

        # Check if we have work completed
        work_completed = session_data.get("work_completed", {})
        if work_completed.get("completed_items") or work_completed.get("files_modified"):
            score += 1

        # Check if we have work remaining defined
        work_remaining = session_data.get("work_remaining", {})
        if work_remaining.get("priority_1") or work_remaining.get("priority_2"):
            score += 1

        # Check if we have active context
        active_context = session_data.get("active_context", {})
        if active_context.get("most_relevant"):
            score += 1

        # Check if governance passed
        governance = session_data.get("governance_status", {})
        if governance.get("validation_passed"):
            score += 1

        # Convert score to confidence level
        if score >= 4:
            return ConfidenceLevel.HIGH
        elif score >= 2:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _build_session_summary(self, session_data: Dict[str, Any]) -> SessionSummary:
        """Build session summary with key decisions"""
        summary_data = session_data.get("session_summary", {})

        return SessionSummary(
            key_decisions=summary_data.get("key_decisions", []),
            critical_insights=summary_data.get("critical_insights", []),
            conversation_highlights=summary_data.get("conversation_highlights", ""),
        )

    def _build_workflow_progress(self, session_data: Dict[str, Any]) -> Optional[WorkflowProgress]:
        """Extract workflow progress if applicable"""
        workflow_data = session_data.get("workflow_progress")

        if not workflow_data:
            return None

        return WorkflowProgress(
            workflow_name=workflow_data.get("workflow_name", ""),
            total_agents=workflow_data.get("total_agents", 0),
            completed_agents=workflow_data.get("completed_agents", 0),
            current_phase=workflow_data.get("current_phase", ""),
            agent_executions=workflow_data.get("agent_executions", []),
        )

    def _build_work_completed(self, session_data: Dict[str, Any]) -> WorkCompleted:
        """Build work completed summary"""
        work_data = session_data.get("work_completed", {})

        return WorkCompleted(
            completed_items=work_data.get("completed_items", []),
            files_modified=work_data.get("files_modified", {}),
            agent_outputs=work_data.get("agent_outputs", []),
        )

    def _build_work_remaining(self, session_data: Dict[str, Any]) -> WorkRemaining:
        """Build prioritized work remaining"""
        work_data = session_data.get("work_remaining", {})

        return WorkRemaining(
            priority_1_critical=work_data.get("priority_1", []),
            priority_2_high=work_data.get("priority_2", []),
            priority_3_nice_to_have=work_data.get("priority_3", []),
            dependencies=work_data.get("dependencies", []),
        )

    def _build_active_context(self, session_data: Dict[str, Any]) -> ActiveContext:
        """Build most relevant active context"""
        context_data = session_data.get("active_context", {})

        return ActiveContext(
            most_relevant=context_data.get("most_relevant", []),
            known_blockers=context_data.get("known_blockers", []),
            open_questions=context_data.get("open_questions", []),
        )

    def _build_governance_status(self, session_data: Dict[str, Any]) -> GovernanceStatus:
        """Extract governance status"""
        gov_data = session_data.get("governance_status", {})

        return GovernanceStatus(
            validation_passed=gov_data.get("validation_passed", True),
            scorecard_pass=gov_data.get("scorecard_pass", 0),
            scorecard_total=gov_data.get("scorecard_total", 0),
            blockers=gov_data.get("blockers", []),
            next_validation_checkpoint=gov_data.get("next_validation_checkpoint"),
        )

    def _build_performance_metrics(self, session_data: Dict[str, Any]) -> PerformanceMetrics:
        """Extract performance metrics"""
        perf_data = session_data.get("performance", {})

        return PerformanceMetrics(
            total_cost=perf_data.get("total_cost", 0.0),
            execution_time_minutes=session_data.get("duration_minutes", 0),
            agents_executed=perf_data.get("agents_executed", 0),
            token_usage=perf_data.get("token_usage", 0),
            context_window_used_percent=perf_data.get("context_window_used_percent", 0.0),
        )

    def _generate_resume_instructions(self, session_data: Dict[str, Any]) -> str:
        """
        Generate specific instructions for resuming work.

        Args:
            session_data: Session data dict

        Returns:
            Resume instructions string
        """
        lines = []

        lines.append("**To Resume This Session:**")
        lines.append("")

        # Step 1: Review this handoff
        lines.append("1. **Review this handoff** - Read the session summary and active context")

        # Step 2: Check work remaining
        work_remaining = session_data.get("work_remaining", {})
        if work_remaining.get("priority_1"):
            next_task = work_remaining["priority_1"][0]
            lines.append(f"2. **Start with**: {next_task}")
        else:
            lines.append("2. **Run `/status`** to check current state")

        # Step 3: Continue workflow or run agent
        workflow_data = session_data.get("workflow_progress")
        if workflow_data:
            workflow_name = workflow_data.get("workflow_name", "")
            lines.append(
                f"3. **Continue workflow**: `/run-workflow {workflow_name}` (will resume automatically)"
            )
        else:
            lines.append("3. **Run appropriate agent** based on next steps")

        # Step 4: Validate
        lines.append("4. **Validate when done**: `/validate-output`")

        return "\n".join(lines)

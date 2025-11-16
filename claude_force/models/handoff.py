"""
Handoff data model for session continuity.

Based on expert review recommendations:
- Decision context (WHY, not just WHAT)
- Active context prioritization
- Session summary with key insights
- Priority-ordered work remaining
- Governance and performance metrics
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ConfidenceLevel(Enum):
    """AI's confidence in handoff completeness"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SessionSummary:
    """Summary of session activities with decision context"""

    key_decisions: List[str] = field(default_factory=list)
    critical_insights: List[str] = field(default_factory=list)
    conversation_highlights: str = ""


@dataclass
class WorkflowProgress:
    """Workflow execution status"""

    workflow_name: str = ""
    total_agents: int = 0
    completed_agents: int = 0
    current_phase: str = ""
    agent_executions: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.total_agents == 0:
            return 0.0
        return (self.completed_agents / self.total_agents) * 100


@dataclass
class WorkCompleted:
    """Summary of completed work"""

    completed_items: List[str] = field(default_factory=list)
    files_modified: Dict[str, str] = field(default_factory=dict)  # path -> description
    agent_outputs: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class WorkRemaining:
    """Prioritized list of remaining work (critical for AI planning)"""

    priority_1_critical: List[str] = field(default_factory=list)  # Blocks everything
    priority_2_high: List[str] = field(
        default_factory=list
    )  # Important but not blocking
    priority_3_nice_to_have: List[str] = field(default_factory=list)  # Can be deferred
    dependencies: List[str] = field(default_factory=list)  # Task dependencies


@dataclass
class ActiveContext:
    """Most relevant context for next session (AI prioritization)"""

    most_relevant: List[str] = field(default_factory=list)  # Top 2-3 critical things
    known_blockers: List[Dict[str, str]] = field(
        default_factory=list
    )  # {'blocker': '', 'mitigation': ''}
    open_questions: List[str] = field(default_factory=list)


@dataclass
class GovernanceStatus:
    """Quality and governance state"""

    validation_passed: bool = False
    scorecard_pass: int = 0
    scorecard_total: int = 0
    blockers: List[str] = field(default_factory=list)
    next_validation_checkpoint: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Session performance data"""

    total_cost: float = 0.0
    execution_time_minutes: int = 0
    agents_executed: int = 0
    token_usage: int = 0
    context_window_used_percent: float = 0.0


@dataclass
class Handoff:
    """
    Complete session handoff for continuity.

    This model follows expert recommendations:
    - Session summary with key decisions (WHY)
    - Active context for immediate orientation
    - Priority-ordered work remaining
    - Governance and performance metrics
    - Confidence level for AI self-assessment
    """

    # Metadata
    session_id: str = ""
    started: datetime = field(default_factory=datetime.now)
    duration_minutes: int = 0
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    resume_instructions: str = ""

    # Original task
    original_task: str = ""

    # Session summary (CRITICAL for decision context)
    session_summary: SessionSummary = field(default_factory=SessionSummary)

    # Progress
    workflow_progress: Optional[WorkflowProgress] = None

    # Work status
    work_completed: WorkCompleted = field(default_factory=WorkCompleted)
    work_remaining: WorkRemaining = field(default_factory=WorkRemaining)

    # Context (CRITICAL for AI orientation)
    active_context: ActiveContext = field(default_factory=ActiveContext)
    technical_context: List[str] = field(default_factory=list)

    # Quality
    governance_status: GovernanceStatus = field(default_factory=GovernanceStatus)

    # Performance
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)

    # Generation metadata
    generated_at: datetime = field(default_factory=datetime.now)

    def to_markdown(self) -> str:
        """
        Convert to markdown format matching /status visual style.

        Format follows expert recommendation with emoji indicators for scannability.
        """
        lines = []

        # Header
        lines.append("## Session Handoff")
        lines.append("")
        lines.append(f"**Session**: {self.session_id}")
        lines.append(f"**Started**: {self.started.strftime('%Y-%m-%d %H:%M')}")
        lines.append(
            f"**Duration**: {self.duration_minutes // 60}h {self.duration_minutes % 60}m"
        )

        # Status emoji based on confidence
        status_emoji = {
            ConfidenceLevel.HIGH: "🟢",
            ConfidenceLevel.MEDIUM: "🟡",
            ConfidenceLevel.LOW: "🔴",
        }
        emoji = status_emoji.get(self.confidence_level, "⚪")
        lines.append(f"**Status**: {emoji} {self.confidence_level.value.title()}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Original Task
        lines.append("## Original Task")
        lines.append("")
        lines.append(self.original_task)
        lines.append("")
        lines.append("---")
        lines.append("")

        # Session Summary
        if self.session_summary.key_decisions or self.session_summary.critical_insights:
            lines.append("## Session Summary")
            lines.append("")

            if self.session_summary.key_decisions:
                lines.append("**Key Decisions Made:**")
                for decision in self.session_summary.key_decisions:
                    lines.append(f"- {decision}")
                lines.append("")

            if self.session_summary.critical_insights:
                lines.append("**Critical Insights:**")
                for insight in self.session_summary.critical_insights:
                    lines.append(f"- {insight}")
                lines.append("")

            if self.session_summary.conversation_highlights:
                lines.append("**Conversation Highlights:**")
                lines.append(self.session_summary.conversation_highlights)
                lines.append("")

            lines.append("---")
            lines.append("")

        # Workflow Progress
        if self.workflow_progress:
            wp = self.workflow_progress
            lines.append("## Progress Summary")
            lines.append("")
            lines.append(
                f"**Overall**: {wp.completed_agents} of {wp.total_agents} agents complete ({wp.completion_percentage:.0f}%)"
            )
            lines.append("")

            for agent_exec in wp.agent_executions:
                status = agent_exec.get("status", "unknown")
                name = agent_exec.get("name", "unknown")
                emoji = {
                    "completed": "✅",
                    "in_progress": "🔄",
                    "pending": "⏳",
                    "failed": "❌",
                }.get(status, "⚪")
                lines.append(f"{emoji} {name}")

            lines.append("")
            lines.append("---")
            lines.append("")

        # Work Completed
        if self.work_completed.completed_items or self.work_completed.files_modified:
            lines.append("## Work Completed")
            lines.append("")

            if self.work_completed.completed_items:
                lines.append("**Completed Items:**")
                for item in self.work_completed.completed_items:
                    lines.append(f"- ✅ {item}")
                lines.append("")

            if self.work_completed.files_modified:
                lines.append("**Files Modified:**")
                for (
                    file_path,
                    description,
                ) in self.work_completed.files_modified.items():
                    lines.append(f"- `{file_path}`: {description}")
                lines.append("")

            if self.work_completed.agent_outputs:
                lines.append("**Agent Outputs:**")
                for output in self.work_completed.agent_outputs:
                    agent = output.get("agent", "unknown")
                    summary = output.get("summary", "")
                    lines.append(f"- **{agent}**: {summary}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Work Remaining (PRIORITY ORDERED)
        wr = self.work_remaining
        if wr.priority_1_critical or wr.priority_2_high or wr.priority_3_nice_to_have:
            lines.append("## Next Steps")
            lines.append("")

            if wr.priority_1_critical:
                lines.append("**PRIORITY 1 (Critical Path):**")
                for item in wr.priority_1_critical:
                    lines.append(f"- 🔴 {item}")
                lines.append("")

            if wr.priority_2_high:
                lines.append("**PRIORITY 2 (High Value):**")
                for item in wr.priority_2_high:
                    lines.append(f"- 🟡 {item}")
                lines.append("")

            if wr.priority_3_nice_to_have:
                lines.append("**PRIORITY 3 (Nice to Have):**")
                for item in wr.priority_3_nice_to_have:
                    lines.append(f"- 🟢 {item}")
                lines.append("")

            if wr.dependencies:
                lines.append("**Dependencies:**")
                for dep in wr.dependencies:
                    lines.append(f"- {dep}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Active Context (CRITICAL for next session)
        ac = self.active_context
        if ac.most_relevant or ac.known_blockers or ac.open_questions:
            lines.append("## Active Context")
            lines.append("")

            if ac.most_relevant:
                lines.append("**Most Relevant Right Now:**")
                for item in ac.most_relevant:
                    lines.append(f"- 💡 {item}")
                lines.append("")

            if ac.known_blockers:
                lines.append("**Known Blockers:**")
                for blocker in ac.known_blockers:
                    b_desc = blocker.get("blocker", "")
                    b_mit = blocker.get("mitigation", "None")
                    lines.append(f"- ⚠️ {b_desc}")
                    lines.append(f"  - Mitigation: {b_mit}")
                lines.append("")

            if ac.open_questions:
                lines.append("**Open Questions:**")
                for question in ac.open_questions:
                    lines.append(f"- ❓ {question}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Governance Status
        gs = self.governance_status
        lines.append("## Quality Status")
        lines.append("")
        status_emoji = "✅" if gs.validation_passed else "❌"
        lines.append(
            f"**Last Validation**: {status_emoji} {'All Checks Pass' if gs.validation_passed else 'Issues Found'}"
        )
        lines.append("")
        lines.append(
            f"- Scorecard: {gs.scorecard_pass}/{gs.scorecard_total} {'✅' if gs.scorecard_pass == gs.scorecard_total else '⚠️'}"
        )

        if gs.blockers:
            lines.append("- Blockers:")
            for blocker in gs.blockers:
                lines.append(f"  - ❌ {blocker}")

        if gs.next_validation_checkpoint:
            lines.append(f"- Next Checkpoint: {gs.next_validation_checkpoint}")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Performance Metrics
        pm = self.performance_metrics
        lines.append("## Cost & Performance")
        lines.append("")
        lines.append(f"💰 **Total Cost**: ${pm.total_cost:.4f}")
        lines.append(
            f"⏱️ **Execution Time**: {pm.execution_time_minutes // 60}h {pm.execution_time_minutes % 60}m"
        )
        lines.append(f"🤖 **Agents Run**: {pm.agents_executed}")
        lines.append(f"📊 **Tokens Used**: {pm.token_usage:,} tokens")
        lines.append(
            f"📈 **Context Window**: {pm.context_window_used_percent:.1f}% used"
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        # Technical Context
        if self.technical_context:
            lines.append("## Technical Context")
            lines.append("")
            for context_item in self.technical_context:
                lines.append(f"- {context_item}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Resume Instructions
        lines.append("## To Resume")
        lines.append("")
        lines.append(self.resume_instructions)
        lines.append("")
        lines.append("---")
        lines.append("")

        # Footer
        lines.append(
            f"**Generated**: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append(
            f"**Saved to**: `.claude/handoffs/handoff-{self.generated_at.strftime('%Y-%m-%d-%H%M%S')}.md`"
        )

        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, markdown: str) -> "Handoff":
        """
        Parse Handoff from markdown format.

        Args:
            markdown: Markdown-formatted handoff content

        Returns:
            Parsed Handoff object

        Raises:
            NotImplementedError: Markdown parsing not yet implemented

        Note:
            This feature is planned for a future release. For now, use
            HandoffGenerator.load_latest_handoff() to load saved handoffs,
            or HandoffGenerator.generate_handoff() to create new ones.
        """
        raise NotImplementedError(
            "Handoff.from_markdown() not yet implemented. "
            "Use HandoffGenerator.load_latest_handoff() to load saved handoffs."
        )

    def __repr__(self) -> str:
        return f"Handoff(session_id='{self.session_id}', duration={self.duration_minutes}min, confidence={self.confidence_level.value})"

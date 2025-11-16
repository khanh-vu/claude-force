"""
Meta-prompting data models for AI-assisted workflow generation.

Based on expert review recommendations:
- Structured XML-style I/O for consistency
- Governance compliance validation
- Iterative refinement with feedback
- Convergence tracking
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
import uuid


@dataclass
class MetaPromptConstraints:
    """Constraints for meta-prompting to respect"""

    governance_rules: List[str] = field(default_factory=list)
    available_resources: Dict[str, List[str]] = field(default_factory=dict)
    budget_limit: Optional[float] = None
    timeline: Optional[str] = None


@dataclass
class MetaPromptContext:
    """Context for meta-prompting to consider"""

    current_state: str = ""
    previous_attempts: List[str] = field(default_factory=list)
    project_info: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetaPromptRequest:
    """
    Input for meta-prompting with structured constraints.

    This model follows expert recommendations for structured meta-prompting:
    - Clear objective statement
    - Explicit constraints (governance, budget, timeline)
    - Context from previous attempts
    - Request tracking
    """

    objective: str
    constraints: MetaPromptConstraints = field(default_factory=MetaPromptConstraints)
    context: MetaPromptContext = field(default_factory=MetaPromptContext)

    # Metadata
    requested_at: datetime = field(default_factory=datetime.now)
    request_id: str = field(
        default_factory=lambda: f"meta-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    )

    def to_xml(self) -> str:
        """
        Convert to XML format for LLM input.

        Format follows expert recommendation for structured AI interaction.
        """
        lines = ["<meta_prompt_request>"]

        # Objective
        lines.append(f"  <objective>{self._escape_xml(self.objective)}</objective>")

        # Constraints
        if (
            self.constraints.governance_rules
            or self.constraints.available_resources
            or self.constraints.budget_limit
        ):
            lines.append("  <constraints>")

            if self.constraints.governance_rules:
                lines.append("    <governance>")
                for rule in self.constraints.governance_rules:
                    lines.append(f"      <rule>{self._escape_xml(rule)}</rule>")
                lines.append("    </governance>")

            if self.constraints.available_resources:
                lines.append("    <resources>")
                for resource_type, items in self.constraints.available_resources.items():
                    lines.append(f"      <{resource_type}>")
                    for item in items:
                        lines.append(f"        <item>{self._escape_xml(item)}</item>")
                    lines.append(f"      </{resource_type}>")
                lines.append("    </resources>")

            if self.constraints.budget_limit:
                lines.append(
                    f"    <budget_limit>${self.constraints.budget_limit:.2f}</budget_limit>"
                )

            if self.constraints.timeline:
                lines.append(
                    f"    <timeline>{self._escape_xml(self.constraints.timeline)}</timeline>"
                )

            lines.append("  </constraints>")

        # Context
        if self.context.current_state or self.context.previous_attempts:
            lines.append("  <context>")

            if self.context.current_state:
                lines.append(
                    f"    <current_state>{self._escape_xml(self.context.current_state)}</current_state>"
                )

            if self.context.previous_attempts:
                lines.append("    <previous_attempts>")
                for attempt in self.context.previous_attempts:
                    lines.append(f"      <attempt>{self._escape_xml(attempt)}</attempt>")
                lines.append("    </previous_attempts>")

            lines.append("  </context>")

        lines.append("</meta_prompt_request>")

        return "\n".join(lines)

    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )


@dataclass
class ProposedApproach:
    """Meta-prompt's proposed approach with rationale"""

    workflow: str = ""
    rationale: str = ""
    alternatives_considered: List[str] = field(default_factory=list)


@dataclass
class GovernanceCompliance:
    """Governance validation result for meta-prompted workflow"""

    rules_applied: List[str] = field(default_factory=list)
    validation_status: bool = False
    violations: List[str] = field(default_factory=list)


@dataclass
class MetaPromptResponse:
    """
    Output from meta-prompting with governance validation.

    This model follows expert recommendations:
    - Refined objective with reasoning
    - Proposed approach with alternatives considered
    - Governance compliance status
    - Success criteria for validation
    - Risk assessment
    """

    refined_objective: str = ""
    reasoning: str = ""
    proposed_approach: ProposedApproach = field(default_factory=ProposedApproach)
    governance_compliance: GovernanceCompliance = field(default_factory=GovernanceCompliance)
    success_criteria: List[str] = field(default_factory=list)
    risk_assessment: List[str] = field(default_factory=list)

    # Iteration tracking
    iteration: int = 1
    converging: bool = True

    # Metadata
    response_id: str = field(
        default_factory=lambda: f"meta-resp-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    )
    generated_at: datetime = field(default_factory=datetime.now)

    def to_xml(self) -> str:
        """
        Convert to XML format for structured output.

        Format follows expert recommendation for AI output parsing.
        """
        lines = ["<meta_prompt_response>"]

        # Refined objective
        lines.append(
            f"  <refined_objective>{self._escape_xml(self.refined_objective)}</refined_objective>"
        )

        # Reasoning
        lines.append(f"  <reasoning>{self._escape_xml(self.reasoning)}</reasoning>")

        # Proposed approach
        lines.append("  <proposed_approach>")
        lines.append(
            f"    <workflow>{self._escape_xml(self.proposed_approach.workflow)}</workflow>"
        )
        lines.append(
            f"    <rationale>{self._escape_xml(self.proposed_approach.rationale)}</rationale>"
        )

        if self.proposed_approach.alternatives_considered:
            lines.append("    <alternatives_considered>")
            for alt in self.proposed_approach.alternatives_considered:
                lines.append(f"      <alternative>{self._escape_xml(alt)}</alternative>")
            lines.append("    </alternatives_considered>")

        lines.append("  </proposed_approach>")

        # Governance compliance
        lines.append("  <governance_compliance>")

        if self.governance_compliance.rules_applied:
            lines.append("    <rules_applied>")
            for rule in self.governance_compliance.rules_applied:
                lines.append(f"      <rule>{self._escape_xml(rule)}</rule>")
            lines.append("    </rules_applied>")

        lines.append(
            f"    <validation_status>{'pass' if self.governance_compliance.validation_status else 'fail'}</validation_status>"
        )

        if self.governance_compliance.violations:
            lines.append("    <violations>")
            for violation in self.governance_compliance.violations:
                lines.append(f"      <violation>{self._escape_xml(violation)}</violation>")
            lines.append("    </violations>")

        lines.append("  </governance_compliance>")

        # Success criteria
        if self.success_criteria:
            lines.append("  <success_criteria>")
            for criterion in self.success_criteria:
                lines.append(f"    <criterion>{self._escape_xml(criterion)}</criterion>")
            lines.append("  </success_criteria>")

        # Risk assessment
        if self.risk_assessment:
            lines.append("  <risk_assessment>")
            for risk in self.risk_assessment:
                lines.append(f"    <risk>{self._escape_xml(risk)}</risk>")
            lines.append("  </risk_assessment>")

        lines.append("</meta_prompt_response>")

        return "\n".join(lines)

    @staticmethod
    def _escape_xml(text: str) -> str:
        """Escape XML special characters"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )


@dataclass
class RefinementIteration:
    """
    Track iterative refinement for meta-prompting.

    This allows the system to learn and improve from failed attempts.
    """

    iteration_number: int = 0
    previous_attempt: str = ""
    validation_failures: List[str] = field(default_factory=list)
    guidance: str = ""
    refined_attempt: str = ""

    def to_xml(self) -> str:
        """Convert to XML format for feedback loop"""
        lines = [f'<refinement_iteration n="{self.iteration_number}">']

        lines.append(
            f"  <previous_attempt>{MetaPromptResponse._escape_xml(self.previous_attempt)}</previous_attempt>"
        )

        if self.validation_failures:
            lines.append("  <validation_failures>")
            for failure in self.validation_failures:
                lines.append(f"    <failure>{MetaPromptResponse._escape_xml(failure)}</failure>")
            lines.append("  </validation_failures>")

        lines.append(f"  <guidance>{MetaPromptResponse._escape_xml(self.guidance)}</guidance>")

        if self.refined_attempt:
            lines.append(
                f"  <refined_attempt>{MetaPromptResponse._escape_xml(self.refined_attempt)}</refined_attempt>"
            )

        lines.append("</refinement_iteration>")

        return "\n".join(lines)

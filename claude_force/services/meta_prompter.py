"""
MetaPrompter service for AI-assisted workflow generation with governance.

Provides:
- Meta-prompting with structured I/O
- Iterative refinement with feedback
- Governance compliance validation
- Workflow generation from high-level goals
- Convergence tracking
"""

from typing import List, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from claude_force.orchestrator import AgentOrchestrator

from ..models.meta_prompt import (
    MetaPromptRequest,
    MetaPromptResponse,
    ProposedApproach,
    GovernanceCompliance,
    RefinementIteration,
)


class MetaPrompter:
    """
    Meta-prompting service with governance integration.

    Features:
    - Structured XML-based meta-prompting
    - Iterative refinement (up to 3 iterations)
    - Governance validation before execution
    - Convergence detection
    - Fallback to closest valid workflow
    """

    MAX_ITERATIONS = 3

    def __init__(self, orchestrator: "AgentOrchestrator"):
        self.orchestrator = orchestrator
        self.governance = getattr(orchestrator, "governance_manager", None)

    def generate_workflow(
        self, request: MetaPromptRequest, auto_validate: bool = True
    ) -> MetaPromptResponse:
        """
        Generate workflow with iterative refinement and governance validation.

        Args:
            request: MetaPromptRequest with objective and constraints
            auto_validate: Automatically validate against governance

        Returns:
            MetaPromptResponse with proposed workflow and validation status
        """
        iterations: List[RefinementIteration] = []

        for iteration in range(1, self.MAX_ITERATIONS + 1):
            # Generate workflow proposal
            response = self._llm_generate_workflow(request, iterations)
            response.iteration = iteration

            # Validate against governance if requested
            if auto_validate:
                validation = self._validate_governance(response, request)
                response.governance_compliance = validation

                if validation.validation_status:
                    # Success! Governance passed
                    return response

                # Failed validation - prepare for retry
                if iteration < self.MAX_ITERATIONS:
                    # Add refinement iteration
                    refinement = RefinementIteration(
                        iteration_number=iteration,
                        previous_attempt=response.proposed_approach.workflow,
                        validation_failures=validation.violations,
                        guidance=self._generate_refinement_guidance(validation),
                        refined_attempt="",  # Will be filled in next iteration
                    )
                    iterations.append(refinement)

                    # Check convergence
                    if not self._is_converging(iterations):
                        response.converging = False
                        break
                else:
                    # Max iterations reached
                    response.converging = False
                    break
            else:
                # No validation requested, return immediately
                return response

        # If we get here, validation failed after all iterations
        # Return response with governance violations
        return response

    def _llm_generate_workflow(
        self, request: MetaPromptRequest, previous_iterations: List[RefinementIteration]
    ) -> MetaPromptResponse:
        """
        Use LLM to generate workflow proposal.

        Args:
            request: MetaPromptRequest
            previous_iterations: List of previous refinement attempts

        Returns:
            MetaPromptResponse with proposed workflow

        Raises:
            RuntimeError: If LLM call fails
        """
        import logging

        logger = logging.getLogger(__name__)

        # Build prompt for LLM
        prompt = self._build_meta_prompt(request, previous_iterations)

        # Add structured response instructions
        prompt += "\n\n## Response Format\n\n"
        prompt += "Please provide your response in the following format:\n\n"
        prompt += "**REFINED OBJECTIVE:**\n[Clarified, specific objective]\n\n"
        prompt += "**REASONING:**\n[Why this approach makes sense]\n\n"
        prompt += "**PROPOSED WORKFLOW:**\n[Step-by-step workflow using available agents and commands]\n\n"
        prompt += "**RATIONALE:**\n[Why this specific workflow was chosen]\n\n"
        prompt += "**SUCCESS CRITERIA:**\n- [Criterion 1]\n- [Criterion 2]\n\n"
        prompt += (
            "**RISK ASSESSMENT:**\n- [Risk 1]: [Mitigation]\n- [Risk 2]: [Mitigation]\n"
        )

        try:
            # Call orchestrator to run meta-prompting
            # Use Sonnet model for better reasoning
            result = self.orchestrator.run_agent(
                agent_name="meta-architect",  # Uses meta-architect if available, falls back to default
                task=prompt,
                model="claude-sonnet-4-5-20250929",
                max_tokens=8192,
                temperature=0.7,  # Some creativity but still focused
            )

            if not result.success:
                error_msg = (
                    "; ".join(result.errors) if result.errors else "Unknown error"
                )
                raise RuntimeError(f"Meta-prompting LLM call failed: {error_msg}")

            # Parse structured response
            response = self._parse_llm_response(result.output, request)
            return response

        except ValueError as e:
            # Agent not found - use fallback
            logger.warning(f"meta-architect agent not found, using fallback: {e}")
            return self._create_fallback_response(request)
        except Exception as e:
            logger.error(f"Meta-prompting failed: {e}")
            raise RuntimeError(f"Meta-prompting failed: {e}")

    def _validate_governance(
        self, response: MetaPromptResponse, request: MetaPromptRequest
    ) -> GovernanceCompliance:
        """
        Validate proposed workflow against governance rules.

        Args:
            response: MetaPromptResponse to validate
            request: Original request with constraints

        Returns:
            GovernanceCompliance with validation result
        """
        violations = []
        rules_applied = []

        workflow = response.proposed_approach.workflow

        # Check 1: Agent availability
        rules_applied.append("agent_availability")
        agents = self._extract_agents_from_workflow(workflow)

        for agent in agents:
            if not self._agent_exists(agent):
                violations.append(f"Agent '{agent}' does not exist or is not available")

        # Check 2: Budget compliance
        if request.constraints.budget_limit:
            rules_applied.append("budget_compliance")
            estimated_cost = self._estimate_workflow_cost(workflow)

            if estimated_cost > request.constraints.budget_limit:
                violations.append(
                    f"Estimated cost ${estimated_cost:.2f} exceeds budget limit ${request.constraints.budget_limit:.2f}"
                )

        # Check 3: Skill requirements
        rules_applied.append("skill_requirements")
        required_skills = self._extract_required_skills(workflow)
        available_skills = self._get_available_skills()

        missing_skills = set(required_skills) - set(available_skills)
        if missing_skills:
            violations.append(f"Missing required skills: {', '.join(missing_skills)}")

        # Check 4: Safety checks (from governance manager)
        if self.governance and hasattr(self.governance, "validate_workflow"):
            rules_applied.append("safety_checks")
            try:
                gov_result = self.governance.validate_workflow(workflow)
                if not gov_result.passed:
                    violations.extend(gov_result.failures)
            except Exception:
                # Governance manager not available or failed
                pass

        return GovernanceCompliance(
            rules_applied=rules_applied,
            validation_status=len(violations) == 0,
            violations=violations,
        )

    def _generate_refinement_guidance(self, validation: GovernanceCompliance) -> str:
        """
        Generate guidance for next refinement iteration.

        Args:
            validation: GovernanceCompliance with violations

        Returns:
            Guidance string for refinement
        """
        guidance_parts = []

        for violation in validation.violations:
            if "does not exist" in violation or "not available" in violation:
                guidance_parts.append(
                    f"Fix: {violation}. Use only available agents. "
                    f"Check agent list with `/list-agents` or use semantic selector."
                )
            elif "exceeds budget" in violation:
                guidance_parts.append(
                    f"Fix: {violation}. Reduce workflow scope, use fewer agents, "
                    f"or prefer Haiku model for simple tasks."
                )
            elif "Missing required skills" in violation:
                guidance_parts.append(
                    f"Fix: {violation}. Either remove skill dependencies or "
                    f"suggest installing required skills."
                )
            else:
                guidance_parts.append(f"Fix: {violation}")

        if not guidance_parts:
            guidance_parts.append(
                "No specific guidance available. Review governance rules."
            )

        return "\n".join(guidance_parts)

    def _is_converging(self, iterations: List[RefinementIteration]) -> bool:
        """
        Check if iterations are converging toward valid solution.

        Args:
            iterations: List of refinement iterations

        Returns:
            True if converging, False otherwise
        """
        if len(iterations) < 2:
            return True

        # Check if number of violations is decreasing
        last_failures = len(iterations[-1].validation_failures)
        prev_failures = len(iterations[-2].validation_failures)

        # If failures are not decreasing, we're diverging
        if last_failures >= prev_failures:
            return False

        # Check for repeated violations (stuck in loop)
        if len(iterations) >= 2:
            last_set = set(iterations[-1].validation_failures)
            prev_set = set(iterations[-2].validation_failures)

            # If same violations appearing, not converging
            if last_set == prev_set:
                return False

        return True

    def _build_meta_prompt(
        self, request: MetaPromptRequest, previous_iterations: List[RefinementIteration]
    ) -> str:
        """
        Build prompt for LLM meta-prompting.

        Args:
            request: MetaPromptRequest
            previous_iterations: Previous refinement attempts

        Returns:
            Prompt string for LLM
        """
        parts = []

        # Header
        parts.append("# Meta-Prompting Request")
        parts.append("")
        parts.append(
            "Please refine the following objective into a concrete workflow plan."
        )
        parts.append("")

        # Include request as XML
        parts.append(request.to_xml())
        parts.append("")

        # Include previous iterations if any
        if previous_iterations:
            parts.append("## Previous Refinement Attempts")
            parts.append("")
            parts.append("The following attempts were made but failed validation:")
            parts.append("")

            for iteration in previous_iterations:
                parts.append(iteration.to_xml())
                parts.append("")

        # Instructions
        parts.append("## Instructions")
        parts.append("")
        parts.append("Generate a workflow that:")
        parts.append("1. Achieves the objective")
        parts.append("2. Respects all constraints")
        parts.append("3. Uses only available resources")
        parts.append("4. Passes all governance rules")
        parts.append("")
        parts.append("Format your response as XML matching MetaPromptResponse schema.")

        return "\n".join(parts)

    def _extract_agents_from_workflow(self, workflow: str) -> List[str]:
        """
        Extract agent names from workflow description.

        Args:
            workflow: Workflow description string

        Returns:
            List of agent names found
        """
        # Simple pattern matching for agent names
        # In production, this would be more sophisticated
        agents = []

        # Look for common patterns: "agent-name" or "/run-agent agent-name"
        patterns = [
            r"/run-agent\s+([a-z-]+)",
            r"agent:\s*([a-z-]+)",
            r"([a-z]+-(?:architect|expert|developer|specialist|engineer))",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, workflow.lower())
            agents.extend(matches)

        # Remove duplicates
        return list(set(agents))

    def _estimate_workflow_cost(self, workflow: str) -> float:
        """
        Estimate cost of proposed workflow.

        Args:
            workflow: Workflow description

        Returns:
            Estimated cost in dollars
        """
        # Simple estimation based on number of agents
        # In production, this would use actual pricing data
        agents = self._extract_agents_from_workflow(workflow)

        # Rough estimate: $0.10 per agent
        base_cost = len(agents) * 0.10

        # Check for complexity indicators
        if "complex" in workflow.lower():
            base_cost *= 1.5
        if "thorough" in workflow.lower() or "comprehensive" in workflow.lower():
            base_cost *= 1.3

        return base_cost

    def _extract_required_skills(self, workflow: str) -> List[str]:
        """
        Extract required skills from workflow description.

        Args:
            workflow: Workflow description

        Returns:
            List of required skills
        """
        skills = []

        # Look for skill mentions
        skill_patterns = [
            r"skill:\s*([a-z-]+)",
            r"requires?\s+([a-z-]+)\s+skill",
            r"using\s+([a-z-]+)\s+skill",
        ]

        for pattern in skill_patterns:
            matches = re.findall(pattern, workflow.lower())
            skills.extend(matches)

        return list(set(skills))

    def _agent_exists(self, agent_name: str) -> bool:
        """
        Check if agent exists in the system.

        Args:
            agent_name: Agent name to check

        Returns:
            True if agent exists
        """
        # Check orchestrator's agent registry
        if hasattr(self.orchestrator, "get_agent_info"):
            try:
                info = self.orchestrator.get_agent_info(agent_name)
                return info is not None  # If we got here, agent exists
            except (ValueError, KeyError):
                # Agent not found in registry
                pass
            except Exception as e:
                # Unexpected error - log it
                import logging

                logging.getLogger(__name__).warning(
                    f"Unexpected error checking agent '{agent_name}': {e}"
                )
                pass

        # Fallback: check if agent file exists
        from pathlib import Path

        agent_file = Path(f".claude/agents/{agent_name}.md")
        template_file = Path(f"claude_force/templates/agents/{agent_name}.md")

        return agent_file.exists() or template_file.exists()

    def _parse_llm_response(
        self, llm_output: str, request: MetaPromptRequest
    ) -> MetaPromptResponse:
        """
        Parse LLM's structured response into MetaPromptResponse.

        Args:
            llm_output: Raw LLM output text
            request: Original request for fallback values

        Returns:
            Parsed MetaPromptResponse
        """
        import re

        # Extract sections using regex
        def extract_section(text: str, header: str) -> str:
            """Extract content under a markdown header."""
            pattern = rf"\*\*{header}:\*\*\s*\n(.+?)(?=\n\*\*|\Z)"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
            return ""

        def extract_list(text: str, header: str) -> List[str]:
            """Extract bullet list items under a header."""
            content = extract_section(text, header)
            if not content:
                return []
            # Extract list items
            items = re.findall(r"^[\-\*]\s*(.+?)$", content, re.MULTILINE)
            return [item.strip() for item in items if item.strip()]

        # Parse each section
        refined_objective = extract_section(llm_output, "REFINED OBJECTIVE")
        reasoning = extract_section(llm_output, "REASONING")
        workflow = extract_section(llm_output, "PROPOSED WORKFLOW")
        rationale = extract_section(llm_output, "RATIONALE")

        success_criteria = extract_list(llm_output, "SUCCESS CRITERIA")
        risk_items = extract_list(llm_output, "RISK ASSESSMENT")

        # Use request objective as fallback
        if not refined_objective:
            refined_objective = request.objective

        # Build response
        return MetaPromptResponse(
            refined_objective=refined_objective or request.objective,
            reasoning=reasoning or "Analysis of objective and constraints",
            proposed_approach=ProposedApproach(
                workflow=workflow or "No workflow generated",
                rationale=rationale or "Approach based on available resources",
                alternatives_considered=[],
            ),
            governance_compliance=GovernanceCompliance(),  # Will be filled by validation
            success_criteria=success_criteria or ["Objective achieved"],
            risk_assessment=risk_items or [],
        )

    def _create_fallback_response(
        self, request: MetaPromptRequest
    ) -> MetaPromptResponse:
        """
        Create fallback response when LLM call fails.

        Args:
            request: Original request

        Returns:
            Basic MetaPromptResponse
        """
        return MetaPromptResponse(
            refined_objective=request.objective,
            reasoning="Fallback response - meta-architect agent not available",
            proposed_approach=ProposedApproach(
                workflow=f"Manual workflow needed for: {request.objective}",
                rationale="LLM-based meta-prompting unavailable, manual planning required",
                alternatives_considered=[],
            ),
            governance_compliance=GovernanceCompliance(
                validation_status=False,
                violations=["Meta-prompting service unavailable"],
            ),
            success_criteria=["Complete the objective manually"],
            risk_assessment=["Risk: No automated workflow generation available"],
        )

    def _get_available_skills(self) -> List[str]:
        """
        Get list of available skills.

        Returns:
            List of skill names
        """
        # In production, this would query orchestrator's skills manager
        if hasattr(self.orchestrator, "get_available_skills"):
            try:
                return self.orchestrator.get_available_skills()
            except Exception:
                pass

        # Fallback: check skills directory
        from pathlib import Path

        skills_dir = Path(".claude/skills")
        if not skills_dir.exists():
            return []

        skills = []
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skills.append(skill_dir.name)

        return skills

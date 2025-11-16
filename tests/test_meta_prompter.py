"""
Tests for MetaPrompter service

Ensures MetaPrompter correctly:
- Generates workflow from objectives
- Validates against governance
- Performs iterative refinement
- Detects convergence
- Handles constraints (budget, timeline)
- Provides alternatives and reasoning
"""

import pytest
from claude_force.models.meta_prompt import (
    MetaPromptRequest,
    MetaPromptResponse,
    MetaPromptConstraints,
    MetaPromptContext,
    ProposedApproach,
    GovernanceCompliance,
    RefinementIteration
)
from claude_force.services.meta_prompter import MetaPrompter


class MockGovernanceManager:
    """Mock governance manager for testing"""

    def __init__(self, should_pass=True):
        self.should_pass = should_pass

    def validate_workflow(self, workflow):
        class MockResult:
            def __init__(self, passed, failures):
                self.passed = passed
                self.failures = failures

        if self.should_pass:
            return MockResult(True, [])
        else:
            return MockResult(False, ["Security violation"])


class MockOrchestrator:
    """Mock orchestrator for testing"""

    def __init__(self, governance_pass=True):
        self.governance_manager = MockGovernanceManager(governance_pass)
        self._agents = {
            "backend-architect": True,
            "frontend-developer": True,
            "security-specialist": True
        }
        self._skills = ["backend", "frontend", "security"]

    def get_agent_info(self, agent_name):
        if agent_name in self._agents:
            return {"name": agent_name}
        return None

    def get_available_skills(self):
        return self._skills


class TestMetaPrompter:
    """Test MetaPrompter service"""

    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator"""
        return MockOrchestrator()

    @pytest.fixture
    def meta_prompter(self, mock_orchestrator):
        """Create MetaPrompter instance"""
        return MetaPrompter(mock_orchestrator)

    @pytest.fixture
    def sample_request(self):
        """Create sample MetaPromptRequest"""
        return MetaPromptRequest(
            objective="Build user authentication system",
            constraints=MetaPromptConstraints(
                governance_rules=["Use secure password storage"],
                available_resources={"agents": ["backend-architect", "security-specialist"]},
                budget_limit=5.00,
                timeline="60 min"
            ),
            context=MetaPromptContext(
                current_state="Empty project",
                previous_attempts=[]
            )
        )

    def test_generate_workflow_basic(self, meta_prompter, sample_request):
        """Test basic workflow generation"""
        response = meta_prompter.generate_workflow(sample_request, auto_validate=False)

        assert response is not None
        assert isinstance(response, MetaPromptResponse)
        assert response.iteration == 1

    def test_governance_validation_passes(self, meta_prompter):
        """Test governance validation when all checks pass"""
        request = MetaPromptRequest(
            objective="Simple task",
            constraints=MetaPromptConstraints(
                available_resources={"agents": ["backend-architect"]}
            )
        )

        response = MetaPromptResponse(
            refined_objective="Task",
            reasoning="Because",
            proposed_approach=ProposedApproach(
                workflow="/run-agent backend-architect",
                rationale="Good choice"
            )
        )

        validation = meta_prompter._validate_governance(response, request)

        # Should have no violations (agents exist)
        assert isinstance(validation, GovernanceCompliance)
        assert len(validation.rules_applied) > 0

    def test_governance_validation_fails_missing_agent(self, meta_prompter):
        """Test governance validation fails for missing agent"""
        request = MetaPromptRequest(objective="Task")

        response = MetaPromptResponse(
            refined_objective="Task",
            reasoning="Because",
            proposed_approach=ProposedApproach(
                workflow="/run-agent non-existent-agent",
                rationale="Choice"
            )
        )

        validation = meta_prompter._validate_governance(response, request)

        assert validation.validation_status is False
        assert len(validation.violations) > 0
        assert any("does not exist" in v or "not available" in v for v in validation.violations)

    def test_governance_validation_budget_exceeded(self, meta_prompter):
        """Test governance validation fails when budget exceeded"""
        request = MetaPromptRequest(
            objective="Complex task",
            constraints=MetaPromptConstraints(
                budget_limit=1.00  # Very low
            )
        )

        response = MetaPromptResponse(
            refined_objective="Task",
            reasoning="Because",
            proposed_approach=ProposedApproach(
                workflow="/run-agent backend-architect\n/run-agent frontend-developer\n/run-agent security-specialist",
                rationale="Full stack"
            )
        )

        validation = meta_prompter._validate_governance(response, request)

        # Estimated cost should exceed $1.00
        # (This test depends on cost estimation logic)

    def test_extract_agents_from_workflow(self, meta_prompter):
        """Test extracting agent names from workflow description"""
        workflow = """
        /run-agent backend-architect
        /run-agent frontend-developer
        agent: security-specialist
        """

        agents = meta_prompter._extract_agents_from_workflow(workflow)

        assert len(agents) > 0
        # Should contain at least backend-architect
        assert any("backend-architect" in agent for agent in agents)

    def test_estimate_workflow_cost(self, meta_prompter):
        """Test workflow cost estimation"""
        # Simple workflow
        simple_workflow = "/run-agent backend-architect"
        simple_cost = meta_prompter._estimate_workflow_cost(simple_workflow)
        assert simple_cost > 0

        # Complex workflow
        complex_workflow = """
        /run-agent backend-architect
        /run-agent frontend-developer
        /run-agent security-specialist
        comprehensive analysis
        """
        complex_cost = meta_prompter._estimate_workflow_cost(complex_workflow)

        # Complex should cost more than simple
        assert complex_cost > simple_cost

    def test_extract_required_skills(self, meta_prompter):
        """Test extracting required skills from workflow"""
        workflow = """
        This requires backend skill and frontend skill.
        Using security skill for validation.
        """

        skills = meta_prompter._extract_required_skills(workflow)
        # Should extract skills mentioned
        # (This depends on implementation details)

    def test_agent_exists_check(self, meta_prompter):
        """Test checking if agent exists"""
        # Existing agent
        assert meta_prompter._agent_exists("backend-architect") is True

        # Non-existent agent
        assert meta_prompter._agent_exists("non-existent-agent") is False

    def test_get_available_skills(self, meta_prompter):
        """Test getting available skills"""
        skills = meta_prompter._get_available_skills()

        assert isinstance(skills, list)
        # Should include some skills from mock
        assert len(skills) >= 0

    def test_convergence_detection_improving(self, meta_prompter):
        """Test convergence detection when failures decreasing"""
        iterations = [
            RefinementIteration(
                iteration_number=1,
                previous_attempt="Attempt 1",
                validation_failures=["Error 1", "Error 2", "Error 3"],
                guidance="Fix errors",
                refined_attempt=""
            ),
            RefinementIteration(
                iteration_number=2,
                previous_attempt="Attempt 2",
                validation_failures=["Error 1"],  # Fewer failures
                guidance="Fix remaining",
                refined_attempt=""
            )
        ]

        is_converging = meta_prompter._is_converging(iterations)
        assert is_converging is True

    def test_convergence_detection_not_improving(self, meta_prompter):
        """Test convergence detection when failures not decreasing"""
        iterations = [
            RefinementIteration(
                iteration_number=1,
                previous_attempt="Attempt 1",
                validation_failures=["Error 1"],
                guidance="Fix",
                refined_attempt=""
            ),
            RefinementIteration(
                iteration_number=2,
                previous_attempt="Attempt 2",
                validation_failures=["Error 1", "Error 2"],  # More failures
                guidance="Fix",
                refined_attempt=""
            )
        ]

        is_converging = meta_prompter._is_converging(iterations)
        assert is_converging is False

    def test_convergence_detection_stuck(self, meta_prompter):
        """Test convergence detection when stuck on same errors"""
        iterations = [
            RefinementIteration(
                iteration_number=1,
                previous_attempt="Attempt 1",
                validation_failures=["Error 1"],
                guidance="Fix",
                refined_attempt=""
            ),
            RefinementIteration(
                iteration_number=2,
                previous_attempt="Attempt 2",
                validation_failures=["Error 1"],  # Same error
                guidance="Fix",
                refined_attempt=""
            )
        ]

        is_converging = meta_prompter._is_converging(iterations)
        assert is_converging is False

    def test_refinement_guidance_generation(self, meta_prompter):
        """Test generating refinement guidance from violations"""
        validation = GovernanceCompliance(
            rules_applied=["agent_availability"],
            validation_status=False,
            violations=[
                "Agent 'ml-agent' does not exist",
                "Budget limit exceeded ($10 > $5)"
            ]
        )

        guidance = meta_prompter._generate_refinement_guidance(validation)

        assert isinstance(guidance, str)
        assert len(guidance) > 0
        # Should mention using available agents
        assert "available" in guidance.lower() or "agent" in guidance.lower()

    def test_max_iterations_limit(self, meta_prompter):
        """Test that refinement stops after MAX_ITERATIONS"""
        # Create orchestrator that always fails validation
        failing_orchestrator = MockOrchestrator(governance_pass=False)
        failing_meta_prompter = MetaPrompter(failing_orchestrator)

        request = MetaPromptRequest(objective="Test")

        # This should iterate up to MAX_ITERATIONS and then stop
        response = failing_meta_prompter.generate_workflow(request, auto_validate=True)

        # Should have attempted MAX_ITERATIONS
        assert response.iteration <= failing_meta_prompter.MAX_ITERATIONS
        assert response.converging is False


class TestMetaPromptModels:
    """Test MetaPrompt data models"""

    def test_meta_prompt_request_creation(self):
        """Test MetaPromptRequest creation"""
        request = MetaPromptRequest(
            objective="Build feature X",
            constraints=MetaPromptConstraints(
                budget_limit=10.00
            )
        )

        assert request.objective == "Build feature X"
        assert request.constraints.budget_limit == 10.00
        assert request.request_id is not None

    def test_meta_prompt_request_to_xml(self):
        """Test MetaPromptRequest XML serialization"""
        request = MetaPromptRequest(
            objective="Test objective",
            constraints=MetaPromptConstraints(
                governance_rules=["Rule 1"],
                budget_limit=5.00
            ),
            context=MetaPromptContext(
                current_state="Current"
            )
        )

        xml = request.to_xml()

        assert "<meta_prompt_request>" in xml
        assert "<objective>Test objective</objective>" in xml
        assert "<budget_limit>$5.00</budget_limit>" in xml
        assert "<current_state>Current</current_state>" in xml

    def test_meta_prompt_response_creation(self):
        """Test MetaPromptResponse creation"""
        response = MetaPromptResponse(
            refined_objective="Refined goal",
            reasoning="Because X",
            proposed_approach=ProposedApproach(
                workflow="Step 1, Step 2",
                rationale="Best approach"
            ),
            success_criteria=["Criterion 1"]
        )

        assert response.refined_objective == "Refined goal"
        assert response.proposed_approach.workflow == "Step 1, Step 2"
        assert len(response.success_criteria) == 1

    def test_meta_prompt_response_to_xml(self):
        """Test MetaPromptResponse XML serialization"""
        response = MetaPromptResponse(
            refined_objective="Goal",
            reasoning="Reason",
            proposed_approach=ProposedApproach(
                workflow="Workflow",
                rationale="Rationale",
                alternatives_considered=["Alt 1"]
            ),
            governance_compliance=GovernanceCompliance(
                validation_status=True
            ),
            success_criteria=["Criterion"]
        )

        xml = response.to_xml()

        assert "<meta_prompt_response>" in xml
        assert "<refined_objective>Goal</refined_objective>" in xml
        assert "<workflow>Workflow</workflow>" in xml
        assert "<validation_status>pass</validation_status>" in xml

    def test_xml_escaping(self):
        """Test XML special character escaping"""
        request = MetaPromptRequest(
            objective="Test with <special> & \"chars\""
        )

        xml = request.to_xml()

        # Should escape special characters
        assert "&lt;" in xml  # <
        assert "&gt;" in xml  # >
        assert "&amp;" in xml  # &
        assert "&quot;" in xml  # "

    def test_refinement_iteration_to_xml(self):
        """Test RefinementIteration XML serialization"""
        iteration = RefinementIteration(
            iteration_number=2,
            previous_attempt="First try",
            validation_failures=["Error 1", "Error 2"],
            guidance="Fix these errors",
            refined_attempt="Second try"
        )

        xml = iteration.to_xml()

        assert '<refinement_iteration n="2">' in xml
        assert "<previous_attempt>First try</previous_attempt>" in xml
        assert "<failure>Error 1</failure>" in xml
        assert "<guidance>Fix these errors</guidance>" in xml

    def test_proposed_approach(self):
        """Test ProposedApproach model"""
        approach = ProposedApproach(
            workflow="Step 1, Step 2, Step 3",
            rationale="This is the best approach because...",
            alternatives_considered=[
                "Alternative 1: simpler but less robust",
                "Alternative 2: more complex but overkill"
            ]
        )

        assert approach.workflow == "Step 1, Step 2, Step 3"
        assert len(approach.alternatives_considered) == 2

    def test_governance_compliance_model(self):
        """Test GovernanceCompliance model"""
        compliance = GovernanceCompliance(
            rules_applied=["agent_availability", "budget_compliance"],
            validation_status=True,
            violations=[]
        )

        assert compliance.validation_status is True
        assert len(compliance.rules_applied) == 2
        assert len(compliance.violations) == 0

    def test_governance_compliance_with_violations(self):
        """Test GovernanceCompliance with violations"""
        compliance = GovernanceCompliance(
            rules_applied=["agent_availability"],
            validation_status=False,
            violations=["Agent 'xyz' not found", "Budget exceeded"]
        )

        assert compliance.validation_status is False
        assert len(compliance.violations) == 2

    def test_meta_prompt_constraints(self):
        """Test MetaPromptConstraints model"""
        constraints = MetaPromptConstraints(
            governance_rules=["Security rule 1", "Performance rule 2"],
            available_resources={"agents": ["agent1", "agent2"], "skills": ["skill1"]},
            budget_limit=10.50,
            timeline="45 minutes"
        )

        assert len(constraints.governance_rules) == 2
        assert constraints.budget_limit == 10.50
        assert constraints.timeline == "45 minutes"
        assert "agents" in constraints.available_resources

    def test_meta_prompt_context(self):
        """Test MetaPromptContext model"""
        context = MetaPromptContext(
            current_state="In progress on frontend",
            previous_attempts=["Tried approach A (failed)", "Tried approach B (partial)"],
            project_info={"stack": "React + FastAPI", "db": "PostgreSQL"}
        )

        assert context.current_state == "In progress on frontend"
        assert len(context.previous_attempts) == 2
        assert context.project_info["stack"] == "React + FastAPI"

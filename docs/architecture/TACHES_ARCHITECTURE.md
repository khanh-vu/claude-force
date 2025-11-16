# TÂCHES Integration Architecture

**Version**: 1.0
**Date**: 2025-11-16
**Status**: Design Phase - Pre-Implementation

## Overview

This document defines the technical architecture for integrating TÂCHES workflow management commands into claude-force. Based on expert reviews, this architecture prioritizes:

1. **Clean UX** - Consolidated commands, consistent naming
2. **Service Layer Separation** - Commands (UI) separate from business logic (Python)
3. **Governance Integration** - Meta-prompting respects existing governance
4. **AI Optimization** - Structured formats for LLM effectiveness
5. **Performance** - Caching and efficient file operations

## Data Models

### 1. Todo Item Model

**File**: `claude_force/models/todo.py`

```python
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Priority(Enum):
    """Todo priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Complexity(Enum):
    """Estimated complexity"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class TodoStatus(Enum):
    """Todo lifecycle status"""
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

@dataclass
class TodoItem:
    """Represents a single todo item with AI-optimized fields"""

    # Core fields
    id: str
    action: str  # Action verb + high-level objective
    why_matters: str  # Context/rationale for this todo

    # Problem definition
    problem: str  # Issue description with user/system impact
    current_state: str  # What happens now
    desired_state: str  # What should happen

    # Success criteria
    success_criteria: List[str]  # Specific measurable outcomes

    # File references
    files: List[str] = field(default_factory=list)  # Paths with line numbers

    # Solution approach (optional)
    solution_approach: Optional[str] = None

    # Required capabilities (not prescriptive agents)
    required_capabilities: List[str] = field(default_factory=list)

    # Suggested resources (optional)
    suggested_agents: List[str] = field(default_factory=list)
    suggested_workflows: List[str] = field(default_factory=list)

    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Other todo IDs
    blocks: List[str] = field(default_factory=list)  # What this blocks

    # Metadata
    priority: Priority = Priority.MEDIUM
    complexity: Complexity = Complexity.MODERATE
    estimated_cost: Optional[float] = None
    added: datetime = field(default_factory=datetime.now)
    completed: Optional[datetime] = None
    status: TodoStatus = TodoStatus.ACTIVE
    tags: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert to markdown format for TO-DOS.md"""
        # Implementation in service layer
        pass

    @classmethod
    def from_markdown(cls, markdown: str) -> 'TodoItem':
        """Parse from markdown format"""
        # Implementation in service layer
        pass
```

**JSON Schema** (for validation):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "action", "why_matters", "problem", "current_state", "desired_state", "success_criteria"],
  "properties": {
    "id": {"type": "string", "pattern": "^todo-[0-9]{8}-[0-9]{6}$"},
    "action": {"type": "string", "minLength": 10, "maxLength": 200},
    "why_matters": {"type": "string", "minLength": 20},
    "problem": {"type": "string", "minLength": 20},
    "current_state": {"type": "string"},
    "desired_state": {"type": "string"},
    "success_criteria": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1
    },
    "files": {
      "type": "array",
      "items": {"type": "string", "pattern": ".*:\\d+(-\\d+)?"}
    },
    "priority": {"enum": ["high", "medium", "low"]},
    "complexity": {"enum": ["simple", "moderate", "complex"]},
    "status": {"enum": ["active", "in_progress", "completed", "archived"]}
  }
}
```

### 2. Handoff Model

**File**: `claude_force/models/handoff.py`

```python
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
    """Summary of session activities"""
    key_decisions: List[str] = field(default_factory=list)
    critical_insights: List[str] = field(default_factory=list)
    conversation_highlights: str = ""

@dataclass
class WorkflowProgress:
    """Workflow execution status"""
    workflow_name: str
    total_agents: int
    completed_agents: int
    current_phase: str
    agent_executions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class WorkCompleted:
    """Summary of completed work"""
    completed_items: List[str] = field(default_factory=list)
    files_modified: Dict[str, str] = field(default_factory=dict)  # path -> description
    agent_outputs: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class WorkRemaining:
    """Prioritized list of remaining work"""
    priority_1_critical: List[str] = field(default_factory=list)
    priority_2_high: List[str] = field(default_factory=list)
    priority_3_nice_to_have: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ActiveContext:
    """Most relevant context for next session"""
    most_relevant: List[str] = field(default_factory=list)
    known_blockers: List[Dict[str, str]] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)

@dataclass
class GovernanceStatus:
    """Quality and governance state"""
    validation_passed: bool
    scorecard_pass: int
    scorecard_total: int
    blockers: List[str] = field(default_factory=list)
    next_validation_checkpoint: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Session performance data"""
    total_cost: float
    execution_time_minutes: int
    agents_executed: int
    token_usage: int
    context_window_used_percent: float

@dataclass
class Handoff:
    """Complete session handoff for continuity"""

    # Metadata
    session_id: str
    started: datetime
    duration_minutes: int
    confidence_level: ConfidenceLevel
    resume_instructions: str

    # Original task
    original_task: str

    # Session summary
    session_summary: SessionSummary

    # Progress
    workflow_progress: Optional[WorkflowProgress] = None

    # Work status
    work_completed: WorkCompleted = field(default_factory=WorkCompleted)
    work_remaining: WorkRemaining = field(default_factory=WorkRemaining)

    # Context
    active_context: ActiveContext = field(default_factory=ActiveContext)
    technical_context: List[str] = field(default_factory=list)

    # Quality
    governance_status: GovernanceStatus = field(default_factory=lambda: GovernanceStatus(False, 0, 0))

    # Performance
    performance_metrics: PerformanceMetrics = field(default_factory=lambda: PerformanceMetrics(0.0, 0, 0, 0, 0.0))

    # Generation metadata
    generated_at: datetime = field(default_factory=datetime.now)

    def to_markdown(self) -> str:
        """Convert to markdown format for whats-next.md"""
        # Implementation in service layer
        pass

    @classmethod
    def from_markdown(cls, markdown: str) -> 'Handoff':
        """Parse from markdown format"""
        # Implementation in service layer
        pass
```

### 3. Meta-Prompt Models

**File**: `claude_force/models/meta_prompt.py`

```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class MetaPromptConstraints:
    """Constraints for meta-prompting"""
    governance_rules: List[str] = field(default_factory=list)
    available_resources: Dict[str, List[str]] = field(default_factory=dict)
    budget_limit: Optional[float] = None
    timeline: Optional[str] = None

@dataclass
class MetaPromptContext:
    """Context for meta-prompting"""
    current_state: str = ""
    previous_attempts: List[str] = field(default_factory=list)

@dataclass
class MetaPromptRequest:
    """Input for meta-prompting"""

    objective: str
    constraints: MetaPromptConstraints = field(default_factory=MetaPromptConstraints)
    context: MetaPromptContext = field(default_factory=MetaPromptContext)

    # Metadata
    requested_at: datetime = field(default_factory=datetime.now)
    request_id: str = ""

@dataclass
class ProposedApproach:
    """Meta-prompt's proposed approach"""
    workflow: str
    rationale: str
    alternatives_considered: List[str] = field(default_factory=list)

@dataclass
class GovernanceCompliance:
    """Governance validation result"""
    rules_applied: List[str] = field(default_factory=list)
    validation_status: bool = False
    violations: List[str] = field(default_factory=list)

@dataclass
class MetaPromptResponse:
    """Output from meta-prompting"""

    refined_objective: str
    reasoning: str
    proposed_approach: ProposedApproach
    governance_compliance: GovernanceCompliance
    success_criteria: List[str] = field(default_factory=list)
    risk_assessment: List[str] = field(default_factory=list)

    # Iteration tracking
    iteration: int = 1
    converging: bool = True

    # Metadata
    response_id: str = ""
    generated_at: datetime = field(default_factory=datetime.now)

@dataclass
class RefinementIteration:
    """Track iterative refinement"""
    iteration_number: int
    previous_attempt: str
    validation_failures: List[str]
    guidance: str
    refined_attempt: str
```

## Service Layer Architecture

### Service Layer Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Slash Commands (.md)                   │
│          /todos    /handoff    /meta-prompt             │
└──────────────────────┬──────────────────────────────────┘
                       │ (Claude interprets & calls)
┌──────────────────────▼──────────────────────────────────┐
│                   Service Layer                         │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │TodoManager   │ │Handoff       │ │MetaPrompter     │ │
│  │              │ │Generator     │ │                 │ │
│  └──────┬───────┘ └──────┬───────┘ └────────┬────────┘ │
│         │                │                   │          │
│  ┌──────▼────────────────▼───────────────────▼────────┐ │
│  │        Shared Services (Cache, Validator)          │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              AgentOrchestrator Integration              │
│  ┌───────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │Semantic   │ │Governance    │ │Performance       │  │
│  │Selector   │ │Manager       │ │Tracker           │  │
│  └───────────┘ └──────────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1. TodoManager Service

**File**: `claude_force/services/todo_manager.py`

```python
from typing import List, Optional, Dict
from pathlib import Path
from ..models.todo import TodoItem, Priority, TodoStatus
from ..response_cache import ResponseCache
from ..path_validator import PathValidator
from ..semantic_selector import SemanticAgentSelector

class TodoManager:
    """Manages todo items with AI-optimized operations"""

    def __init__(
        self,
        todo_path: str = ".claude/TO-DOS.md",
        cache: Optional[ResponseCache] = None,
        semantic_selector: Optional[SemanticAgentSelector] = None
    ):
        self.todo_path = Path(todo_path)
        self._cache = cache or ResponseCache()
        self._semantic_selector = semantic_selector
        self._validator = PathValidator(allowed_dirs=[".claude"])

    def add_todo(self, todo: TodoItem) -> None:
        """Add todo with validation and persistence"""
        # Validate todo
        self._validate_todo(todo)

        # Load existing todos
        todos = self.get_todos()

        # Check for duplicates
        similar = self._find_similar_todos(todo, todos)
        if similar:
            # Return similar todos for user decision
            return similar

        # Add new todo
        todos.append(todo)

        # Persist
        self._write_todos(todos)

        # Invalidate cache
        self._cache.delete(self._cache_key())

    def get_todos(
        self,
        filter_by: Optional[Dict] = None,
        include_archived: bool = False
    ) -> List[TodoItem]:
        """Retrieve todos with optional filtering and caching"""
        cache_key = self._cache_key()

        # Try cache first
        cached = self._cache.get(cache_key)
        if cached:
            todos = cached
        else:
            # Parse from file
            todos = self._parse_todos()

            # Cache with TTL
            self._cache.set(cache_key, todos, ttl=3600)

        # Filter
        if filter_by:
            todos = self._apply_filters(todos, filter_by)

        # Exclude archived by default
        if not include_archived:
            todos = [t for t in todos if t.status != TodoStatus.ARCHIVED]

        return todos

    def suggest_agent_for_todo(self, todo: TodoItem) -> Dict[str, float]:
        """Use SemanticSelector to recommend agent"""
        if not self._semantic_selector:
            return {}

        # Build query from todo
        query = f"{todo.action}. {todo.problem}. Required: {', '.join(todo.required_capabilities)}"

        # Get recommendations
        matches = self._semantic_selector.find_best_agent(query, top_k=3)

        return {match.agent_name: match.confidence for match in matches}

    def suggest_workflow_for_todo(self, todo: TodoItem) -> Optional[str]:
        """Suggest workflow based on todo complexity and capabilities"""
        # Simple heuristic-based workflow suggestion
        # Can be enhanced with ML later

        if todo.complexity == Complexity.SIMPLE:
            # Single agent likely sufficient
            return None

        # Check required capabilities
        caps = set(todo.required_capabilities)

        # Map capabilities to workflows
        # (This would be more sophisticated in production)
        if "frontend" in caps and "backend" in caps:
            return "full-stack-feature"
        elif "refactoring" in caps:
            return "refactoring-workflow"

        return None

    def complete_todo(self, todo_id: str) -> None:
        """Mark todo as completed"""
        todos = self.get_todos(include_archived=True)

        for todo in todos:
            if todo.id == todo_id:
                todo.status = TodoStatus.COMPLETED
                todo.completed = datetime.now()
                break

        self._write_todos(todos)
        self._cache.delete(self._cache_key())

    def archive_completed_todos(self) -> int:
        """Archive completed todos to separate file"""
        todos = self.get_todos(include_archived=True)

        completed = [t for t in todos if t.status == TodoStatus.COMPLETED]
        active = [t for t in todos if t.status != TodoStatus.COMPLETED]

        # Write archive
        if completed:
            self._write_archive(completed)

        # Write active
        self._write_todos(active)

        # Clear cache
        self._cache.delete(self._cache_key())

        return len(completed)

    # Private methods

    def _validate_todo(self, todo: TodoItem) -> None:
        """Validate todo against schema and rules"""
        # Validate required fields
        if not todo.action:
            raise ValueError("Todo action is required")

        if not todo.success_criteria:
            raise ValueError("At least one success criterion is required")

        # Validate file paths
        for file_path in todo.files:
            # Extract path without line numbers
            path = file_path.split(':')[0]
            self._validator.validate_path(path, base_dir=Path.cwd())

    def _find_similar_todos(self, todo: TodoItem, existing: List[TodoItem]) -> List[TodoItem]:
        """Find similar todos using simple text matching"""
        # Simple implementation - could use embeddings for better matching
        similar = []

        for existing_todo in existing:
            if existing_todo.status == TodoStatus.ARCHIVED:
                continue

            # Check for similar action
            if self._similarity_score(todo.action, existing_todo.action) > 0.7:
                similar.append(existing_todo)

        return similar

    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calculate simple similarity score"""
        # Very basic - just word overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        overlap = len(words1 & words2)
        total = len(words1 | words2)

        return overlap / total if total > 0 else 0.0

    def _cache_key(self) -> str:
        """Generate cache key based on file mtime"""
        if not self.todo_path.exists():
            return "todos:empty"

        mtime = self.todo_path.stat().st_mtime
        return f"todos:{mtime}"

    def _parse_todos(self) -> List[TodoItem]:
        """Parse todos from markdown file"""
        if not self.todo_path.exists():
            return []

        # Implementation will parse markdown format
        # Returns list of TodoItem objects
        pass

    def _write_todos(self, todos: List[TodoItem]) -> None:
        """Write todos to markdown file with file locking"""
        import fcntl

        self.todo_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.todo_path, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                content = self._serialize_todos(todos)
                f.write(content)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def _serialize_todos(self, todos: List[TodoItem]) -> str:
        """Serialize todos to markdown format"""
        # Implementation will generate markdown
        pass

    def _write_archive(self, todos: List[TodoItem]) -> None:
        """Write archived todos to dated archive file"""
        from datetime import datetime

        archive_dir = Path(".claude/archives/todos")
        archive_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        archive_file = archive_dir / f"todos-{date_str}.md"

        # Append to archive (don't overwrite)
        with open(archive_file, 'a') as f:
            content = self._serialize_todos(todos)
            f.write(f"\n\n# Archived {datetime.now().isoformat()}\n\n")
            f.write(content)
```

### 2. HandoffGenerator Service

**File**: `claude_force/services/handoff_generator.py`

```python
from typing import Optional
from pathlib import Path
from datetime import datetime
from ..models.handoff import Handoff, ConfidenceLevel
from ..orchestrator import AgentOrchestrator

class HandoffGenerator:
    """Generates session handoffs for continuity"""

    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator

    def generate_handoff(
        self,
        session_id: str,
        confidence_level: ConfidenceLevel = ConfidenceLevel.HIGH
    ) -> Handoff:
        """Generate structured handoff from current session"""

        # Extract session state from orchestrator
        session_state = self.orchestrator.get_session_state(session_id)

        # Extract workflow progress if in workflow
        workflow_progress = None
        if session_state.get('workflow_name'):
            workflow_progress = self._extract_workflow_progress(session_state)

        # Build handoff object
        handoff = Handoff(
            session_id=session_id,
            started=session_state['started'],
            duration_minutes=session_state['duration_minutes'],
            confidence_level=confidence_level,
            resume_instructions=self._generate_resume_instructions(session_state),
            original_task=session_state.get('original_task', ''),
            session_summary=self._build_session_summary(session_state),
            workflow_progress=workflow_progress,
            work_completed=self._build_work_completed(session_state),
            work_remaining=self._build_work_remaining(session_state),
            active_context=self._build_active_context(session_state),
            technical_context=session_state.get('technical_context', []),
            governance_status=self._build_governance_status(session_state),
            performance_metrics=self._build_performance_metrics(session_state)
        )

        return handoff

    def save_handoff(self, handoff: Handoff, output_path: Optional[Path] = None) -> Path:
        """Save handoff to file"""
        if output_path is None:
            # Default location
            handoff_dir = Path(".claude/handoffs")
            handoff_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            output_path = handoff_dir / f"handoff-{timestamp}.md"

        # Convert to markdown
        markdown = handoff.to_markdown()

        # Write file
        output_path.write_text(markdown)

        # Also write to whats-next.md for easy discovery
        whats_next = Path(".claude/whats-next.md")
        whats_next.write_text(markdown)

        return output_path

    # Private helper methods

    def _extract_workflow_progress(self, session_state: dict):
        """Extract workflow progress from session state"""
        # Implementation
        pass

    def _build_session_summary(self, session_state: dict):
        """Build session summary with key decisions"""
        # Implementation
        pass

    def _build_work_completed(self, session_state: dict):
        """Build work completed summary"""
        # Implementation
        pass

    def _build_work_remaining(self, session_state: dict):
        """Build prioritized work remaining"""
        # Implementation
        pass

    def _build_active_context(self, session_state: dict):
        """Build most relevant active context"""
        # Implementation
        pass

    def _build_governance_status(self, session_state: dict):
        """Extract governance status"""
        # Implementation
        pass

    def _build_performance_metrics(self, session_state: dict):
        """Extract performance metrics"""
        # Implementation
        pass

    def _generate_resume_instructions(self, session_state: dict) -> str:
        """Generate specific instructions for resuming"""
        # Implementation
        pass
```

### 3. MetaPrompter Service

**File**: `claude_force/services/meta_prompter.py`

```python
from typing import Optional, List
from ..models.meta_prompt import (
    MetaPromptRequest,
    MetaPromptResponse,
    RefinementIteration
)
from ..orchestrator import AgentOrchestrator

class MetaPrompter:
    """Meta-prompting service with governance integration"""

    MAX_ITERATIONS = 3

    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.governance = orchestrator.governance_manager

    def generate_workflow(
        self,
        request: MetaPromptRequest
    ) -> MetaPromptResponse:
        """Generate workflow with iterative refinement"""

        iterations: List[RefinementIteration] = []

        for iteration in range(1, self.MAX_ITERATIONS + 1):
            # Generate workflow proposal
            response = self._llm_generate_workflow(request, iterations)
            response.iteration = iteration

            # Validate against governance
            validation = self._validate_governance(response)

            if validation.validation_status:
                # Success!
                return response

            # Failed validation - prepare for retry
            if iteration < self.MAX_ITERATIONS:
                # Add refinement iteration
                refinement = RefinementIteration(
                    iteration_number=iteration,
                    previous_attempt=response.proposed_approach.workflow,
                    validation_failures=validation.violations,
                    guidance=self._generate_refinement_guidance(validation),
                    refined_attempt=""  # Will be filled in next iteration
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

        # If we get here, validation failed
        # Return response with governance violations
        return response

    def _llm_generate_workflow(
        self,
        request: MetaPromptRequest,
        previous_iterations: List[RefinementIteration]
    ) -> MetaPromptResponse:
        """Use LLM to generate workflow proposal"""

        # Build prompt for LLM
        prompt = self._build_meta_prompt(request, previous_iterations)

        # Call orchestrator to get LLM response
        # (This would use Claude to refine the prompt)
        result = self.orchestrator.call_llm_for_meta_prompting(prompt)

        # Parse response into MetaPromptResponse
        response = self._parse_llm_response(result)

        return response

    def _validate_governance(self, response: MetaPromptResponse) -> 'GovernanceCompliance':
        """Validate proposed workflow against governance rules"""

        violations = []

        # Check 1: Agent availability
        workflow = response.proposed_approach.workflow
        agents = self._extract_agents_from_workflow(workflow)

        for agent in agents:
            if not self.orchestrator.agent_exists(agent):
                violations.append(f"Agent '{agent}' does not exist")

        # Check 2: Budget compliance
        estimated_cost = self._estimate_workflow_cost(workflow)
        if response.proposed_approach.budget_limit and estimated_cost > response.proposed_approach.budget_limit:
            violations.append(f"Estimated cost ${estimated_cost} exceeds budget ${response.proposed_approach.budget_limit}")

        # Check 3: Skill requirements
        required_skills = self._extract_required_skills(workflow)
        available_skills = self.orchestrator.get_available_skills()

        missing_skills = set(required_skills) - set(available_skills)
        if missing_skills:
            violations.append(f"Missing required skills: {', '.join(missing_skills)}")

        # Check 4: Safety checks (from governance manager)
        if hasattr(self.governance, 'validate_workflow'):
            gov_result = self.governance.validate_workflow(workflow)
            if not gov_result.passed:
                violations.extend(gov_result.failures)

        return GovernanceCompliance(
            rules_applied=[
                "agent_availability",
                "budget_compliance",
                "skill_requirements",
                "safety_checks"
            ],
            validation_status=len(violations) == 0,
            violations=violations
        )

    def _generate_refinement_guidance(self, validation: 'GovernanceCompliance') -> str:
        """Generate guidance for next refinement iteration"""
        guidance_parts = []

        for violation in validation.violations:
            if "does not exist" in violation:
                guidance_parts.append(f"Fix: {violation}. Use only available agents.")
            elif "exceeds budget" in violation:
                guidance_parts.append(f"Fix: {violation}. Reduce workflow scope or use cheaper models.")
            elif "Missing required skills" in violation:
                guidance_parts.append(f"Fix: {violation}. Remove dependencies or suggest skill installation.")
            else:
                guidance_parts.append(f"Fix: {violation}")

        return "\n".join(guidance_parts)

    def _is_converging(self, iterations: List[RefinementIteration]) -> bool:
        """Check if iterations are converging toward valid solution"""
        if len(iterations) < 2:
            return True

        # Simple heuristic: check if number of violations is decreasing
        # More sophisticated: check if same violations repeating

        return True  # Simplified for now

    def _build_meta_prompt(
        self,
        request: MetaPromptRequest,
        previous_iterations: List[RefinementIteration]
    ) -> str:
        """Build prompt for LLM meta-prompting"""
        # Implementation would create structured prompt
        pass

    def _parse_llm_response(self, llm_result: str) -> MetaPromptResponse:
        """Parse LLM response into structured format"""
        # Implementation would parse XML/structured output
        pass

    def _extract_agents_from_workflow(self, workflow: str) -> List[str]:
        """Extract agent names from workflow description"""
        # Implementation
        pass

    def _estimate_workflow_cost(self, workflow: str) -> float:
        """Estimate cost of proposed workflow"""
        # Implementation using cost estimation
        pass

    def _extract_required_skills(self, workflow: str) -> List[str]:
        """Extract required skills from workflow"""
        # Implementation
        pass
```

## File Structure and Organization

```
claude_force/
├── models/
│   ├── __init__.py
│   ├── todo.py              # TodoItem, Priority, Complexity, TodoStatus
│   └── handoff.py           # Handoff, SessionSummary, WorkflowProgress, etc.
│   └── meta_prompt.py       # MetaPromptRequest, MetaPromptResponse, etc.
│
├── services/
│   ├── __init__.py
│   ├── todo_manager.py      # TodoManager service
│   ├── handoff_generator.py # HandoffGenerator service
│   └── meta_prompter.py     # MetaPrompter service
│
└── (existing files...)

.claude/
├── commands/
│   ├── todos.md             # Consolidated todo command
│   ├── handoff.md           # Handoff generation command
│   └── meta-prompt.md       # Meta-prompting command
│
├── TO-DOS.md                # Active todos
├── whats-next.md            # Latest handoff
├── handoffs/                # Handoff archive
│   └── handoff-YYYY-MM-DD-HHMMSS.md
└── archives/
    └── todos/               # Archived todos
        └── todos-YYYY-MM-DD.md
```

## Integration with Existing Components

### 1. AgentOrchestrator Extensions

Add to `claude_force/orchestrator.py`:

```python
class AgentOrchestrator:
    # ... existing code ...

    def __init__(self, ...):
        # ... existing init ...

        # New: Add todo manager and handoff generator
        self.todo_manager = None  # Lazy init
        self.handoff_generator = None  # Lazy init
        self.meta_prompter = None  # Lazy init

    @property
    def todos(self) -> TodoManager:
        """Lazy-loaded TodoManager"""
        if self.todo_manager is None:
            from .services.todo_manager import TodoManager
            self.todo_manager = TodoManager(
                cache=self.response_cache,
                semantic_selector=self.semantic_selector
            )
        return self.todo_manager

    @property
    def handoffs(self) -> HandoffGenerator:
        """Lazy-loaded HandoffGenerator"""
        if self.handoff_generator is None:
            from .services.handoff_generator import HandoffGenerator
            self.handoff_generator = HandoffGenerator(self)
        return self.handoff_generator

    @property
    def meta_prompt(self) -> MetaPrompter:
        """Lazy-loaded MetaPrompter"""
        if self.meta_prompter is None:
            from .services.meta_prompter import MetaPrompter
            self.meta_prompter = MetaPrompter(self)
        return self.meta_prompter

    def get_session_state(self, session_id: str) -> dict:
        """Get current session state for handoff generation"""
        # Implementation to extract current session data
        pass

    def call_llm_for_meta_prompting(self, prompt: str) -> str:
        """Call LLM for meta-prompting"""
        # Implementation
        pass
```

### 2. CLI Integration

Add to `claude_force/cli.py`:

```python
# New command group for workflow management
@click.group()
def workflow():
    """Workflow management commands"""
    pass

@workflow.command()
@click.option('--add', help='Add new todo')
@click.option('--complete', type=int, help='Complete todo by number')
@click.option('--clear', is_flag=True, help='Archive completed todos')
def todos(add, complete, clear):
    """Manage todos"""
    orchestrator = get_orchestrator()

    if add:
        # Add todo flow
        pass
    elif complete:
        # Complete todo
        pass
    elif clear:
        # Archive completed
        pass
    else:
        # List todos
        pass

@workflow.command()
@click.option('--save', help='Custom save location')
def handoff(save):
    """Generate session handoff"""
    orchestrator = get_orchestrator()
    # Generate handoff
    pass

@workflow.command()
@click.argument('goal')
def meta_prompt(goal):
    """Meta-prompt for workflow generation"""
    orchestrator = get_orchestrator()
    # Meta-prompting flow
    pass
```

## Next Steps

1. Review this architecture document
2. Get approval from stakeholders
3. Begin Week 1 implementation:
   - Day 1-2: Implement data models
   - Day 3-4: Implement TodoManager service
   - Day 5: Implement /todos command

---

**Status**: Ready for review and implementation
**Next Document**: Command specifications and documentation drafts

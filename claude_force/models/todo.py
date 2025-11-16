"""
Todo item data model for AI-optimized task capture.

Based on expert review recommendations:
- Success criteria instead of just descriptions
- Required capabilities instead of prescriptive agent assignments
- Dependency tracking for complex workflows
- AI-friendly structured format
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class Priority(Enum):
    """Todo priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Complexity(Enum):
    """Estimated complexity for resource planning"""
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
    """
    Represents a single todo item with AI-optimized fields.

    This model follows the expert-recommended format:
    - Clear success criteria for AI to validate completion
    - "Why this matters" for context understanding
    - Current vs desired state for problem clarity
    - Required capabilities (not agents) for flexibility
    - Dependency tracking for workflow management
    """

    # Core fields
    id: str = field(default_factory=lambda: f"todo-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}")
    action: str = ""  # Action verb + high-level objective
    why_matters: str = ""  # Context/rationale for this todo

    # Problem definition
    problem: str = ""  # Issue description with user/system impact
    current_state: str = ""  # What happens now
    desired_state: str = ""  # What should happen

    # Success criteria (CRITICAL for AI validation)
    success_criteria: List[str] = field(default_factory=list)  # Specific measurable outcomes

    # File references with line numbers
    files: List[str] = field(default_factory=list)  # Format: path/to/file.py:123-145

    # Solution approach (optional - not prescriptive)
    solution_approach: Optional[str] = None

    # Required capabilities (not agents - more flexible)
    required_capabilities: List[str] = field(default_factory=list)

    # Suggested resources (optional recommendations)
    suggested_agents: List[str] = field(default_factory=list)
    suggested_workflows: List[str] = field(default_factory=list)

    # Dependencies for workflow management
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
        """
        Convert to markdown format for TO-DOS.md.

        Format follows expert recommendation for AI-optimized structure:
        ```markdown
        ### [ACTION] - [High-Level Objective]

        **Why This Matters:** [Context]

        **Success Criteria:**
        - [ ] [Criterion 1]
        - [ ] [Criterion 2]

        **Problem:** [Description]

        **Current State:**
        - **Files:** [paths:lines]
        - **Current Behavior:** [what happens now]
        - **Desired Behavior:** [what should happen]

        **Solution Approach:** [optional]

        **Required Capabilities:**
        - [Cap 1]
        - [Cap 2]

        **Suggested Resources:**
        - **Agents:** [agent-names]
        - **Workflows:** [workflow-names]

        **Dependencies:**
        - Depends on: [todo IDs]
        - Blocks: [what this blocks]

        **Metadata:**
        - Priority: [high/medium/low]
        - Complexity: [simple/moderate/complex]
        - Estimated Cost: [$X.XX]
        - Added: [timestamp]
        - Tags: [#tag1, #tag2]
        ```
        """
        lines = []

        # Header
        lines.append(f"### {self.action}")
        lines.append("")

        # Why this matters
        lines.append(f"**Why This Matters:** {self.why_matters}")
        lines.append("")

        # Success criteria
        lines.append("**Success Criteria:**")
        for criterion in self.success_criteria:
            status = "x" if self.status == TodoStatus.COMPLETED else " "
            lines.append(f"- [{status}] {criterion}")
        lines.append("")

        # Problem
        lines.append(f"**Problem:** {self.problem}")
        lines.append("")

        # Current state
        lines.append("**Current State:**")
        if self.files:
            lines.append(f"- **Files:** {', '.join(self.files)}")
        lines.append(f"- **Current Behavior:** {self.current_state}")
        lines.append(f"- **Desired Behavior:** {self.desired_state}")
        lines.append("")

        # Solution approach (optional)
        if self.solution_approach:
            lines.append(f"**Solution Approach:** {self.solution_approach}")
            lines.append("")

        # Required capabilities
        if self.required_capabilities:
            lines.append("**Required Capabilities:**")
            for cap in self.required_capabilities:
                lines.append(f"- {cap}")
            lines.append("")

        # Suggested resources
        if self.suggested_agents or self.suggested_workflows:
            lines.append("**Suggested Resources:**")
            if self.suggested_agents:
                lines.append(f"- **Agents:** {', '.join(self.suggested_agents)}")
            if self.suggested_workflows:
                lines.append(f"- **Workflows:** {', '.join(self.suggested_workflows)}")
            lines.append("")

        # Dependencies
        if self.depends_on or self.blocks:
            lines.append("**Dependencies:**")
            if self.depends_on:
                lines.append(f"- Depends on: {', '.join(self.depends_on)}")
            if self.blocks:
                lines.append(f"- Blocks: {', '.join(self.blocks)}")
            lines.append("")

        # Metadata
        lines.append("**Metadata:**")
        lines.append(f"- **ID:** `{self.id}`")
        lines.append(f"- **Priority:** {self.priority.value}")
        lines.append(f"- **Complexity:** {self.complexity.value}")
        lines.append(f"- **Status:** {self.status.value}")
        if self.estimated_cost is not None:
            lines.append(f"- **Estimated Cost:** ${self.estimated_cost:.2f}")
        lines.append(f"- **Added:** {self.added.isoformat()}")
        if self.completed:
            lines.append(f"- **Completed:** {self.completed.isoformat()}")
        if self.tags:
            tags_str = ", ".join(f"#{tag}" for tag in self.tags)
            lines.append(f"- **Tags:** {tags_str}")
        lines.append("")

        return "\n".join(lines)

    @classmethod
    def from_markdown(cls, markdown: str, section_id: Optional[str] = None) -> 'TodoItem':
        """
        Parse TodoItem from markdown format.

        Args:
            markdown: Markdown text for a single todo section
            section_id: Optional ID to use (extracted from metadata if present)

        Returns:
            TodoItem instance
        """
        todo = cls()

        lines = markdown.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()

            # Parse header
            if line.startswith("### "):
                todo.action = line[4:].strip()
                continue

            # Parse sections
            if line.startswith("**Why This Matters:**"):
                todo.why_matters = line.split(":", 1)[1].strip()
                current_section = None
            elif line.startswith("**Success Criteria:**"):
                current_section = "success_criteria"
            elif line.startswith("**Problem:**"):
                todo.problem = line.split(":", 1)[1].strip()
                current_section = None
            elif line.startswith("**Current State:**"):
                current_section = "current_state"
            elif line.startswith("**Solution Approach:**"):
                todo.solution_approach = line.split(":", 1)[1].strip()
                current_section = None
            elif line.startswith("**Required Capabilities:**"):
                current_section = "required_capabilities"
            elif line.startswith("**Suggested Resources:**"):
                current_section = "suggested_resources"
            elif line.startswith("**Dependencies:**"):
                current_section = "dependencies"
            elif line.startswith("**Metadata:**"):
                current_section = "metadata"
            # Parse content based on current section
            elif current_section == "success_criteria" and line.startswith("- ["):
                # Extract criterion (remove checkbox)
                criterion = line[6:].strip()  # Skip "- [ ] " or "- [x] "
                todo.success_criteria.append(criterion)
            elif current_section == "current_state":
                if line.startswith("- **Files:**"):
                    files_str = line.split(":", 1)[1].strip()
                    todo.files = [f.strip() for f in files_str.split(",")]
                elif line.startswith("- **Current Behavior:**"):
                    todo.current_state = line.split(":", 1)[1].strip()
                elif line.startswith("- **Desired Behavior:**"):
                    todo.desired_state = line.split(":", 1)[1].strip()
            elif current_section == "required_capabilities" and line.startswith("- "):
                todo.required_capabilities.append(line[2:].strip())
            elif current_section == "suggested_resources":
                if line.startswith("- **Agents:**"):
                    agents_str = line.split(":", 1)[1].strip()
                    todo.suggested_agents = [a.strip() for a in agents_str.split(",")]
                elif line.startswith("- **Workflows:**"):
                    workflows_str = line.split(":", 1)[1].strip()
                    todo.suggested_workflows = [w.strip() for w in workflows_str.split(",")]
            elif current_section == "dependencies":
                if line.startswith("- Depends on:"):
                    deps_str = line.split(":", 1)[1].strip()
                    todo.depends_on = [d.strip() for d in deps_str.split(",")]
                elif line.startswith("- Blocks:"):
                    blocks_str = line.split(":", 1)[1].strip()
                    todo.blocks = [b.strip() for b in blocks_str.split(",")]
            elif current_section == "metadata":
                if line.startswith("- **ID:**"):
                    todo.id = line.split("`")[1]  # Extract from backticks
                elif line.startswith("- **Priority:**"):
                    priority_str = line.split(":")[1].strip()
                    todo.priority = Priority(priority_str)
                elif line.startswith("- **Complexity:**"):
                    complexity_str = line.split(":")[1].strip()
                    todo.complexity = Complexity(complexity_str)
                elif line.startswith("- **Status:**"):
                    status_str = line.split(":")[1].strip()
                    todo.status = TodoStatus(status_str)
                elif line.startswith("- **Estimated Cost:**"):
                    cost_str = line.split("$")[1].strip()
                    todo.estimated_cost = float(cost_str)
                elif line.startswith("- **Added:**"):
                    date_str = line.split(":", 1)[1].strip()
                    todo.added = datetime.fromisoformat(date_str)
                elif line.startswith("- **Completed:**"):
                    date_str = line.split(":", 1)[1].strip()
                    todo.completed = datetime.fromisoformat(date_str)
                elif line.startswith("- **Tags:**"):
                    tags_str = line.split(":", 1)[1].strip()
                    todo.tags = [t.strip().lstrip("#") for t in tags_str.split(",")]

        # Validate required fields
        if not todo.action or not todo.action.strip():
            raise ValueError("Todo action is required and cannot be empty")

        # Validate files (security check for path traversal)
        if todo.files:
            for file_path in todo.files:
                if file_path and (".." in file_path or file_path.startswith("/")):
                    raise ValueError(
                        f"Invalid file path '{file_path}': "
                        "absolute paths and parent directory references are not allowed"
                    )

        return todo

    def __repr__(self) -> str:
        return f"TodoItem(id='{self.id}', action='{self.action[:50]}...', priority={self.priority.value}, status={self.status.value})"

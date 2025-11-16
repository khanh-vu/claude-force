"""
TodoManager service for AI-optimized task capture and management.

Provides:
- Todo CRUD operations with validation
- Markdown serialization/deserialization
- Agent and workflow recommendations
- Duplicate detection
- Performance-optimized with caching
- File locking for concurrent access
"""

from typing import List, Optional, Dict, Tuple, TYPE_CHECKING
from pathlib import Path
from datetime import datetime
import fcntl
import re

if TYPE_CHECKING:
    from claude_force.semantic_selector import SemanticAgentSelector

from ..models.todo import TodoItem, Priority, Complexity, TodoStatus
from ..response_cache import ResponseCache
from ..path_validator import PathValidator


class TodoManager:
    """
    Manages todo items with AI-optimized operations.

    Features:
    - Automatic agent recommendations via SemanticSelector
    - Duplicate detection with similarity scoring
    - Cached reads for performance
    - Atomic writes with file locking
    - Archive management for completed todos
    """

    def __init__(
        self,
        todo_path: str = ".claude/TO-DOS.md",
        cache: Optional[ResponseCache] = None,
        semantic_selector: Optional["SemanticAgentSelector"] = None,
    ):
        self.todo_path = Path(todo_path)
        self._cache = cache or ResponseCache()
        self._semantic_selector = semantic_selector
        self._validator = PathValidator(
            allowed_dirs=[".claude", "src", "tests", "docs"]
        )

    def add_todo(
        self, todo: TodoItem, check_duplicates: bool = True
    ) -> Tuple[bool, Optional[List[TodoItem]]]:
        """
        Add todo with validation and duplicate checking.

        Args:
            todo: TodoItem to add
            check_duplicates: Whether to check for similar todos

        Returns:
            Tuple of (success, similar_todos)
            - If success=True, todo was added, similar_todos=None
            - If success=False, similar todos found, user should decide
        """
        # Validate todo
        self._validate_todo(todo)

        # Load existing todos
        todos = self.get_todos(include_archived=False)

        # Check for duplicates if requested
        if check_duplicates:
            similar = self._find_similar_todos(todo, todos)
            if similar:
                return (False, similar)

        # Suggest agent and workflow
        if self._semantic_selector:
            suggestions = self.suggest_agent_for_todo(todo)
            if suggestions:
                # Take top 3 suggestions
                todo.suggested_agents = list(suggestions.keys())[:3]

        workflow = self.suggest_workflow_for_todo(todo)
        if workflow:
            todo.suggested_workflows = [workflow]

        # Add new todo
        todos.append(todo)

        # Persist
        self._write_todos(todos)

        # Invalidate cache
        self._invalidate_cache()

        return (True, None)

    def get_todos(
        self, filter_by: Optional[Dict] = None, include_archived: bool = False
    ) -> List[TodoItem]:
        """
        Retrieve todos with optional filtering and caching.

        Args:
            filter_by: Optional filters (e.g., {'priority': 'high', 'status': 'active'})
            include_archived: Whether to include archived todos

        Returns:
            List of TodoItem objects
        """
        cache_key = self._cache_key()

        # Try cache first
        cached = self._cache.get(cache_key)
        if cached:
            todos = cached
        else:
            # Parse from file
            todos = self._parse_todos()

            # Cache with 1 hour TTL
            self._cache.set(cache_key, todos, ttl=3600)

        # Filter
        if filter_by:
            todos = self._apply_filters(todos, filter_by)

        # Exclude archived by default
        if not include_archived:
            todos = [t for t in todos if t.status != TodoStatus.ARCHIVED]

        return todos

    def get_todo_by_id(self, todo_id: str) -> Optional[TodoItem]:
        """Get a specific todo by ID"""
        todos = self.get_todos(include_archived=True)
        for todo in todos:
            if todo.id == todo_id:
                return todo
        return None

    def update_todo(self, todo: TodoItem) -> bool:
        """
        Update an existing todo.

        Args:
            todo: TodoItem with updated fields

        Returns:
            True if updated, False if not found
        """
        todos = self.get_todos(include_archived=True)

        for i, existing_todo in enumerate(todos):
            if existing_todo.id == todo.id:
                todos[i] = todo
                self._write_todos(todos)
                self._invalidate_cache()
                return True

        return False

    def suggest_agent_for_todo(self, todo: TodoItem) -> Dict[str, float]:
        """
        Use SemanticSelector to recommend agents.

        Args:
            todo: TodoItem to analyze

        Returns:
            Dict mapping agent names to confidence scores
        """
        if not self._semantic_selector:
            return {}

        # Build query from todo
        query_parts = [
            todo.action,
            todo.problem,
            f"Required capabilities: {', '.join(todo.required_capabilities)}"
            if todo.required_capabilities
            else "",
        ]
        query = ". ".join(filter(None, query_parts))

        # Get recommendations
        try:
            matches = self._semantic_selector.find_best_agent(query, top_k=5)
            return {match.agent_name: match.confidence for match in matches}
        except Exception as e:
            # If semantic selector fails, return empty
            import logging

            logging.getLogger(__name__).warning(
                f"Semantic agent selection failed for query '{query}': {e}"
            )
            return {}

    def suggest_workflow_for_todo(self, todo: TodoItem) -> Optional[str]:
        """
        Suggest workflow based on todo complexity and capabilities.

        Args:
            todo: TodoItem to analyze

        Returns:
            Workflow name or None
        """
        # Simple heuristic-based workflow suggestion
        # Can be enhanced with ML later

        if todo.complexity == Complexity.SIMPLE:
            # Single agent likely sufficient
            return None

        # Check required capabilities
        caps = set(todo.required_capabilities)

        # Map capabilities to workflows
        if {"frontend", "backend"} & caps:
            return "full-stack-feature"
        elif {"refactoring"} & caps:
            return "refactoring-workflow"
        elif {"bug", "investigation"} & caps:
            return "bug-investigation"
        elif {"documentation"} & caps:
            return "documentation-suite"

        return None

    def complete_todo(self, todo_id: str) -> bool:
        """
        Mark todo as completed.

        Args:
            todo_id: ID of todo to complete

        Returns:
            True if completed, False if not found
        """
        todos = self.get_todos(include_archived=True)

        for todo in todos:
            if todo.id == todo_id:
                todo.status = TodoStatus.COMPLETED
                todo.completed = datetime.now()
                self._write_todos(todos)
                self._invalidate_cache()
                return True

        return False

    def delete_todo(self, todo_id: str) -> bool:
        """
        Delete a todo (permanently remove).

        Args:
            todo_id: ID of todo to delete

        Returns:
            True if deleted, False if not found
        """
        todos = self.get_todos(include_archived=True)
        original_count = len(todos)

        todos = [t for t in todos if t.id != todo_id]

        if len(todos) < original_count:
            self._write_todos(todos)
            self._invalidate_cache()
            return True

        return False

    def archive_completed_todos(self) -> int:
        """
        Archive completed todos to separate file.

        Returns:
            Number of todos archived
        """
        todos = self.get_todos(include_archived=True)

        completed = [t for t in todos if t.status == TodoStatus.COMPLETED]
        active = [t for t in todos if t.status != TodoStatus.COMPLETED]

        # Write archive
        if completed:
            self._write_archive(completed)

        # Update active todos
        self._write_todos(active)

        # Clear cache
        self._invalidate_cache()

        return len(completed)

    # Private methods

    def _validate_todo(self, todo: TodoItem) -> None:
        """
        Validate todo against schema and rules.

        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        if not todo.action:
            raise ValueError("Todo action is required")

        if not todo.success_criteria:
            raise ValueError("At least one success criterion is required")

        if not todo.problem:
            raise ValueError("Problem description is required")

        # Validate file paths
        for file_path in todo.files:
            # Extract path without line numbers
            path = file_path.split(":")[0]
            try:
                self._validator.validate_path(path, base_dir=Path.cwd())
            except Exception as e:
                raise ValueError(f"Invalid file path '{path}': {e}")

    def _find_similar_todos(
        self, todo: TodoItem, existing: List[TodoItem]
    ) -> List[TodoItem]:
        """
        Find similar todos using text similarity.

        Args:
            todo: New todo to compare
            existing: List of existing todos

        Returns:
            List of similar todos (similarity > 0.7)
        """
        similar = []

        for existing_todo in existing:
            if existing_todo.status == TodoStatus.ARCHIVED:
                continue

            # Check for similar action
            similarity = self._similarity_score(todo.action, existing_todo.action)
            if similarity > 0.7:
                similar.append(existing_todo)

        return similar

    def _similarity_score(self, text1: str, text2: str) -> float:
        """
        Calculate simple similarity score using word overlap.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize texts
        words1 = set(re.findall(r"\w+", text1.lower()))
        words2 = set(re.findall(r"\w+", text2.lower()))

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        overlap = len(words1 & words2)
        total = len(words1 | words2)

        return overlap / total if total > 0 else 0.0

    def _apply_filters(self, todos: List[TodoItem], filters: Dict) -> List[TodoItem]:
        """
        Apply filters to todo list.

        Args:
            todos: List of todos to filter
            filters: Dict of filter conditions

        Returns:
            Filtered list of todos
        """
        filtered = todos

        if "priority" in filters:
            priority = Priority(filters["priority"])
            filtered = [t for t in filtered if t.priority == priority]

        if "status" in filters:
            status = TodoStatus(filters["status"])
            filtered = [t for t in filtered if t.status == status]

        if "complexity" in filters:
            complexity = Complexity(filters["complexity"])
            filtered = [t for t in filtered if t.complexity == complexity]

        if "tags" in filters:
            required_tags = set(filters["tags"])
            filtered = [t for t in filtered if required_tags & set(t.tags)]

        return filtered

    def _cache_key(self) -> str:
        """
        Generate cache key based on file hash for reliable invalidation.

        Returns:
            Cache key string

        Note:
            Uses file size + mtime + content hash to detect changes
            even when modifications happen within the same second.
        """
        if not self.todo_path.exists():
            return "todos:empty"

        import hashlib

        stat = self.todo_path.stat()

        # Combine multiple indicators for better cache key uniqueness
        # Size changes = definitely modified
        # mtime changes = likely modified
        # Content hash (first 100 bytes) = catch same-second modifications
        try:
            with open(self.todo_path, "rb") as f:
                # Hash first 100 bytes for quick check
                sample = f.read(100)
                content_hash = hashlib.md5(sample).hexdigest()[:8]
        except Exception:
            content_hash = "none"

        return f"todos:{stat.st_size}:{int(stat.st_mtime)}:{content_hash}"

    def _invalidate_cache(self) -> None:
        """
        Invalidate cached todos.

        Note:
            Attempts to delete the current cache key. Due to hash-based
            keys, rapid successive writes are automatically handled.
        """
        if self.todo_path.exists():
            cache_key = self._cache_key()
            self._cache.delete(cache_key)

    def _parse_todos(self) -> List[TodoItem]:
        """
        Parse todos from markdown file.

        Returns:
            List of TodoItem objects
        """
        if not self.todo_path.exists():
            return []

        content = self.todo_path.read_text()

        # Split by todo sections (### headers)
        sections = re.split(r"\n### ", content)

        todos = []
        for section in sections:
            if not section.strip():
                continue

            # Add back the ### prefix
            if not section.startswith("###"):
                section = "### " + section

            try:
                todo = TodoItem.from_markdown(section)
                todos.append(todo)
            except Exception as e:
                # Skip malformed sections
                import logging

                logging.getLogger(__name__).debug(
                    f"Skipping malformed todo section: {e}"
                )
                continue

        return todos

    def _write_todos(self, todos: List[TodoItem]) -> None:
        """
        Write todos to markdown file with file locking.

        Args:
            todos: List of TodoItem objects to write
        """
        self.todo_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.todo_path, "w") as f:
            # Acquire exclusive lock
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                content = self._serialize_todos(todos)
                f.write(content)
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def _serialize_todos(self, todos: List[TodoItem]) -> str:
        """
        Serialize todos to markdown format.

        Args:
            todos: List of TodoItem objects

        Returns:
            Markdown string
        """
        lines = []

        # Header
        lines.append("# Active Todos")
        lines.append("")
        lines.append(
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append(f"**Total**: {len(todos)} todos")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Group by priority
        high_priority = [
            t
            for t in todos
            if t.priority == Priority.HIGH and t.status == TodoStatus.ACTIVE
        ]
        medium_priority = [
            t
            for t in todos
            if t.priority == Priority.MEDIUM and t.status == TodoStatus.ACTIVE
        ]
        low_priority = [
            t
            for t in todos
            if t.priority == Priority.LOW and t.status == TodoStatus.ACTIVE
        ]
        in_progress = [t for t in todos if t.status == TodoStatus.IN_PROGRESS]
        completed = [t for t in todos if t.status == TodoStatus.COMPLETED]

        # In Progress section
        if in_progress:
            lines.append("## 🔄 In Progress")
            lines.append("")
            for todo in in_progress:
                lines.append(todo.to_markdown())
                lines.append("---")
                lines.append("")

        # High Priority
        if high_priority:
            lines.append("## 🔴 High Priority")
            lines.append("")
            for todo in high_priority:
                lines.append(todo.to_markdown())
                lines.append("---")
                lines.append("")

        # Medium Priority
        if medium_priority:
            lines.append("## 🟡 Medium Priority")
            lines.append("")
            for todo in medium_priority:
                lines.append(todo.to_markdown())
                lines.append("---")
                lines.append("")

        # Low Priority
        if low_priority:
            lines.append("## 🟢 Low Priority")
            lines.append("")
            for todo in low_priority:
                lines.append(todo.to_markdown())
                lines.append("---")
                lines.append("")

        # Completed (for reference)
        if completed:
            lines.append("## ✅ Recently Completed")
            lines.append("")
            for todo in completed[:5]:  # Show last 5 completed
                lines.append(todo.to_markdown())
                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def _write_archive(self, todos: List[TodoItem]) -> None:
        """
        Write archived todos to dated archive file.

        Args:
            todos: List of completed TodoItem objects to archive
        """
        archive_dir = Path(".claude/archives/todos")
        archive_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        archive_file = archive_dir / f"todos-{date_str}.md"

        # Build archive content
        lines = []
        lines.append(
            f"# Archived Todos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        lines.append("")
        lines.append(f"**Count**: {len(todos)} todos")
        lines.append("")
        lines.append("---")
        lines.append("")

        for todo in todos:
            lines.append(todo.to_markdown())
            lines.append("---")
            lines.append("")

        content = "\n".join(lines)

        # Append to archive (don't overwrite) with file locking for concurrent access
        with open(archive_file, "a") as f:
            # Acquire exclusive lock to prevent race conditions
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                # Check size after acquiring lock (not before)
                f.seek(0, 2)  # Seek to end
                if f.tell() > 0:  # Check current position (file size)
                    f.write("\n\n")
                f.write(content)
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

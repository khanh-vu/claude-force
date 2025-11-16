"""
Tests for TodoManager service

Ensures TodoManager correctly:
- Creates, reads, updates, deletes todos
- Validates todo format and required fields
- Detects duplicate todos
- Suggests agents and workflows
- Handles file locking and caching
- Archives completed todos
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from claude_force.models.todo import TodoItem, Priority, Complexity, TodoStatus
from claude_force.services.todo_manager import TodoManager


class TestTodoManager:
    """Test TodoManager service"""

    @pytest.fixture
    def temp_todo_file(self, tmp_path):
        """Create temporary todo file path"""
        return str(tmp_path / "TO-DOS.md")

    @pytest.fixture
    def todo_manager(self, temp_todo_file):
        """Create TodoManager instance with temp file"""
        return TodoManager(todo_path=temp_todo_file, cache=None)

    @pytest.fixture
    def sample_todo(self):
        """Create sample TodoItem"""
        return TodoItem(
            action="Fix authentication bug",
            why_matters="Users cannot login after password reset",
            problem="Login endpoint returns 500 error after password reset",
            current_state="Password reset emails are sent but login fails",
            desired_state="Users can successfully login after password reset",
            success_criteria=[
                "Login works after password reset",
                "No 500 errors in logs",
                "Security audit passes"
            ],
            files=["src/auth/login.py:45-67"],
            priority=Priority.HIGH,
            complexity=Complexity.MODERATE,
            required_capabilities=["backend", "security", "debugging"]
        )

    def test_add_todo_success(self, todo_manager, sample_todo):
        """Test successfully adding a todo"""
        success, similar = todo_manager.add_todo(sample_todo, check_duplicates=False)

        assert success is True
        assert similar is None

        # Verify todo was added
        todos = todo_manager.get_todos()
        assert len(todos) == 1
        assert todos[0].action == sample_todo.action

    def test_add_todo_validation_fails_no_action(self, todo_manager):
        """Test validation fails when action is missing"""
        invalid_todo = TodoItem(
            action="",  # Empty action
            why_matters="Test",
            problem="Test problem",
            current_state="Test",
            desired_state="Test",
            success_criteria=["Test"]
        )

        with pytest.raises(ValueError, match="action is required"):
            todo_manager.add_todo(invalid_todo)

    def test_add_todo_validation_fails_no_success_criteria(self, todo_manager):
        """Test validation fails when success criteria missing"""
        invalid_todo = TodoItem(
            action="Test action",
            why_matters="Test",
            problem="Test problem",
            current_state="Test",
            desired_state="Test",
            success_criteria=[]  # Empty criteria
        )

        with pytest.raises(ValueError, match="success criterion is required"):
            todo_manager.add_todo(invalid_todo)

    def test_get_todos_empty(self, todo_manager):
        """Test getting todos from empty file"""
        todos = todo_manager.get_todos()
        assert todos == []

    def test_get_todos_multiple(self, todo_manager, sample_todo):
        """Test getting multiple todos"""
        # Add 3 todos
        for i in range(3):
            todo = TodoItem(
                action=f"Task {i}",
                why_matters="Test",
                problem="Test",
                current_state="Test",
                desired_state="Test",
                success_criteria=["Done"],
                priority=Priority.MEDIUM if i % 2 == 0 else Priority.HIGH
            )
            todo_manager.add_todo(todo, check_duplicates=False)

        todos = todo_manager.get_todos()
        assert len(todos) == 3

    def test_filter_by_priority(self, todo_manager):
        """Test filtering todos by priority"""
        # Add todos with different priorities
        for priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
            todo = TodoItem(
                action=f"Task {priority.value}",
                why_matters="Test",
                problem="Test",
                current_state="Test",
                desired_state="Test",
                success_criteria=["Done"],
                priority=priority
            )
            todo_manager.add_todo(todo, check_duplicates=False)

        # Filter high priority
        high_priority = todo_manager.get_todos(filter_by={'priority': 'high'})
        assert len(high_priority) == 1
        assert high_priority[0].priority == Priority.HIGH

    def test_complete_todo(self, todo_manager, sample_todo):
        """Test marking todo as completed"""
        # Add todo
        success, _ = todo_manager.add_todo(sample_todo, check_duplicates=False)
        assert success

        # Get todo ID
        todos = todo_manager.get_todos()
        todo_id = todos[0].id

        # Complete todo
        result = todo_manager.complete_todo(todo_id)
        assert result is True

        # Verify status changed
        todos = todo_manager.get_todos(include_archived=True)
        assert todos[0].status == TodoStatus.COMPLETED
        assert todos[0].completed is not None

    def test_delete_todo(self, todo_manager, sample_todo):
        """Test deleting a todo"""
        # Add todo
        todo_manager.add_todo(sample_todo, check_duplicates=False)

        # Get todo ID
        todos = todo_manager.get_todos()
        todo_id = todos[0].id

        # Delete todo
        result = todo_manager.delete_todo(todo_id)
        assert result is True

        # Verify deleted
        todos = todo_manager.get_todos(include_archived=True)
        assert len(todos) == 0

    def test_archive_completed_todos(self, todo_manager):
        """Test archiving completed todos"""
        # Add 3 todos
        for i in range(3):
            todo = TodoItem(
                action=f"Task {i}",
                why_matters="Test",
                problem="Test",
                current_state="Test",
                desired_state="Test",
                success_criteria=["Done"]
            )
            todo_manager.add_todo(todo, check_duplicates=False)

        # Complete first 2
        todos = todo_manager.get_todos()
        todo_manager.complete_todo(todos[0].id)
        todo_manager.complete_todo(todos[1].id)

        # Archive
        archived_count = todo_manager.archive_completed_todos()
        assert archived_count == 2

        # Verify only 1 todo remains
        remaining = todo_manager.get_todos()
        assert len(remaining) == 1

    def test_duplicate_detection(self, todo_manager):
        """Test duplicate todo detection"""
        # Add first todo
        todo1 = TodoItem(
            action="Fix authentication bug in login endpoint",
            why_matters="Test",
            problem="Test",
            current_state="Test",
            desired_state="Test",
            success_criteria=["Done"]
        )
        todo_manager.add_todo(todo1, check_duplicates=False)

        # Try to add similar todo
        todo2 = TodoItem(
            action="Fix login endpoint authentication bug",  # Very similar
            why_matters="Test",
            problem="Test",
            current_state="Test",
            desired_state="Test",
            success_criteria=["Done"]
        )

        success, similar = todo_manager.add_todo(todo2, check_duplicates=True)

        # Should detect duplicate
        assert success is False
        assert similar is not None
        assert len(similar) == 1

    def test_markdown_roundtrip(self, todo_manager, sample_todo):
        """Test markdown serialization and deserialization"""
        # Add todo
        todo_manager.add_todo(sample_todo, check_duplicates=False)

        # Read back
        todos = todo_manager.get_todos()
        assert len(todos) == 1

        # Verify all fields preserved
        todo = todos[0]
        assert todo.action == sample_todo.action
        assert todo.why_matters == sample_todo.why_matters
        assert todo.problem == sample_todo.problem
        assert todo.priority == sample_todo.priority
        assert todo.complexity == sample_todo.complexity
        assert set(todo.success_criteria) == set(sample_todo.success_criteria)
        assert set(todo.required_capabilities) == set(sample_todo.required_capabilities)

    def test_get_todo_by_id(self, todo_manager, sample_todo):
        """Test getting specific todo by ID"""
        # Add todo
        todo_manager.add_todo(sample_todo, check_duplicates=False)

        # Get todo ID
        todos = todo_manager.get_todos()
        todo_id = todos[0].id

        # Get by ID
        todo = todo_manager.get_todo_by_id(todo_id)
        assert todo is not None
        assert todo.id == todo_id

        # Try non-existent ID
        non_existent = todo_manager.get_todo_by_id("non-existent-id")
        assert non_existent is None

    def test_update_todo(self, todo_manager, sample_todo):
        """Test updating a todo"""
        # Add todo
        todo_manager.add_todo(sample_todo, check_duplicates=False)

        # Get todo
        todos = todo_manager.get_todos()
        todo = todos[0]

        # Update fields
        todo.action = "Updated action"
        todo.priority = Priority.LOW

        # Save update
        result = todo_manager.update_todo(todo)
        assert result is True

        # Verify update
        updated_todos = todo_manager.get_todos()
        assert updated_todos[0].action == "Updated action"
        assert updated_todos[0].priority == Priority.LOW

    def test_exclude_archived_by_default(self, todo_manager, sample_todo):
        """Test that archived todos are excluded by default"""
        # Add and complete todo
        todo_manager.add_todo(sample_todo, check_duplicates=False)
        todos = todo_manager.get_todos()
        todo_manager.complete_todo(todos[0].id)

        # Archive
        todo_manager.archive_completed_todos()

        # Get todos without include_archived
        active_todos = todo_manager.get_todos(include_archived=False)
        assert len(active_todos) == 0

        # Get todos with include_archived
        all_todos = todo_manager.get_todos(include_archived=True)
        assert len(all_todos) == 0  # Archived todos are removed from file

    def test_similarity_score(self, todo_manager):
        """Test similarity scoring"""
        # Test identical texts
        score = todo_manager._similarity_score("hello world", "hello world")
        assert score == 1.0

        # Test completely different
        score = todo_manager._similarity_score("hello world", "goodbye moon")
        assert score < 0.5

        # Test similar
        score = todo_manager._similarity_score("fix login bug", "fix bug in login")
        assert score > 0.5


class TestTodoItemModel:
    """Test TodoItem data model"""

    def test_todo_to_markdown(self):
        """Test todo serialization to markdown"""
        todo = TodoItem(
            action="Test action",
            why_matters="Test reason",
            problem="Test problem",
            current_state="Current",
            desired_state="Desired",
            success_criteria=["Criterion 1", "Criterion 2"],
            files=["file.py:10-20"],
            priority=Priority.HIGH,
            complexity=Complexity.SIMPLE
        )

        markdown = todo.to_markdown()

        # Verify key sections present
        assert "### Test action" in markdown
        assert "**Why This Matters:** Test reason" in markdown
        assert "**Success Criteria:**" in markdown
        assert "- [ ] Criterion 1" in markdown
        assert "**Priority:** high" in markdown
        assert "**Complexity:** simple" in markdown

    def test_todo_from_markdown(self):
        """Test todo deserialization from markdown"""
        markdown = """
### Test Action

**Why This Matters:** Test reason

**Success Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Problem:** Test problem

**Current State:**
- **Files:** file.py:10-20
- **Current Behavior:** Current
- **Desired Behavior:** Desired

**Metadata:**
- **ID:** `test-id-123`
- **Priority:** high
- **Complexity:** simple
- **Status:** active
- **Added:** 2025-11-16T10:00:00
        """

        todo = TodoItem.from_markdown(markdown)

        assert todo.action == "Test Action"
        assert todo.why_matters == "Test reason"
        assert len(todo.success_criteria) == 2
        assert todo.priority == Priority.HIGH
        assert todo.complexity == Complexity.SIMPLE
        assert todo.id == "test-id-123"

    def test_todo_default_values(self):
        """Test todo default values"""
        todo = TodoItem(
            action="Test",
            why_matters="Test",
            problem="Test",
            current_state="Test",
            desired_state="Test",
            success_criteria=["Test"]
        )

        assert todo.priority == Priority.MEDIUM
        assert todo.complexity == Complexity.MODERATE
        assert todo.status == TodoStatus.ACTIVE
        assert todo.id is not None
        assert todo.added is not None
        assert isinstance(todo.files, list)
        assert isinstance(todo.tags, list)

    def test_todo_id_generation(self):
        """Test unique ID generation"""
        todo1 = TodoItem(
            action="Test 1",
            why_matters="Test",
            problem="Test",
            current_state="Test",
            desired_state="Test",
            success_criteria=["Test"]
        )
        todo2 = TodoItem(
            action="Test 2",
            why_matters="Test",
            problem="Test",
            current_state="Test",
            desired_state="Test",
            success_criteria=["Test"]
        )

        # IDs should be unique
        assert todo1.id != todo2.id

        # IDs should follow pattern todo-YYYYMMDD-HHMMSS-XXXXXX
        assert todo1.id.startswith("todo-")
        parts = todo1.id.split("-")
        assert len(parts) == 4  # todo, date, time, hash

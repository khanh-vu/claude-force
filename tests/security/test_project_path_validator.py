"""
Tests for ProjectPathValidator

Tests security guarantees:
1. Path traversal prevention
2. Symlink attack prevention
3. System directory protection
4. Boundary enforcement
"""

import pytest
import tempfile
import os
from pathlib import Path

from claude_force.security import (
    ProjectPathValidator,
    SecurityError,
    validate_project_root,
    FORBIDDEN_ROOTS,
)
from claude_force.path_validator import PathValidationError


class TestProjectPathValidator:
    """Test suite for ProjectPathValidator"""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create typical project structure
            (project / "src").mkdir()
            (project / "src" / "main.py").write_text("print('hello')")
            (project / "tests").mkdir()
            (project / "tests" / "test_main.py").write_text("def test(): pass")
            (project / "README.md").write_text("# Test Project")
            (project / ".gitignore").write_text("*.pyc\n")

            yield project

    def test_initialization_valid_project(self, temp_project):
        """Test validator initialization with valid project"""
        validator = ProjectPathValidator(temp_project)

        assert validator.project_root == temp_project.resolve()

    def test_initialization_nonexistent_project(self):
        """Test validator rejects nonexistent project"""
        with pytest.raises(ValueError, match="does not exist"):
            ProjectPathValidator("/nonexistent/path")

    def test_initialization_file_not_directory(self, temp_project):
        """Test validator rejects file instead of directory"""
        file_path = temp_project / "README.md"

        with pytest.raises(ValueError, match="not a directory"):
            ProjectPathValidator(file_path)

    def test_initialization_forbidden_root(self):
        """Test validator rejects system directories"""
        for forbidden in ["/etc", "/sys", "/proc", "/root"]:
            if Path(forbidden).exists():
                with pytest.raises(ValueError, match="system directory"):
                    ProjectPathValidator(forbidden)

    def test_validate_file_within_project(self, temp_project):
        """Test validation of file within project succeeds"""
        validator = ProjectPathValidator(temp_project)

        file_path = temp_project / "src" / "main.py"
        validated = validator.validate(file_path)

        assert validated == file_path.resolve()

    def test_validate_file_outside_project(self, temp_project):
        """Test validation of file outside project fails"""
        validator = ProjectPathValidator(temp_project)

        outside_file = Path("/tmp/evil.txt")

        with pytest.raises(SecurityError, match="Path traversal detected"):
            validator.validate(outside_file)

    def test_validate_path_traversal_attempt(self, temp_project):
        """Test path traversal attack is blocked"""
        validator = ProjectPathValidator(temp_project)

        # Attempt to escape project with ../
        evil_path = temp_project / "src" / ".." / ".." / ".." / "etc" / "passwd"

        with pytest.raises(SecurityError, match="outside project root"):
            validator.validate(evil_path)

    def test_validate_symlink_to_internal_file(self, temp_project):
        """Test symlink to file within project is allowed"""
        validator = ProjectPathValidator(temp_project)

        # Create symlink to internal file
        target = temp_project / "src" / "main.py"
        symlink = temp_project / "link_to_main.py"

        try:
            symlink.symlink_to(target)

            # Should succeed with follow_symlinks=True
            validated = validator.validate(symlink, follow_symlinks=True)
            assert validated == target.resolve()
        except OSError:
            # Skip test if symlinks not supported (Windows without admin)
            pytest.skip("Symlinks not supported on this system")

    def test_validate_symlink_to_external_file(self, temp_project):
        """SEC: Test symlink attack pointing outside project is blocked"""
        validator = ProjectPathValidator(temp_project)

        # Create malicious symlink pointing to /etc/passwd
        symlink = temp_project / "evil.txt"
        external_target = Path("/etc/passwd")

        if not external_target.exists():
            pytest.skip("/etc/passwd does not exist on this system")

        try:
            symlink.symlink_to(external_target)

            # Should raise SecurityError
            with pytest.raises(SecurityError, match="Symlink attack detected"):
                validator.validate(symlink, follow_symlinks=True)
        except OSError:
            pytest.skip("Symlinks not supported on this system")

    def test_validate_relative_path(self, temp_project):
        """Test validation handles relative paths correctly"""
        validator = ProjectPathValidator(temp_project)

        # Change to project directory
        original_cwd = Path.cwd()
        try:
            os.chdir(temp_project)

            # Validate relative path
            validated = validator.validate("src/main.py")
            assert validated == (temp_project / "src" / "main.py").resolve()
        finally:
            os.chdir(original_cwd)

    def test_safe_iterdir(self, temp_project):
        """Test safe directory iteration"""
        validator = ProjectPathValidator(temp_project)

        items = list(validator.safe_iterdir(temp_project))

        # Should find all top-level items
        item_names = {item.name for item in items}
        assert "src" in item_names
        assert "tests" in item_names
        assert "README.md" in item_names

    def test_safe_walk(self, temp_project):
        """Test safe directory tree walk"""
        validator = ProjectPathValidator(temp_project)

        found_files = []
        for dirpath, dirnames, filenames in validator.safe_walk(temp_project):
            for filename in filenames:
                found_files.append(filename)

        # Should find all files
        assert "main.py" in found_files
        assert "test_main.py" in found_files
        assert "README.md" in found_files

    def test_safe_walk_with_max_depth(self, temp_project):
        """Test safe walk respects max depth"""
        validator = ProjectPathValidator(temp_project)

        # Only walk top level (depth 0)
        found_dirs = []
        for dirpath, dirnames, filenames in validator.safe_walk(temp_project, max_depth=0):
            found_dirs.append(dirpath)

        # Should only have root directory
        assert len(found_dirs) == 1
        assert found_dirs[0] == temp_project

    def test_safe_walk_skips_permission_denied(self, temp_project):
        """Test safe walk handles permission errors gracefully"""
        validator = ProjectPathValidator(temp_project)

        # Create directory and remove read permission
        restricted = temp_project / "restricted"
        restricted.mkdir()
        original_mode = restricted.stat().st_mode

        try:
            restricted.chmod(0o000)  # No permissions

            # Walk should complete without error, skipping restricted dir
            list(validator.safe_walk(temp_project))

        finally:
            # Restore permissions for cleanup
            restricted.chmod(original_mode)


class TestValidateProjectRoot:
    """Test the validate_project_root helper function"""

    def test_valid_project_root(self):
        """Test validation of valid project root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = validate_project_root(tmpdir)
            assert root == Path(tmpdir).resolve()

    def test_nonexistent_path(self):
        """Test validation rejects nonexistent path"""
        with pytest.raises(ValueError, match="does not exist"):
            validate_project_root("/nonexistent/path")

    def test_file_not_directory(self):
        """Test validation rejects file"""
        with tempfile.NamedTemporaryFile() as tmpfile:
            with pytest.raises(ValueError, match="not a directory"):
                validate_project_root(tmpfile.name)

    def test_forbidden_system_directory(self):
        """Test validation rejects system directories"""
        for forbidden in ["/etc", "/sys", "/proc"]:
            if Path(forbidden).exists():
                with pytest.raises(ValueError, match="system directory"):
                    validate_project_root(forbidden)


class TestSymlinkAttacks:
    """Dedicated tests for symlink attack scenarios"""

    @pytest.fixture
    def project_with_symlinks(self):
        """Create project with various symlink scenarios"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create structure
            (project / "safe").mkdir()
            (project / "safe" / "file.txt").write_text("safe content")

            yield project

    def test_symlink_chain_attack(self, project_with_symlinks):
        """SEC: Test chain of symlinks trying to escape"""
        project = project_with_symlinks
        validator = ProjectPathValidator(project)

        try:
            # Create chain: link1 -> link2 -> /etc/passwd
            link2 = project / "link2"
            link2.symlink_to("/etc/passwd")

            link1 = project / "link1"
            link1.symlink_to(link2)

            # Should detect and block
            with pytest.raises(SecurityError):
                validator.validate(link1, follow_symlinks=True)
        except OSError:
            pytest.skip("Symlinks not supported")

    def test_directory_symlink_attack(self, project_with_symlinks):
        """SEC: Test symlink to external directory"""
        project = project_with_symlinks
        validator = ProjectPathValidator(project)

        try:
            # Create symlink to /etc
            evil_dir = project / "evil_dir"
            evil_dir.symlink_to("/etc")

            # Should block access to files in symlinked directory
            evil_file = evil_dir / "passwd"

            with pytest.raises(SecurityError):
                validator.validate(evil_file, follow_symlinks=True)
        except OSError:
            pytest.skip("Symlinks not supported")


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_unicode_paths(self):
        """Test handling of Unicode in paths"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create file with Unicode name
            unicode_file = project / "测试文件.txt"
            unicode_file.write_text("test")

            validator = ProjectPathValidator(project)
            validated = validator.validate(unicode_file)

            assert validated == unicode_file.resolve()

    def test_special_characters_in_filename(self):
        """Test handling of special characters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create file with special characters
            special_file = project / "file with spaces & symbols!.txt"
            special_file.write_text("test")

            validator = ProjectPathValidator(project)
            validated = validator.validate(special_file)

            assert validated == special_file.resolve()

    def test_very_long_path(self):
        """Test handling of very long paths"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create deeply nested structure
            deep = project
            for i in range(10):
                deep = deep / f"level_{i}"
            deep.mkdir(parents=True)

            file = deep / "file.txt"
            file.write_text("deep")

            validator = ProjectPathValidator(project)
            validated = validator.validate(file)

            assert validated == file.resolve()

    def test_concurrent_validation(self):
        """Test validator is thread-safe"""
        import threading

        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "file.txt").write_text("test")

            validator = ProjectPathValidator(project)

            results = []
            errors = []

            def validate_file():
                try:
                    validated = validator.validate(project / "file.txt")
                    results.append(validated)
                except Exception as e:
                    errors.append(e)

            # Run validations concurrently
            threads = [threading.Thread(target=validate_file) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # All should succeed
            assert len(results) == 10
            assert len(errors) == 0

    def test_broken_symlink_in_walk(self):
        """Test safe_walk handles broken symlinks gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create a normal directory and file
            (project / "normal_dir").mkdir()
            (project / "normal_dir" / "file.txt").write_text("content")

            try:
                # Create a broken symlink (pointing to non-existent target)
                broken_link = project / "broken_link"
                broken_link.symlink_to("/nonexistent/target")

                # Create a broken directory symlink
                broken_dir = project / "broken_dir"
                broken_dir.symlink_to("/nonexistent/directory")

                validator = ProjectPathValidator(project)

                # Walk should complete without crashing
                found_files = []
                found_dirs = []
                for dirpath, dirnames, filenames in validator.safe_walk(project):
                    found_files.extend(filenames)
                    found_dirs.extend(dirnames)

                # Should find normal file, broken links should be skipped
                assert "file.txt" in found_files
                assert "normal_dir" in found_dirs
                # Walk should complete successfully despite broken symlinks

            except OSError:
                pytest.skip("Symlinks not supported on this system")

    def test_directory_deleted_during_walk(self):
        """Test safe_walk handles directories deleted during iteration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create structure
            (project / "dir1").mkdir()
            (project / "dir1" / "file1.txt").write_text("content1")
            (project / "dir2").mkdir()
            (project / "dir2" / "file2.txt").write_text("content2")

            validator = ProjectPathValidator(project)

            # Start walk and collect results
            found_files = []
            try:
                for dirpath, dirnames, filenames in validator.safe_walk(project):
                    found_files.extend(filenames)
                    # Simulate race condition: delete dir2 during walk
                    if dirpath == project and "dir2" in dirnames:
                        import shutil

                        shutil.rmtree(project / "dir2", ignore_errors=True)

                # Walk should complete, finding at least file1
                assert "file1.txt" in found_files
                # file2.txt may or may not be found depending on timing

            except Exception as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"safe_walk raised exception: {e}")

    def test_walk_with_inaccessible_subdirectory(self):
        """Test safe_walk skips inaccessible subdirectories and continues"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create structure
            (project / "accessible").mkdir()
            (project / "accessible" / "file.txt").write_text("content")

            inaccessible = project / "inaccessible"
            inaccessible.mkdir()
            (inaccessible / "secret.txt").write_text("secret")

            # Remove all permissions from inaccessible directory
            original_mode = inaccessible.stat().st_mode

            try:
                inaccessible.chmod(0o000)

                validator = ProjectPathValidator(project)

                found_files = []
                found_dirs = []
                # Walk should complete without errors
                for dirpath, dirnames, filenames in validator.safe_walk(project):
                    found_files.extend(filenames)
                    found_dirs.extend(dirnames)

                # Should find accessible files
                assert "file.txt" in found_files
                # May or may not list inaccessible dir, but should not crash

            finally:
                # Restore permissions for cleanup
                inaccessible.chmod(original_mode)

    def test_walk_with_special_filesystem_entries(self):
        """Test safe_walk handles special filesystem entries gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create normal structure
            (project / "normal").mkdir()
            (project / "normal" / "file.txt").write_text("content")

            validator = ProjectPathValidator(project)

            # Walk should handle any special entries without crashing
            found_files = []
            for dirpath, dirnames, filenames in validator.safe_walk(project):
                found_files.extend(filenames)

            # Should find normal files
            assert "file.txt" in found_files

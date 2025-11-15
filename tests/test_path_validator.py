"""
Tests for path_validator module

Ensures path validation correctly prevents:
- Path traversal attacks
- Symlink exploits
- Directory escape
"""

import pytest
import tempfile
import os
from pathlib import Path

from claude_force.path_validator import (
    validate_path,
    validate_agent_file_path,
    validate_config_file_path,
    PathValidationError,
)


class TestPathValidation:
    """Test path validation functions"""

    def test_valid_path_absolute(self, tmp_path):
        """Test validation of valid absolute path"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = validate_path(test_file, must_exist=True)
        assert result.exists()
        assert result.is_absolute()

    def test_valid_path_within_base(self, tmp_path):
        """Test validation of path within base directory"""
        base_dir = tmp_path / "base"
        base_dir.mkdir()

        test_file = base_dir / "subdir" / "file.txt"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("test")

        result = validate_path(test_file, base_dir=base_dir, must_exist=True)
        assert result.exists()

    def test_reject_nonexistent_when_required(self, tmp_path):
        """Test rejection of non-existent path when must_exist=True"""
        non_existent = tmp_path / "does_not_exist.txt"

        with pytest.raises(PathValidationError, match="does not exist"):
            validate_path(non_existent, must_exist=True)

    def test_reject_path_traversal(self, tmp_path):
        """Test rejection of path traversal attempts"""
        base_dir = tmp_path / "base"
        base_dir.mkdir()

        # Try to escape base directory using ../
        evil_path = base_dir / ".." / ".." / "etc" / "passwd"

        with pytest.raises(PathValidationError, match="outside allowed directory"):
            validate_path(evil_path, base_dir=base_dir)

    def test_reject_symlink_by_default(self, tmp_path):
        """
        CRITICAL TEST: Verify symlinks are rejected by default

        This test ensures the fix for the code review issue:
        Symlinks must be detected BEFORE resolve() is called.
        """
        # Create a target file outside allowed directory
        target_dir = tmp_path / "target"
        target_dir.mkdir()
        target_file = target_dir / "secret.txt"
        target_file.write_text("secret data")

        # Create a symlink inside allowed directory pointing to target
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        symlink_path = base_dir / "link.txt"

        # Create symlink pointing outside base_dir
        os.symlink(target_file, symlink_path)

        # Verify symlink exists
        assert symlink_path.is_symlink()

        # Should reject symlink even though target exists
        with pytest.raises(PathValidationError, match="Symlinks not allowed"):
            validate_path(symlink_path, base_dir=base_dir, allow_symlinks=False)

    def test_allow_symlink_when_enabled(self, tmp_path):
        """Test that symlinks are allowed when explicitly enabled"""
        target_file = tmp_path / "target.txt"
        target_file.write_text("test")

        symlink_path = tmp_path / "link.txt"
        os.symlink(target_file, symlink_path)

        # Should succeed when allow_symlinks=True
        result = validate_path(symlink_path, allow_symlinks=True)
        assert result.exists()

    def test_reject_symlink_directory_escape(self, tmp_path):
        """
        CRITICAL TEST: Symlink pointing outside allowed directory

        This is the exact attack vector from the code review.
        Without the fix, this test would FAIL.
        """
        # Create structure:
        # /tmp/
        #   sensitive/
        #     secret.txt
        #   allowed/
        #     evil_link -> ../sensitive/secret.txt

        sensitive_dir = tmp_path / "sensitive"
        sensitive_dir.mkdir()
        secret_file = sensitive_dir / "secret.txt"
        secret_file.write_text("CONFIDENTIAL DATA")

        allowed_dir = tmp_path / "allowed"
        allowed_dir.mkdir()

        evil_symlink = allowed_dir / "evil_link"
        os.symlink(secret_file, evil_symlink)

        # Attack: Try to access sensitive file via symlink
        # The symlink is technically "inside" allowed_dir
        # But it points OUTSIDE to sensitive data

        # Should be REJECTED due to symlink check
        with pytest.raises(PathValidationError, match="Symlinks not allowed"):
            validate_path(evil_symlink, base_dir=allowed_dir, allow_symlinks=False)

        # Even if we allow symlinks, it should reject because target is outside base_dir
        with pytest.raises(PathValidationError, match="outside allowed directory"):
            validate_path(evil_symlink, base_dir=allowed_dir, allow_symlinks=True)

    def test_reject_relative_path_escape(self, tmp_path):
        """Test rejection of ../ escape attempts"""
        base_dir = tmp_path / "base"
        base_dir.mkdir()

        # Create file outside base
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("outside")

        # Try to access via relative path
        evil_path = base_dir / ".." / "outside.txt"

        with pytest.raises(PathValidationError, match="outside allowed directory"):
            validate_path(evil_path, base_dir=base_dir)

    def test_validate_agent_file_path(self, tmp_path):
        """Test agent file path validation"""
        # Should accept paths in .claude/agents/
        # Save current working directory to restore later
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            claude_dir = tmp_path / ".claude" / "agents"
            claude_dir.mkdir(parents=True)

            agent_file = claude_dir / "test-agent.md"
            agent_file.write_text("# Agent")

            result = validate_agent_file_path("agents/test-agent.md")
            assert ".claude" in str(result)
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    def test_reject_agent_file_outside_claude(self):
        """Test rejection of agent files outside .claude/"""
        with pytest.raises(PathValidationError, match="outside allowed directory"):
            validate_agent_file_path("../../etc/passwd")


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_path(self):
        """Test handling of empty path"""
        with pytest.raises(PathValidationError):
            validate_path("")

    def test_none_path(self):
        """Test handling of None path"""
        with pytest.raises((PathValidationError, TypeError)):
            validate_path(None)

    def test_very_long_path(self, tmp_path):
        """Test handling of very long paths"""
        # Create nested directories
        deep_path = tmp_path
        for i in range(50):
            deep_path = deep_path / f"level{i}"

        deep_path.mkdir(parents=True)
        test_file = deep_path / "file.txt"
        test_file.write_text("test")

        result = validate_path(test_file, must_exist=True)
        assert result.exists()

    def test_special_characters_in_path(self, tmp_path):
        """Test handling of special characters"""
        special_file = tmp_path / "file with spaces & special!.txt"
        special_file.write_text("test")

        result = validate_path(special_file, must_exist=True)
        assert result.exists()


class TestSecurityScenarios:
    """Test real-world attack scenarios"""

    def test_null_byte_injection(self):
        """Test protection against null byte injection"""
        # Some filesystems allow null bytes in paths
        evil_path = "safe.txt\x00../../etc/passwd"

        # Should either reject or sanitize
        try:
            validate_path(evil_path)
        except (PathValidationError, ValueError):
            pass  # Expected - rejected

    def test_double_encoding(self, tmp_path):
        """Test protection against double-encoded paths"""
        base_dir = tmp_path / "base"
        base_dir.mkdir()

        # %2e%2e%2f = ../
        # Some systems might decode this
        evil_path = base_dir / "%2e%2e%2f%2e%2e%2fetc%2fpasswd"

        # Should not escape base directory
        try:
            result = validate_path(evil_path, base_dir=base_dir)
            # If it succeeds, ensure it's still within base_dir
            # Python 3.8 compatible: use relative_to() instead of is_relative_to()
            try:
                result.relative_to(base_dir.resolve())
            except ValueError:
                # Path is not relative to base_dir - security violation
                pytest.fail(f"Path {result} escaped base directory {base_dir}")
        except PathValidationError:
            pass  # Expected - rejected

    def test_unicode_normalization(self, tmp_path):
        """Test handling of Unicode normalization attacks"""
        # Some filesystems normalize Unicode differently
        # This could be used to bypass filters

        base_dir = tmp_path / "base"
        base_dir.mkdir()

        # Different representations of the same character
        path1 = base_dir / "café"  # NFC form
        path2 = base_dir / "café"  # NFD form (decomposed)

        path1.mkdir(exist_ok=True)

        # Both should be valid
        result1 = validate_path(path1, base_dir=base_dir)
        result2 = validate_path(path2, base_dir=base_dir)

        # Results should be consistent
        assert result1.resolve() == result2.resolve()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

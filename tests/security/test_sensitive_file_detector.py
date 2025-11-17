"""
Tests for SensitiveFileDetector

Tests privacy protection:
1. Environment file detection
2. Credentials detection
3. Private key detection
4. Custom pattern support
5. Directory filtering
"""

import pytest
import tempfile
from pathlib import Path

from claude_force.security import (
    SensitiveFileDetector,
    is_sensitive_file,
    get_default_detector,
)


class TestSensitiveFileDetector:
    """Test suite for SensitiveFileDetector"""

    @pytest.fixture
    def detector(self):
        """Create a fresh detector instance"""
        return SensitiveFileDetector()

    @pytest.fixture
    def project_with_sensitive_files(self):
        """Create a project with various sensitive files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create regular files
            (project / "src").mkdir()
            (project / "src" / "main.py").write_text("print('hello')")
            (project / "README.md").write_text("# Project")

            # Create sensitive files
            (project / ".env").write_text("API_KEY=secret123")
            (project / ".env.production").write_text("API_KEY=prod_secret")
            (project / "credentials.json").write_text('{"key": "secret"}')
            (project / "service-account.json").write_text('{"private_key": "xxx"}')
            (project / "id_rsa").write_text("PRIVATE KEY")
            (project / "database.yml").write_text("password: secret")
            (project / "secrets.json").write_text('{"token": "xxx"}')

            # Create certificate files
            (project / "cert.pem").write_text("CERTIFICATE")
            (project / "private.key").write_text("PRIVATE KEY")

            # Create sensitive directory
            (project / ".ssh").mkdir()
            (project / ".ssh" / "config").write_text("Host github.com")
            (project / ".ssh" / "id_rsa").write_text("PRIVATE KEY")

            yield project

    # Environment Files
    def test_detect_env_file(self, detector):
        """Test detection of .env file"""
        assert detector.is_sensitive(Path(".env"))
        assert detector.is_sensitive(Path(".env.local"))
        assert detector.is_sensitive(Path(".env.production"))
        assert detector.is_sensitive(Path("env.staging"))

    def test_env_file_reason(self, detector):
        """Test reason for .env detection"""
        reason = detector.get_sensitivity_reason(Path(".env"))
        assert "environment" in reason.lower()

    # Credentials
    def test_detect_credentials_files(self, detector):
        """Test detection of credential files"""
        assert detector.is_sensitive(Path("credentials.json"))
        assert detector.is_sensitive(Path("credentials.yaml"))
        assert detector.is_sensitive(Path("credentials.yml"))
        assert detector.is_sensitive(Path("service-account.json"))
        assert detector.is_sensitive(Path("service-account-prod.json"))

    def test_detect_secrets_files(self, detector):
        """Test detection of secrets files"""
        assert detector.is_sensitive(Path("secrets.json"))
        assert detector.is_sensitive(Path("secrets.yaml"))
        assert detector.is_sensitive(Path("secrets.yml"))
        assert detector.is_sensitive(Path(".secrets"))

    # Private Keys
    def test_detect_ssh_keys(self, detector):
        """Test detection of SSH private keys"""
        assert detector.is_sensitive(Path("id_rsa"))
        assert detector.is_sensitive(Path("id_dsa"))
        assert detector.is_sensitive(Path("id_ecdsa"))
        assert detector.is_sensitive(Path("id_ed25519"))
        assert detector.is_sensitive(Path("deploy_rsa"))

    def test_detect_pem_files(self, detector):
        """Test detection of PEM certificates/keys"""
        assert detector.is_sensitive(Path("cert.pem"))
        assert detector.is_sensitive(Path("private.pem"))
        assert detector.is_sensitive(Path("certificate.pem"))

    def test_detect_key_files(self, detector):
        """Test detection of .key files"""
        assert detector.is_sensitive(Path("private.key"))
        assert detector.is_sensitive(Path("server.key"))
        assert detector.is_sensitive(Path("certificate.key"))

    # Cloud Provider Configs
    def test_detect_aws_credentials(self, detector):
        """Test detection of AWS credentials"""
        assert detector.is_sensitive(Path(".aws/credentials"))
        assert detector.is_sensitive(Path(".aws/config"))

    def test_detect_gcp_credentials(self, detector):
        """Test detection of GCP credentials"""
        assert detector.is_sensitive(Path(".gcp/credentials"))

    # Sensitive Directories
    def test_detect_ssh_directory(self, detector):
        """Test detection of .ssh directory"""
        assert detector.is_sensitive(Path(".ssh"))
        assert detector.is_sensitive(Path(".ssh/config"))
        assert detector.is_sensitive(Path(".ssh/known_hosts"))

    def test_detect_git_directory(self, detector):
        """Test detection of .git directory"""
        assert detector.is_sensitive(Path(".git"))
        assert detector.is_sensitive(Path(".git/config"))

    # Database Configs
    def test_detect_database_configs(self, detector):
        """Test detection of database configuration files"""
        assert detector.is_sensitive(Path("database.yml"))
        assert detector.is_sensitive(Path("database.yaml"))
        assert detector.is_sensitive(Path("db.yml"))

    # API Keys and Tokens
    def test_detect_api_key_files(self, detector):
        """Test detection of API key files"""
        assert detector.is_sensitive(Path(".api-keys.json"))
        assert detector.is_sensitive(Path("api_keys.txt"))

    def test_detect_npmrc(self, detector):
        """Test detection of NPM credentials"""
        assert detector.is_sensitive(Path(".npmrc"))

    def test_detect_pypirc(self, detector):
        """Test detection of PyPI credentials"""
        assert detector.is_sensitive(Path(".pypirc"))

    # Password Files
    def test_detect_password_files(self, detector):
        """Test detection of password files"""
        assert detector.is_sensitive(Path("passwords.txt"))
        assert detector.is_sensitive(Path("password.txt"))
        assert detector.is_sensitive(Path("passwd"))

    # Non-Sensitive Files
    def test_regular_files_not_sensitive(self, detector):
        """Test regular files are not flagged"""
        assert not detector.is_sensitive(Path("main.py"))
        assert not detector.is_sensitive(Path("README.md"))
        assert not detector.is_sensitive(Path("package.json"))
        assert not detector.is_sensitive(Path("requirements.txt"))
        assert not detector.is_sensitive(Path("Dockerfile"))

    def test_test_files_not_sensitive(self, detector):
        """Test files are not flagged"""
        assert not detector.is_sensitive(Path("test_main.py"))
        assert not detector.is_sensitive(Path("tests/test_auth.py"))

    # Custom Patterns
    def test_custom_patterns(self):
        """Test detector with custom patterns"""
        detector = SensitiveFileDetector(custom_patterns=[r"internal-.*\.txt"])

        assert detector.is_sensitive(Path("internal-notes.txt"))
        assert detector.is_sensitive(Path("internal-passwords.txt"))
        assert not detector.is_sensitive(Path("external-notes.txt"))

    def test_custom_directories(self):
        """Test detector with custom sensitive directories"""
        detector = SensitiveFileDetector(custom_dirs={"internal", "confidential"})

        assert detector.is_sensitive(Path("internal/file.txt"))
        assert detector.is_sensitive(Path("confidential/data.json"))
        assert not detector.is_sensitive(Path("public/file.txt"))

    # Scan Directory
    def test_scan_directory(self, detector, project_with_sensitive_files):
        """Test scanning directory for sensitive files"""
        results = detector.scan_directory(project_with_sensitive_files)

        # Should find all sensitive files
        paths = [r["path"] for r in results]
        assert any(".env" in p for p in paths)
        assert any("credentials.json" in p for p in paths)
        assert any("id_rsa" in p for p in paths)
        assert any(".ssh" in p for p in paths)

    def test_scan_directory_non_recursive(self, detector, project_with_sensitive_files):
        """Test non-recursive directory scan"""
        results = detector.scan_directory(project_with_sensitive_files, recursive=False)

        # Should only find top-level sensitive files
        paths = [r["path"] for r in results]
        assert any(".env" in p for p in paths)

        # Should NOT find files in .ssh subdirectory
        assert not any(".ssh/id_rsa" in p for p in paths)

    # Filter Files
    def test_filter_safe_files(self, detector, project_with_sensitive_files):
        """Test filtering safe files from list"""
        all_files = list(project_with_sensitive_files.rglob("*"))
        all_files = [f for f in all_files if f.is_file()]

        safe_files = detector.filter_safe_files(all_files)

        # Safe files should include regular files
        safe_names = {f.name for f in safe_files}
        assert "main.py" in safe_names
        assert "README.md" in safe_names

        # Safe files should NOT include sensitive files
        assert ".env" not in safe_names
        assert "credentials.json" not in safe_names
        assert "id_rsa" not in safe_names

    # Should Skip Content
    def test_should_skip_content(self, detector):
        """Test should_skip_content method"""
        should_skip, reason = detector.should_skip_content(".env")

        assert should_skip is True
        assert reason is not None
        assert "environment" in reason.lower()

        should_skip, reason = detector.should_skip_content("main.py")
        assert should_skip is False
        assert reason is None

    # Skip Report
    def test_create_skip_report(self, detector):
        """Test creation of skip report"""
        skipped = [
            Path(".env"),
            Path("credentials.json"),
            Path("id_rsa"),
        ]

        report = detector.create_skip_report(skipped)

        assert "Sensitive Files Skipped" in report
        assert ".env" in report
        assert "credentials.json" in report
        assert "3 sensitive files" in report

    def test_create_skip_report_empty(self, detector):
        """Test skip report with no files"""
        report = detector.create_skip_report([])

        assert "No sensitive files" in report


class TestModuleFunctions:
    """Test module-level convenience functions"""

    def test_is_sensitive_file(self):
        """Test is_sensitive_file convenience function"""
        assert is_sensitive_file(".env")
        assert is_sensitive_file("credentials.json")
        assert not is_sensitive_file("main.py")

    def test_get_default_detector(self):
        """Test get_default_detector returns singleton"""
        detector1 = get_default_detector()
        detector2 = get_default_detector()

        assert detector1 is detector2  # Same instance


class TestCaseInsensitivity:
    """Test case-insensitive pattern matching"""

    def test_uppercase_env_file(self):
        """Test .ENV is detected"""
        assert is_sensitive_file(".ENV")
        assert is_sensitive_file(".Env")

    def test_uppercase_credentials(self):
        """Test CREDENTIALS.JSON is detected"""
        assert is_sensitive_file("CREDENTIALS.JSON")
        assert is_sensitive_file("Credentials.Json")

    def test_mixed_case_key_files(self):
        """Test mixed case key files are detected"""
        assert is_sensitive_file("Private.Key")
        assert is_sensitive_file("CERT.PEM")


class TestEdgeCases:
    """Test edge cases and unusual scenarios"""

    def test_file_with_sensitive_extension_in_path(self):
        """Test file path containing .env but not as filename"""
        # This should NOT be flagged (.env is part of directory name)
        assert not is_sensitive_file("config/.env_sample/settings.py")

    def test_backup_files_with_sensitive_content(self):
        """Test backup files that might contain sensitive data"""
        assert is_sensitive_file("backup.sql")
        assert is_sensitive_file("dump.sql.gz")
        assert is_sensitive_file("backup-2024.tar.gz")

    def test_private_and_confidential_files(self):
        """Test files marked as private or confidential"""
        assert is_sensitive_file("private-notes.txt")
        assert is_sensitive_file("confidential-report.pdf")

    def test_unicode_filenames(self):
        """Test handling of Unicode filenames"""
        detector = SensitiveFileDetector()

        # Note: Current patterns are ASCII-based
        # Unicode filenames like "密码.txt" (password in Chinese) are NOT detected
        # This is intentional - we don't want false positives on non-English files
        # Users can add custom patterns if needed

        # Regular file with Unicode - should NOT be flagged
        assert not detector.is_sensitive(Path("测试.py"))  # "test" in Chinese
        assert not detector.is_sensitive(Path("密码.txt"))  # "password" in Chinese

        # But ASCII sensitive patterns still work on any file
        assert detector.is_sensitive(Path("中文/credentials.json"))  # Chinese dir + English filename

    def test_hidden_files(self):
        """Test detection of hidden sensitive files"""
        assert is_sensitive_file(".env")
        assert is_sensitive_file(".secrets")
        assert is_sensitive_file(".api-keys.json")

    def test_nested_sensitive_directories(self):
        """Test deeply nested sensitive directories"""
        assert is_sensitive_file(".ssh/keys/production/id_rsa")
        assert is_sensitive_file("secrets/production/api/keys.json")


class TestPerformance:
    """Test performance characteristics"""

    def test_many_files_performance(self):
        """Test detector performance with many files"""
        import time

        detector = SensitiveFileDetector()

        # Create list of 10,000 file paths
        files = [Path(f"file_{i}.py") for i in range(10000)]
        files.extend([Path(".env"), Path("credentials.json")])  # Add some sensitive

        start = time.time()
        safe_files = detector.filter_safe_files(files)
        duration = time.time() - start

        # Should complete quickly (< 1 second)
        assert duration < 1.0

        # Should filter correctly
        assert len(safe_files) == 10000  # Only .py files

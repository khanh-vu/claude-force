```markdown
# Security Guarantees

This document outlines the security measures implemented in claude-force for safe project analysis and integration.

## Overview

Claude-force implements multiple layers of security to protect your code, credentials, and sensitive data during project analysis and agent operations.

## Security Principles

1. **Least Privilege**: Only access what's necessary
2. **Defense in Depth**: Multiple layers of protection
3. **Fail Secure**: Errors block operations rather than allowing them
4. **Privacy First**: Sensitive data is never read or transmitted
5. **Transparency**: Clear logging of what's accessed and why

---

## 1. Path Traversal Protection

### Threat: Malicious Path Access

**Attack Scenario**:
```python
# Attacker tries to access system files
evil_path = "../../../etc/passwd"
```

**Protection**:
```python
from claude_force.security import ProjectPathValidator

validator = ProjectPathValidator("/home/user/my-project")

# This will raise SecurityError
validator.validate("../../../etc/passwd")
# SecurityError: Path traversal detected
```

### Implementation

- All file paths are validated against project root boundary
- Resolved paths are checked to prevent `../` escaping
- System directories are explicitly forbidden
- Symlinks are validated to ensure targets are safe

### Forbidden Directories

The following directories can NEVER be analyzed:
- `/etc` - System configuration
- `/sys` - System information
- `/proc` - Process information
- `/root` - Root user home
- `/boot` - Boot files
- `/dev` - Device files
- `C:\Windows` - Windows system directory
- `C:\Windows\System32` - Windows system files

**Example**:
```python
from claude_force.security import validate_project_root

# This raises ValueError
validate_project_root("/etc")
# ValueError: Cannot analyze system directory: /etc
```

---

## 2. Symlink Attack Prevention

### Threat: Symlink to Sensitive Files

**Attack Scenario**:
```bash
# Attacker creates symlink in project
cd /tmp/my-project
ln -s /etc/passwd exposed_secrets.txt

# Hopes analysis will read /etc/passwd
```

**Protection**:
```python
# Symlinks are detected BEFORE following
validator.validate("exposed_secrets.txt", follow_symlinks=True)
# SecurityError: Symlink attack detected:
# exposed_secrets.txt -> /etc/passwd
# Target is outside project root
```

### Implementation

1. **Check Before Resolve**: Symlinks are detected before `Path.resolve()`
2. **Validate Target**: Target path is validated against project boundary
3. **Log Warning**: Symlink attempts are logged
4. **Fail Secure**: Invalid symlinks raise `SecurityError`

**Safe Symlinks**:
```python
# Symlinks WITHIN project are allowed
project/
  src/
    main.py
  link_to_main.py -> src/main.py  # OK (target in project)
```

**Unsafe Symlinks**:
```python
# Symlinks OUTSIDE project are blocked
project/
  evil.txt -> /etc/passwd  # BLOCKED
  malicious/ -> /home/other_user/  # BLOCKED
```

---

## 3. Sensitive File Protection

### Threat: Credential Exposure

**Attack Scenario**:
```
# Project contains sensitive files
.env                  # API keys
credentials.json      # Service account
id_rsa               # SSH private key
database.yml         # DB passwords
```

**Protection**:
```python
from claude_force.security import SensitiveFileDetector

detector = SensitiveFileDetector()

if detector.is_sensitive(".env"):
    print("Skipping sensitive file")
    # File is NEVER read
```

### Protected File Types

#### Environment Files
- `.env`, `.env.local`, `.env.production`
- `env.staging`, `env.development`

#### Credentials
- `credentials.json`, `credentials.yaml`
- `service-account.json`
- `secrets.json`, `secrets.yaml`

#### Private Keys
- `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`
- `*.pem`, `*.key`, `*.p12`, `*.pfx`
- `certificate.key`, `private.key`

#### Cloud Provider Configs
- `.aws/credentials`, `.aws/config`
- `.gcp/credentials`
- `.azure/credentials`

#### Database Configs
- `database.yml`, `database.yaml`
- `db.yml`, `db.yaml`

#### API Keys & Tokens
- `.api-keys.json`, `api_keys.txt`
- `.npmrc`, `.pypirc`

#### Password Files
- `passwords.txt`, `password.txt`
- `passwd`, `shadow`

#### Backup Files (may contain secrets)
- `*.sql`, `*.sql.gz`
- `backup*.tar.gz`

### Sensitive Directories

These directories are completely skipped:
- `.git` - Git repository data
- `.ssh` - SSH keys and configs
- `.gnupg` - GPG keys
- `.aws` - AWS credentials
- `credentials/` - Credential storage
- `secrets/` - Secret storage
- `private/` - Private files
- `confidential/` - Confidential data

### Implementation

```python
# Automatic filtering during analysis
detector = SensitiveFileDetector()

for file in project_files:
    should_skip, reason = detector.should_skip_content(file)
    if should_skip:
        logger.warning(f"Skipping {file}: {reason}")
        continue  # Never read file content

    # Safe to analyze
    analyze_file(file)
```

### Custom Sensitive Patterns

You can add custom patterns:

```python
detector = SensitiveFileDetector(
    custom_patterns=[
        r"internal-.*\.txt",  # internal-notes.txt
        r"company-secrets.*",  # company-secrets.json
    ],
    custom_dirs={"internal", "confidential"}
)
```

---

## 4. Command Injection Prevention

### Threat: Shell Command Injection

**Attack Scenario**:
```python
# DANGEROUS: User input in shell command
filename = "file.txt; rm -rf /"  # Malicious input
os.system(f"cat {filename}")  # EXECUTES: cat file.txt; rm -rf /
```

**Protection**:
```python
# SAFE: Use subprocess without shell
import subprocess

result = subprocess.run(
    ['cat', filename],  # List form prevents injection
    shell=False,        # Never use shell=True with user input
    capture_output=True,
    text=True
)
```

### Implementation Rules

#### ❌ NEVER Do This
```python
import os
import subprocess

# DANGEROUS: shell=True with user input
os.system(f"grep {pattern} {file}")
subprocess.run(f"cat {file}", shell=True)

# DANGEROUS: String formatting in commands
os.popen(f"ls {directory}")
```

#### ✅ ALWAYS Do This
```python
import subprocess

# SAFE: List form, no shell
subprocess.run(['grep', pattern, file], shell=False)
subprocess.run(['cat', file], shell=False, capture_output=True)

# SAFE: Use Path objects
from pathlib import Path
Path(directory).iterdir()  # No shell needed
```

### Validation

All subprocess calls in claude-force:
- Use list form arguments
- Set `shell=False` explicitly
- Validate input before execution
- Use `shlex.quote()` if shell is absolutely necessary

---

## 5. File Operation Safety

### Backup Before Modification

All file modifications are protected by backups:

```python
from claude_force.security import safe_file_operation

with safe_file_operation(project_root) as backup:
    try:
        # Perform modifications
        modify_files()
    except Exception:
        # Automatic rollback on error
        backup.rollback()
```

### Atomic Operations

File operations are atomic (all-or-nothing):

1. **Create backup** of original state
2. **Perform changes** in staging area
3. **Validate** changes
4. **Commit** (atomic rename) or **Rollback**

### Disk Space Validation

Before operations, check available space:

```python
import shutil

stat = shutil.disk_usage(project_root)
required = estimate_space_needed()

if stat.free < required * 1.2:  # 20% buffer
    raise InsufficientSpaceError(
        f"Need {required / 1e9:.2f}GB, "
        f"only {stat.free / 1e9:.2f}GB available"
    )
```

---

## 6. Permission Handling

### Read-Only Operations

Project analysis is read-only by default:
- No files are modified
- No files are created outside `.claude/`
- No files are deleted

### Write Operations

File writes are restricted to:
- `.claude/` directory only
- User-specified output files
- Temporary directories

### Permission Checks

Before any write operation:

```python
def check_write_permissions(path: Path):
    """Verify write permissions before starting"""
    test_file = path / ".write_test_temp"

    try:
        test_file.write_text("test")
        test_file.unlink()
    except (PermissionError, OSError) as e:
        raise InsufficientPermissionsError(
            f"Cannot write to {path}. "
            f"Ensure you have write permissions.\n"
            f"Error: {e}"
        )
```

---

## 7. Logging and Audit Trail

### What's Logged

- File access attempts (paths only, not content)
- Sensitive files skipped
- Security errors and warnings
- Path validation failures
- Symlink following

### Log Levels

```python
import logging

# Security events
logger.warning("Skipping sensitive file: .env")
logger.warning("Symlink detected: link.txt -> /etc/passwd")

# Security violations
logger.error("Path traversal attempt: ../../../etc/passwd")
logger.error("Forbidden directory access: /sys")
```

### Audit Log Example

```
2024-01-20 10:30:15 INFO  ProjectPathValidator initialized for: /home/user/my-project
2024-01-20 10:30:16 DEBUG Validating path: src/main.py
2024-01-20 10:30:17 WARNING Skipping sensitive file: .env (Environment variables)
2024-01-20 10:30:18 WARNING Symlink detected: link.txt -> /etc/passwd
2024-01-20 10:30:18 ERROR SecurityError: Symlink attack detected
2024-01-20 10:30:19 INFO Analysis complete: 127 files, 3 sensitive skipped
```

---

## 8. Error Handling

### Fail Secure Principle

When in doubt, block the operation:

```python
try:
    validated_path = validator.validate(user_path)
except SecurityError as e:
    # Operation is BLOCKED
    logger.error(f"Security violation: {e}")
    raise  # Don't continue

except PathValidationError as e:
    # Invalid path, block operation
    logger.warning(f"Invalid path: {e}")
    raise
```

### Clear Error Messages

```python
# Good error message
SecurityError(
    "Symlink attack detected: link.txt -> /etc/passwd\n"
    "Target is outside project root: /home/user/project"
)

# Provides:
# - What happened (symlink attack)
# - Where (link.txt)
# - Why it's blocked (target outside project)
```

---

## 9. Testing

### Security Test Coverage

All security features have comprehensive tests:

- **Path Validation**: 20+ test cases
  - Valid paths
  - Path traversal attempts
  - Symlink attacks
  - Forbidden directories
  - Edge cases (Unicode, long paths, etc.)

- **Sensitive File Detection**: 30+ test cases
  - All sensitive file types
  - Custom patterns
  - Directory filtering
  - Case insensitivity
  - Performance with many files

- **Command Injection**: 10+ test cases
  - Shell injection attempts
  - Special characters in filenames
  - Safe subprocess usage

### Running Security Tests

```bash
# Run all security tests
pytest tests/security/ -v

# Run with coverage
pytest tests/security/ --cov=claude_force.security --cov-report=html

# Run specific security test
pytest tests/security/test_project_path_validator.py::TestSymlinkAttacks -v
```

---

## 10. Best Practices

### For Users

1. **Trust Your Instincts**: If claude-force blocks something, there's a reason
2. **Review Logs**: Check what was skipped and why
3. **Use Dry-Run**: Test with `--dry-run` before making changes
4. **Backup First**: Always have a git commit or backup
5. **Report Issues**: If something legitimate is blocked, report it

### For Developers

1. **Validate All Paths**: Use `ProjectPathValidator` for any user input
2. **Check Sensitivity**: Use `SensitiveFileDetector` before reading files
3. **No Shell Commands**: Never use `shell=True` with user input
4. **Test Security**: Write tests for security edge cases
5. **Log Security Events**: Log all security-relevant actions

### Code Review Checklist

When reviewing code that handles user files:

- [ ] All paths validated with `ProjectPathValidator`
- [ ] Sensitive files checked with `SensitiveFileDetector`
- [ ] No `shell=True` in subprocess calls
- [ ] No `os.system()` with user input
- [ ] Proper error handling (fail secure)
- [ ] Security tests added
- [ ] Audit logging in place

---

## 11. Incident Response

### If You Suspect a Security Issue

1. **Stop Using**: Stop using the affected feature immediately
2. **Document**: Note exactly what happened and when
3. **Report**: File a security issue at [security contact]
4. **Don't Share**: Don't publicly disclose until patched

### Reporting Security Issues

**DO NOT** create public GitHub issues for security vulnerabilities.

Instead:
- Email: security@claude-force.dev (if available)
- Use GitHub Security Advisories (private disclosure)
- Provide: Steps to reproduce, impact, suggested fix

---

## 12. Security Guarantees Summary

| Threat | Protection | Status |
|--------|-----------|--------|
| Path Traversal | ProjectPathValidator | ✅ Implemented |
| Symlink Attacks | Symlink validation | ✅ Implemented |
| Credential Exposure | SensitiveFileDetector | ✅ Implemented |
| Command Injection | No shell=True policy | ✅ Implemented |
| System File Access | Forbidden roots | ✅ Implemented |
| Data Loss | Backup/rollback | 🚧 In Progress |
| Insufficient Permissions | Permission checks | 🚧 In Progress |
| Concurrent Modification | File locking | 🚧 Planned |

---

## 13. Privacy Policy

### What Claude-Force Accesses

**Reads**:
- File and directory names (for analysis)
- File metadata (size, modification time)
- File content of non-sensitive files (for analysis)

**Does NOT Read**:
- Sensitive files (see list above)
- Files outside project boundary
- System files
- Other users' files

### What's Sent to APIs

When using AI agents:
- Code snippets (only non-sensitive files)
- File structure information
- Task descriptions

**Never sent**:
- Contents of sensitive files
- Credentials or secrets
- Personal information (unless in code comments)

### Data Retention

- Local analysis: No data leaves your machine
- API calls: Subject to provider's retention policy
- Logs: Stored locally only

---

## Questions?

If you have questions about security:
- Read this document thoroughly
- Check test files for examples
- Ask in GitHub Discussions
- For vulnerabilities: Use private disclosure

**Last Updated**: 2024-01-20
**Version**: 1.0.0
```

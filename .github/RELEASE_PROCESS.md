# Release Process

Step-by-step guide for creating a new release of claude-force.

## Prerequisites

- [ ] All tests passing (`pytest test_claude_system.py -v`)
- [ ] No outstanding critical bugs
- [ ] CHANGELOG updated with all changes
- [ ] Documentation up to date
- [ ] PyPI API token configured in GitHub Secrets

## Release Steps

### 1. Prepare Release

```bash
# Update version number
./scripts/bump-version.sh patch  # or minor, or major

# Review changes
git diff

# Commit version bump
git add .
git commit -m "chore: bump version to X.Y.Z"
```

### 2. Update CHANGELOG

Edit `CHANGELOG_V2.1.md` (or create new CHANGELOG if major version):

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature 1
- New feature 2

### Changed
- Updated behavior 1

### Fixed
- Bug fix 1
- Bug fix 2

### Security
- Security improvement 1
```

Commit the changelog:
```bash
git add CHANGELOG_V2.1.md
git commit -m "docs: update CHANGELOG for vX.Y.Z"
```

### 3. Create Git Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release version X.Y.Z

Major changes:
- Feature 1
- Feature 2
- Bug fix 1
"

# Verify tag
git tag -l -n9 vX.Y.Z
```

### 4. Push to GitHub

```bash
# Push commits
git push origin main  # or your release branch

# Push tags
git push origin --tags
```

### 5. Automated Release

GitHub Actions will automatically:
1. Build the package
2. Run `twine check`
3. Publish to PyPI
4. Create GitHub Release with artifacts
5. Generate release notes

Monitor the workflow at: https://github.com/khanh-vu/claude-force/actions

### 6. Verify Release

After workflow completes:

```bash
# Wait a few minutes for PyPI to update, then:
pip install --upgrade claude-force

# Verify version
pip show claude-force
claude-force --version
```

Expected output: `claude-force vX.Y.Z`

### 7. Announce Release

- [ ] GitHub Discussions announcement
- [ ] Update project README if needed
- [ ] Social media (if applicable)

## Testing a Release (TestPyPI)

Before creating a production release, test on TestPyPI:

### 1. Trigger Test Release Workflow

Go to GitHub Actions → "Test Release (TestPyPI)" → Run workflow

Enter version: `X.Y.Z-rc1` (release candidate)

### 2. Verify TestPyPI Installation

```bash
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  claude-force==X.Y.Z-rc1
```

### 3. Test the Installation

```bash
claude-force --version
claude-force --help
# Run basic commands to verify
```

### 4. Fix Issues if Found

If issues are found:
1. Fix the bugs
2. Increment RC version (rc2, rc3, etc.)
3. Repeat test release process

## Hotfix Releases

For urgent bug fixes:

```bash
# Create hotfix branch
git checkout -b hotfix/X.Y.Z main

# Make fixes
# ... commit changes ...

# Bump patch version
./scripts/bump-version.sh patch

# Tag and release
git tag -a vX.Y.Z -m "Hotfix: brief description"
git push origin hotfix/X.Y.Z --tags

# Merge back to main
git checkout main
git merge hotfix/X.Y.Z
git push origin main
```

## Release Checklist

### Pre-Release
- [ ] All tests passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] No `YOUR_USERNAME` or other placeholders
- [ ] All URLs point to correct locations

### Release
- [ ] Git tag created
- [ ] Tag pushed to GitHub
- [ ] GitHub Actions workflow triggered
- [ ] Workflow completed successfully
- [ ] PyPI package published
- [ ] GitHub Release created

### Post-Release
- [ ] Installation verified (`pip install claude-force`)
- [ ] Version verified (`claude-force --version`)
- [ ] Basic functionality tested
- [ ] Documentation accessible
- [ ] Release announced

## Rollback Procedure

If a release has critical issues:

### 1. Yank from PyPI

```bash
# Install twine
pip install twine

# Yank the problematic version
twine yank -r pypi claude-force X.Y.Z -m "Reason for yanking"
```

This removes the version from default pip install but keeps it available for users who explicitly request it.

### 2. Create Fixed Release

```bash
# Bump patch version
./scripts/bump-version.sh patch

# Make fixes
# ... commit ...

# Release as normal
git tag -a vX.Y.Z+1 -m "Fix for issue in vX.Y.Z"
git push --tags
```

## GitHub Secrets Required

Configure these secrets in GitHub repository settings:

- `PYPI_API_TOKEN`: PyPI API token for publishing
- `TEST_PYPI_API_TOKEN`: TestPyPI API token for testing

### Creating PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Create new token with scope "Entire account" or specific to claude-force
3. Copy token (starts with `pypi-`)
4. Add to GitHub Secrets as `PYPI_API_TOKEN`

### Creating TestPyPI Token

1. Go to https://test.pypi.org/manage/account/token/
2. Create token
3. Add to GitHub Secrets as `TEST_PYPI_API_TOKEN`

## Troubleshooting

### Workflow Failed: "Failed to upload to PyPI"

Check:
1. API token is valid
2. Version doesn't already exist on PyPI
3. Package passes `twine check`

### GitHub Release Not Created

Check:
1. `GITHUB_TOKEN` has write permissions
2. Tag format is correct (vX.Y.Z)
3. Workflow has `contents: write` permission

### Can't Install from PyPI

Wait 5-10 minutes for PyPI CDN to update, then try again.

## Version Numbering

Follow Semantic Versioning (semver):

- **Major** (X.0.0): Breaking changes, incompatible API changes
- **Minor** (x.Y.0): New features, backward compatible
- **Patch** (x.y.Z): Bug fixes, backward compatible

Examples:
- `2.1.0` → `2.1.1`: Bug fix (patch)
- `2.1.0` → `2.2.0`: New feature (minor)
- `2.1.0` → `3.0.0`: Breaking change (major)

## Support

For questions about the release process:
- Check GitHub Actions logs
- Review this document
- Open an issue: https://github.com/khanh-vu/claude-force/issues

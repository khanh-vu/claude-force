# Hotfix: Fix PyPI Publishing and Changelog Generation for v1.0.0 Release

## Summary

This PR fixes two critical issues preventing the v1.0.0 release from completing successfully:

1. **PyPI Trusted Publishing not configured** - Temporarily disabled to use API token method
2. **Changelog generation failing** - Tags weren't available after checking out main branch

## Changes

### 1. PyPI Publishing Fix (`.github/workflows/release.yml`)

**Problem**: Workflow tried to use PyPI Trusted Publishing, but the publisher hasn't been configured on PyPI.org yet.

**Solution**: Temporarily commented out the `environment` configuration to fall back to API token authentication:

```yaml
publish-pypi:
  # Temporarily disable environment to use API token instead of trusted publishing
  # environment:
  #   name: pypi
  #   url: https://pypi.org/p/claude-force
```

**Action Required**: Before merging, ensure `PYPI_API_TOKEN` secret is configured in repository settings.

### 2. Changelog Generation Fix (`.github/workflows/release.yml`)

**Problem**: After checking out `main` branch, tags weren't available for git-cliff to generate the changelog.

**Solution**:
- Added explicit `git fetch --force --tags` step
- Changed args from `--tag v$VERSION` to `--latest` for cleaner generation

```yaml
- name: Fetch all tags
  run: git fetch --force --tags

- name: Generate changelog with git-cliff
  args: --latest --output CHANGELOG.md
```

## Testing

After this PR is merged, the v1.0.0 release can be retried by:

```bash
# Delete the failed tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Recreate the tag (triggers the fixed workflow)
git tag v1.0.0
git push origin v1.0.0
```

## Impact

- ✅ **Low Risk**: Only affects release workflow
- ✅ **No Code Changes**: Only CI/CD configuration updates
- ✅ **Backward Compatible**: Doesn't affect existing functionality
- ✅ **Quick Revert**: Can easily revert if needed

## Post-Release Tasks

After v1.0.0 is successfully released, we can optionally:

1. Set up PyPI Trusted Publishing (recommended for security)
2. Re-enable the environment configuration in the workflow
3. Remove API token dependency

## Checklist

- [x] PyPI publishing environment temporarily disabled
- [x] Tag fetching added to changelog step
- [x] Changelog generation args updated
- [ ] `PYPI_API_TOKEN` secret configured in repository settings
- [ ] PR merged to main
- [ ] v1.0.0 tag recreated to trigger fixed workflow

## Related

- Fixes failed release: https://github.com/khanh-vu/claude-force/actions/runs/19387997710
- Original error: PyPI trusted publisher configuration missing
- Changelog error: Tags not accessible after main checkout

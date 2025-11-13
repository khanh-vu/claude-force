# Git Workflow Skill

## Overview
Best practices and patterns for Git workflows, commit conventions, branching strategies, and collaborative development.

## Capabilities
- Commit message conventions
- Branching strategies
- Pull request workflows
- Git best practices
- Conflict resolution
- Code review integration

---

## Commit Message Conventions

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Formatting, missing semicolons, etc. (no code change)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvement
- **test**: Adding or updating tests
- **chore**: Changes to build process or auxiliary tools
- **ci**: Changes to CI configuration files and scripts
- **revert**: Reverts a previous commit

### Examples

```bash
# Feature
git commit -m "feat(auth): add JWT authentication

Implemented JWT-based authentication with refresh tokens.
Added middleware for protected routes.

Closes #123"

# Bug fix
git commit -m "fix(api): resolve race condition in order processing

Added transaction locking to prevent duplicate orders.

Fixes #456"

# Documentation
git commit -m "docs(readme): update installation instructions

Added Docker setup instructions and troubleshooting section."

# Refactor
git commit -m "refactor(users): extract validation logic to separate module

Moved user validation functions to utils/validators.js
for better reusability and testing."

# Performance
git commit -m "perf(database): optimize user query with indexes

Added composite index on (email, status) for 10x query speedup.

Benchmark results:
- Before: 500ms avg
- After: 50ms avg"

# Test
git commit -m "test(auth): add integration tests for login flow

Added tests for successful login, failed login, and token refresh."

# Breaking change
git commit -m "feat(api)!: change user API response format

BREAKING CHANGE: User API now returns snake_case instead of camelCase.
Migration guide in docs/migrations/v2.md

Closes #789"
```

### Good Practices

✅ **Good Commits**:
```bash
feat(cart): add quantity validation
fix(checkout): prevent duplicate orders
docs(api): update authentication examples
test(users): add edge case tests for email validation
```

❌ **Bad Commits**:
```bash
fixed stuff
WIP
update
changes
asdf
```

---

## Branching Strategies

### Git Flow

```
main (production)
  └─ develop (integration)
       ├─ feature/user-authentication
       ├─ feature/shopping-cart
       ├─ bugfix/payment-error
       ├─ release/v1.2.0
       └─ hotfix/critical-security-fix
```

**Branch Types**:
- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: New features
- **bugfix/***: Bug fixes
- **release/***: Release preparation
- **hotfix/***: Production hotfixes

**Workflow**:
```bash
# Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication

# Work on feature
git add .
git commit -m "feat(auth): add login form"

# Keep feature branch updated
git checkout develop
git pull origin develop
git checkout feature/user-authentication
git merge develop

# Finish feature
git checkout develop
git merge feature/user-authentication
git push origin develop
git branch -d feature/user-authentication
```

### GitHub Flow (Simpler)

```
main
  ├─ feature/add-dark-mode
  ├─ fix/navbar-responsive
  └─ docs/update-readme
```

**Workflow**:
```bash
# Create feature branch
git checkout -b feature/add-dark-mode

# Make changes and commit
git add .
git commit -m "feat(ui): add dark mode toggle"

# Push and create pull request
git push -u origin feature/add-dark-mode
# Open PR on GitHub

# After PR is approved and merged
git checkout main
git pull origin main
git branch -d feature/add-dark-mode
```

### Trunk-Based Development

```
main (always deployable)
  ├─ short-lived-feature-1 (1-2 days)
  └─ short-lived-feature-2 (1-2 days)
```

**Best for**:
- CI/CD environments
- Small, frequent changes
- Feature flags

---

## Branch Naming Conventions

```
<type>/<description>

Examples:
feature/user-authentication
feature/shopping-cart-checkout
bugfix/payment-processing-error
hotfix/security-vulnerability-CVE-2023-1234
refactor/extract-validation-logic
docs/update-api-documentation
test/add-integration-tests
```

---

## Pull Request Workflow

### 1. Create Quality PR

**PR Title**:
```
feat(auth): implement JWT authentication
```

**PR Description**:
```markdown
## Summary
Implements JWT-based authentication with refresh tokens.

## Changes
- Added JWT token generation and validation
- Created authentication middleware
- Implemented refresh token endpoint
- Added token blacklisting for logout

## Testing
- [x] Unit tests for token generation
- [x] Integration tests for auth endpoints
- [x] Manual testing of login/logout flow

## Screenshots
[If UI changes]

## Breaking Changes
None

## Checklist
- [x] Code follows project style guide
- [x] Tests added and passing
- [x] Documentation updated
- [x] No console.log statements
- [x] No commented-out code
```

### 2. Before Creating PR

```bash
# Update from main
git checkout main
git pull origin main
git checkout feature/my-feature
git rebase main

# Run tests
npm test

# Run linter
npm run lint

# Check for sensitive data
git diff main

# Push to remote
git push origin feature/my-feature --force-with-lease
```

### 3. Code Review Process

**Reviewer Checklist**:
- [ ] Code meets requirements
- [ ] Tests are comprehensive
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Code is readable and maintainable
- [ ] Documentation is updated
- [ ] No unnecessary changes

**Review Comments**:
```markdown
**Blocking**: SQL injection vulnerability on line 45
❌ Use parameterized queries instead of string concatenation

**Suggestion**: Consider extracting this logic
💡 This validation logic is duplicated in 3 places. Consider extracting to a utility function.

**Praise**: Excellent error handling
✅ Great job on comprehensive error handling with descriptive messages.

**Question**: Why did you choose approach X?
❓ Is there a specific reason for using X over Y? I'm curious about the trade-offs.
```

---

## Git Best Practices

### 1. Write Atomic Commits

```bash
# ❌ Bad: One commit with multiple unrelated changes
git add .
git commit -m "fix login, update readme, refactor utils"

# ✅ Good: Separate commits for each logical change
git add src/auth/login.js
git commit -m "fix(auth): resolve login redirect issue"

git add README.md
git commit -m "docs(readme): update installation instructions"

git add src/utils/validators.js
git commit -m "refactor(utils): extract email validation"
```

### 2. Commit Early and Often

```bash
# Commit after completing each logical unit of work
git add src/components/Button.tsx
git commit -m "feat(ui): add Button component structure"

git add src/components/Button.test.tsx
git commit -m "test(ui): add Button component tests"

git add src/components/Button.stories.tsx
git commit -m "docs(ui): add Button Storybook stories"
```

### 3. Use Interactive Staging

```bash
# Stage specific parts of files
git add -p

# Stage specific files
git add src/auth/login.js src/auth/logout.js

# Check what will be committed
git diff --staged
```

### 4. Keep History Clean

```bash
# Interactive rebase to clean up commits before PR
git rebase -i main

# Squash fixup commits
git commit --fixup <commit-hash>
git rebase -i --autosquash main

# Amend last commit (only if not pushed)
git commit --amend

# Change commit message
git commit --amend -m "new message"
```

---

## Handling Conflicts

### Merge Conflicts

```bash
# Update your branch
git fetch origin
git merge origin/main

# If conflicts occur
# 1. Open conflicted files
# 2. Resolve conflicts (look for <<<<<<<, =======, >>>>>>>)
# 3. Stage resolved files
git add resolved-file.js

# 4. Complete merge
git commit
```

### Rebase Conflicts

```bash
# Start rebase
git rebase main

# If conflicts occur
# 1. Resolve conflicts in files
# 2. Stage resolved files
git add resolved-file.js

# 3. Continue rebase
git rebase --continue

# Or abort if needed
git rebase --abort
```

---

## Useful Git Commands

### Inspection

```bash
# View commit history
git log --oneline --graph --all

# View specific file history
git log --follow --all -- path/to/file

# View changes in commit
git show <commit-hash>

# Find who changed a line
git blame path/to/file

# Search commit messages
git log --grep="auth"

# Search code changes
git log -S"functionName"
```

### Undoing Changes

```bash
# Discard local changes
git checkout -- file.js

# Unstage file
git reset HEAD file.js

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert commit (creates new commit)
git revert <commit-hash>

# Recover deleted branch
git reflog
git checkout -b recovered-branch <commit-hash>
```

### Stashing

```bash
# Stash current changes
git stash

# Stash with message
git stash save "WIP: implementing feature"

# List stashes
git stash list

# Apply stash
git stash pop

# Apply specific stash
git stash apply stash@{2}

# Delete stash
git stash drop stash@{2}
```

### Remote Operations

```bash
# Add remote
git remote add origin <url>

# Update remote URL
git remote set-url origin <new-url>

# Fetch all branches
git fetch --all

# Prune deleted remote branches
git fetch --prune

# Push with upstream
git push -u origin feature-branch

# Force push safely
git push --force-with-lease

# Delete remote branch
git push origin --delete feature-branch
```

---

## Git Hooks

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "Running pre-commit checks..."

# Run linter
npm run lint
if [ $? -ne 0 ]; then
  echo "❌ Linting failed. Please fix errors before committing."
  exit 1
fi

# Run tests
npm test
if [ $? -ne 0 ]; then
  echo "❌ Tests failed. Please fix tests before committing."
  exit 1
fi

# Check for console.log
if git diff --cached | grep -i "console.log"; then
  echo "❌ console.log found. Please remove before committing."
  exit 1
fi

echo "✅ Pre-commit checks passed!"
```

### Using Husky

```bash
npm install --save-dev husky

npx husky install

npx husky add .husky/pre-commit "npm test"
npx husky add .husky/pre-commit "npm run lint"
```

---

## .gitignore Best Practices

```gitignore
# Dependencies
node_modules/
vendor/
*.pyc
__pycache__/

# Build outputs
dist/
build/
*.min.js
*.min.css

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test coverage
coverage/
.nyc_output/

# Temporary files
tmp/
temp/
*.tmp

# But keep important empty directories
!.gitkeep
```

---

## Collaborative Workflows

### Reviewing PRs

```bash
# Fetch PR locally
git fetch origin pull/123/head:pr-123
git checkout pr-123

# Test changes
npm install
npm test

# Leave feedback on GitHub
```

### Syncing Fork

```bash
# Add upstream remote
git remote add upstream https://github.com/original/repo.git

# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

---

## Git Aliases

Add to `~/.gitconfig`:

```ini
[alias]
  st = status
  co = checkout
  br = branch
  ci = commit
  unstage = reset HEAD --
  last = log -1 HEAD
  lg = log --oneline --graph --all --decorate
  amend = commit --amend --no-edit
  pushf = push --force-with-lease
  undo = reset --soft HEAD~1
  wip = commit -am "WIP"
  cleanup = !git branch --merged | grep -v '\\*\\|main\\|develop' | xargs -n 1 git branch -d
```

Usage:
```bash
git st          # git status
git lg          # git log --oneline --graph --all
git amend       # git commit --amend --no-edit
git cleanup     # delete merged branches
```

---

## Troubleshooting

### Common Issues

**Issue**: Committed to wrong branch
```bash
# Move commits to correct branch
git branch feature-branch
git reset --hard HEAD~1
git checkout feature-branch
```

**Issue**: Need to edit old commit
```bash
# Interactive rebase
git rebase -i HEAD~5
# Mark commit as 'edit', make changes, then:
git add .
git commit --amend
git rebase --continue
```

**Issue**: Large file committed accidentally
```bash
# Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/large-file" \
  --prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner (faster)
java -jar bfg.jar --delete-files large-file repo.git
```

---

## Quick Reference

### Common Workflows

**Start new feature**:
```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature
```

**Commit changes**:
```bash
git add .
git commit -m "feat(scope): description"
```

**Update feature branch**:
```bash
git checkout main
git pull origin main
git checkout feature/my-feature
git rebase main
```

**Create PR**:
```bash
git push -u origin feature/my-feature
# Open PR on GitHub/GitLab
```

**After PR merged**:
```bash
git checkout main
git pull origin main
git branch -d feature/my-feature
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-13
**Maintained By**: Development Team

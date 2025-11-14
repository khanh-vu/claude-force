#!/bin/bash
# Version bump script for claude-force
# Usage: ./scripts/bump-version.sh <major|minor|patch>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current version from setup.py
CURRENT_VERSION=$(grep "version=" setup.py | sed 's/.*version="\([^"]*\)".*/\1/')

echo -e "${GREEN}Current version: ${CURRENT_VERSION}${NC}"

# Parse version parts
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Determine new version based on bump type
BUMP_TYPE="${1:-patch}"

case "$BUMP_TYPE" in
  major)
    NEW_MAJOR=$((MAJOR + 1))
    NEW_VERSION="${NEW_MAJOR}.0.0"
    ;;
  minor)
    NEW_MINOR=$((MINOR + 1))
    NEW_VERSION="${MAJOR}.${NEW_MINOR}.0"
    ;;
  patch)
    NEW_PATCH=$((PATCH + 1))
    NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"
    ;;
  *)
    echo -e "${RED}Error: Invalid bump type '${BUMP_TYPE}'${NC}"
    echo "Usage: $0 <major|minor|patch>"
    exit 1
    ;;
esac

echo -e "${YELLOW}New version: ${NEW_VERSION}${NC}"

# Ask for confirmation
read -p "Bump version from ${CURRENT_VERSION} to ${NEW_VERSION}? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Aborted${NC}"
    exit 1
fi

# Update version in files
echo -e "${GREEN}Updating version in files...${NC}"

# Update setup.py
sed -i "s/version=\"${CURRENT_VERSION}\"/version=\"${NEW_VERSION}\"/" setup.py

# Update pyproject.toml
sed -i "s/version = \"${CURRENT_VERSION}\"/version = \"${NEW_VERSION}\"/" pyproject.toml

# Update __init__.py
if [ -f "claude_force/__init__.py" ]; then
    sed -i "s/__version__ = \"${CURRENT_VERSION}\"/__version__ = \"${NEW_VERSION}\"/" claude_force/__init__.py
fi

# Update docs/conf.py
if [ -f "docs/conf.py" ]; then
    sed -i "s/release = '${CURRENT_VERSION}'/release = '${NEW_VERSION}'/" docs/conf.py
    sed -i "s/version = '${CURRENT_VERSION}'/version = '${NEW_VERSION}'/" docs/conf.py
fi

echo -e "${GREEN}Version bumped successfully!${NC}"
echo -e "${YELLOW}Files updated:${NC}"
echo "  - setup.py"
echo "  - pyproject.toml"
echo "  - claude_force/__init__.py"
echo "  - docs/conf.py"

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review changes: git diff"
echo "2. Commit: git add . && git commit -m \"chore: bump version to ${NEW_VERSION}\""
echo "3. Tag: git tag -a v${NEW_VERSION} -m \"Release version ${NEW_VERSION}\""
echo "4. Push: git push && git push --tags"
echo "5. GitHub Actions will automatically create the release"

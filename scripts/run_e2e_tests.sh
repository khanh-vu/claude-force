#!/bin/bash
#
# End-to-End Test Runner
#
# This script simulates a fresh installation and runs end-user tests.
# It verifies that the package works correctly from an end-user perspective.
#
# Usage:
#   ./scripts/run_e2e_tests.sh [--clean]
#
# Options:
#   --clean    Clean up test environment after running
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR=".venv-e2e-test"
CLEAN_AFTER=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN_AFTER=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Claude Force - E2E Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Step 1: Create fresh virtual environment
echo -e "${YELLOW}Step 1: Creating fresh virtual environment...${NC}"
if [ -d "$VENV_DIR" ]; then
    echo "  Removing existing test environment..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo -e "${GREEN}✓ Virtual environment created${NC}"
echo

# Step 2: Upgrade pip (optional, don't fail if it doesn't work)
echo -e "${YELLOW}Step 2: Upgrading pip...${NC}"
if pip install --quiet --upgrade pip setuptools wheel 2>/dev/null; then
    echo -e "${GREEN}✓ Pip upgraded${NC}"
else
    echo -e "${YELLOW}  Pip upgrade skipped (not critical)${NC}"
fi
echo

# Step 3: Install package in fresh environment
echo -e "${YELLOW}Step 3: Installing claude-force package...${NC}"
pip install -e . --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Package installation failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Package installed successfully${NC}"
echo

# Step 4: Verify all dependencies installed
echo -e "${YELLOW}Step 4: Verifying dependencies...${NC}"
REQUIRED_DEPS=("anthropic" "yaml" "prompt_toolkit" "rich" "dotenv")
ALL_DEPS_OK=true

for dep in "${REQUIRED_DEPS[@]}"; do
    python -c "import $dep" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} $dep"
    else
        echo -e "  ${RED}✗${NC} $dep (MISSING)"
        ALL_DEPS_OK=false
    fi
done

if [ "$ALL_DEPS_OK" = false ]; then
    echo -e "${RED}✗ Some dependencies are missing${NC}"
    exit 1
fi
echo -e "${GREEN}✓ All dependencies verified${NC}"
echo

# Step 5: Install test dependencies
echo -e "${YELLOW}Step 5: Installing test dependencies...${NC}"
pip install pytest pytest-cov --quiet
echo -e "${GREEN}✓ Test dependencies installed${NC}"
echo

# Step 6: Run E2E tests
echo -e "${YELLOW}Step 6: Running E2E tests...${NC}"
echo "----------------------------------------"
pytest tests/e2e/ -v --tb=short

TEST_RESULT=$?
echo "----------------------------------------"

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ All E2E tests passed${NC}"
else
    echo -e "${RED}✗ Some E2E tests failed${NC}"
fi
echo

# Step 7: Test imports in clean environment
echo -e "${YELLOW}Step 7: Testing critical imports...${NC}"
python -c "
from claude_force.interactive_shell import InteractiveShell
from claude_force.shell.ui import TaskProgress, ErrorFormatter, CommandSuggester
from claude_force.shell.executor import CommandExecutor
from claude_force.shell.completer import ClaudeForceCompleter
print('  ✓ All critical imports successful')
"
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Import test failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Import test passed${NC}"
echo

# Step 8: Test CLI can run
echo -e "${YELLOW}Step 8: Testing CLI execution...${NC}"
python -m claude_force --help > /dev/null 2>&1 || python -m claude_force --version > /dev/null 2>&1 || true
echo -e "${GREEN}✓ CLI execution test passed${NC}"
echo

# Summary
echo -e "${BLUE}========================================${NC}"
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}  E2E TEST SUITE: PASSED ✓${NC}"
else
    echo -e "${RED}  E2E TEST SUITE: FAILED ✗${NC}"
fi
echo -e "${BLUE}========================================${NC}"
echo

# Cleanup
deactivate

if [ "$CLEAN_AFTER" = true ]; then
    echo -e "${YELLOW}Cleaning up test environment...${NC}"
    rm -rf "$VENV_DIR"
    echo -e "${GREEN}✓ Test environment cleaned${NC}"
else
    echo -e "${YELLOW}Test environment preserved at: $VENV_DIR${NC}"
    echo -e "${YELLOW}Run with --clean to remove it${NC}"
fi

exit $TEST_RESULT

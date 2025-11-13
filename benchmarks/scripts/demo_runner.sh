#!/bin/bash
#
# Demo Runner Script
#
# This script runs a complete demo of the benchmark system with nice formatting.
# Perfect for recording as a GIF or video.
#

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Functions
print_header() {
    echo -e "\n${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}${BOLD}  $1${NC}"
    echo -e "${BLUE}${BOLD}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${YELLOW}▶${NC} ${BOLD}$1${NC}"
    sleep 1
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
    sleep 0.5
}

print_info() {
    echo -e "${PURPLE}ℹ${NC} $1"
}

# Main demo
clear

print_header "🚀 Claude Multi-Agent System Benchmark Demo"

echo -e "${BOLD}System Overview:${NC}"
echo "  • 15 Specialized Agents"
echo "  • 6 Coordinated Workflows"
echo "  • 9 Integrated Skills"
echo "  • Real-world Scenarios"
echo ""
sleep 2

# Step 1: Show directory structure
print_step "Step 1: Benchmark Structure"
echo ""
tree benchmarks/ -L 2 -I '*.json|*.html|__pycache__' || ls -R benchmarks/
echo ""
sleep 2

# Step 2: Run benchmarks
print_header "📊 Running Benchmarks"
print_step "Executing benchmark suite..."
echo ""
python3 benchmarks/scripts/run_all.py
print_success "Benchmarks completed!"
sleep 1

# Step 3: Generate visual report
print_header "📈 Generating Visual Report"
print_step "Creating ASCII charts and metrics..."
echo ""
python3 benchmarks/scripts/generate_visual_report.py
print_success "Visual report generated!"
sleep 1

# Step 4: Generate dashboard
print_header "🎨 Building Interactive Dashboard"
print_step "Generating HTML dashboard..."
echo ""
python3 benchmarks/scripts/generate_dashboard.py
print_success "Dashboard ready!"
sleep 1

# Step 5: Summary
print_header "✨ Demo Complete"

echo -e "${BOLD}Generated Files:${NC}"
echo "  📊 JSON Reports:        benchmarks/reports/results/*.json"
echo "  🎨 HTML Dashboard:      benchmarks/reports/dashboard/index.html"
echo "  📈 Visual Report:       (displayed above)"
echo ""

echo -e "${BOLD}Next Steps:${NC}"
echo "  1. Open dashboard:      open benchmarks/reports/dashboard/index.html"
echo "  2. View scenarios:      ls benchmarks/scenarios/*/  "
echo "  3. Capture screenshots: See benchmarks/screenshots/README.md"
echo ""

print_info "Benchmark system ready for demonstration! 🎉"
echo ""

# Benchmark Scripts

Automation and visualization scripts for the Claude Multi-Agent System benchmarks.

## 📜 Available Scripts

### 1. `run_all.py`
**Purpose**: Execute all benchmarks and generate JSON reports

**Usage**:
```bash
python3 benchmarks/scripts/run_all.py
```

**Output**:
- `benchmarks/reports/results/complete_benchmark.json` - Full results
- `benchmarks/reports/results/agent_selection.json` - Agent selection metrics
- Terminal output with progress and summary

**What it does**:
1. Runs agent selection performance tests
2. Analyzes available scenarios
3. Generates aggregate metrics
4. Saves JSON reports

---

### 2. `generate_visual_report.py`
**Purpose**: Create beautiful ASCII art terminal report

**Usage**:
```bash
python3 benchmarks/scripts/generate_visual_report.py
```

**Output**: Terminal display with:
- System overview boxes
- Performance bar charts (████████░░░░)
- Accuracy distribution graphs
- Success indicators with emojis
- Scenario catalog with color coding

**Perfect for**:
- Terminal screenshots
- Quick status checks
- CI/CD pipeline output
- Command-line demos

---

### 3. `generate_dashboard.py`
**Purpose**: Generate interactive HTML dashboard

**Usage**:
```bash
python3 benchmarks/scripts/generate_dashboard.py
```

**Output**:
- `benchmarks/reports/dashboard/index.html` - Interactive dashboard

**Features**:
- Responsive design
- Gradient color scheme
- Hover effects on cards
- Progress bars
- Sortable tables
- Mobile-friendly

**Perfect for**:
- Presentations
- Stakeholder demos
- Documentation
- Web sharing

---

### 4. `demo_runner.sh`
**Purpose**: Automated demo with visual effects

**Usage**:
```bash
./benchmarks/scripts/demo_runner.sh
```

**What it shows**:
1. **Directory structure** - File organization
2. **Benchmark execution** - Live progress
3. **Visual report** - ASCII charts
4. **Dashboard generation** - HTML creation
5. **Summary** - Next steps

**Features**:
- Colored output (blue headers, green checkmarks)
- Step-by-step progression
- Automatic pauses for readability
- Professional formatting

**Perfect for**:
- Screen recordings
- Live demos
- Training sessions
- Video tutorials

---

## 🎬 Recording a Demo

### Option 1: Terminal Recording (asciinema)

```bash
# Install asciinema
brew install asciinema  # macOS
# or
sudo apt install asciinema  # Linux

# Record demo
asciinema rec demo.cast

# Run demo script
./benchmarks/scripts/demo_runner.sh

# Stop recording (Ctrl+D)

# Play recording
asciinema play demo.cast

# Upload to share
asciinema upload demo.cast
```

**Advantages**:
- Small file size
- Copy-paste from recording
- Shareable URL
- Perfect terminal representation

### Option 2: Screen Recording (Video)

#### macOS (Kap)
```bash
# Install Kap
brew install --cask kap

# 1. Open Kap
# 2. Select terminal window
# 3. Click record
# 4. Run: ./benchmarks/scripts/demo_runner.sh
# 5. Stop recording
# 6. Export as GIF or MP4
```

#### Linux (Peek)
```bash
# Install Peek
sudo apt install peek  # Ubuntu/Debian
# or
flatpak install peek   # Flatpak

# 1. Open Peek
# 2. Position over terminal
# 3. Click record
# 4. Run: ./benchmarks/scripts/demo_runner.sh
# 5. Stop recording
# 6. Save as GIF
```

#### Cross-platform (OBS Studio)
```bash
# Install OBS Studio
# Download from: https://obsproject.com/

# Setup:
# 1. Add "Window Capture" source
# 2. Select terminal window
# 3. Start recording
# 4. Run demo
# 5. Stop recording
# 6. Video saved to ~/Videos/
```

### Option 3: Dashboard Recording

For HTML dashboard:

```bash
# 1. Generate dashboard
python3 benchmarks/scripts/generate_dashboard.py

# 2. Open in browser
open benchmarks/reports/dashboard/index.html

# 3. Use browser dev tools
# Chrome: Cmd+Shift+P → "Capture full size screenshot"

# Or record scrolling:
# - Use OBS Studio
# - Use Loom (https://loom.com)
# - Use QuickTime Screen Recording (macOS)
```

---

## 📸 Screenshot Guidelines

### Terminal Screenshots

**Preparation**:
```bash
# Use large terminal window (100+ columns)
clear

# Set nice color scheme
# Recommended: Dracula, Solarized Dark, Nord

# Run visual report
python3 benchmarks/scripts/generate_visual_report.py

# Take screenshot (macOS: Cmd+Shift+4)
# Select terminal window
```

**Settings**:
- Font size: 14-16pt
- Terminal size: 80-120 columns x 30-40 rows
- Theme: Dark theme with good contrast
- No distracting background

### Dashboard Screenshots

**Preparation**:
```bash
# Generate fresh dashboard
python3 benchmarks/scripts/generate_dashboard.py

# Open in clean browser profile
open -a "Google Chrome" --new --args --incognito \
  benchmarks/reports/dashboard/index.html

# Set window size: 1920x1080
# Zoom: 100%
```

**What to capture**:
1. **Full page**: Chrome DevTools → Cmd+Shift+P → "Capture full size screenshot"
2. **Executive summary**: Top metrics cards section
3. **Performance charts**: Agent selection metrics
4. **Scenario catalog**: Table with all scenarios
5. **Detailed results**: Test results table

---

## 🎨 Creating Attractive Demos

### Tips for Terminal Demos

1. **Use colored output**: Leverage the demo_runner.sh colors
2. **Pause appropriately**: Let viewers read output
3. **Clear screen**: Start fresh with `clear`
4. **Show context**: Display directory structure first
5. **Highlight success**: Use visual indicators (✓, ✅, 🎉)

### Tips for Dashboard Demos

1. **Smooth scrolling**: Scroll slowly through sections
2. **Hover effects**: Show interactive elements
3. **Highlight key metrics**: Point out important numbers
4. **Responsive demo**: Show mobile view if relevant
5. **Browser dev tools**: Hide if not needed

### Demo Script Example

```bash
#!/bin/bash
# 30-second demo script

clear
echo "🚀 Claude Multi-Agent System Benchmark Demo"
sleep 2

echo -e "\n📁 Benchmarks available:"
ls benchmarks/scenarios/*/
sleep 2

echo -e "\n⚡ Running benchmarks..."
python3 benchmarks/scripts/run_all.py | tail -20
sleep 2

echo -e "\n📊 Visual report:"
python3 benchmarks/scripts/generate_visual_report.py | head -30
sleep 3

echo -e "\n🎨 Dashboard ready!"
echo "   Open: benchmarks/reports/dashboard/index.html"
sleep 1
```

---

## 🔄 Continuous Demo Recording

For CI/CD pipelines:

```yaml
# .github/workflows/benchmark-demo.yml
name: Generate Benchmark Demo

on:
  push:
    branches: [main]

jobs:
  demo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run benchmarks
        run: python3 benchmarks/scripts/run_all.py

      - name: Generate dashboard
        run: python3 benchmarks/scripts/generate_dashboard.py

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: benchmark-results
          path: benchmarks/reports/
```

---

## 📊 Output Examples

### run_all.py output:
```
======================================================================
CLAUDE MULTI-AGENT SYSTEM - COMPREHENSIVE BENCHMARK
======================================================================
Test 1/10: Add a health check endpoint to the API...
  ⚠️ Accuracy: 50.00% | Time: 0.03ms

✅ ALL BENCHMARKS COMPLETED SUCCESSFULLY
```

### generate_visual_report.py output:
```
Average Accuracy               ██████████████████████████████░░░░░░░░░░  75.0%
✅ Agent Coverage             100%  │  All agents used in workflows
```

### generate_dashboard.py output:
```
✅ Dashboard generated: benchmarks/reports/dashboard/index.html
📊 Open in browser: file:///path/to/dashboard/index.html
```

---

## 🆘 Troubleshooting

### "Python module not found"
```bash
# Ensure you're in the project root
cd /path/to/claude-force

# Run with python3
python3 benchmarks/scripts/run_all.py
```

### "No results file found"
```bash
# Generate results first
python3 benchmarks/scripts/run_all.py

# Then generate dashboard
python3 benchmarks/scripts/generate_dashboard.py
```

### "Permission denied"
```bash
# Make scripts executable
chmod +x benchmarks/scripts/*.sh
chmod +x benchmarks/scripts/*.py
```

---

**Last Updated**: 2025-11-13
**Version**: 1.0.0

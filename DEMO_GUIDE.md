# 🎬 Quick Demo & Screenshot Guide

## 30-Second Demo Recording

### Option 1: Terminal Demo (Best for README)

```bash
# 1. Record with asciinema
asciinema rec claude-force-demo.cast

# 2. Run the demo
./benchmarks/scripts/demo_runner.sh

# 3. Stop recording (Ctrl+D)

# 4. Convert to GIF (optional)
agg claude-force-demo.cast demo.gif

# 5. Upload and get shareable link
asciinema upload claude-force-demo.cast
```

### Option 2: Screen Recording (Best for presentations)

```bash
# macOS - Using Kap
# 1. Install: brew install --cask kap
# 2. Open Kap, select terminal window
# 3. Run: ./benchmarks/scripts/demo_runner.sh
# 4. Export as GIF or MP4

# Linux - Using Peek
# 1. Install: sudo apt install peek
# 2. Position Peek over terminal
# 3. Run: ./benchmarks/scripts/demo_runner.sh
# 4. Save GIF
```

---

## 5 Essential Screenshots

### 1. Terminal Visual Report ⭐
```bash
# Generate beautiful ASCII charts
python3 benchmarks/scripts/generate_visual_report.py

# Take screenshot (macOS: Cmd+Shift+4, select terminal)
# Save as: screenshots/terminal_visual_report.png
```

**What you'll capture**:
```
================================================================================
                  🚀 CLAUDE MULTI-AGENT SYSTEM BENCHMARK REPORT
================================================================================

Average Accuracy               ██████████████████████████████░░░░░░░░░░  75.0%

✅ Agent Coverage             100%  │  All agents used in workflows
```

---

### 2. HTML Dashboard Overview ⭐
```bash
# Generate dashboard
python3 benchmarks/scripts/generate_dashboard.py

# Open in browser
open benchmarks/reports/dashboard/index.html

# Chrome: Cmd+Shift+P → "Capture full size screenshot"
# Save as: screenshots/dashboard_overview.png
```

**What you'll capture**: Beautiful gradient cards, charts, tables

---

### 3. Benchmark Execution ⭐
```bash
# Run benchmarks
python3 benchmarks/scripts/run_all.py

# While running, take screenshot showing:
# - Test progress (Test 1/10...)
# - Accuracy percentages (✅ 100%, ⚠️ 75%)
# - Success message

# Save as: screenshots/benchmark_execution.png
```

---

### 4. Scenario Catalog
```bash
# Show available scenarios
tree benchmarks/scenarios/

# Or list with descriptions
cat benchmarks/README.md | grep -A 3 "SIMPLE\|MEDIUM\|COMPLEX"

# Save as: screenshots/scenario_catalog.png
```

---

### 5. System Architecture
```bash
# Display the architecture diagram
head -30 benchmarks/README.md

# Shows the ASCII art system overview
# Save as: screenshots/system_architecture.png
```

---

## Quick GIF Creation

### For GitHub README

```bash
# 1. Create optimized GIF (800px wide, 10fps)
ffmpeg -i demo.mp4 -vf "fps=10,scale=800:-1:flags=lanczos" demo.gif

# 2. Optimize size
gifsicle -O3 --colors 256 demo.gif -o demo-optimized.gif

# 3. Add to README
echo "![Demo](./screenshots/demo-optimized.gif)" >> README.md
```

---

## One-Command Demo

```bash
# Run everything and generate all outputs
./benchmarks/scripts/demo_runner.sh && \
python3 benchmarks/scripts/generate_visual_report.py && \
python3 benchmarks/scripts/generate_dashboard.py && \
echo "✅ All demo files generated!"
```

---

## Where to Add Screenshots

### In Main README (.claude/README.md)
```markdown
## 📊 Benchmarks & Demo

![Benchmark Results](../screenshots/terminal_visual_report.png)

See full interactive dashboard: [View Dashboard](./benchmarks/reports/dashboard/index.html)
```

### In Benchmark README (benchmarks/README.md)
```markdown
## Visual Output

Terminal Report:
![Terminal Report](screenshots/terminal_visual_report.png)

Dashboard:
![Dashboard](screenshots/dashboard_overview.png)
```

### In GitHub Issues/PRs
```markdown
## Demo

![Demo GIF](https://user-images.githubusercontent.com/YOUR_IMAGE_URL.gif)
```

---

## Recording Settings

### Terminal Settings
- **Font**: Monaco, Menlo, or Fira Code
- **Size**: 14-16pt
- **Window**: 100-120 columns x 30-40 rows
- **Theme**: Dracula, Solarized Dark, or Nord
- **Background**: Solid color (no transparency)

### Browser Settings
- **Window**: 1920x1080
- **Zoom**: 100%
- **Mode**: Incognito/Private (clean UI)
- **DevTools**: Closed

### Screen Recording
- **Resolution**: 1920x1080 or higher
- **FPS**: 30fps for video, 10fps for GIF
- **Format**: MP4 for video, GIF for animations
- **Max GIF size**: 5MB for GitHub

---

## Tools Installation

```bash
# macOS
brew install asciinema          # Terminal recording
brew install --cask kap         # Screen recording (GIF)
brew install gifsicle           # GIF optimization
brew install ffmpeg             # Video conversion

# Linux (Ubuntu/Debian)
sudo apt install asciinema peek gifsicle ffmpeg

# Verify installation
asciinema --version
ffmpeg -version
```

---

## Troubleshooting

### GIF too large
```bash
# Reduce size
gifsicle -O3 --colors 128 --lossy=80 input.gif -o output.gif

# Or reduce dimensions
ffmpeg -i input.gif -vf "scale=600:-1" output.gif
```

### Terminal colors not showing
```bash
# Ensure terminal supports 256 colors
echo $TERM  # Should show: xterm-256color

# Set if needed
export TERM=xterm-256color
```

### Dashboard not loading
```bash
# Regenerate
rm benchmarks/reports/dashboard/index.html
python3 benchmarks/scripts/generate_dashboard.py

# Check file exists
ls -lh benchmarks/reports/dashboard/index.html
```

---

## Share Your Demo!

Once you have screenshots/recordings:

1. **Add to repository**: `git add screenshots/` and commit
2. **Update README**: Add images with relative paths
3. **Create GitHub Release**: Attach demo files
4. **Tweet/Blog**: Share your setup with the community!

---

**Quick Reference**: See `benchmarks/screenshots/README.md` for detailed guides

**Need help?** Check `benchmarks/scripts/README.md` for troubleshooting

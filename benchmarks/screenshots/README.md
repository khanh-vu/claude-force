# Benchmark Screenshots & Recordings

This directory contains visual assets demonstrating the Claude Multi-Agent System in action.

## 📸 Required Screenshots

### 1. Dashboard Overview
**File**: `01_dashboard_overview.png`
**What to capture**:
- Full dashboard view showing all metrics
- Executive summary cards
- Agent selection performance
- Scenario catalog

**How to capture**:
```bash
# Open dashboard
open benchmarks/reports/dashboard/index.html

# Take full-page screenshot
# Chrome: Cmd+Shift+P → "Capture full size screenshot"
# Firefox: Right-click → "Take a Screenshot" → "Save full page"
```

### 2. Agent Selection Metrics
**File**: `02_agent_selection_metrics.png`
**What to capture**:
- Agent selection accuracy charts
- Performance distribution
- Timing metrics

### 3. Scenario Catalog
**File**: `03_scenario_catalog.png`
**What to capture**:
- List of all available scenarios
- Simple, Medium, Complex categorization
- Status badges

### 4. Detailed Test Results
**File**: `04_detailed_results.png`
**What to capture**:
- Test results table
- Accuracy badges
- Agent selections vs expected

### 5. Terminal Output
**File**: `05_terminal_benchmark_run.png`
**What to capture**:
- Running `python3 benchmarks/scripts/run_all.py`
- Console output with progress
- Success messages

## 🎥 Recommended Screen Recordings

### 1. Complete Benchmark Run
**File**: `demo_benchmark_run.mp4` or `demo_benchmark_run.gif`
**Duration**: 30-60 seconds
**What to show**:
1. Terminal showing file structure: `tree benchmarks/`
2. Run: `python3 benchmarks/scripts/run_all.py`
3. Show progress and results
4. Generate dashboard: `python3 benchmarks/scripts/generate_dashboard.py`
5. Open dashboard in browser

**Recording tools**:
- **macOS**: QuickTime Player (Cmd+Shift+5) or Kap
- **Linux**: SimpleScreenRecorder or Peek (for GIFs)
- **Windows**: OBS Studio or ScreenToGif

### 2. Dashboard Tour
**File**: `demo_dashboard_tour.mp4` or `demo_dashboard_tour.gif`
**Duration**: 20-30 seconds
**What to show**:
1. Scroll through dashboard
2. Hover over metric cards
3. Show responsive design
4. Highlight key metrics

### 3. Agent Selection Demo
**File**: `demo_agent_selection.gif`
**Duration**: 15 seconds
**What to show**:
- Running agent selection tests
- Real-time accuracy calculation
- Performance metrics

## 📊 Visual Assets

### System Architecture Diagram
**File**: `architecture_diagram.png`
**Tools**: draw.io, Excalidraw, or Mermaid
**Content**:
```
┌─────────────────────────────────────────────────┐
│         Claude Multi-Agent System               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  15      │  │    6     │  │    9     │     │
│  │  Agents  │  │Workflows │  │  Skills  │     │
│  └──────────┘  └──────────┘  └──────────┘     │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │         Benchmark System                │   │
│  ├─────────────────────────────────────────┤   │
│  │                                         │   │
│  │  • 4 Real-World Scenarios               │   │
│  │  • Performance Metrics                  │   │
│  │  • Interactive Dashboard                │   │
│  │  • Quality Comparisons                  │   │
│  │                                         │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

## 🎨 Creating High-Quality Screenshots

### Best Practices

1. **Resolution**: Capture at 1920x1080 or higher
2. **Browser**: Use Chrome/Firefox with clean profile (no extensions showing)
3. **Zoom**: Set to 100% for consistency
4. **Window Size**: Maximize or use consistent size
5. **Theme**: Use light theme for readability
6. **Annotations**: Add arrows/highlights using:
   - Snagit
   - Annotate (macOS)
   - ShareX (Windows)
   - Flameshot (Linux)

### Screenshot Checklist

- [ ] High resolution (min 1920px wide)
- [ ] Clean browser (no personal bookmarks/extensions visible)
- [ ] Relevant content centered
- [ ] No sensitive information visible
- [ ] Good lighting/contrast
- [ ] Clear text (not blurry)

## 🎬 Creating GIFs from Videos

### Using FFmpeg

```bash
# Convert video to GIF
ffmpeg -i input.mp4 -vf "fps=10,scale=800:-1:flags=lanczos" -c:v gif output.gif

# Optimize GIF size
gifsicle -O3 --colors 256 output.gif -o optimized.gif
```

### Using Online Tools

- **ezgif.com**: Convert video to GIF, resize, optimize
- **CloudConvert**: High-quality conversions
- **gifski**: Best quality GIF encoder (command line)

## 📝 Adding Screenshots to Documentation

### In README.md

```markdown
## Dashboard Preview

![Benchmark Dashboard](benchmarks/screenshots/01_dashboard_overview.png)

### Agent Selection Performance

![Agent Selection](benchmarks/screenshots/02_agent_selection_metrics.png)
```

### In GitHub README

Make sure images are accessible:
1. Commit images to repository
2. Use relative paths
3. Or use GitHub's asset hosting

## 🔄 Updating Screenshots

When to update screenshots:
- After major dashboard changes
- When adding new scenarios
- After UI improvements
- For version releases

---

**Last Updated**: 2025-11-13
**Maintained By**: Development Team

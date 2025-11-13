#!/usr/bin/env python3
"""
Generate HTML Dashboard

Creates an interactive HTML dashboard from benchmark results.
"""

import json
from pathlib import Path
from datetime import datetime


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Multi-Agent System - Benchmark Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .header .timestamp {{
            margin-top: 20px;
            opacity: 0.8;
            font-size: 0.9em;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 50px;
        }}

        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .metric-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .metric-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}

        .metric-unit {{
            font-size: 0.5em;
            color: #666;
            font-weight: normal;
        }}

        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.5s ease;
        }}

        .status-good {{ border-left-color: #28a745; }}
        .status-warning {{ border-left-color: #ffc107; }}
        .status-error {{ border-left-color: #dc3545; }}

        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        .table tr:hover {{
            background: #f8f9fa;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}

        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}

        .badge-danger {{
            background: #f8d7da;
            color: #721c24;
        }}

        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e9ecef;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        @media (max-width: 768px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Claude Multi-Agent System</h1>
            <div class="subtitle">Benchmark Dashboard</div>
            <div class="timestamp">Generated: {generated_at}</div>
        </div>

        <div class="content">
            <!-- Summary Section -->
            <section class="section">
                <h2 class="section-title">📊 Executive Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-card status-good">
                        <div class="metric-label">Agents Configured</div>
                        <div class="metric-value">{agents_count}</div>
                    </div>
                    <div class="metric-card status-good">
                        <div class="metric-label">Workflows Available</div>
                        <div class="metric-value">{workflows_count}</div>
                    </div>
                    <div class="metric-card status-good">
                        <div class="metric-label">Skills Available</div>
                        <div class="metric-value">{skills_count}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Total Scenarios</div>
                        <div class="metric-value">{total_scenarios}</div>
                    </div>
                </div>
            </section>

            <!-- Agent Selection Performance -->
            <section class="section">
                <h2 class="section-title">🎯 Agent Selection Performance</h2>
                <div class="grid-2">
                    <div class="metric-card {accuracy_status}">
                        <div class="metric-label">Average Accuracy</div>
                        <div class="metric-value">{accuracy}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {accuracy}%">
                                {accuracy}%
                            </div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Average Selection Time</div>
                        <div class="metric-value">{selection_time}<span class="metric-unit">ms</span></div>
                    </div>
                </div>

                <h3 style="margin-top: 30px; margin-bottom: 15px;">Accuracy Distribution</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Accuracy Range</th>
                            <th>Test Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {accuracy_distribution_rows}
                    </tbody>
                </table>
            </section>

            <!-- Scenarios -->
            <section class="section">
                <h2 class="section-title">📝 Available Scenarios</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Simple Scenarios</div>
                        <div class="metric-value">{simple_count}</div>
                        <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                            1-2 agents, 5-10 minutes
                        </p>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Medium Scenarios</div>
                        <div class="metric-value">{medium_count}</div>
                        <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                            3-5 agents, 15-25 minutes
                        </p>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Complex Scenarios</div>
                        <div class="metric-value">{complex_count}</div>
                        <p style="margin-top: 10px; font-size: 0.9em; color: #666;">
                            6+ agents, 30+ minutes
                        </p>
                    </div>
                </div>

                <h3 style="margin-top: 30px; margin-bottom: 15px;">Scenario Catalog</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Scenario</th>
                            <th>Difficulty</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {scenarios_rows}
                    </tbody>
                </table>
            </section>

            <!-- Test Results Details -->
            <section class="section">
                <h2 class="section-title">🔍 Detailed Test Results</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Task Description</th>
                            <th>Expected</th>
                            <th>Selected</th>
                            <th>Accuracy</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {detailed_results_rows}
                    </tbody>
                </table>
            </section>
        </div>

        <div class="footer">
            <p><strong>Claude Multi-Agent System Benchmark v1.0.0</strong></p>
            <p style="margin-top: 10px;">Generated: {generated_at}</p>
            <p style="margin-top: 5px; font-size: 0.9em;">
                For more information, see <code>benchmarks/README.md</code>
            </p>
        </div>
    </div>
</body>
</html>
"""


def generate_dashboard(results_path: str = "benchmarks/reports/results/complete_benchmark.json",
                       output_path: str = "benchmarks/reports/dashboard/index.html"):
    """Generate HTML dashboard from benchmark results"""

    results_file = Path(results_path)
    if not results_file.exists():
        print(f"❌ Results file not found: {results_path}")
        print(f"   Expected path: {results_file.absolute()}")
        print("   Run 'python3 benchmarks/scripts/run_all.py' first to generate results.")
        return False

    # Load results
    try:
        with open(results_file) as f:
            results = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in results file: {e}")
        print(f"   File: {results_path}")
        return False
    except Exception as e:
        print(f"❌ Error reading results file: {e}")
        return False

    # Extract data with defaults
    summary = results.get("summary", {})
    agent_selection = summary.get("agent_selection", {})
    scenarios = summary.get("scenarios_available", {})
    system_info = summary.get("system_info", {})

    accuracy = round(agent_selection.get("average_accuracy", 0) * 100, 1)
    selection_time = round(agent_selection.get("average_time_ms", 0), 2)

    # Determine accuracy status
    if accuracy >= 80:
        accuracy_status = "status-good"
    elif accuracy >= 50:
        accuracy_status = "status-warning"
    else:
        accuracy_status = "status-error"

    # Generate accuracy distribution rows
    accuracy_dist = results.get("agent_selection", {}).get("accuracy_distribution", {})
    total_tests = agent_selection.get("tests_run", 0)
    dist_rows = []
    for tier, count in accuracy_dist.items():
        percentage = (count / total_tests * 100) if total_tests > 0 else 0
        badge_class = "badge-success" if "high" in tier.lower() else "badge-warning" if "medium" in tier.lower() else "badge-danger"
        dist_rows.append(f"""
            <tr>
                <td><span class="badge {badge_class}">{tier}</span></td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
        """)

    # Generate scenarios rows
    scenarios_data = results.get("scenarios", {})
    scenarios_rows = []
    for difficulty in ["simple", "medium", "complex"]:
        for scenario in scenarios_data.get(difficulty, []):
            badge_map = {
                "simple": "badge-success",
                "medium": "badge-warning",
                "complex": "badge-danger"
            }
            scenarios_rows.append(f"""
                <tr>
                    <td>{scenario['name'].replace('_', ' ').replace('-', ' ').title()}</td>
                    <td><span class="badge {badge_map[difficulty]}">{difficulty.upper()}</span></td>
                    <td><span class="badge badge-info">{scenario['status'].upper()}</span></td>
                </tr>
            """)

    # Generate detailed results rows
    detailed_results = results.get("agent_selection", {}).get("detailed_results", [])
    detailed_rows = []
    for result in detailed_results:
        acc = result.get("accuracy", 0)
        acc_badge = "badge-success" if acc >= 0.8 else "badge-warning" if acc >= 0.5 else "badge-danger"
        time_val = round(result.get("selection_time_ms", 0), 2)

        expected = ", ".join(result.get("expected_agents", []))
        selected = ", ".join(result.get("selected_agents", []))

        detailed_rows.append(f"""
            <tr>
                <td>{result.get('task_description', '')[:80]}...</td>
                <td style="font-size: 0.85em;">{expected}</td>
                <td style="font-size: 0.85em;">{selected}</td>
                <td><span class="badge {acc_badge}">{acc:.1%}</span></td>
                <td>{time_val}ms</td>
            </tr>
        """)

    # Fill template
    html = HTML_TEMPLATE.format(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        agents_count=system_info.get("agents_configured", 15),
        workflows_count=system_info.get("workflows_configured", 6),
        skills_count=system_info.get("skills_available", 9),
        total_scenarios=scenarios.get("total", 0),
        accuracy=accuracy,
        accuracy_status=accuracy_status,
        selection_time=selection_time,
        accuracy_distribution_rows="".join(dist_rows),
        simple_count=scenarios.get("simple", 0),
        medium_count=scenarios.get("medium", 0),
        complex_count=scenarios.get("complex", 0),
        scenarios_rows="".join(scenarios_rows),
        detailed_results_rows="".join(detailed_rows)
    )

    # Save dashboard
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(html)

        print(f"✅ Dashboard generated: {output_path}")
        print(f"📊 Open in browser: file://{output_file.absolute()}")
        return True

    except PermissionError:
        print(f"❌ Error: Permission denied writing to {output_path}")
        print("   Check file/directory permissions")
        return False
    except OSError as e:
        print(f"❌ Error: Failed to save dashboard: {e}")
        print(f"   Output path: {output_path}")
        return False
    except Exception as e:
        print(f"❌ Error: Unexpected error saving dashboard: {e}")
        return False


def main():
    """Main entry point"""
    import sys

    print("Generating benchmark dashboard...")

    try:
        success = generate_dashboard()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

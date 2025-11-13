# VS Code Integration Guide

How to integrate Claude-Force with Visual Studio Code for seamless multi-agent development.

## 📦 Setup

### 1. Install Claude-Force

```bash
pip install claude-force
# or from source:
pip install -e .
```

### 2. Configure API Key

Add to your VS Code settings (.vscode/settings.json):

```json
{
  "terminal.integrated.env.osx": {
    "ANTHROPIC_API_KEY": "your-api-key-here"
  },
  "terminal.integrated.env.linux": {
    "ANTHROPIC_API_KEY": "your-api-key-here"
  },
  "terminal.integrated.env.windows": {
    "ANTHROPIC_API_KEY": "your-api-key-here"
  }
}
```

**Better**: Use environment variables in your shell profile instead.

---

## 🎯 Usage Patterns

### Pattern 1: Code Review on Save

Create a VS Code task (`.vscode/tasks.json`):

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Claude: Review Current File",
      "type": "shell",
      "command": "claude-force",
      "args": [
        "run",
        "agent",
        "code-reviewer",
        "--task-file",
        "${file}",
        "--output",
        "${file}.review.md"
      ],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      },
      "problemMatcher": []
    },
    {
      "label": "Claude: Security Scan",
      "type": "shell",
      "command": "claude-force",
      "args": [
        "run",
        "agent",
        "security-specialist",
        "--task",
        "Review ${file} for security vulnerabilities"
      ],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

**Usage**:
1. Open Command Palette: `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
2. Type: "Tasks: Run Task"
3. Select: "Claude: Review Current File"

### Pattern 2: Keyboard Shortcuts

Add to `keybindings.json`:

```json
[
  {
    "key": "cmd+shift+r",
    "command": "workbench.action.tasks.runTask",
    "args": "Claude: Review Current File"
  },
  {
    "key": "cmd+shift+s",
    "command": "workbench.action.tasks.runTask",
    "args": "Claude: Security Scan"
  }
]
```

### Pattern 3: Git Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run code review before commit

echo "🔍 Running Claude code review..."

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|ts)$')

if [ -z "$STAGED_FILES" ]; then
  echo "No code files to review"
  exit 0
fi

# Run review on each file
for FILE in $STAGED_FILES; do
  echo "Reviewing: $FILE"
  claude-force run agent code-reviewer --task-file "$FILE" --output "$FILE.review.md"

  if [ $? -ne 0 ]; then
    echo "❌ Review failed for $FILE"
    exit 1
  fi
done

echo "✅ All files reviewed"
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Pattern 4: Snippet for Quick Agent Calls

Add to VS Code snippets (File → Preferences → User Snippets → python.json):

```json
{
  "Claude Force Agent": {
    "prefix": "claude-agent",
    "body": [
      "from claude_force import AgentOrchestrator",
      "",
      "orchestrator = AgentOrchestrator()",
      "result = orchestrator.run_agent(",
      "    agent_name='${1:code-reviewer}',",
      "    task='${2:Review this code}'",
      ")",
      "",
      "if result.success:",
      "    print(result.output)",
      "else:",
      "    print(f'Error: {result.errors}')",
      "$0"
    ],
    "description": "Create a Claude Force agent call"
  }
}
```

**Usage**: Type `claude-agent` and press Tab.

---

## 🔧 Advanced Integration

### Custom Extension (TypeScript)

Create a VS Code extension that integrates Claude-Force:

```typescript
// extension.ts
import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export function activate(context: vscode.ExtensionContext) {

  // Command: Review current file
  let reviewCommand = vscode.commands.registerCommand(
    'claude-force.reviewFile',
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showErrorMessage('No active file');
        return;
      }

      const filePath = editor.document.fileName;

      vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Claude reviewing file...',
        cancellable: false
      }, async () => {
        try {
          const { stdout } = await execAsync(
            `claude-force run agent code-reviewer --task-file "${filePath}"`
          );

          // Show result in new editor
          const doc = await vscode.workspace.openTextDocument({
            content: stdout,
            language: 'markdown'
          });
          await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);

        } catch (error) {
          vscode.window.showErrorMessage(`Review failed: ${error}`);
        }
      });
    }
  );

  context.subscriptions.push(reviewCommand);
}
```

### Status Bar Integration

```typescript
// Add to extension.ts
const statusBarItem = vscode.window.createStatusBarItem(
  vscode.StatusBarAlignment.Right,
  100
);
statusBarItem.text = "$(symbol-misc) Claude";
statusBarItem.command = 'claude-force.reviewFile';
statusBarItem.tooltip = 'Review with Claude';
statusBarItem.show();

context.subscriptions.push(statusBarItem);
```

---

## 🎨 Output Panel Integration

Create an output panel for Claude results:

```typescript
const outputChannel = vscode.window.createOutputChannel('Claude Force');

// In your command:
outputChannel.clear();
outputChannel.show(true);
outputChannel.appendLine('Running Claude code review...');
outputChannel.appendLine(stdout);
```

---

## 🧪 Testing Integration

Add to your test setup:

```python
# conftest.py
import pytest
from claude_force import AgentOrchestrator

@pytest.fixture
def orchestrator():
    return AgentOrchestrator()

# test_mycode.py
def test_code_quality_with_claude(orchestrator):
    """Use Claude to review test code"""
    result = orchestrator.run_agent(
        'code-reviewer',
        task=open('mycode.py').read()
    )

    assert result.success
    assert 'LGTM' in result.output or 'looks good' in result.output.lower()
```

---

## 📁 Workspace Organization

Recommended structure:

```
your-project/
├── .vscode/
│   ├── settings.json       # API key, etc.
│   ├── tasks.json          # Claude tasks
│   ├── keybindings.json    # Shortcuts
│   └── extensions.json     # Recommended extensions
├── .claude/
│   └── claude.json         # Agent configuration
├── src/
│   └── your-code.py
└── reviews/
    └── *.review.md         # Claude review outputs
```

### Recommended Extensions List

`.vscode/extensions.json`:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "GitHub.copilot",  # Works great with Claude-Force!
    "esbenp.prettier-vscode"
  ]
}
```

---

## 🚀 Example Workflow

1. **Write Code**: Edit `src/app.py`

2. **Review**: Press `Cmd+Shift+R` to run Claude code review

3. **Fix Issues**: Claude suggests improvements

4. **Security Scan**: Press `Cmd+Shift+S` for security check

5. **Commit**: Pre-commit hook runs final review

6. **Push**: Code is production-ready!

---

## 💡 Pro Tips

### Tip 1: Context-Aware Reviews

Pass relevant context to Claude:

```bash
claude-force run agent code-reviewer --task "$(cat <<EOF
Review this code:

File: $(basename $FILE)
Project: $(git remote get-url origin)
Recent changes: $(git log -1 --oneline)

Code:
$(cat $FILE)
EOF
)"
```

### Tip 2: Batch Processing

Review multiple files:

```bash
for file in src/**/*.py; do
  echo "Reviewing: $file"
  claude-force run agent code-reviewer --task-file "$file" \
    --output "reviews/$(basename $file).review.md"
done
```

### Tip 3: Integrate with GitHub Actions

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Claude-Force
        run: pip install claude-force
      - name: Review PR
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          CHANGED_FILES=$(git diff --name-only ${{ github.event.pull_request.base.sha }})
          for file in $CHANGED_FILES; do
            claude-force run agent code-reviewer --task-file "$file"
          done
```

---

## 🔐 Security Considerations

1. **Never commit API keys** - Use environment variables
2. **Use .gitignore** for review outputs if they contain sensitive info
3. **Rotate keys regularly**
4. **Use separate keys** for development and production

---

## 📚 Additional Resources

- [VS Code Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [Claude-Force Documentation](../README.md)

---

**Happy Coding with Claude! 🚀**

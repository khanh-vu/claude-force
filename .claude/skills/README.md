# Claude Skills Integration

## Overview
This directory integrates Claude's built-in skills with the multi-agent system, allowing agents to leverage document creation, data processing, and other specialized capabilities.

## Available Skills

### 1. DOCX Skill
**Location**: `/mnt/skills/public/docx/SKILL.md`

**Capabilities**:
- Create professional Word documents
- Edit existing .docx files
- Handle tracked changes and comments
- Preserve formatting
- Extract text and structure

**When to Use**:
- Creating reports, proposals, documentation
- Generating professional business documents
- Editing uploaded Word files

**Usage in Agents**:
```python
# Always read the skill first
file_read("/mnt/skills/public/docx/SKILL.md")

# Then use the documented patterns
from docx import Document
doc = Document()
# ... follow patterns from SKILL.md
```

### 2. XLSX Skill
**Location**: `/mnt/skills/public/xlsx/SKILL.md`

**Capabilities**:
- Create and edit spreadsheets
- Write formulas and data validation
- Format cells and tables
- Create charts and visualizations
- Process CSV/Excel data

**When to Use**:
- Data analysis and reporting
- Financial models
- Data processing and transformation
- Creating dashboards

**Usage in Agents**:
```python
# Read skill documentation
file_read("/mnt/skills/public/xlsx/SKILL.md")

# Follow the patterns for openpyxl
from openpyxl import Workbook
wb = Workbook()
# ... implement per SKILL.md guidance
```

### 3. PPTX Skill
**Location**: `/mnt/skills/public/pptx/SKILL.md`

**Capabilities**:
- Create presentations
- Add slides with layouts
- Insert images and charts
- Format text and shapes
- Work with master slides

**When to Use**:
- Creating presentations
- Pitch decks
- Training materials
- Visual reports

**Usage in Agents**:
```python
# Read skill first
file_read("/mnt/skills/public/pptx/SKILL.md")

# Then create presentation
from pptx import Presentation
prs = Presentation()
# ... follow SKILL.md patterns
```

### 4. PDF Skill
**Location**: `/mnt/skills/public/pdf/SKILL.md`

**Capabilities**:
- Extract text and tables from PDFs
- Create new PDFs
- Fill PDF forms
- Merge and split PDFs
- Handle metadata

**When to Use**:
- Processing uploaded PDFs
- Creating PDF reports
- Filling forms programmatically
- Extracting data from documents

**Usage in Agents**:
```python
# Read skill first
file_read("/mnt/skills/public/pdf/SKILL.md")

# Then process PDFs
# ... follow patterns from SKILL.md
```

## Integration Pattern for Agents

### Step 1: Determine if Skills are Needed
Check if the task requires document creation or processing:
- Creating .docx, .xlsx, .pptx, or .pdf files
- Processing uploaded documents
- Data extraction or transformation

### Step 2: Read the Skill Documentation
**CRITICAL**: Always read the skill documentation BEFORE using it:

```python
# Example for creating a Word document
file_read("/mnt/skills/public/docx/SKILL.md")
# Now you have the best practices and patterns

# Then proceed with implementation
from docx import Document
# ... follow the patterns you just read
```

### Step 3: Follow the Skill Patterns
The skill documentation contains:
- Tested patterns and best practices
- Common pitfalls to avoid
- Optimal library usage
- Error handling strategies

### Step 4: Save to Outputs Directory
```python
# Work in /home/claude for development
output_path = "/home/claude/report.docx"
# ... create document

# Move to outputs for user access
import shutil
shutil.move(output_path, "/mnt/user-data/outputs/report.docx")
```

## Agent-Specific Skill Usage

### Document Writer Expert
**Primary Skills**: DOCX, PDF
- Creates technical documentation
- Generates user guides
- Produces professional reports

**Pattern**:
```markdown
1. Read task requirements
2. file_read("/mnt/skills/public/docx/SKILL.md")
3. Create document using best practices
4. Move to /mnt/user-data/outputs/
5. Provide download link
```

### Python Expert
**Primary Skills**: XLSX, PDF
- Data processing and analysis
- Report generation
- ETL scripts

**Pattern**:
```python
# For data processing
file_read("/mnt/skills/public/xlsx/SKILL.md")
# ... process data
# ... create spreadsheet with results
```

### API Documenter
**Primary Skills**: DOCX, PDF
- API reference documentation
- Integration guides
- PDF manuals

### Frontend Architect / UI Components Expert
**Primary Skills**: PPTX (occasionally)
- Architecture diagrams
- Design system presentations
- Component documentation

## Skill Configuration in claude.json

The skills are configured in `.claude/claude.json`:

```json
{
  "skills_integration": {
    "enabled": true,
    "skills_path": "skills/",
    "available_skills": [
      "docx",
      "xlsx",
      "pptx",
      "pdf"
    ]
  }
}
```

## Best Practices

### 1. Always Read Skills First
```python
# ❌ DON'T: Jump straight to code
from docx import Document
doc = Document()  # Might miss important patterns

# ✅ DO: Read the skill first
file_read("/mnt/skills/public/docx/SKILL.md")
from docx import Document
doc = Document()  # Now using best practices
```

### 2. Follow File Handling Rules
```python
# ✅ Work in /home/claude
work_file = "/home/claude/document.docx"
create_document(work_file)

# ✅ Move final output to outputs directory
shutil.move(work_file, "/mnt/user-data/outputs/document.docx")

# ✅ Provide computer:// link
print("[View your document](computer:///mnt/user-data/outputs/document.docx)")
```

### 3. Handle User Uploads
```python
# User uploaded files are in /mnt/user-data/uploads
uploaded_file = "/mnt/user-data/uploads/data.xlsx"

# Read and process
file_read("/mnt/skills/public/xlsx/SKILL.md")
# ... process uploaded_file

# Save results to outputs
result_file = "/mnt/user-data/outputs/processed_data.xlsx"
```

### 4. Error Handling
```python
try:
    file_read("/mnt/skills/public/docx/SKILL.md")
    # ... document creation
    shutil.move(work_file, output_file)
except Exception as e:
    # Log error in work.md
    # Provide fallback or clear error message
    pass
```

## Adding Custom Skills

To add a custom skill:

1. Create directory: `.claude/skills/custom-skill-name/`
2. Create `SKILL.md` with:
   - Overview and capabilities
   - Installation requirements
   - Usage patterns
   - Best practices
   - Examples

3. Update `claude.json`:
```json
{
  "skills_integration": {
    "available_skills": [
      "docx", "xlsx", "pptx", "pdf",
      "custom-skill-name"
    ]
  }
}
```

4. Reference in agent files as needed

## Troubleshooting

### Skill File Not Found
```
Error: /mnt/skills/public/docx/SKILL.md not found
```

**Solution**: Claude's skills may not be available in your environment. Document this in your output and use standard library documentation instead.

### Permission Errors
```
Error: Permission denied: /mnt/user-data/outputs/
```

**Solution**: Ensure you're writing to `/home/claude` first, then moving to outputs.

### Library Not Available
```
ImportError: No module named 'docx'
```

**Solution**:
```bash
pip install python-docx --break-system-packages
```

## Examples

### Example 1: Document Writer Creating Report

```python
# Step 1: Read the skill
file_read("/mnt/skills/public/docx/SKILL.md")

# Step 2: Create document in working directory
from docx import Document
doc = Document()
doc.add_heading('Project Report', 0)
# ... add content per SKILL.md patterns
doc.save('/home/claude/report.docx')

# Step 3: Move to outputs
shutil.move('/home/claude/report.docx', 
            '/mnt/user-data/outputs/project-report.docx')

# Step 4: Provide link in work.md
# [View your report](computer:///mnt/user-data/outputs/project-report.docx)
```

### Example 2: Python Expert Processing Data

```python
# Step 1: Read the skill
file_read("/mnt/skills/public/xlsx/SKILL.md")

# Step 2: Read user upload
input_file = "/mnt/user-data/uploads/sales-data.csv"
df = pd.read_csv(input_file)

# Step 3: Process and create report
# ... analysis per SKILL.md patterns

# Step 4: Save to outputs
output_file = "/mnt/user-data/outputs/sales-analysis.xlsx"
with pd.ExcelWriter(output_file) as writer:
    df.to_excel(writer, sheet_name='Analysis')

# Step 5: Provide link
# [View analysis](computer:///mnt/user-data/outputs/sales-analysis.xlsx)
```

## Summary

- **Always** read skill documentation first: `file_read("/mnt/skills/public/{skill}/SKILL.md")`
- Work in `/home/claude`, finalize in `/mnt/user-data/outputs/`
- Provide `computer://` links for user access
- Follow patterns from SKILL.md for best results
- Handle errors gracefully with fallbacks

---

**Last Updated**: 2024-11-13  
**Version**: 1.0.0  
**Maintained By**: System Administrator

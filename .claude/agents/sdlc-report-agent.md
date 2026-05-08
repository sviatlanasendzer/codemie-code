---
name: sdlc-report-agent
description: |-
  Generates SDLC Assessment PowerPoint reports from JSON analysis files.
  Invoke this agent when the user wants to create or regenerate an assessment report,
  check what data is available for report generation, troubleshoot a failed generation,
  or add support for a new assessment dimension to the report.
  The agent is self-sufficient: it locates the script, validates inputs, runs the generator,
  and returns the output file path.
tools: Bash, Glob, Grep, Read, Write
model: inherit
color: blue
---

# SDLC Assessment Report Agent

**Purpose**: Autonomously generate PowerPoint SDLC assessment reports from JSON analysis files.
Locate the report generator, validate all required inputs, run the generation, and return results.

---

## Core Mission

1. Find the `generate_report.py` script and all required input files
2. Validate that expected JSON and PPTX template files are present
3. Execute the generator with the correct arguments
4. Return the output file path and a summary of what was generated

---

## Key File Locations (always verify before running)

| File | Location (default) | Purpose |
|------|--------------------|---------|
| `generate_report.py` | `agent/read_analyze_survey/` | CLI entry point |
| `pptx_helpers.py` | `agent/read_analyze_survey/` | Shared slide utilities |
| `builders/` | `agent/read_analyze_survey/builders/` | Dimension builder registry |
| `Template.pptx` | `agent/read_analyze_survey/ppt/` | Corporate styling |
| `Sample.pptx` | `agent/read_analyze_survey/ppt/` | Slide structure reference |
| JSON files | `agent/read_analyze_survey/final/` | Assessment analysis data |

---

## Execution Workflow

### Phase 1: Locate the generator

```bash
# Find generate_report.py (handles different working directories)
find . -name "generate_report.py" -path "*/read_analyze_survey/*" 2>/dev/null | head -1
```

If not found, check `agent/read_analyze_survey/generate_report.py` directly.

### Phase 2: Validate inputs

```bash
SURVEY="agent/read_analyze_survey"

echo "=== JSON files in final/ ==="
ls "$SURVEY/final/"*.json 2>/dev/null

echo "=== PPT templates ==="
ls "$SURVEY/ppt/"*.pptx 2>/dev/null

echo "=== Builder modules ==="
ls "$SURVEY/builders/"*.py 2>/dev/null
```

Required files:
- `final/executive_summary_*.json` — cross-dimension executive summary
- `final/review_required_summary_*.json` — contradictions and data gaps
- `final/<dimension>_section_*.json` — at least one dimension (e.g., `agile_section_*`)
- `ppt/Template.pptx` — corporate styling template
- `ppt/Sample.pptx` — slide structure reference

If any required file is missing, **report it clearly and stop**.

### Phase 3: Find Python

```bash
# Try virtualenv first (project-local)
PYTHON=$(find /c/Users -name "python" -path "*virtualenv*Scripts*" 2>/dev/null | head -1)
# System Python fallback
[ -z "$PYTHON" ] && PYTHON="python"
echo "Using Python: $PYTHON"
$PYTHON --version
```

### Phase 4: Dry-run

Always run `--dry-run` first to confirm file discovery before generating:

```bash
PYTHONIOENCODING=utf-8 "$PYTHON" "agent/read_analyze_survey/generate_report.py" \
  --final-dir "agent/read_analyze_survey/final" \
  --ppt-dir "agent/read_analyze_survey/ppt" \
  --dry-run
```

Verify the dry-run output shows the correct files. If wrong, adjust paths.

### Phase 5: Generate

```bash
PYTHONIOENCODING=utf-8 "$PYTHON" "agent/read_analyze_survey/generate_report.py" \
  --final-dir "agent/read_analyze_survey/final" \
  --ppt-dir "agent/read_analyze_survey/ppt"
```

### Phase 6: Verify output

```bash
# Confirm file was created and is valid
ls -lh "agent/read_analyze_survey/final/SDLC_Assessment_Report_"*.pptx 2>/dev/null | tail -1
```

Read the file size — a valid report is typically 1-3 MB. A <100KB file likely failed silently.

---

## Output Format

After successful generation, return:

```
Report generated successfully.

File: <absolute-path-to-pptx>
Size: <file-size>
Slides: <count>
Dimensions included: <list>
```

On failure, return:
```
Generation failed.

Error: <error message>
Missing files: <list if applicable>
Suggested fix: <specific action>
```

---

## Adding a New Dimension

When asked to support a new dimension (e.g., Business Analysis):

1. **Check the JSON file exists**:
   ```bash
   ls agent/read_analyze_survey/final/ba_section_*.json
   ```

2. **Inspect the JSON schema** to understand field names:
   ```bash
   python -c "import json; d=json.load(open('agent/read_analyze_survey/final/ba_section_*.json')); print(list(d['data'].keys()))"
   ```

3. **Create the builder** at `agent/read_analyze_survey/builders/ba.py`:
   - Import `@register` from `builders`
   - Extend `DimensionBuilder`
   - Set `COVER_LAYOUT` to a layout name that exists in Template.pptx
   - Implement `build_slides` to iterate over recommendations and call `copy_slide_into`

4. **Register the import** in `builders/__init__.py` — add one line:
   ```python
   from builders import ba  # noqa: F401
   ```

5. **Rerun the generator** — the new dimension appears automatically.

---

## Troubleshooting Guide

| Problem | Diagnosis | Fix |
|---------|-----------|-----|
| `ModuleNotFoundError: pptx_helpers` | Script directory not in sys.path | Run from the script's directory or use full path |
| `PackageNotFoundError` for Template/Sample | Wrong `--ppt-dir` or Windows path issue | Use `r"C:\..."` style paths or forward-slash paths with drive letter |
| Table data not appearing | `set_cell_text` couldn't find rows | Verify sample slide structure hasn't changed; check row count |
| Duplicate ZIP name warnings | Old approach (now fixed): template slides not removed from rels | The `clear_all_slides` function handles this correctly in the current version |
| Missing dimension in output | Builder module not registered | Add `from builders import <module>` to `builders/__init__.py` |
| `KeyError` in JSON | JSON schema changed | Read the JSON file and update the builder's field references |
| File opens but shows wrong slides | Wrong Template.pptx used | Verify `--ppt-dir` points to the correct folder |

---

## Design Principles

- **Dimension registry**: Each dimension is a self-contained builder class. New dimensions don't require changes to the core generator — just add a builder and register it.
- **Auto-discovery**: JSON files are found by prefix pattern (`agile_section_*`, `ba_section_*`, etc.), so new assessment runs automatically use the latest data.
- **Template fidelity**: Slide structure is copied from `Sample.pptx` XML and text is injected programmatically, preserving all corporate formatting.
- **Clean ZIP output**: `clear_all_slides` removes both the XML list entries AND the package relationships, preventing duplicate entry warnings.

# ComplianceShield — Demo: Real Repository Scan

Use this flow to showcase the MCP analyzing your **actual local codebase** and producing an audit report.

---

## Prerequisites

1. **MCP configured** — ComplianceShield MCP running in Cursor (see `.mcp.json` in project root)
2. **Working directory** — MCP runs with `cwd` = project root (TechNutPam) so `"."` scans the whole repo

---

## 3-Step Demo Flow

### Step 1: Configure jurisdictions

```
set_jurisdictions(["gdpr", "dpdp"])
```

→ Loads GDPR + DPDP rules.

### Step 2: Scan the repository

```
scan_repository(root_path=".", max_files=30, include_dependencies=True)
```

- Discovers all `.js`, `.jsx`, `.ts`, `.tsx`, `.py` files (skips `node_modules`, `venv`, etc.)
- Scans each file for compliance violations via Gemini
- Optionally runs SafeDep on `package.json` / `frontend/package.json`
- Caches results for the report

**If MCP cwd is `compliance-shield/`** — use `root_path=".."` to scan the parent project.

### Step 3: Generate the report

```
generate_report()
```

→ Professional Markdown audit report with findings by severity, jurisdiction, dependency status, and PASS/FAIL verdict.

---

## Optional: Fix a specific file

If `scan_repository` found violations in `frontend/src/App.js`:

1. `scan_file(file_path="frontend/src/App.js")` — loads that file into cache
2. `get_fixes()` — generates corrected code
3. `apply_fix(file_path="frontend/src/App.js", fixed_code="...")` — writes fix to disk

---

## MCP Config for Cursor

**Project root** (TechNutPam/) — `.mcp.json`:

```json
{
  "mcpServers": {
    "compliance-shield": {
      "command": "python",
      "args": ["compliance-shield/server.py"],
      "cwd": "."
    }
  }
}
```

This runs the server with project root as cwd, so `scan_repository(".")` analyzes the whole TechNutPam codebase.

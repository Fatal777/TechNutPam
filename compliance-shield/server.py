"""
ComplianceShield MCP Server
============================
A Concierge-wrapped MCP server that enforces compliance at the protocol level.

Architecture (from master plan):
  Stage 1: configure   → set_jurisdictions
  Stage 2: wrap_prompt → compliance_wrap          (BEFORE code gen)
  Stage 3: scan        → scan_code, scan_dependencies  (AFTER code exists)
  Stage 4: remediate   → get_fixes, apply_fix
  Stage 5: report      → generate_report

Sponsor integrations:
  - Concierge   : workflow stage enforcement (this file)
  - SafeDep     : dependency malware scanning (scan_dependencies)
  - Gemini API  : code analysis + remediation (scan_code, get_fixes, generate_report)
  - Emergent.sh : web dashboard (separate — see Person C)

Usage:
  stdio (Claude Code / Cursor):  python server.py
  HTTP  (Lovable / remote):       python server.py --http
"""

import json
import os
import sys

import httpx
from mcp.server.fastmcp import FastMCP

import google.generativeai as genai

# ── API Keys ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY      = "AIzaSyAMcMTXwqL1KVvFRD11WvRo-CGUwgdXuJM"
SAFEDEP_API_KEY     = "sfd_sTm9Ij-e-BHd_9WE_wiwkqr7PN6ijxt_K0NrVjskMBeOCRJgdxRBhVqx"
SAFEDEP_TENANT_ID   = "default-team.technutapm.safedep.io"
CRUSTDATA_API_TOKEN = "340b6f6b71f89771df811206e81be5788e173e74"

# ── Gemini setup ──────────────────────────────────────────────────────────────
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ── FastMCP instance (tools registered here, Concierge wraps below) ───────────
mcp = FastMCP("compliance-shield")


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: load_rules
# Reads jurisdiction JSON files from rules/ directory.
# Called by compliance_wrap and scan_code.
# NOTE: This was missing from the original plan and caused NameError crashes.
# ═══════════════════════════════════════════════════════════════════════════════
def load_rules(jurisdictions: list[str]) -> str:
    """Load and format compliance rules for the given jurisdictions."""
    rules_text = []
    base_dir = os.path.dirname(__file__)

    for j in jurisdictions:
        path = os.path.join(base_dir, "rules", f"{j}.json")
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            for rule in data.get("rules", []):
                ref = rule.get("article") or rule.get("section") or ""
                rules_text.append(f"  [{rule['id']}] {rule['rule']}: {rule['description']} ({ref})")
        else:
            rules_text.append(f"  [WARNING] No rule file found for jurisdiction: {j}")

    return "\n".join(rules_text) if rules_text else "No rules loaded."


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: Repository discovery
# Discovers code files for scan_repository. Skips common build/dep directories.
# ═══════════════════════════════════════════════════════════════════════════════
CODE_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".py", ".mjs", ".cjs"}
SKIP_DIRS = {"node_modules", "venv", ".venv", "__pycache__", ".git", "dist", "build", ".next", ".nuxt", "vendor", "coverage", ".turbo"}


def _discover_code_files(root_path: str, max_files: int = 50) -> list[str]:
    """Discover code files under root_path, respecting skip dirs. Returns absolute paths."""
    root = os.path.abspath(os.path.expanduser(root_path))
    if not os.path.isdir(root):
        return []
    found = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # Prune skip dirs from descent
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in CODE_EXTENSIONS:
                found.append(os.path.join(dirpath, f))
                if len(found) >= max_files:
                    return found
    return found


def _run_single_file_scan(code: str, filename: str, jurisdictions: list[str], rules_text: str) -> tuple[list, str]:
    """Run Gemini scan on one file. Returns (findings_list, raw_json_text)."""
    prompt = f"""You are a compliance auditor. Analyze this code for violations.

Active jurisdictions: {', '.join(j.upper() for j in jurisdictions)}

Rules to check:
{rules_text}

Code to audit ({filename}):
```
{code}
```

Return ONLY a valid JSON array of findings (no other text, no markdown fences):
[
  {{
    "severity": "critical",
    "jurisdiction": "GDPR",
    "rule_id": "GDPR-1",
    "rule": "No PII in logs",
    "line": 12,
    "violation": "SSN logged to console in plain text",
    "fixedCode": "console.log(`New user: ${{name}}, ${{email}}`);  // SSN removed"
  }}
]

If no violations found, return: []"""
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip().strip("```json").strip("```").strip()
        findings = json.loads(raw)
        return (findings, raw)
    except (json.JSONDecodeError, Exception):
        return ([], "[]")


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: configure
# Tools: set_jurisdictions, upload_policy
# Purpose: Tell the server which regulations apply and optionally load custom PDFs
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def set_jurisdictions(jurisdictions: list[str]) -> str:
    """
    Toggle compliance jurisdictions for this session.
    Supported values: gdpr, dpdp, hipaa, soc2

    Call this FIRST before wrapping prompts or scanning code.
    Example: set_jurisdictions(["gdpr", "dpdp"])
    """
    valid = {"gdpr", "dpdp", "hipaa", "soc2"}
    invalid = [j for j in jurisdictions if j.lower() not in valid]
    if invalid:
        return f"❌ Invalid jurisdictions: {invalid}. Valid options: {sorted(valid)}"

    clean = [j.lower() for j in jurisdictions]
    app.set_state("jurisdictions", clean)
    app.set_state("scan_count", app.get_state("scan_count") or 0)

    rules_preview = load_rules(clean)
    return (
        f"✅ Active jurisdictions: {', '.join(j.upper() for j in clean)}\n\n"
        f"Rules loaded ({len(rules_preview.splitlines())} entries):\n{rules_preview}\n\n"
        f"Next: use compliance_wrap before generating code, or scan_code on existing code."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: wrap_prompt
# Tools: compliance_wrap
# Purpose: Inject compliance constraints into prompts BEFORE code generation.
#          This is the "code is born compliant" mechanism.
#          Separated from scan stage intentionally — different timing in workflow.
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def compliance_wrap(user_prompt: str) -> str:
    """
    Wrap a coding prompt with jurisdiction-specific compliance constraints.

    Use this BEFORE asking an AI to generate code. The wrapped prompt instructs
    the AI to produce compliant code from the start, avoiding violations before
    they are written.

    This is Stage 2 (wrap_prompt). It is intentionally separate from scanning
    (Stage 3) because it operates at different timing: pre-generation vs post-generation.
    """
    jurisdictions = app.get_state("jurisdictions") or ["gdpr"]
    rules = load_rules(jurisdictions)

    wrapped = f"""You are generating code that MUST comply with: {', '.join(j.upper() for j in jurisdictions)}.

MANDATORY COMPLIANCE REQUIREMENTS (enforced by ComplianceShield):
{rules}

DEVELOPER'S REQUEST:
{user_prompt}

COMPLIANCE INSTRUCTIONS:
1. Satisfy ALL listed rules by default — do not wait to be asked.
2. Add inline comments on compliance-relevant lines, e.g.:
     # [GDPR-2] Data encrypted at rest using AES-256
     # [DPDP-2] Processing only for consented purpose: account creation
3. Never log PII (names, emails, SSNs, phone numbers) to console or files.
4. Always validate explicit user consent before collecting personal data.
5. Include a /delete endpoint or data deletion mechanism if storing user data.
6. Never hardcode secrets — use environment variables.

Generate compliant code that will pass an enterprise security review."""

    return wrapped


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: scan
# Tools: scan_code, scan_dependencies
# Purpose: Audit existing code and dependencies for violations.
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def scan_code(code: str, filename: str = "unknown") -> str:
    """
    Scan existing code for compliance violations against active jurisdictions.

    Returns a JSON array of findings, each with severity, rule violated,
    line number, and a suggested fix. Results are cached for the remediate stage.

    Use this AFTER code has been generated (Stage 3). For pre-generation
    compliance injection, use compliance_wrap (Stage 2) instead.
    """
    jurisdictions = app.get_state("jurisdictions") or ["gdpr"]
    rules = load_rules(jurisdictions)

    # Billing counter — persists in session (for full persistence use SQLite)
    count = (app.get_state("scan_count") or 0) + 1
    app.set_state("scan_count", count)
    app.set_state("last_scan_code", code)
    app.set_state("last_scan_file", filename)

    prompt = f"""You are a compliance auditor. Analyze this code for violations.

Active jurisdictions: {', '.join(j.upper() for j in jurisdictions)}

Rules to check:
{rules}

Code to audit ({filename}):
```
{code}
```

Return ONLY a valid JSON array of findings (no other text, no markdown fences):
[
  {{
    "severity": "critical",
    "jurisdiction": "GDPR",
    "rule_id": "GDPR-1",
    "rule": "No PII in logs",
    "line": 12,
    "violation": "SSN logged to console in plain text",
    "fixedCode": "console.log(`New user: ${{name}}, ${{email}}`);  // SSN removed"
  }}
]

If no violations found, return: []"""

    try:
        response = model.generate_content(prompt)
        findings_text = response.text.strip().strip("```json").strip("```").strip()
        app.set_state("last_findings", findings_text)

        findings = json.loads(findings_text)
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in findings:
            s = f.get("severity", "low").lower()
            by_severity[s] = by_severity.get(s, 0) + 1

        summary = (
            f"🔍 Scan complete for {filename}\n"
            f"Found {len(findings)} violation(s): "
            f"{by_severity['critical']} critical, {by_severity['high']} high, "
            f"{by_severity['medium']} medium, {by_severity['low']} low\n\n"
            f"Findings:\n{findings_text}"
        )
        return summary

    except json.JSONDecodeError:
        # If Gemini returns non-JSON, still surface it
        app.set_state("last_findings", response.text)
        return f"Scan complete (raw output):\n{response.text}"
    except Exception as e:
        return f"❌ Scan error: {str(e)}"


@mcp.tool()
async def scan_dependencies(package_json: str) -> str:
    """
    Scan package.json dependencies for malware and known vulnerabilities.

    Uses SafeDep threat intelligence with FAIL-CLOSED policy:
    packages are blocked if safety cannot be explicitly confirmed.

    Chains the SafeDep API as specified in the master architecture.
    """
    try:
        pkg_data = json.loads(package_json)
    except json.JSONDecodeError:
        return "❌ Invalid JSON. Provide the full contents of your package.json file."

    packages = pkg_data.get("dependencies", {})
    packages.update(pkg_data.get("devDependencies", {}))

    if not packages:
        return "⚠️ No dependencies found in package.json."

    results = []
    async with httpx.AsyncClient(timeout=30) as client:
        for pkg, version in list(packages.items())[:20]:  # Cap at 20 for demo speed
            clean_version = version.lstrip("^~>=<")
            try:
                resp = await client.post(
                    "https://api.safedep.io/safedep.services.malysis.v1.MalwareAnalysisService/QueryPackageAnalysis",
                    headers={
                        "Authorization": SAFEDEP_API_KEY,
                        "X-Tenant-ID": SAFEDEP_TENANT_ID,
                        "Content-Type": "application/json",
                    },
                    json={
                        "ecosystem": "npm",
                        "package_name": pkg,
                        "version": clean_version,
                    },
                )
                data = resp.json()
                inference = data.get("report", {}).get("inference", {})
                is_malware = inference.get("isMalware")
                reasoning = inference.get("reasoning", "No details available")

                results.append({
                    "package": f"{pkg}@{clean_version}",
                    "status": "🚫 BLOCKED" if is_malware != False else "✅ SAFE",
                    "safe": is_malware == False,   # Fail-closed: only True if explicitly safe
                    "blocked": is_malware != False,
                    "reason": reasoning[:300],
                })

            except Exception as e:
                # Fail-closed: network errors → block the package
                results.append({
                    "package": f"{pkg}@{clean_version}",
                    "status": "⚠️ UNKNOWN — BLOCKED (fail-closed)",
                    "safe": False,
                    "blocked": True,
                    "reason": f"SafeDep lookup failed: {str(e)}",
                })

    blocked = [r for r in results if r["blocked"]]
    summary = {
        "verdict": "❌ FAIL" if blocked else "✅ PASS",
        "total_scanned": len(results),
        "safe": len(results) - len(blocked),
        "blocked": len(blocked),
        "results": results,
    }
    app.set_state("dep_scan_results", json.dumps(summary))
    return json.dumps(summary, indent=2)


@mcp.tool()
async def scan_repository(root_path: str = ".", max_files: int = 30, include_dependencies: bool = True) -> str:
    """
    Scan a local repository or directory for compliance violations.

    Discovers all code files (.js, .jsx, .ts, .tsx, .py) under root_path, scans each
    against active jurisdictions, and optionally runs dependency audit on package.json.
    Results are cached for generate_report — call that next for an audit-ready report.

    Use this for real codebase analysis. Pass "." for current dir, or a path like
    ".." or "/absolute/path/to/project" for your workspace.

    Example: scan_repository(root_path="..")  — scans parent directory (whole project)
    """
    root = os.path.abspath(os.path.expanduser(root_path))
    if not os.path.isdir(root):
        return f"❌ Path does not exist or is not a directory: {root}"

    jurisdictions = app.get_state("jurisdictions") or ["gdpr"]
    rules = load_rules(jurisdictions)

    files = _discover_code_files(root, max_files)
    if not files:
        return f"❌ No code files found under {root} (supported: {', '.join(CODE_EXTENSIONS)})"

    all_findings = []
    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()
        except Exception as e:
            all_findings.append({
                "file": filepath,
                "severity": "medium",
                "rule_id": "SCAN-ERR",
                "rule": "File read error",
                "violation": str(e),
                "line": 0,
            })
            by_severity["medium"] = by_severity.get("medium", 0) + 1
            continue

        rel_path = os.path.relpath(filepath, root)
        findings, _ = _run_single_file_scan(code, rel_path, jurisdictions, rules)
        for f in findings:
            f["file"] = rel_path
            all_findings.append(f)
            s = f.get("severity", "low").lower()
            by_severity[s] = by_severity.get(s, 0) + 1

    # Optional: scan package.json
    dep_note = ""
    for candidate in ["package.json", "frontend/package.json", "backend/package.json"]:
        pkg_path = os.path.join(root, candidate)
        if os.path.isfile(pkg_path) and include_dependencies:
            try:
                with open(pkg_path, "r") as f:
                    pkg_json = f.read()
                dep_result = await scan_dependencies(pkg_json)
                dep_note = f"\n\nDependency scan ({candidate}):\n{dep_result}"
                break
            except Exception:
                pass

    count = (app.get_state("scan_count") or 0) + 1
    app.set_state("scan_count", count)
    repo_findings_json = json.dumps(all_findings, indent=2)
    app.set_state("last_findings", repo_findings_json)
    app.set_state("repo_scan_root", root)

    summary = (
        f"🔍 Repository scan complete: {root}\n"
        f"Scanned {len(files)} file(s) | Found {len(all_findings)} violation(s): "
        f"{by_severity['critical']} critical, {by_severity['high']} high, "
        f"{by_severity['medium']} medium, {by_severity['low']} low\n\n"
        f"Next: call generate_report() for an audit-ready report.{dep_note}"
    )
    return summary


@mcp.tool()
async def scan_file(file_path: str) -> str:
    """
    Scan a single file from disk for compliance violations.

    Reads the file at file_path (relative to cwd or absolute) and runs a compliance
    audit. Results are cached for get_fixes and generate_report. Use apply_fix
    after get_fixes to write fixes back to disk.

    Example: scan_file(file_path="frontend/src/App.js")
    """
    path = os.path.abspath(os.path.expanduser(file_path))
    if not os.path.isfile(path):
        return f"❌ File not found: {path}"

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()
    except Exception as e:
        return f"❌ Error reading file: {e}"

    jurisdictions = app.get_state("jurisdictions") or ["gdpr"]
    rules = load_rules(jurisdictions)

    count = (app.get_state("scan_count") or 0) + 1
    app.set_state("scan_count", count)
    app.set_state("last_scan_code", code)
    app.set_state("last_scan_file", path)

    findings, raw = _run_single_file_scan(code, file_path, jurisdictions, rules)
    app.set_state("last_findings", raw)

    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        s = f.get("severity", "low").lower()
        by_severity[s] = by_severity.get(s, 0) + 1

    return (
        f"🔍 Scan complete for {file_path}\n"
        f"Found {len(findings)} violation(s): "
        f"{by_severity['critical']} critical, {by_severity['high']} high, "
        f"{by_severity['medium']} medium, {by_severity['low']} low\n\n"
        f"Findings:\n{raw}\n\n"
        f"Next: get_fixes() for remediation, or generate_report() for full audit."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: remediate
# Tools: get_fixes, apply_fix
# Purpose: Generate and apply auto-remediation diffs.
#          apply_fix was missing from the original plan — implemented here.
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def get_fixes(findings_json: str = "") -> str:
    """
    Generate auto-remediation diffs from scan findings.

    If findings_json is omitted, uses cached results from the last scan_code call.
    Returns a unified diff the developer can accept with apply_fix.
    """
    if not findings_json:
        findings_json = app.get_state("last_findings") or "[]"

    original_code = app.get_state("last_scan_code") or ""
    filename = app.get_state("last_scan_file") or "unknown"
    jurisdictions = app.get_state("jurisdictions") or []

    if findings_json == "[]":
        return "✅ No findings to fix. Run scan_code first."

    prompt = f"""You are a compliance engineer. Fix all violations in this code.

VIOLATIONS FOUND:
{findings_json}

ORIGINAL CODE ({filename}):
```
{original_code}
```

JURISDICTIONS: {', '.join(j.upper() for j in jurisdictions)}

Produce:
1. The complete FIXED version of the file (not just a snippet — the full file)
2. A change summary listing what was fixed and which rule it satisfies

Format:
FIXED CODE:
```
[complete fixed file here]
```

CHANGES MADE:
- [GDPR-1] Removed SSN from console.log on line 8
- [GDPR-2] Added bcrypt encryption for password storage on line 15
- [GDPR-3] Added consent validation before data collection on line 22
[etc.]"""

    response = model.generate_content(prompt)
    app.set_state("last_fix", response.text)
    return response.text


@mcp.tool()
async def apply_fix(file_path: str, fixed_code: str) -> str:
    """
    Apply remediated code to a file on disk.

    Backs up the original file to <file_path>.bak before writing.
    Use this to accept a fix from get_fixes with one action.
    After applying, run scan_code again to confirm violations are resolved.

    NOTE: This tool was planned in the master architecture but not implemented
    in the original server.py code. It is required for the remediate stage to work.
    """
    try:
        # Back up original
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                original = f.read()
            with open(file_path + ".bak", "w") as f:
                f.write(original)
            backup_note = f"Original backed up to {file_path}.bak"
        else:
            backup_note = "No existing file to back up — creating new file."

        # Write fixed code
        with open(file_path, "w") as f:
            f.write(fixed_code)

        return (
            f"✅ Fix applied to {file_path}\n"
            f"{backup_note}\n"
            f"Next: run scan_code on {file_path} to confirm violations are resolved."
        )
    except PermissionError:
        return f"❌ Permission denied writing to {file_path}"
    except Exception as e:
        return f"❌ Error applying fix: {str(e)}"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 5: report
# Tools: generate_report
# Purpose: Produce audit-ready compliance reports.
#          Stage is NOT terminal — developer can re-scan after reporting.
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def generate_report(scan_results: str = "") -> str:
    """
    Generate a professional compliance report from scan results.

    Suitable for sharing with enterprise security reviewers and auditors.
    If scan_results is omitted, uses cached results from the last scan session.
    """
    if not scan_results:
        scan_results = app.get_state("last_findings") or "No code scan results in session."

    dep_results = app.get_state("dep_scan_results") or "No dependency scan performed."
    jurisdictions = app.get_state("jurisdictions") or []
    scan_count = app.get_state("scan_count") or 0

    prompt = f"""Generate a professional compliance audit report in Markdown.

SESSION CONTEXT:
- Tool: ComplianceShield MCP Server
- Jurisdictions assessed: {', '.join(j.upper() for j in jurisdictions) or 'None configured'}
- Scans performed this session: {scan_count}

CODE SCAN RESULTS:
{scan_results}

DEPENDENCY SCAN RESULTS (SafeDep):
{dep_results}

Produce this exact structure:

# ComplianceShield Compliance Audit Report

**Assessed Jurisdictions:** {', '.join(j.upper() for j in jurisdictions) or 'None'}
**Scans Performed:** {scan_count}
**Overall Status:** [PASS ✅ or FAIL ❌]

## Executive Summary
(2–3 sentences for a non-technical audience: what was checked, what was found)

## Findings by Severity

| Severity | Count | Jurisdictions |
|----------|-------|---------------|
| Critical | N | ... |
| High | N | ... |
| Medium | N | ... |
| Low | N | ... |

## Findings by Jurisdiction
(Group violations under GDPR / DPDP / HIPAA / SOC2 subheadings)

## Dependency Security (SafeDep)
(Summarise the dependency scan: total checked, safe, blocked, package names)

## Recommended Remediation Actions
(Numbered priority list — most critical first)

## Compliance Verdict
**OVERALL STATUS: PASS ✅ / FAIL ❌**
(One paragraph explaining why)"""

    response = model.generate_content(prompt)
    app.set_state("last_report", response.text)
    return response.text


# ═══════════════════════════════════════════════════════════════════════════════
# MCP RESOURCES — readable compliance data for context injection
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.resource("compliance://rules/{jurisdiction}")
def get_rules_resource(jurisdiction: str) -> str:
    """Get raw compliance rule definitions for a jurisdiction."""
    path = os.path.join(os.path.dirname(__file__), "rules", f"{jurisdiction}.json")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return json.dumps({"error": f"No rule file for jurisdiction: {jurisdiction}"})


@mcp.resource("compliance://status")
def get_status() -> str:
    """Get the current compliance session configuration and scan statistics."""
    return json.dumps({
        "active_jurisdictions": app.get_state("jurisdictions") or [],
        "custom_rules_loaded": len(app.get_state("custom_rules") or []),
        "scan_count": app.get_state("scan_count") or 0,
        "last_report_available": bool(app.get_state("last_report")),
        "last_findings_cached": bool(app.get_state("last_findings")),
    }, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# MCP PROMPTS — reusable compliance review templates
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.prompt()
def compliance_review(code: str, language: str = "javascript") -> str:
    """Reusable prompt template for inline compliance review."""
    jurisdictions = app.get_state("jurisdictions") or ["gdpr"]
    return (
        f"Review this {language} code for compliance with "
        f"{', '.join(j.upper() for j in jurisdictions)}.\n\n"
        f"For each violation:\n"
        f"1. State which rule is violated (include article/section)\n"
        f"2. Rate severity: critical / high / medium / low\n"
        f"3. Show the exact fix as a before/after code diff\n\n"
        f"Code:\n```{language}\n{code}\n```"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CONCIERGE WRAPPER
# ─────────────────────────────────────────────────────────────────────────────
# IMPORTANT ORDERING NOTE:
#   Tools are registered on `mcp` (FastMCP) via @mcp.tool() decorators above.
#   Concierge wraps the fully-registered `mcp` instance here.
#   Tools reference `app` as a module-level global, resolved at call time —
#   so app.set_state / app.get_state work correctly even though they are
#   defined before app is assigned.
#
# 5-stage architecture matches the master plan README exactly:
#   configure → wrap_prompt → scan → remediate → report
#
# KEY FIX FROM ANALYSIS:
#   - wrap_prompt is its own stage (not merged with scan) — different timings
#   - report is NOT a terminal stage — allows re-scanning after reporting
#   - configure is reachable from any stage — change jurisdictions mid-session
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from concierge import Concierge

    app = Concierge(mcp)

    # 5-stage workflow — mirrors the master plan architecture
    app.stages = {
        "configure":    ["set_jurisdictions"],
        "wrap_prompt":  ["compliance_wrap"],
        "scan":         ["scan_code", "scan_dependencies", "scan_repository", "scan_file"],
        "remediate":    ["get_fixes", "apply_fix"],
        "report":       ["generate_report"],
    }

    # Transition graph — no terminal stages; always a path forward
    app.transitions = {
        "configure":    ["wrap_prompt", "scan"],
        "wrap_prompt":  ["scan", "configure"],
        "scan":         ["remediate", "report", "configure"],
        "remediate":    ["scan", "report"],
        "report":       ["scan", "configure"],
    }

    print("✅ Concierge wrapper active — workflow stages enforced.", file=sys.stderr)

except ImportError:
    # Graceful fallback: run as plain FastMCP if concierge is not installed.
    # Wraps FastMCP with a simple in-memory state store so all tools work.
    # Install concierge for full stage enforcement: pip install concierge
    class _StatefulMCP:
        """FastMCP wrapper that adds set_state/get_state for tools to use."""
        def __init__(self, fmcp):
            self._mcp = fmcp
            self._state = {}
        def set_state(self, key, value):
            self._state[key] = value
        def get_state(self, key, default=None):
            return self._state.get(key, default)
        def run(self, **kwargs):
            self._mcp.run(**kwargs)
        def streamable_http_app(self):
            return self._mcp.streamable_http_app()

    app = _StatefulMCP(mcp)
    print(
        "⚠️  WARNING: concierge package not found. Running without stage enforcement.\n"
        "   Install with: pip install concierge",
        file=sys.stderr,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if "--http" in sys.argv:
        # HTTP mode: for Lovable / remote web dashboard clients
        # Test with: curl http://localhost:8080/sse
        try:
            http_app = app.streamable_http_app()
            import uvicorn
            print("🌐 ComplianceShield running in HTTP mode on :8080", file=sys.stderr)
            uvicorn.run(http_app, host="0.0.0.0", port=8080)
        except AttributeError:
            print("❌ HTTP mode requires Concierge. Install with: pip install concierge", file=sys.stderr)
            sys.exit(1)
    else:
        # stdio mode: for Claude Code and Cursor (default, recommended for demo)
        print("🛡️  ComplianceShield MCP server starting (stdio mode)...", file=sys.stderr)
        app.run(transport="stdio")

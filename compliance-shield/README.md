# ComplianceShield 🛡️

> **Your AI can code. Now it can also lawyer.**

A live compliance layer that lives inside your IDE. ComplianceShield wraps your
AI coding prompts with jurisdiction-specific rules, scans generated code for
violations, audits dependencies for malware, and produces audit-ready reports —
all without leaving Claude Code, Cursor, or Lovable.

**Supported regulations:** GDPR (EU) · DPDP (India) · HIPAA (US) · SOC2

---

## Quick Start

### 1. Install dependencies

```bash
git clone https://github.com/your-org/compliance-shield
cd compliance-shield
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Add to Claude Code (one line)

```bash
claude mcp add compliance-shield --transport stdio -- python /path/to/server.py
```

Or drop `.mcp.json` into your project root — Claude Code auto-detects it.

### 3. Verify

In Claude Code, type `/mcp`. You should see `compliance-shield` listed as connected.

---

## The 5-Stage Workflow

ComplianceShield enforces a strict workflow via Concierge. You cannot skip stages — this is protocol-level enforcement, not a suggestion.

```
Stage 1: configure    → set which regulations apply to your project
Stage 2: wrap_prompt  → inject compliance rules BEFORE generating code
Stage 3: scan         → audit code + dependencies AFTER generation
Stage 4: remediate    → generate and apply one-click fixes
Stage 5: report       → export audit-ready report for enterprise reviews
```

### Stage 1 — Configure
```
set_jurisdictions(["gdpr", "dpdp"])
```

### Stage 2 — Wrap your prompt (before generating code)
```
compliance_wrap("build a user registration API with email and phone")
```
Paste the output as your next Claude prompt. Code generated from a wrapped prompt is born compliant.

### Stage 3 — Scan existing code
```
scan_code(code="<paste your code>", filename="routes/register.js")
scan_dependencies(package_json="<paste package.json>")
```

### Stage 4 — Fix violations
```
get_fixes()                                           # uses cached scan results
apply_fix(file_path="register.js", fixed_code="...")  # writes fix, backs up original
```

### Stage 5 — Generate compliance report
```
generate_report()
```
Returns a professional Markdown report ready for enterprise security reviewers.

---

## Running Tests

```bash
python test_server.py smoke    # no API keys needed, < 5 seconds
python test_server.py          # full suite
```

---

## HTTP Mode (for Lovable / remote clients)

```bash
python server.py --http
# Then in Lovable: Settings → Connectors → New MCP Server → http://localhost:8080
```

---

## Architecture

```
Developer's IDE (Claude Code / Cursor / Lovable / VSCode)
       |
       | MCP Protocol (stdio or HTTP)
       v
+--[Concierge Wrapper]-- Enforces compliance workflow stages
|       |
|       |  Stage 1: configure    → set_jurisdictions
|       |  Stage 2: wrap_prompt  → compliance_wrap
|       |  Stage 3: scan         → scan_code, scan_dependencies
|       |  Stage 4: remediate    → get_fixes, apply_fix
|       |  Stage 5: report       → generate_report
|       v
|   [Gemini API]  -- Code analysis + auto-remediation
|   [SafeDep]     -- Dependency malware/vulnerability scanning
|   [CrustData]   -- Real-time compliance intelligence
|
+--[Emergent.sh Dashboard] -- Web UI for reports and config
```

**Sponsor integrations:** Concierge · SafeDep · CrustData · Gemini API · Emergent.sh

---

## Pricing
- **Free:** 10 scans/month, 1 jurisdiction
- **Pro (₹8,299/month):** Unlimited scans, all 4 jurisdictions, audit reports
- **Enterprise (₹4,16,000/year):** Everything + audit trail export + security whitepaper

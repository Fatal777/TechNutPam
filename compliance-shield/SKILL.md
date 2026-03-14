# ComplianceShield — Claude Code Skill

## Description
ComplianceShield is a live compliance agent that checks your code against GDPR,
India's DPDP Act, HIPAA, and SOC2 while you build. It wraps your prompts with
compliance rules before code generation, scans existing code for violations,
audits dependencies for malware, and generates audit-ready reports — all without
leaving your IDE.

## Setup

### 1. Install the MCP server (one line)
```bash
claude mcp add compliance-shield --transport stdio -- python /path/to/compliance-shield/server.py
```

Or drop the `.mcp.json` file into your project root and Claude Code will auto-detect it.

### 2. Verify connection
In Claude Code, run `/mcp` — you should see `compliance-shield` listed as connected
with the following tool available (Stage 1 — configure):
- `set_jurisdictions`

---

## Workflow

ComplianceShield enforces a 5-stage workflow. You cannot skip stages — this is
intentional. Concierge enforces the order at the MCP protocol level.

### Stage 1 — Configure
Tell the server which regulations apply to your project.

**Tool:** `set_jurisdictions`
```
set_jurisdictions(["gdpr", "dpdp"])
```
Supported values: `gdpr`, `dpdp`, `hipaa`, `soc2`

---

### Stage 2 — Wrap Prompt (pre-generation)
Before asking Claude to generate code, wrap your request so code is born compliant.

**Tool:** `compliance_wrap`
```
compliance_wrap("build a user registration form that collects name, email, and phone")
```
Returns a compliance-injected prompt. Paste the output as your next message to Claude.

---

### Stage 3 — Scan (post-generation)
After code exists, scan it for violations.

**Tool:** `scan_code`
```
scan_code(code="<paste your code here>", filename="routes/register.js")
```
Returns a JSON array of findings: severity, rule violated, line number, suggested fix.

**Tool:** `scan_dependencies`
```
scan_dependencies(package_json="<paste your package.json contents>")
```
Uses SafeDep threat intelligence. Fail-closed: packages are blocked unless
SafeDep explicitly confirms them as safe.

---

### Stage 4 — Remediate
Generate and apply fixes for flagged violations.

**Tool:** `get_fixes`
```
get_fixes()   # Uses cached findings from last scan_code call
```
Returns the fully corrected file and a list of changes made.

**Tool:** `apply_fix`
```
apply_fix(file_path="routes/register.js", fixed_code="<corrected code>")
```
Writes the fix to disk. Backs up the original to `register.js.bak`.
Re-run `scan_code` to confirm violations are resolved.

---

### Stage 5 — Report
Generate an audit-ready compliance report.

**Tool:** `generate_report`
```
generate_report()   # Uses cached scan results from the session
```
Returns a professional Markdown report with findings by severity and jurisdiction,
dependency audit results, and a PASS/FAIL verdict.

---

## Resources
Read compliance rules directly as MCP resources:
```
compliance://rules/gdpr
compliance://rules/dpdp
compliance://rules/hipaa
compliance://rules/soc2
compliance://status
```

## Prompts
Use the built-in review prompt template:
```
compliance_review(code="<your code>", language="javascript")
```

---

## Example: Full Session Flow

```
1. set_jurisdictions(["gdpr", "dpdp"])
   → "Active jurisdictions: GDPR, DPDP. 14 rules loaded."

2. compliance_wrap("build a user registration API endpoint")
   → Returns compliance-injected prompt with GDPR + DPDP rules

3. [Use the wrapped prompt to generate code with Claude]

4. scan_code(code=<generated code>, filename="register.js")
   → "Found 0 violations" ← code was born compliant

   OR (on pre-existing code):
   → "Found 6 violations: 3 critical, 2 high, 1 medium"

5. get_fixes()
   → Returns corrected file + change summary

6. apply_fix("register.js", fixed_code)
   → Fix applied. Original backed up.

7. scan_code(code=<fixed code>)   ← re-scan to confirm
   → "Found 0 violations ✅"

8. generate_report()
   → Professional audit report: PASS ✅
```

---

## Pricing
- **Free:** 10 scans/month, 1 jurisdiction
- **Pro (₹8,299/month):** Unlimited scans, all 4 jurisdictions, reports
- **Enterprise (₹4,16,000/year):** Everything + audit trail export + security whitepaper


# ComplianceShield — Implementation Guide
## Reconciled Master Reference (Anchored to Original Plan)

> **Purpose of this document:** This is the single source of truth for the hackathon build.
> Every decision here traces back to the original problem statement and master plan.
> When in doubt during the 4-hour sprint, refer to this document first.

---

## Problem Statement (Never Lose Sight Of This)

> *Developers vibe-coding with Lovable, Claude Code, Cursor, and Emergent.sh ship fast
> but with zero compliance awareness. Their AI-generated code violates GDPR, DPDP (India),
> HIPAA, SOC2 — and they don't discover it until an enterprise security review kills the deal.*

**Our answer:** A LIVE compliance layer — not a post-code scanner — that lives inside the
developer's IDE via MCP. Code is born compliant. Violations are caught inline. Fixes are
one click. Reports are export-ready.

**Pitch line:** *"Your AI can code. Now it can also lawyer."*

---

## Architecture — 5-Stage Workflow (Master Plan)

```
Developer's IDE (Claude Code / Cursor / Lovable / VSCode)
       |
       | MCP Protocol (stdio or HTTP)
       v
+--[Concierge Wrapper]-- Enforces compliance workflow stages
|
|  Stage 1: "configure"
|    Tools: set_jurisdictions, upload_policy
|    Sponsors: Unsiloed AI (upload_policy parses compliance PDFs)
|
|  Stage 2: "wrap_prompt"
|    Tools: compliance_wrap
|    Purpose: Inject rules BEFORE code generation — "code born compliant"
|    NOTE: Intentionally separate stage from scan (different timing)
|
|  Stage 3: "scan"
|    Tools: scan_code, scan_dependencies
|    Sponsors: SafeDep (scan_dependencies), Gemini API (scan_code)
|
|  Stage 4: "remediate"
|    Tools: get_fixes, apply_fix
|    Sponsors: Gemini API (get_fixes generates diffs)
|
|  Stage 5: "report"
|    Tools: generate_report
|    Sponsors: Gemini API (report generation), Emergent.sh (displays reports)
|
+--[Emergent.sh Dashboard]-- Web UI for reports, jurisdiction config, billing
       |
       v
  [Razorpay] -- Billing for SaaS plans
```

**5 Sponsor Tools — All Meaningfully Integrated:**

| Sponsor | Tool | Stage | What it does |
|---------|------|-------|-------------|
| Concierge | Workflow wrapper | All | Protocol-level stage enforcement — can't skip scans |
| SafeDep | scan_dependencies | Stage 3 | Malware/vuln scanning of npm packages, fail-closed |
| Unsiloed AI | upload_policy | Stage 1 | Parses GDPR/DPDP/HIPAA/SOC2 PDFs into rule text |
| Emergent.sh | Dashboard | Stage 5 | Web UI showing scan results, reports, Razorpay pricing |
| Razorpay | Pricing page | Stage 5 | Payment checkout for Free/Pro/Enterprise plans |
| Gemini API | scan_code, get_fixes, generate_report | Stages 3–5 | Core AI engine |

---

## What Changed From the Original Plan (And Why)

### Change 1: Stage Design — 5 Stages Not 4

**Original plan's server.py had:**
```python
app.stages = {
    "configure":  ["set_jurisdictions", "upload_policy"],
    "analyze":    ["compliance_wrap", "scan_code", "scan_dependencies"],  # ← merged
    "remediate":  ["get_fixes", "apply_fix"],
    "report":     ["generate_report"],
}
```

**This implementation uses:**
```python
app.stages = {
    "configure":    ["set_jurisdictions", "upload_policy"],
    "wrap_prompt":  ["compliance_wrap"],              # ← its own stage
    "scan":         ["scan_code", "scan_dependencies"],
    "remediate":    ["get_fixes", "apply_fix"],
    "report":       ["generate_report"],
}
```

**Why:** The original README/architecture diagram already specified 5 stages.
The server.py code drifted from it. `compliance_wrap` operates BEFORE code generation;
`scan_code` operates AFTER. Merging them into "analyze" obscures this distinction
and confuses the developer about which to call when.

### Change 2: "report" Is Not a Terminal Stage

**Original plan:**
```python
app.transitions = {
    ...
    "report": [],    # ← terminal — session dies here
}
```

**This implementation:**
```python
app.transitions = {
    ...
    "report": ["scan", "configure"],    # ← can always re-scan or reconfigure
}
```

**Why:** Developers iterate. After seeing a report, they fix code and re-scan.
A terminal "report" stage forces a session restart, destroying all state
(jurisdictions, scan count, cached findings). This breaks the real workflow.

### Change 3: `load_rules()` Helper — Was Missing, Now Implemented

**Original plan:** Called `load_rules(jurisdictions)` in `compliance_wrap` and
`scan_code` but never defined the function. This causes `NameError` at runtime
before the demo even starts.

**This implementation:** `load_rules()` is implemented in `server.py` and reads
from `rules/*.json` files, including any custom rules from `upload_policy`.

### Change 4: `apply_fix` Tool — Was Listed, Now Implemented

**Original plan:** Listed `apply_fix` in the remediate stage but provided no
`@mcp.tool()` definition. Concierge would likely fail to start or the stage
would silently have one tool missing.

**This implementation:** `apply_fix(file_path, fixed_code)` writes the corrected
file to disk with automatic backup to `*.bak`.

### Change 5: Concierge Import Order — Explicit and Safe

**This implementation:** All `@mcp.tool()` decorators run on `mcp` (FastMCP) first.
Concierge wraps `mcp` afterward. Tools reference `app` as a module-level global,
resolved at call time — so `app.set_state` / `app.get_state` work correctly.
A graceful fallback runs as plain FastMCP if `concierge` is not installed,
with a visible warning — so the server never silently fails to start.

### Change 5: Tool Name Consistency

**Original plan:** Used `upload_policy_doc` in some places and `upload_policy`
in others. This implementation uses `upload_policy` everywhere, matching the
stages dict.

---

## File Structure

```
compliance-shield/
│
├── server.py                    ← Person A | Main MCP server (Concierge-wrapped)
│
├── rules/
│   ├── gdpr.json                ← Person D | GDPR rules (8 rules, Art. refs)
│   ├── dpdp.json                ← Person D | India DPDP rules (6 rules, Sec. refs)
│   ├── hipaa.json               ← Person D | HIPAA rules (6 rules, CFR refs)
│   └── soc2.json                ← Person D | SOC2 controls (7 rules, CC refs)
│
├── integrations/
│   ├── safedep.py               ← Person B | SafeDep REST API wrapper
│   └── unsiloed.py              ← Person B | Unsiloed AI async polling wrapper
│
├── demo/
│   ├── bad-express-app.js       ← Person D | 8-violation demo app (Node.js)
│   └── bad-package.json         ← Person D | package.json with flatmap-stream
│
├── .mcp.json                    ← Person A | Drop-in project MCP config
├── .env.example                 ← All    | API key template
├── requirements.txt             ← Person A | Python dependencies
├── IMPLEMENTATION_GUIDE.md      ← This file
└── README.md                    ← Person D | Setup instructions
```

---

## Hour-by-Hour Build Plan (Reconciled)

### First 15 Minutes: ALL TEAM — Setup Sprint

All four people work in parallel:

**Person A:** Get Gemini API key from ai.google.dev, verify `pip install concierge` works
(confirm exact PyPI package name — use `pip install concierge` not `concierge-sdk`).

**Person B:** Sign up for SafeDep at app.safedep.io (get API key + Tenant ID),
sign up for Unsiloed AI at docs.unsiloed.ai.

**Person C:** Create Emergent.sh project, get Razorpay test API keys.

**Person D:** Clone/init GitHub repo, create the directory structure, commit rules/ files.

```bash
# All team runs:
mkdir compliance-shield && cd compliance-shield
python -m venv venv && source venv/bin/activate
pip install mcp[cli] concierge google-generativeai httpx python-dotenv uvicorn
cp .env.example .env   # then fill in keys
```

**Immediate first test (Person A, minute 15):**
```python
# smoke_test.py — run this BEFORE writing any business logic
from mcp.server.fastmcp import FastMCP
from concierge import Concierge

mcp = FastMCP("test")

@mcp.tool()
def hello() -> str:
    return app.get_state("x") or "no state"

app = Concierge(mcp)
app.set_state("x", "state works")
print("hello:", hello())   # should print "state works"
print("Concierge OK")
```
This test resolves Risk 1 (tool decoration) and Risk 3 (state access) in 5 minutes.

---

### Hour 1 (0:15 – 1:15): Core MCP Server

**Person A (60 min):** Build `server.py` using this guide as the reference.
- Implement `set_jurisdictions`, `compliance_wrap`, `scan_code`, `get_fixes`, `generate_report`
- Wire `load_rules()` helper
- Set up Concierge stages and transitions exactly as documented above

**Person B (60 min):** Implement the integrations
- SafeDep: Use `integrations/safedep.py` as reference — wire into `scan_dependencies` in server.py
- Unsiloed AI: Use `integrations/unsiloed.py` as reference — wire into `upload_policy` in server.py

**Person C (60 min):** Build Emergent.sh dashboard
Use this prompt verbatim in Emergent.sh:
```
Build a compliance dashboard web app called "ComplianceShield" with:

PAGE 1 - Landing: Hero "Your Legal Department in a Box", 3-step how-it-works
  (Install MCP → Toggle jurisdictions → Code compliantly), setup instructions
  showing: claude mcp add compliance-shield --transport stdio -- python server.py

PAGE 2 - Dashboard: Left sidebar jurisdiction toggles (GDPR, DPDP, HIPAA, SOC2),
  main scan results table (timestamp, file, findings count, severity breakdown),
  click → detail view showing severity badge, rule, violation, fixed code, Accept Fix button.
  Right panel: SafeDep dependency results (safe/blocked packages).

PAGE 3 - Reports: list of reports, date/jurisdictions/status, Export PDF button.

PAGE 4 - Pricing:
  Free: 10 scans/month, 1 jurisdiction
  Pro INR 8,299/month: unlimited scans, all jurisdictions, reports
  Enterprise INR 4,16,000/year: everything + audit trail
  Razorpay payment buttons in test mode.

Dark theme, modern SaaS look, responsive.
```

**Person D (60 min):** Compliance rules + demo assets
- `rules/gdpr.json`, `rules/dpdp.json`, `rules/hipaa.json`, `rules/soc2.json` (already created)
- `demo/bad-express-app.js` (8 violations — already created)
- `demo/bad-package.json` (includes flatmap-stream — already created)

---

### Hour 2 (1:15 – 2:15): Wire and Test

**Person A (60 min):**
- Add `@mcp.resource("compliance://rules/{jurisdiction}")` and `@mcp.resource("compliance://status")`
- Add `@mcp.prompt()` for `compliance_review`
- Add `apply_fix` tool (already in server.py)
- Test: Install in Claude Code and run all 9 verification steps (see below)

**Person B (60 min):** Integration testing
- Test SafeDep with `express`, `lodash`, `flatmap-stream` (should flag flatmap-stream)
- Test Unsiloed AI with a GDPR PDF — confirm parsed text is stored in state
- Add timeout handling and error fallbacks throughout

**Person C (60 min):** Dashboard API wiring
- Bridge dashboard jurisdiction toggles → call `set_jurisdictions` on MCP server
- Wire "Scan Code" form → `scan_code` + `scan_dependencies`
- Wire "Generate Report" → `generate_report`

**Person D (60 min):** End-to-end testing in Claude Code
```bash
claude mcp add compliance-shield --transport stdio -- python /path/to/server.py
```
Then test all 9 verification steps, document failures, feed to team.

---

### Hour 3 (2:15 – 3:15): Polish + Razorpay

**Person A (30 min):** Create `.mcp.json`, verify HTTP mode works, write SKILL.md
**Person A (30 min):** Add scan counter state tracking, final Concierge transition testing

**Person B (60 min):** HTTP mode
```python
# Test that the server runs in HTTP mode for Lovable
python server.py --http
```
Test from Lovable: Settings → Connectors → New MCP Server → `http://localhost:8080`

**Person C (60 min):** Razorpay integration on Emergent.sh pricing page
```javascript
const rzp = new Razorpay({
  key_id: "rzp_test_...",
  amount: 829900,  // INR 8,299 in paise
  currency: "INR",
  name: "ComplianceShield",
  description: "Pro Plan — All Jurisdictions",
  handler: function(response) {
    alert("Payment successful! All jurisdictions unlocked.");
  }
});
rzp.open();
```

**Person D (60 min):** Demo script prep + backup slides + 3x full rehearsal

---

### Hour 4 (3:15 – 4:00): Dress Rehearsal

- 15 min bug fixes
- 20 min: run through demo script 3 times, refine timing
- 10 min: record a backup screen recording in case live demo fails

---

## Demo Script (3 Minutes Exactly)

### Opening (30 sec)
> "50 million developers now use AI to write code. But here's the problem —
> AI doesn't know about GDPR. Or India's DPDP Act. Or HIPAA. Every vibe-coded app
> fails its first enterprise security review. We built ComplianceShield —
> the Legal Department that lives inside your IDE."

### Live Demo (2 min)

1. Show Claude Code with `/mcp` → ComplianceShield shows green, all 7 tools visible in Stage 1
2. *"Let me configure for GDPR and India DPDP..."*
   → Call `set_jurisdictions(["gdpr", "dpdp"])` → shows 13 rules loaded
3. *"Now before I write a single line of code, I'll wrap my prompt..."*
   → Call `compliance_wrap("build a user registration form with email and phone")`
   → Show the wrapped prompt with injected GDPR+DPDP constraints
4. *"But what about code that's already been written?"*
   → Paste `demo/bad-express-app.js` → Call `scan_code`
   → Show findings: "8 violations — 4 critical, 2 high..."
5. **[KEY DEMO MOMENT]** *"Watch what happens if I try to jump straight to a report..."*
   → Try calling `generate_report` from Stage 3 (scan)
   → Show: **tool not in tools/list** — Concierge blocked it
   → *"Concierge enforces the workflow at the protocol level. You can't skip the scan.
       Compliance is enforced. Not suggested."*
6. *"Back to the scan — one click to fix..."*
   → Call `get_fixes` → show the remediation diff
7. *"And dependencies..."*
   → Call `scan_dependencies` with `demo/bad-package.json`
   → Show SafeDep flagging `flatmap-stream` as malware
8. *"Now the report for your auditor..."*
   → Call `generate_report` → show the professional markdown output
9. Flash of Emergent.sh dashboard showing scan history and Razorpay pricing page

### Close (30 sec)
> "ComplianceShield is an MCP server. One line to install. Works in Claude Code,
> Cursor, Lovable, VSCode. Powered by Concierge workflow enforcement, SafeDep
> dependency scanning, Unsiloed AI policy parsing, Gemini for analysis,
> Razorpay for billing. Built on Emergent.sh.
> Your AI can code — now it can also lawyer. $99 a month."

---

## Verification Checklist (Person D runs this in Hour 2)

```
1. ✅ Install: claude mcp add compliance-shield --transport stdio -- python server.py
2. ✅ /mcp shows compliance-shield green with 7 tools (in configure stage)
3. ✅ set_jurisdictions(["gdpr", "dpdp"]) → "Active jurisdictions: GDPR, DPDP"
4. ✅ compliance_wrap("build login form") → wrapped prompt with rules injected
5. ✅ scan_code(bad_express_app_contents) → JSON with 8 violations
6. ✅ get_fixes() → remediation diff using cached findings
7. ✅ apply_fix("demo/bad-express-app.js", fixed_code) → file written, .bak created
8. ✅ scan_dependencies(bad_package_json_contents) → flatmap-stream BLOCKED
9. ✅ generate_report() → professional markdown audit report
10. ✅ upload_policy("path/to/gdpr.pdf") → "Policy parsed, N chars extracted"
11. ✅ CONCIERGE ENFORCEMENT: call generate_report from scan stage → blocked
12. ✅ HTTP mode: python server.py --http → connects from Lovable
13. ✅ Web dashboard: Emergent.sh shows scan history, reports, Razorpay pricing
14. ✅ Razorpay: Click "Buy Pro" → test checkout opens
```

---

## Pre-Hackathon Must-Confirm (15 Minutes Before Clock Starts)

| # | Check | Who | Risk if skipped |
|---|-------|-----|----------------|
| 1 | `pip install concierge` works (not `concierge-sdk`) | Person A | Server won't start |
| 2 | Run `smoke_test.py` — `app.get_state()` inside `@mcp.tool()` works | Person A | All tools broken |
| 3 | Concierge transitions are automatic or require `app.transition_to()` | Person A | Demo stuck in configure |
| 4 | Gemini API key active and `gemini-2.0-flash` model accessible | Person A | All AI tools broken |
| 5 | SafeDep API key + Tenant ID accepted by /QueryPackageAnalysis | Person B | scan_dependencies broken |
| 6 | Unsiloed AI API key accepted by /parse endpoint | Person B | upload_policy broken |
| 7 | Emergent.sh project can be shared as public URL | Person C | No dashboard to show |
| 8 | Razorpay test checkout opens (rzp_test_ keys) | Person C | No billing demo |

---

## Business Model (Aligned to Original Plan)

| Plan | Price | Limits | Jurisdictions |
|------|-------|--------|---------------|
| Free | ₹0 | 10 scans/month | 1 jurisdiction |
| Pro | ₹8,299/month (~$99) | Unlimited scans | All 4 |
| Enterprise | ₹4,16,000/year (~$5,000) | Unlimited + audit trail + whitepaper | All 4 + custom |

**Target customer:** B2B SaaS founders who need enterprise deals but can't afford a compliance team.
One enterprise deal saved = 12+ months of Pro subscription. ROI is immediate.

---

## YC Fit (From Master Plan)

**Primary category:** AI Developer Tools & Infra
**Secondary category:** AI Native Enterprise Software

ComplianceShield is the missing compliance infrastructure layer for the
entire vibe-coding ecosystem — the same layer that legal teams provide
to traditional engineering orgs, now delivered as an MCP server.

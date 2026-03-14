Context
Problem: Developers vibe-coding with Lovable, Claude Code, Cursor, and Emergent.sh ship fast but with zero compliance awareness. Their AI-generated code violates GDPR, DPDP (India), HIPAA, SOC2 - and they don't discover it until an enterprise security review kills the deal.
Our Approach: NOT a post-code scanner. A LIVE compliance layer that sits inside the developer's coding environment.
We build a Concierge-wrapped MCP server that integrates directly into Claude Code, Cursor, VSCode, and Lovable. While the developer is coding, our MCP server:

Wraps their prompts with jurisdiction-specific compliance constraints (code is born compliant)
Scans every dependency in real-time via SafeDep before installation
Analyzes generated code against toggled compliance frameworks
Auto-generates remediation diffs the developer can accept with one click
Generates exportable compliance reports

Why MCP + Concierge is the right architecture:

MCP is the universal protocol supported by Claude Code, Cursor, Cline, Lovable, Windsurf
Concierge enforces compliance workflow steps at the protocol level (can't skip scans)
SafeDep already HAS an MCP server we can chain
Developer never leaves their IDE - compliance happens inline
One-line setup: claude mcp add compliance-shield --transport http https://our-server.com/mcp


YC RFS Categories (Fall 2025 + Spring 2026)

Category
Ideas
AI Developer Tools & Infra
Cursor for PMs (S26), Make LLMs Easy to Train (S26), Multi-Agent Infra (F25)
AI + Enterprise / B2B
AI Native Enterprise Software (F25), AI-Native Agencies (S26), First 10-person $100B Co (F25)
AI + Government
LLMs for Gov Consulting (F25), AI for Government (S26), Fraud Hunter Infra (S26)
AI + Finance
AI-Native Hedge Funds (S26), Stablecoin Financial Services (S26)
AI + Physical/Industrial
Worker Retraining (F25), AI Guidance for Physical Work (S26), Modern Metal Mills (S26)
AI Foundation Models
Video Generation as Primitive (F25), Large Spatial Models (S26)
ComplianceShield fits: AI Developer Tools & Infra + AI Native Enterprise Software. We're the missing compliance infrastructure layer for the entire vibe-coding ecosystem.


Architecture
Developer's IDE (Claude Code / Cursor / Lovable / VSCode)
       |
       | MCP Protocol (stdio or HTTP)
       v
+--[Concierge Wrapper]-- Enforces compliance workflow stages
|       |
|       |  Stage 1: "configure"
|       |    Tools: set_jurisdictions, upload_policy_doc, get_regulatory_updates
|       |
|       |  Stage 2: "wrap_prompt"
|       |    Tools: compliance_wrap, search_compliance_web, ask_compliance_question
|       |
|       |  Stage 3: "scan"
|       |    Tools: scan_code, scan_dependencies, search_compliance_news
|       |
|       |  Stage 4: "remediate"
|       |    Tools: get_fixes, apply_fix
|       |
|       |  Stage 5: "report"
|       |    Tools: generate_report, export_pdf
|       |
|       v
|   [Gemini API]  -- Code analysis + auto-remediation
|   [SafeDep]     -- Dependency malware/vulnerability scanning
|   [Unsiloed AI] -- Parse compliance PDFs into structured rules
|   [CrustData]   -- Real-time compliance intelligence (web search + news search)
|
+--[Emergent.sh Dashboard]-- Web UI for reports, jurisdiction config, billing
       |
       v
  [Razorpay] -- Billing for SaaS plans
Sponsor tools: 6 meaningfully integrated

Concierge - Wraps our MCP server, enforces workflow stages
SafeDep - Chained MCP for dependency security scanning
Unsiloed AI - Parses compliance PDFs into machine-readable rules
CrustData - Real-time compliance intelligence via Web Search + News Search APIs
Emergent.sh - Dashboard UI for web-based config/reports/billing
Razorpay - Payment integration for subscription plans

Core AI: Gemini API (code analysis, compliance checking, auto-remediation)


Tech Stack
MCP Server: Python with FastMCP + concierge-sdk
AI Engine: Google Gemini API (google-generativeai Python SDK)
Compliance Intelligence: CrustData Web Search + News Search API (real-time regulatory updates, enforcement news, AI-powered compliance Q&A)
Dependency Scanning: SafeDep REST API / MCP chaining
Document Parsing: Unsiloed AI REST API
Dashboard/Web UI: Emergent.sh (vibe-coded)
Payments: Razorpay Checkout (test mode)
Deployment: MCP server runs locally via stdio OR hosted via HTTP


---

## CrustData Compliance Intelligence Integration

CrustData provides the **real-time compliance intelligence layer** for ComplianceShield. While the static rule files (`rules/*.json`) define what the compliance rules ARE, CrustData tells us what's **happening right now** — enforcement actions, regulatory updates, new guidance, and AI-powered answers to compliance questions.

### API Endpoints Used

| Endpoint | Method | Purpose | Cost |
|----------|--------|---------|------|
| `/screener/web-search` | POST | Search web, news, AI, scholar sources | 1 credit/query |
| `/screener/web-fetch` | POST | Fetch full HTML from up to 10 URLs | 1 credit/URL |

**Auth:** `Authorization: Token <CRUSTDATA_API_TOKEN>` header
**Rate Limit:** 10 requests/minute
**Base URL:** `https://api.crustdata.com`

### Source Types

The web-search endpoint supports multiple source types via the `sources` parameter:

- `"web"` — General web results (compliance guidance, regulatory body websites)
- `"news"` — News articles (enforcement actions, regulatory updates, breach reports)
- `"ai"` — Google AI Mode (synthesized answers to compliance questions)
- `"scholar-articles"` — Academic/legal papers on compliance topics
- `"social"` — Social media discussions about regulatory changes

### 5 MCP Tools

These are registered via `register_crustdata_tools(mcp)` from `integrations/crustdata_tools.py`:

#### 1. `search_compliance_news(jurisdictions, topic?)`
Search for latest regulatory news, enforcement actions, and fines.

```
# Example: Latest GDPR enforcement news
search_compliance_news(["gdpr"])

# Example: HIPAA breach notifications
search_compliance_news(["hipaa"], topic="data breach")

# Example: All jurisdictions, encryption-related news
search_compliance_news(["gdpr", "dpdp", "hipaa", "soc2"], topic="encryption")
```

**How it works:** Builds queries like `"GDPR enforcement OR update OR regulation"`, searches CrustData news sources with geo-targeting (GDPR→GB, DPDP→IN, HIPAA→US), returns results with jurisdiction tags.

#### 2. `search_compliance_web(query, jurisdictions?)`
Free-form web search scoped to compliance topics.

```
# Example: Research cookie consent implementation
search_compliance_web("cookie consent implementation requirements", ["gdpr"])

# Example: Data encryption standards
search_compliance_web("encryption at rest requirements", ["hipaa", "gdpr"])

# Example: General compliance search (no jurisdiction filter)
search_compliance_web("data retention policy best practices")
```

**How it works:** Augments queries with jurisdiction-specific terms, geo-targets by region, searches CrustData web sources.

#### 3. `fetch_regulation_content(urls)`
Fetch full content from regulatory URLs and get AI-summarized compliance guidance.

```
# Example: Fetch and summarize official GDPR guidance
fetch_regulation_content(["https://gdpr.eu/what-is-gdpr/", "https://ico.org.uk/for-organisations/guide-to-data-protection/"])
```

**How it works:** Uses CrustData Web Fetch to get full HTML (max 10 URLs), then passes each page through Gemini to extract: Key Requirements, Obligations, Penalties, and Implementation Guidance.

#### 4. `get_regulatory_updates(jurisdictions, days?)`
Get a severity-rated digest of what changed in the last N days.

```
# Example: What changed in GDPR this month?
get_regulatory_updates(["gdpr"], days=30)

# Example: All jurisdictions, last quarter
get_regulatory_updates(["gdpr", "dpdp", "hipaa", "soc2"], days=90)
```

**How it works:** Searches CrustData news with date filtering (Unix timestamps), collects results across jurisdictions, then uses Gemini to produce a structured digest with `jurisdiction`, `change`, `severity` (critical/high/medium/low), and `action_required` for each update.

#### 5. `ask_compliance_question(question, jurisdictions?)`
Ask a compliance question and get an AI-synthesized answer.

```
# Example: Quick GDPR question
ask_compliance_question("What are the GDPR requirements for cookie consent?", ["gdpr"])

# Example: HIPAA encryption question
ask_compliance_question("What encryption is required for HIPAA?", ["hipaa"])

# Example: Cross-jurisdiction question
ask_compliance_question("Can I store Indian user data on AWS US servers?", ["dpdp", "gdpr"])
```

**How it works:** First tries CrustData's `sources: ["ai"]` (Google AI Mode) for a direct synthesized answer at 1 credit. If AI mode returns no results, falls back to web search + Gemini summarization.

### File Structure

```
integrations/
├── __init__.py              # Exports CrustDataClient, ComplianceSearchEngine, register_crustdata_tools
├── crustdata.py             # Async API client (web-search, web-fetch, rate throttling)
├── compliance_search.py     # Compliance search engine (jurisdiction mapping, Gemini summarization, caching)
└── crustdata_tools.py       # 5 MCP tool definitions with register_crustdata_tools(mcp)
```

### Integration into server.py

```python
from mcp.server.fastmcp import FastMCP
from integrations import register_crustdata_tools

mcp = FastMCP("compliance-shield")
register_crustdata_tools(mcp)  # Registers all 5 CrustData tools
```

### Jurisdiction Configuration

Each jurisdiction maps to a geolocation and search terms for optimal results:

| Jurisdiction | Geo Code | Primary Search Terms | Regulatory Bodies |
|-------------|----------|---------------------|-------------------|
| `gdpr` | GB | GDPR, EU data protection, EDPB | edpb.europa.eu, gdpr.eu, ico.org.uk |
| `dpdp` | IN | DPDP Act, India data protection | meity.gov.in |
| `hipaa` | US | HIPAA, health data privacy, HHS | hhs.gov, hipaajournal.com |
| `soc2` | US | SOC 2 compliance, AICPA trust services | aicpa.org |

### Caching & Credits

- Results are cached in-memory for 5 minutes to avoid burning credits on repeated queries
- CrustData charges 1 credit per search query (regardless of `fetch_content`)
- Web Fetch costs 1 credit per URL fetched
- Built-in rate throttling ensures we stay under the 10 RPM limit

---

4-Hour Hackathon Execution Plan (3-4 Person Team)
Team Roles
Person A (MCP Server Lead): Core MCP server + Concierge wrapper + Gemini integration
Person B (Integrations): SafeDep + Unsiloed AI integration into MCP tools
Person C (Dashboard/UI): Emergent.sh web dashboard + Razorpay billing
Person D (Rules + Demo): Compliance rules, bad code samples, demo prep, testing

First 15 Minutes: ALL TEAM - Setup Sprint
Sign up for API keys in parallel:


Person A: Gemini API key (ai.google.dev) + Concierge SDK
Person B: SafeDep (app.safedep.io) + Unsiloed AI (docs.unsiloed.ai) + CrustData (app.crustdata.com)
Person C: Emergent.sh + Razorpay (test mode)
Person D: GitHub repo init + project structure


Initialize Python project:

bash
 mkdir compliance-shield && cd compliance-shield
 python -m venv venv && source venv/bin/activate
 pip install "mcp[cli]" concierge-sdk google-generativeai httpx python-dotenv
````
- Create shared `.env`:
````
 GEMINI_API_KEY=...
 CRUSTDATA_API_TOKEN=...
 SAFEDEP_API_KEY=...
 SAFEDEP_TENANT_ID=...
 UNSILOED_API_KEY=...
 RAZORPAY_KEY_ID=...
 RAZORPAY_KEY_SECRET=...


Hour 1 (0:15 - 1:15): Core MCP Server + Compliance Engine
Person A - MCP Server with Concierge (60 min)
Build server.py - the core MCP server:
python
from mcp.server.fastmcp import FastMCP
from concierge import Concierge
import google.generativeai as genai
import os, json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# Create MCP server wrapped with Concierge
mcp = FastMCP("compliance-shield")
app = Concierge(mcp)

# Define workflow stages
app.stages = {
   "configure":  ["set_jurisdictions", "upload_policy"],
   "analyze":    ["compliance_wrap", "scan_code", "scan_dependencies"],
   "remediate":  ["get_fixes", "apply_fix"],
   "report":     ["generate_report"],
}
app.transitions = {
   "configure": ["analyze"],
   "analyze":   ["remediate", "report"],
   "remediate": ["report", "analyze"],
   "report":    [],
}
Build core MCP tools:
python
@mcp.tool()
async def set_jurisdictions(jurisdictions: list[str]) -> str:
   """Toggle compliance jurisdictions: gdpr, dpdp, hipaa, soc2"""
   app.set_state("jurisdictions", jurisdictions)
   return f"Active jurisdictions: {', '.join(jurisdictions)}"

@mcp.tool()
async def compliance_wrap(user_prompt: str) -> str:
   """Wrap a coding prompt with compliance constraints.
   Use this BEFORE generating code to ensure compliance from birth."""
   jurisdictions = app.get_state("jurisdictions") or ["gdpr"]
   rules = load_rules(jurisdictions)  # Load jurisdiction rules
   wrapped = f"""You are generating code that MUST comply with: {', '.join(jurisdictions)}.

MANDATORY REQUIREMENTS:
{rules}

USER'S REQUEST: {user_prompt}

Generate compliant code. Add comments marking compliance-relevant sections."""
   return wrapped

@mcp.tool()
async def scan_code(code: str, filename: str = "unknown") -> str:
   """Scan code for compliance violations against active jurisdictions."""
   jurisdictions = app.get_state("jurisdictions") or ["gdpr"]
   rules = load_rules(jurisdictions)

   prompt = f"""Analyze this code for compliance violations.
Active jurisdictions: {', '.join(jurisdictions)}
Rules: {rules}

Code ({filename}):
````
{code}
````

Return JSON array of findings:
[{{"severity": "critical|high|medium|low", "jurisdiction": "...",
  "rule": "...", "line": N, "violation": "...",
  "fixedCode": "..corrected snippet.."}}]
Return ONLY the JSON array, no other text."""

   response = model.generate_content(prompt)
   return response.text

@mcp.tool()
async def get_fixes(findings_json: str) -> str:
   """Generate auto-remediation diffs from scan findings."""
   prompt = f"""Given these compliance findings:
{findings_json}

Generate a unified diff that fixes ALL violations.
Format as a standard unified diff that can be applied with 'patch'.
Include comments explaining each fix."""

   response = model.generate_content(prompt)
   return response.text
Person B - SafeDep + Unsiloed + CrustData Integration (60 min)
CrustData Compliance Intelligence (DONE - already built):
The CrustData integration is complete in `integrations/`. To wire it into the MCP server, add one line to `server.py`:
```python
from integrations import register_crustdata_tools
register_crustdata_tools(mcp)  # adds 5 compliance intelligence tools
```
This gives the MCP server: `search_compliance_news`, `search_compliance_web`, `fetch_regulation_content`, `get_regulatory_updates`, `ask_compliance_question`.

SafeDep MCP tool (30 min):
python
import httpx

SAFEDEP_URL = "https://mcp.safedep.io/model-context-protocol/threats/v1/mcp"

@mcp.tool()
async def scan_dependencies(package_json: str) -> str:
   """Scan package.json dependencies for malware and vulnerabilities.
   Uses SafeDep threat intelligence. FAIL-CLOSED: blocks if uncertain."""
   packages = json.loads(package_json).get("dependencies", {})
   results = []

   async with httpx.AsyncClient() as client:
       for pkg, version in packages.items():
           resp = await client.post(
               "https://api.safedep.io/safedep.services.malysis.v1.MalwareAnalysisService/QueryPackageAnalysis",
               headers={
                   "Authorization": os.getenv("SAFEDEP_API_KEY"),
                   "X-Tenant-ID": os.getenv("SAFEDEP_TENANT_ID"),
                   "Content-Type": "application/json",
               },
               json={"ecosystem": "npm", "package_name": pkg, "version": version}
           )
           data = resp.json()
           is_malware = data.get("report", {}).get("inference", {}).get("isMalware")
           results.append({
               "package": f"{pkg}@{version}",
               "safe": is_malware == False,  # fail-closed: only safe if explicitly False
               "blocked": is_malware != False,
               "details": data.get("report", {}).get("inference", {}).get("reasoning", "")
           })

   blocked = [r for r in results if r["blocked"]]
   return json.dumps({
       "total": len(results),
       "safe": len(results) - len(blocked),
       "blocked": len(blocked),
       "results": results
   }, indent=2)
Unsiloed AI tool (30 min):
python
@mcp.tool()
async def upload_policy(file_path: str) -> str:
   """Parse a compliance policy PDF and extract rules using Unsiloed AI.
   Supports GDPR, DPDP, HIPAA, SOC2 policy documents."""
   async with httpx.AsyncClient() as client:
       # Submit document for parsing
       with open(file_path, "rb") as f:
           resp = await client.post(
               "https://prod.visionapi.unsiloed.ai/parse",
               headers={"api-key": os.getenv("UNSILOED_API_KEY")},
               files={"file": f}
           )
       job_id = resp.json().get("job_id")

       # Poll for results
       import asyncio
       for _ in range(30):
           result = await client.get(
               f"https://prod.visionapi.unsiloed.ai/parse/{job_id}",
               headers={"api-key": os.getenv("UNSILOED_API_KEY")}
           )
           if result.json().get("status") == "completed":
               parsed = result.json().get("result", {}).get("markdown", "")
               # Store parsed rules in state
               existing = app.get_state("custom_rules") or []
               existing.append(parsed)
               app.set_state("custom_rules", existing)
               return f"Policy parsed. Extracted {len(parsed)} chars of compliance rules."
           await asyncio.sleep(2)

       return "Parsing timed out. Try again."
````

**Person C - Emergent.sh Dashboard (60 min)**

Prompt for Emergent.sh:
````
Build a compliance dashboard web app called "ComplianceShield" with:

PAGE 1 - Landing Page:
- Hero: "Your Legal Department in a Box"
- Subtitle: "AI compliance agent that lives in your IDE"
- How it works: 3 steps (Install MCP -> Toggle jurisdictions -> Code compliantly)
- Setup instructions showing: claude mcp add compliance-shield ...
- CTA: "Get Started Free" and "View Pricing"

PAGE 2 - Dashboard:
- Left sidebar: Jurisdiction toggles (GDPR, DPDP India, HIPAA, SOC2) as on/off switches
- Main area: Recent scan results in a table (timestamp, file, findings count, severity breakdown)
- Click a scan -> detail view with findings cards, each showing:
 - Severity badge (Critical=red, High=orange, Medium=yellow, Low=blue)
 - Jurisdiction tag
 - Rule violated
 - Code snippet with violation highlighted
 - "Fixed Code" section with corrected version
 - "Accept Fix" button
- Right panel: Dependency scan results (SafeDep) showing safe/blocked packages

PAGE 3 - Reports:
- List of generated compliance reports
- Each report shows: date, jurisdictions checked, findings summary, status
- "Export PDF" button for each report
- "Generate Security Whitepaper" button

PAGE 4 - Pricing:
- Free: 10 scans/month, 1 jurisdiction
- Pro $99/month: Unlimited scans, all jurisdictions, reports
- Enterprise $5000/year: Everything + security whitepaper + audit trail export
- Razorpay payment buttons

Dark theme, modern SaaS look, responsive.
Person D - Compliance Rules + Demo Code (60 min)
Create rules/ directory with jurisdiction rule files:
rules/gdpr.json:
json
{
 "jurisdiction": "GDPR (EU)",
 "rules": [
   {"id": "GDPR-1", "rule": "No PII in logs", "description": "Personal data must not be logged to console, files, or monitoring systems", "article": "Art. 5(1)(f)"},
   {"id": "GDPR-2", "rule": "Encryption at rest", "description": "Personal data must be encrypted when stored", "article": "Art. 32"},
   {"id": "GDPR-3", "rule": "Explicit consent", "description": "Must obtain explicit user consent before collecting personal data", "article": "Art. 7"},
   {"id": "GDPR-4", "rule": "Right to deletion", "description": "Must implement data deletion endpoint/mechanism", "article": "Art. 17"},
   {"id": "GDPR-5", "rule": "Data minimization", "description": "Only collect data that is necessary for the stated purpose", "article": "Art. 5(1)(c)"},
   {"id": "GDPR-6", "rule": "No cross-border transfer without safeguards", "description": "Data cannot leave EU without adequate protection", "article": "Art. 46"}
 ]
}
rules/dpdp.json (India Digital Personal Data Protection Act):
json
{
 "jurisdiction": "DPDP (India)",
 "rules": [
   {"id": "DPDP-1", "rule": "Data localization", "description": "Critical personal data must be stored in India", "section": "Sec. 17"},
   {"id": "DPDP-2", "rule": "Purpose limitation", "description": "Data processing only for the purpose consented to", "section": "Sec. 5"},
   {"id": "DPDP-3", "rule": "Consent manager", "description": "Must provide mechanism for users to manage consent", "section": "Sec. 6"},
   {"id": "DPDP-4", "rule": "Data breach notification", "description": "Must notify Data Protection Board of breaches", "section": "Sec. 8"},
   {"id": "DPDP-5", "rule": "Grievance officer", "description": "Must appoint a grievance redressal officer", "section": "Sec. 13"}
 ]
}
Create demo "bad code" samples:
demo/bad-express-app.js - Node.js app with multiple violations:
javascript
const express = require('express');
const mysql = require('mysql');
const app = express();

const DB_PASSWORD = "admin123";  // VIOLATION: Hardcoded secret
const db = mysql.createConnection({host: 'localhost', password: DB_PASSWORD});

app.post('/register', (req, res) => {
 const {name, email, ssn, phone} = req.body;
 console.log(`New user: ${name}, ${email}, SSN: ${ssn}`);  // VIOLATION: PII in logs

 const query = `INSERT INTO users VALUES ('${name}', '${email}', '${ssn}')`;  // VIOLATION: SQL injection
 db.query(query);

 // No consent check  // VIOLATION: No explicit consent (GDPR Art. 7)
 // No encryption     // VIOLATION: No encryption at rest (GDPR Art. 32)
 // SSN collected but not needed  // VIOLATION: Data minimization (GDPR Art. 5)
 // No deletion endpoint  // VIOLATION: Right to deletion (GDPR Art. 17)

 res.json({success: true, userData: {name, email, ssn}});  // VIOLATION: Exposing PII in response
});

app.listen(3000);


Hour 2 (1:15 - 2:15): Wire Everything Together
Person A - Complete MCP Server + Prompts/Resources (60 min)
Add MCP resources (compliance rules as readable context):
python
@mcp.resource("compliance://rules/{jurisdiction}")
def get_rules(jurisdiction: str) -> str:
   """Get compliance rules for a jurisdiction."""
   rules_path = f"rules/{jurisdiction}.json"
   with open(rules_path) as f:
       return f.read()

@mcp.resource("compliance://status")
def get_status() -> str:
   """Get current compliance configuration."""
   return json.dumps({
       "active_jurisdictions": app.get_state("jurisdictions") or [],
       "custom_rules_loaded": len(app.get_state("custom_rules") or []),
       "scan_count": app.get_state("scan_count") or 0,
   })
Add MCP prompts (reusable compliance templates):
python
@mcp.prompt()
def compliance_review(code: str, language: str = "javascript") -> str:
   """Review code for compliance issues."""
   jurisdictions = app.get_state("jurisdictions") or ["gdpr"]
   return f"""Review this {language} code for compliance with {', '.join(jurisdictions)}.
For each violation found, explain:
1. What rule is violated and why
2. The severity (critical/high/medium/low)
3. The exact fix needed

Code:
````{language}
{code}
```"""
```

Add `generate_report` tool:
```python
@mcp.tool()
async def generate_report(scan_results: str) -> str:
   """Generate a compliance report from scan results."""
   jurisdictions = app.get_state("jurisdictions") or []
   prompt = f"""Generate a professional compliance report in Markdown:

SCAN RESULTS:
{scan_results}

JURISDICTIONS CHECKED: {', '.join(jurisdictions)}

Format:
# ComplianceShield Compliance Report
## Summary
## Findings by Severity
## Findings by Jurisdiction
## Recommended Actions
## Compliance Status: PASS/FAIL"""

   response = model.generate_content(prompt)
   return response.text
```

Wire up server entry point:
```python
if __name__ == "__main__":
   app.run(transport="stdio")
   # For HTTP hosting: app.run(transport="streamable-http", host="0.0.0.0", port=8080)
```

**Person B - Integration Testing + Error Handling (60 min)**
- Test SafeDep integration with real packages (express, lodash, a known bad one)
- Test Unsiloed AI with a sample GDPR PDF
- Add error handling: timeouts, API failures, graceful fallbacks
- Create `test_server.py` that calls each MCP tool programmatically

**Person C - Dashboard API Wiring (60 min)**
- Build API backend (on Emergent.sh or separate FastAPI) that bridges dashboard <-> MCP server
- Wire dashboard jurisdiction toggles to call `set_jurisdictions` tool
- Wire "Scan Code" form to call `scan_code` + `scan_dependencies`
- Wire findings display to show results from scans
- Wire "Export Report" to call `generate_report`

**Person D - End-to-End Testing in Claude Code (60 min)**
- Install the MCP server locally in Claude Code:
```bash
 claude mcp add compliance-shield --transport stdio -- python /path/to/server.py
```
- Test the full flow in Claude Code:
 1. `/mcp` to verify server is connected
 2. Use `set_jurisdictions` tool to enable GDPR + DPDP
 3. Use `compliance_wrap` on a prompt -> see wrapped prompt with rules
 4. Use `scan_code` on bad demo code -> see findings
 5. Use `scan_dependencies` on a package.json -> see SafeDep results
 6. Use `get_fixes` -> see remediation diffs
 7. Use `generate_report` -> see compliance report
- Document any bugs, feed to team

---

### Hour 3 (2:15 - 3:15): Razorpay + Polish + Setup Config

**Person A - .mcp.json Config for Easy Setup (30 min)**
Create a project `.mcp.json` that any developer can drop into their project:
```json
{
 "mcpServers": {
   "compliance-shield": {
     "command": "python",
     "args": ["-m", "compliance_shield.server"],
     "env": {
       "GEMINI_API_KEY": "${GEMINI_API_KEY}",
       "CRUSTDATA_API_TOKEN": "${CRUSTDATA_API_TOKEN}",
       "SAFEDEP_API_KEY": "${SAFEDEP_API_KEY}",
       "SAFEDEP_TENANT_ID": "${SAFEDEP_TENANT_ID}",
       "UNSILOED_API_KEY": "${UNSILOED_API_KEY}"
     }
   }
 }
}
```
- Also create a `SKILL.md` for Claude Code agent integration
- Test setup flow: clone repo -> set env vars -> server works

**Person A - Additional polish (30 min)**
- Add `hipaa.json` and `soc2.json` rule files
- Ensure Concierge stage transitions work correctly
- Add scan counter in state for billing limit enforcement

**Person B - Hosted HTTP Mode (60 min)**
- Set up server to also run in HTTP mode for Lovable/remote clients:
```python
 # For remote/hosted deployment
 http_app = app.streamable_http_app()
```
- Test connection from Lovable (Settings -> Connectors -> New MCP server)
- Ensure CORS headers work for web dashboard

**Person C - Razorpay Integration (60 min)**
- Build pricing page on Emergent.sh dashboard
- Integrate Razorpay Checkout (test mode):
```javascript
 const rzp = new Razorpay({
   key_id: "rzp_test_...",
   amount: 9900,  // INR 99 or USD 99
   name: "ComplianceShield",
   description: "Pro Plan - All Jurisdictions",
   handler: function(response) {
     // Unlock all jurisdictions
     alert("Payment successful! All jurisdictions unlocked.");
   }
 });
```
- Plans: Free (10 scans/mo, 1 jurisdiction) / Pro INR 8,299/mo / Enterprise INR 4,16,000/yr

**Person D - Demo Script + Slides (60 min)**
- Write and rehearse 3-minute demo script
- Create 2-3 backup slides (problem, architecture, pricing)
- Test full demo flow 3 times

---

### Hour 4 (3:15 - 4:00): Final Demo Rehearsal

**All Team (45 min)**

Bug fixes (15 min): Fix remaining issues from testing
Demo rehearsal (20 min): Run through 3 times, refine timing
Backup plan (10 min): If live demo breaks, have screenshots/recording ready

### Demo Script (3 minutes)

**Opening (30 sec):**
"50 million developers now use AI to write code. But here's the problem - AI doesn't know about GDPR. Or India's DPDP Act. Or HIPAA. Every vibe-coded app fails its first enterprise security review. We built ComplianceShield - the Legal Department that lives inside your IDE."

**Live Demo (2 min):**
1. Show Claude Code with ComplianceShield MCP connected (`/mcp` shows it green)
2. "Let me toggle on GDPR and India DPDP..." -> call `set_jurisdictions(["gdpr", "dpdp"])`
3. "Now watch - I'll ask Claude to build a user registration form, but through our Compliance Wrapper..." -> call `compliance_wrap("build a user registration form with email and phone")`
4. Show the wrapped prompt with injected compliance constraints
5. "But what about code that's ALREADY written?" -> paste the bad Express app -> call `scan_code`
6. Show findings: "6 violations found - PII in logs, SQL injection, no consent, no encryption..."
7. "One click to fix..." -> call `get_fixes` -> show the diff
8. "And dependencies?" -> call `scan_dependencies` with a package.json -> show SafeDep blocking a malicious package
9. "What's new in GDPR this month?" -> call `search_compliance_news(["gdpr"])` -> show latest enforcement actions from CrustData
10. "Quick question..." -> call `ask_compliance_question("What are the GDPR requirements for cookie consent?")` -> show AI-synthesized answer
11. "Generate a compliance report for your auditor..." -> call `generate_report`
12. Quick flash of web dashboard on Emergent.sh showing reports and Razorpay pricing

**Close (30 sec):**
"ComplianceShield is an MCP server. One line to install. Works in Claude Code, Cursor, Lovable, VSCode. Powered by Concierge workflow enforcement, SafeDep dependency scanning, Unsiloed AI policy parsing, CrustData for real-time regulatory intelligence, Gemini for analysis, Razorpay for billing. Built on Emergent.sh. Your AI can code - now it can also lawyer. $99 a month."

---

## Key Files to Create

| File | Owner | Purpose |
|------|-------|---------|
| `server.py` | Person A | Main MCP server with Concierge wrapper + all tools |
| `rules/gdpr.json` | Person D | GDPR compliance rule definitions |
| `rules/dpdp.json` | Person D | India DPDP Act rule definitions |
| `rules/hipaa.json` | Person D | HIPAA rule definitions |
| `rules/soc2.json` | Person D | SOC2 control definitions |
| `integrations/crustdata.py` | Person B | CrustData Web Search + Web Fetch API client |
| `integrations/compliance_search.py` | Person B | Compliance-aware search engine (jurisdiction queries + Gemini summarization) |
| `integrations/crustdata_tools.py` | Person B | 5 CrustData MCP tools (news, web, fetch, updates, Q&A) |
| `integrations/safedep.py` | Person B | SafeDep API wrapper |
| `integrations/unsiloed.py` | Person B | Unsiloed AI parser wrapper |
| `demo/bad-express-app.js` | Person D | Demo: insecure Node.js app |
| `demo/bad-package.json` | Person D | Demo: package.json with vulnerable deps |
| `.mcp.json` | Person A | Project config for easy MCP setup |
| `SKILL.md` | Person A | Claude Code skill definition |
| `.env.example` | All | Template for API keys |
| `requirements.txt` | Person A | Python dependencies |
| `README.md` | Person D | Setup instructions |

Dashboard (on Emergent.sh - Person C):
- Landing page with setup instructions
- Scan results viewer
- Report generator/exporter
- Pricing page with Razorpay checkout

---

## Verification / Demo Test Plan

1. **Install MCP in Claude Code:** `claude mcp add compliance-shield --transport stdio -- python server.py`
2. **Verify connection:** `/mcp` shows compliance-shield as connected with all tools
3. **Set jurisdictions:** Call `set_jurisdictions(["gdpr", "dpdp"])` -> confirms active
4. **Compliance Wrapper:** Call `compliance_wrap("build login form")` -> shows wrapped prompt with GDPR+DPDP rules injected
5. **Scan bad code:** Call `scan_code` with demo Express app -> returns findings JSON with 6+ violations
6. **Auto-fix:** Call `get_fixes` with findings -> returns unified diff
7. **Scan dependencies:** Call `scan_dependencies` with package.json -> SafeDep returns safe/blocked
8. **Upload policy:** Call `upload_policy` with GDPR PDF -> Unsiloed parses it
9. **Compliance news:** Call `search_compliance_news(["gdpr", "dpdp"])` -> returns latest regulatory news from CrustData
10. **Regulatory updates:** Call `get_regulatory_updates(["gdpr"], days=30)` -> returns digest of recent changes with severity ratings
11. **Compliance Q&A:** Call `ask_compliance_question("What encryption is required for HIPAA?", ["hipaa"])` -> returns AI answer
12. **Generate report:** Call `generate_report` -> returns markdown compliance report
13. **Concierge enforcement:** Try calling `generate_report` before scanning -> should be blocked (wrong stage)
14. **Web dashboard:** Open Emergent.sh dashboard -> see scan history, reports, pricing
15. **Razorpay checkout:** Click "Buy Pro" -> Razorpay test checkout opens

---

## Why This Wins the Hackathon

1. **It's LIVE, not post-hoc:** Works inside the IDE while you code, not a separate website
2. **MCP is the right protocol:** One-line install into any AI coding tool
3. **Concierge enforces compliance:** Can't skip security steps - protocol-level enforcement
4. **6 sponsor tools integrated meaningfully** (not bolted on)
5. **Real problem, real business:** B2B founders need this to close enterprise deals
6. **Demo is visceral:** Watching an MCP tool flag violations inside Claude Code in real-time is compelling
7. **Pitch line sticks:** "Your AI can code, but it can't lawyer."


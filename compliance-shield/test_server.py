"""
ComplianceShield — MCP Server Test Suite
==========================================
Programmatic tests for all 7 MCP tools.
Run this WITHOUT needing Claude Code installed.

Usage:
    python test_server.py              # run all tests
    python test_server.py smoke        # quick smoke test only
    python test_server.py <test_name>  # run one specific test

Each test calls the tool functions directly (not via MCP protocol),
which lets Person B verify logic and integrations independently of
the Concierge wrapper and MCP transport layer.

Prerequisites:
    pip install -r requirements.txt
    cp .env.example .env && fill in API keys
"""

import asyncio
import json
import os
import sys
import traceback
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Import server tools directly ──────────────────────────────────────────────
# We import the tool functions from server.py to call them in isolation.
# This bypasses MCP transport and Concierge staging so tests run fast.

# Patch: create a minimal app stub so server.py doesn't crash on import
# if concierge is not installed yet.
class _AppStub:
    """Minimal in-memory state store for testing without Concierge."""
    def __init__(self):
        self._state = {}
    def set_state(self, key, value):
        self._state[key] = value
    def get_state(self, key, default=None):
        return self._state.get(key, default)
    def run(self, **kwargs):
        pass

# ── Test utilities ────────────────────────────────────────────────────────────

PASS = "✅ PASS"
FAIL = "❌ FAIL"
SKIP = "⏭  SKIP"

results = []

def test(name: str):
    """Decorator to register and run a named test."""
    def decorator(fn):
        results.append((name, fn))
        return fn
    return decorator

async def run_tests(filter_name: str | None = None):
    passed = failed = skipped = 0
    print(f"\n{'='*60}")
    print("  ComplianceShield — Test Suite")
    print(f"{'='*60}\n")

    for name, fn in results:
        if filter_name and filter_name not in name:
            continue
        try:
            result = await fn()
            if result is True:
                print(f"  {PASS}  {name}")
                passed += 1
            elif result == "skip":
                print(f"  {SKIP}  {name}")
                skipped += 1
            else:
                print(f"  {FAIL}  {name}")
                print(f"         → {result}")
                failed += 1
        except Exception as e:
            print(f"  {FAIL}  {name}")
            print(f"         → Exception: {e}")
            if "--verbose" in sys.argv:
                traceback.print_exc()
            failed += 1

    print(f"\n{'='*60}")
    print(f"  Results: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"{'='*60}\n")
    return failed == 0


# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: load_rules helper
# ─────────────────────────────────────────────────────────────────────────────
@test("load_rules: loads gdpr.json correctly")
async def test_load_rules_gdpr():
    # Import after sys.path manipulation so it finds server.py
    sys.path.insert(0, str(Path(__file__).parent))
    from server import load_rules
    result = load_rules(["gdpr"])
    assert "GDPR-1" in result, f"Expected GDPR-1 in rules, got: {result[:200]}"
    assert "GDPR-7" in result, "Expected GDPR-7 (hardcoded secrets) in rules"
    return True

@test("load_rules: loads dpdp.json correctly")
async def test_load_rules_dpdp():
    from server import load_rules
    result = load_rules(["dpdp"])
    assert "DPDP-1" in result, f"Expected DPDP-1 in rules, got: {result[:200]}"
    return True

@test("load_rules: loads hipaa.json correctly")
async def test_load_rules_hipaa():
    from server import load_rules
    result = load_rules(["hipaa"])
    assert "HIPAA-1" in result, f"Expected HIPAA-1 in rules"
    return True

@test("load_rules: loads soc2.json correctly")
async def test_load_rules_soc2():
    from server import load_rules
    result = load_rules(["soc2"])
    assert "SOC2-CC6.1" in result, "Expected SOC2-CC6.1 in rules"
    return True

@test("load_rules: handles multiple jurisdictions")
async def test_load_rules_multi():
    from server import load_rules
    result = load_rules(["gdpr", "dpdp"])
    assert "GDPR-1" in result and "DPDP-1" in result, "Expected both GDPR and DPDP rules"
    return True

@test("load_rules: handles missing jurisdiction gracefully")
async def test_load_rules_missing():
    from server import load_rules
    result = load_rules(["nonexistent"])
    assert "WARNING" in result or "No rules" in result, f"Expected warning, got: {result}"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: set_jurisdictions
# ─────────────────────────────────────────────────────────────────────────────
@test("set_jurisdictions: accepts valid jurisdictions")
async def test_set_jurisdictions_valid():
    # We need to mock app for this test
    import server as srv
    original_app = getattr(srv, 'app', None)
    srv.app = _AppStub()

    result = await srv.set_jurisdictions(["gdpr", "dpdp"])
    stored = srv.app.get_state("jurisdictions")

    srv.app = original_app
    assert stored == ["gdpr", "dpdp"], f"Expected ['gdpr', 'dpdp'], got {stored}"
    assert "GDPR" in result and "DPDP" in result, f"Expected jurisdiction names in response"
    return True

@test("set_jurisdictions: rejects invalid jurisdiction")
async def test_set_jurisdictions_invalid():
    import server as srv
    original_app = getattr(srv, 'app', None)
    srv.app = _AppStub()

    result = await srv.set_jurisdictions(["gdpr", "ccpa"])  # ccpa is not supported
    srv.app = original_app
    assert "Invalid" in result or "invalid" in result, f"Expected rejection, got: {result}"
    return True

@test("set_jurisdictions: loads rules preview in response")
async def test_set_jurisdictions_preview():
    import server as srv
    original_app = getattr(srv, 'app', None)
    srv.app = _AppStub()

    result = await srv.set_jurisdictions(["gdpr"])
    srv.app = original_app
    assert "GDPR-1" in result, f"Expected rules preview in response, got: {result[:300]}"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: compliance_wrap
# ─────────────────────────────────────────────────────────────────────────────
@test("compliance_wrap: injects GDPR rules into prompt")
async def test_compliance_wrap_gdpr():
    import server as srv
    original_app = getattr(srv, 'app', None)
    stub = _AppStub()
    stub.set_state("jurisdictions", ["gdpr"])
    srv.app = stub

    result = await srv.compliance_wrap("build a user registration form")
    srv.app = original_app

    assert "GDPR" in result, "Expected GDPR mention in wrapped prompt"
    assert "MANDATORY" in result, "Expected MANDATORY compliance requirements"
    assert "user registration form" in result, "Expected original prompt preserved"
    return True

@test("compliance_wrap: falls back to gdpr if no jurisdictions set")
async def test_compliance_wrap_fallback():
    import server as srv
    original_app = getattr(srv, 'app', None)
    stub = _AppStub()
    # Deliberately don't set jurisdictions
    srv.app = stub

    result = await srv.compliance_wrap("build a login page")
    srv.app = original_app

    assert "GDPR" in result, "Expected fallback to GDPR"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: scan_code (requires GEMINI_API_KEY)
# ─────────────────────────────────────────────────────────────────────────────
@test("scan_code: returns JSON findings for bad code (requires GEMINI_API_KEY)")
async def test_scan_code_bad():
    if not os.getenv("GEMINI_API_KEY"):
        return "skip"

    import server as srv
    original_app = getattr(srv, 'app', None)
    stub = _AppStub()
    stub.set_state("jurisdictions", ["gdpr"])
    srv.app = stub

    bad_code = '''
const DB_PASSWORD = "admin123";
app.post("/register", (req, res) => {
    const {name, email, ssn} = req.body;
    console.log(`User: ${name}, SSN: ${ssn}`);
    db.query(`INSERT INTO users VALUES ('${name}', '${email}', '${ssn}')`);
    res.json({success: true, userData: {name, email, ssn}});
});
'''
    result = await srv.scan_code(code=bad_code, filename="test-register.js")
    srv.app = original_app

    # Should find at least 1 violation
    assert "violation" in result.lower() or "[" in result, f"Expected violations, got: {result[:300]}"
    # Should cache findings
    assert stub.get_state("last_findings") is not None, "Expected findings cached in state"
    return True

@test("scan_code: increments scan counter")
async def test_scan_code_counter():
    if not os.getenv("GEMINI_API_KEY"):
        return "skip"

    import server as srv
    original_app = getattr(srv, 'app', None)
    stub = _AppStub()
    stub.set_state("jurisdictions", ["gdpr"])
    stub.set_state("scan_count", 3)
    srv.app = stub

    await srv.scan_code(code="const x = 1;", filename="clean.js")
    srv.app = original_app

    assert stub.get_state("scan_count") == 4, f"Expected count 4, got {stub.get_state('scan_count')}"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: scan_dependencies (requires SAFEDEP_API_KEY)
# ─────────────────────────────────────────────────────────────────────────────
@test("scan_dependencies: parses package.json correctly")
async def test_scan_deps_parse():
    import server as srv
    original_app = getattr(srv, 'app', None)
    srv.app = _AppStub()

    # Test with empty dependencies — should not crash
    result = await srv.scan_dependencies('{"name": "test", "dependencies": {}}')
    srv.app = original_app

    assert "No dependencies" in result or "error" in result.lower(), \
        f"Expected empty deps message, got: {result[:200]}"
    return True

@test("scan_dependencies: rejects invalid JSON")
async def test_scan_deps_invalid_json():
    import server as srv
    original_app = getattr(srv, 'app', None)
    srv.app = _AppStub()

    result = await srv.scan_dependencies("not valid json {{")
    srv.app = original_app

    assert "Invalid" in result or "error" in result.lower(), \
        f"Expected error message, got: {result[:200]}"
    return True

@test("scan_dependencies: scans real packages via SafeDep (requires SAFEDEP_API_KEY)")
async def test_scan_deps_real():
    if not os.getenv("SAFEDEP_API_KEY"):
        return "skip"

    import server as srv
    original_app = getattr(srv, 'app', None)
    srv.app = _AppStub()

    pkg_json = json.dumps({
        "dependencies": {
            "express": "^4.18.2",
            "lodash": "^4.17.21"
        }
    })
    result = await srv.scan_dependencies(pkg_json)
    srv.app = original_app

    data = json.loads(result)
    assert "total_scanned" in data, "Expected total_scanned in result"
    assert data["total_scanned"] == 2, f"Expected 2 packages scanned, got {data['total_scanned']}"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: get_fixes (requires GEMINI_API_KEY)
# ─────────────────────────────────────────────────────────────────────────────
@test("get_fixes: uses cached findings when called with no args (requires GEMINI_API_KEY)")
async def test_get_fixes_cached():
    if not os.getenv("GEMINI_API_KEY"):
        return "skip"

    import server as srv
    original_app = getattr(srv, 'app', None)
    stub = _AppStub()
    stub.set_state("jurisdictions", ["gdpr"])
    stub.set_state("last_findings", '[{"severity":"critical","rule_id":"GDPR-1","violation":"PII in log","line":3}]')
    stub.set_state("last_scan_code", 'console.log("SSN:", ssn);')
    stub.set_state("last_scan_file", "test.js")
    srv.app = stub

    result = await srv.get_fixes()
    srv.app = original_app

    assert result and len(result) > 50, f"Expected a fix response, got: {result[:200]}"
    return True

@test("get_fixes: returns helpful message when no findings exist")
async def test_get_fixes_empty():
    import server as srv
    original_app = getattr(srv, 'app', None)
    stub = _AppStub()
    srv.app = stub

    result = await srv.get_fixes()
    srv.app = original_app

    assert "No findings" in result or "scan_code" in result, \
        f"Expected guidance message, got: {result[:200]}"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: apply_fix
# ─────────────────────────────────────────────────────────────────────────────
@test("apply_fix: writes fixed code to file and creates backup")
async def test_apply_fix_writes():
    import server as srv
    original_app = getattr(srv, 'app', None)
    srv.app = _AppStub()

    # Create a temp test file
    test_path = "/tmp/cs_test_apply_fix.js"
    with open(test_path, "w") as f:
        f.write('console.log("original code");')

    fixed = 'console.log("fixed code");  // GDPR-1: no PII logged'
    result = await srv.apply_fix(file_path=test_path, fixed_code=fixed)
    srv.app = original_app

    assert os.path.exists(test_path), "Fixed file should exist"
    assert os.path.exists(test_path + ".bak"), "Backup file should exist"

    with open(test_path) as f:
        written = f.read()
    assert "fixed code" in written, f"Expected fixed code in file, got: {written}"

    # Cleanup
    os.remove(test_path)
    os.remove(test_path + ".bak")
    return True

@test("apply_fix: handles missing file gracefully")
async def test_apply_fix_missing_file():
    import server as srv
    original_app = getattr(srv, 'app', None)
    srv.app = _AppStub()

    result = await srv.apply_fix(
        file_path="/tmp/cs_nonexistent_file_xyz.js",
        fixed_code="const x = 1;"
    )
    srv.app = original_app

    # Should not crash — should create the file since it doesn't exist
    assert "Fix applied" in result or "Error" in result, \
        f"Expected handled response, got: {result[:200]}"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: generate_report (requires GEMINI_API_KEY)
# ─────────────────────────────────────────────────────────────────────────────
@test("generate_report: produces structured markdown (requires GEMINI_API_KEY)")
async def test_generate_report():
    if not os.getenv("GEMINI_API_KEY"):
        return "skip"

    import server as srv
    original_app = getattr(srv, 'app', None)
    stub = _AppStub()
    stub.set_state("jurisdictions", ["gdpr", "dpdp"])
    stub.set_state("scan_count", 2)
    stub.set_state("last_findings", '[{"severity":"critical","rule_id":"GDPR-1","violation":"PII in log"}]')
    srv.app = stub

    result = await srv.generate_report()
    srv.app = original_app

    assert "ComplianceShield" in result, "Expected report title"
    assert "GDPR" in result, "Expected jurisdiction in report"
    # Report should be cached
    assert stub.get_state("last_report") is not None, "Expected report cached in state"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: Smoke test — runs fast with no API keys needed
# ─────────────────────────────────────────────────────────────────────────────
@test("smoke: server.py imports without errors")
async def test_import():
    try:
        import server  # noqa
        return True
    except ImportError as e:
        return f"Import failed: {e}"

@test("smoke: all rule files exist and are valid JSON")
async def test_rule_files():
    base = Path(__file__).parent / "rules"
    for jurisdiction in ["gdpr", "dpdp", "hipaa", "soc2"]:
        path = base / f"{jurisdiction}.json"
        assert path.exists(), f"Missing rule file: {path}"
        with open(path) as f:
            data = json.load(f)
        assert "rules" in data, f"No 'rules' key in {jurisdiction}.json"
        assert len(data["rules"]) > 0, f"Empty rules in {jurisdiction}.json"
    return True

@test("smoke: demo files exist")
async def test_demo_files():
    base = Path(__file__).parent / "demo"
    assert (base / "bad-express-app.js").exists(), "Missing bad-express-app.js"
    assert (base / "bad-package.json").exists(), "Missing bad-package.json"
    return True

@test("smoke: .env.example has all required keys")
async def test_env_example():
    path = Path(__file__).parent / ".env.example"
    assert path.exists(), "Missing .env.example"
    content = path.read_text()
    for key in ["GEMINI_API_KEY", "SAFEDEP_API_KEY", "SAFEDEP_TENANT_ID", "UNSILOED_API_KEY"]:
        assert key in content, f"Missing {key} in .env.example"
    return True


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    filter_arg = sys.argv[1] if len(sys.argv) > 1 else None

    if filter_arg == "smoke":
        # Quick smoke test — no API keys needed, < 5 seconds
        print("\n🚀 Running smoke tests only (no API keys required)...")
        filter_arg = "smoke"

    success = asyncio.run(run_tests(filter_arg))
    sys.exit(0 if success else 1)

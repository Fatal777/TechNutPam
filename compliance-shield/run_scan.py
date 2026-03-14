#!/usr/bin/env python3
"""
Standalone ComplianceShield repo scanner.
Runs full scan with all jurisdictions (GDPR, DPDP, HIPAA, SOC2) without MCP.
Usage: python run_scan.py [root_path]
"""
import asyncio
import json
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Must set cwd to project root so scan finds files
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

from server import (
    load_rules,
    _discover_code_files,
    _run_single_file_scan,
    CODE_EXTENSIONS,
    model,
)
from server import app  # Stateful app (Concierge or fallback)
from server import scan_dependencies, generate_report


async def run_full_scan(root_path: str = ".", max_files: int = 30) -> dict:
    """Run full compliance scan with all 4 jurisdictions."""
    jurisdictions = ["gdpr", "dpdp", "hipaa", "soc2"]
    app.set_state("jurisdictions", jurisdictions)
    app.set_state("scan_count", 0)
    rules = load_rules(jurisdictions)

    root = os.path.abspath(os.path.expanduser(root_path))
    if not os.path.isdir(root):
        return {"error": f"Path not found: {root}"}

    files = _discover_code_files(root, max_files)
    if not files:
        return {"error": f"No code files found under {root}"}

    all_findings = []
    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for i, filepath in enumerate(files):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                code = f.read()
        except Exception as e:
            all_findings.append({
                "file": os.path.relpath(filepath, root),
                "severity": "medium",
                "rule_id": "SCAN-ERR",
                "rule": "File read error",
                "violation": str(e),
                "line": 0,
            })
            by_severity["medium"] += 1
            continue

        rel_path = os.path.relpath(filepath, root)
        findings, _ = _run_single_file_scan(code, rel_path, jurisdictions, rules)
        for f in findings:
            f["file"] = rel_path
            all_findings.append(f)
            s = f.get("severity", "low").lower()
            by_severity[s] = by_severity.get(s, 0) + 1

        # Progress
        print(f"  Scanned {i+1}/{len(files)}: {rel_path}", file=sys.stderr)

    # Dependency scan
    dep_results = "No package.json found."
    for candidate in ["package.json", "frontend/package.json"]:
        pkg_path = os.path.join(root, candidate)
        if os.path.isfile(pkg_path):
            try:
                with open(pkg_path, "r") as f:
                    dep_results = await scan_dependencies(f.read())
                break
            except Exception:
                pass

    app.set_state("scan_count", 1)
    app.set_state("last_findings", json.dumps(all_findings, indent=2))
    # dep_scan_results already set by scan_dependencies

    report = await generate_report()
    return {
        "root": root,
        "files_scanned": len(files),
        "total_violations": len(all_findings),
        "by_severity": by_severity,
        "findings": all_findings,
        "report": report,
    }


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    print("ComplianceShield — Full scan (GDPR, DPDP, HIPAA, SOC2)", file=sys.stderr)
    print(f"Root: {os.path.abspath(root)}\n", file=sys.stderr)
    result = asyncio.run(run_full_scan(root))
    if "error" in result:
        print(result["error"], file=sys.stderr)
        sys.exit(1)
    json.dump(result, sys.stdout, indent=2)


if __name__ == "__main__":
    main()

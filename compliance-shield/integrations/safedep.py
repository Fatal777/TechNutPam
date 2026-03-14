"""
SafeDep Integration — ComplianceShield
=======================================
Wraps the SafeDep REST API for dependency malware and vulnerability scanning.
Used by scan_dependencies tool in server.py.

SafeDep is integrated as per the master plan architecture:
  Stage 3 (scan) → scan_dependencies → SafeDep REST API

API reference: https://docs.safedep.io
Dashboard:     https://app.safedep.io
"""

import json
import os
from typing import Any

import httpx

SAFEDEP_BASE = "https://api.safedep.io"
ANALYSIS_ENDPOINT = (
    f"{SAFEDEP_BASE}/safedep.services.malysis.v1.MalwareAnalysisService/QueryPackageAnalysis"
)

SUPPORTED_ECOSYSTEMS = {"npm", "pypi", "maven", "go", "rubygems", "nuget"}


async def scan_package(
    pkg: str,
    version: str,
    ecosystem: str = "npm",
    api_key: str | None = None,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    """
    Query SafeDep for a single package's malware analysis.

    Returns a dict with:
      - package: "pkg@version"
      - safe: bool (fail-closed: False unless explicitly confirmed)
      - blocked: bool
      - status: human-readable string
      - reason: SafeDep's reasoning (up to 300 chars)

    FAIL-CLOSED policy: if the API is unreachable or returns ambiguous data,
    the package is blocked. This is intentional — security over convenience.
    """
    _api_key = api_key or os.getenv("SAFEDEP_API_KEY", "")
    _tenant_id = tenant_id or os.getenv("SAFEDEP_TENANT_ID", "")
    clean_version = version.lstrip("^~>=<")

    if ecosystem not in SUPPORTED_ECOSYSTEMS:
        return {
            "package": f"{pkg}@{clean_version}",
            "safe": False,
            "blocked": True,
            "status": f"⚠️ Unsupported ecosystem: {ecosystem}",
            "reason": f"SafeDep supports: {sorted(SUPPORTED_ECOSYSTEMS)}",
        }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                ANALYSIS_ENDPOINT,
                headers={
                    "Authorization": _api_key,
                    "X-Tenant-ID": _tenant_id,
                    "Content-Type": "application/json",
                },
                json={
                    "ecosystem": ecosystem,
                    "package_name": pkg,
                    "version": clean_version,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        inference = data.get("report", {}).get("inference", {})
        is_malware = inference.get("isMalware")
        reasoning = inference.get("reasoning", "No details available")[:300]

        is_safe = is_malware == False  # Strict check — None or True → blocked
        return {
            "package": f"{pkg}@{clean_version}",
            "safe": is_safe,
            "blocked": not is_safe,
            "status": "✅ SAFE" if is_safe else "🚫 BLOCKED",
            "reason": reasoning,
        }

    except httpx.HTTPStatusError as e:
        return {
            "package": f"{pkg}@{clean_version}",
            "safe": False,
            "blocked": True,
            "status": "⚠️ API ERROR — BLOCKED (fail-closed)",
            "reason": f"SafeDep HTTP {e.response.status_code}: {str(e)[:200]}",
        }
    except Exception as e:
        return {
            "package": f"{pkg}@{clean_version}",
            "safe": False,
            "blocked": True,
            "status": "⚠️ NETWORK ERROR — BLOCKED (fail-closed)",
            "reason": str(e)[:200],
        }


async def scan_package_json(
    package_json_str: str,
    ecosystem: str = "npm",
    max_packages: int = 20,
) -> dict[str, Any]:
    """
    Scan all dependencies in a package.json string.

    Combines both 'dependencies' and 'devDependencies'.
    Caps at max_packages for demo speed (SafeDep has rate limits).
    """
    try:
        pkg_data = json.loads(package_json_str)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON. Provide the full contents of package.json."}

    packages = {}
    packages.update(pkg_data.get("dependencies", {}))
    packages.update(pkg_data.get("devDependencies", {}))

    if not packages:
        return {"error": "No dependencies found in package.json."}

    results = []
    for pkg, version in list(packages.items())[:max_packages]:
        result = await scan_package(pkg, version, ecosystem)
        results.append(result)

    blocked = [r for r in results if r["blocked"]]
    return {
        "verdict": "❌ FAIL" if blocked else "✅ PASS",
        "total_scanned": len(results),
        "safe": len(results) - len(blocked),
        "blocked": len(blocked),
        "results": results,
    }

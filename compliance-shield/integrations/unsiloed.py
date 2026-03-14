"""
Unsiloed AI Integration — ComplianceShield
==========================================
Parses compliance policy PDFs (GDPR, DPDP, HIPAA, SOC2) into structured
machine-readable rules using the Unsiloed AI vision API.

Used by the upload_policy tool in server.py (Stage 1: configure).

API reference: https://docs.unsiloed.ai
"""

import asyncio
import os
from pathlib import Path

import httpx

UNSILOED_BASE = "https://prod.visionapi.unsiloed.ai"
PARSE_ENDPOINT = f"{UNSILOED_BASE}/parse"
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


async def parse_policy_document(
    file_path: str,
    api_key: str | None = None,
    poll_interval: float = 2.0,
    max_wait: int = 60,
) -> dict:
    """
    Submit a compliance policy PDF to Unsiloed AI and return extracted rules.

    Process:
      1. POST the file to /parse → get job_id
      2. Poll GET /parse/{job_id} until status == "completed"
      3. Return the extracted markdown text

    Returns:
      {
        "success": bool,
        "markdown": str,          # extracted rule text
        "char_count": int,
        "job_id": str,
        "error": str | None
      }
    """
    _api_key = api_key or os.getenv("UNSILOED_API_KEY", "")
    if not _api_key:
        return {"success": False, "error": "UNSILOED_API_KEY not set in environment."}

    path = Path(file_path)
    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return {
            "success": False,
            "error": f"Unsupported file type: {path.suffix}. Supported: {SUPPORTED_EXTENSIONS}",
        }

    async with httpx.AsyncClient(timeout=120) as client:
        # Step 1: Submit for parsing
        try:
            with open(file_path, "rb") as f:
                resp = await client.post(
                    PARSE_ENDPOINT,
                    headers={"api-key": _api_key},
                    files={"file": (path.name, f, "application/pdf")},
                )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"Unsiloed AI submission failed: HTTP {e.response.status_code}",
            }
        except Exception as e:
            return {"success": False, "error": f"Submission error: {str(e)}"}

        job_id = resp.json().get("job_id")
        if not job_id:
            return {
                "success": False,
                "error": "No job_id in Unsiloed AI response. Check API key.",
            }

        # Step 2: Poll for completion
        elapsed = 0
        while elapsed < max_wait:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            try:
                result = await client.get(
                    f"{PARSE_ENDPOINT}/{job_id}",
                    headers={"api-key": _api_key},
                )
                data = result.json()
                status = data.get("status")

                if status == "completed":
                    markdown = data.get("result", {}).get("markdown", "")
                    return {
                        "success": True,
                        "markdown": markdown,
                        "char_count": len(markdown),
                        "job_id": job_id,
                        "error": None,
                    }
                elif status == "failed":
                    return {
                        "success": False,
                        "job_id": job_id,
                        "error": f"Parsing failed: {data.get('error', 'unknown')}",
                    }
                # Still processing → continue polling

            except Exception as e:
                return {"success": False, "job_id": job_id, "error": f"Poll error: {str(e)}"}

        return {
            "success": False,
            "job_id": job_id,
            "error": f"Timed out after {max_wait}s. Job may still be processing.",
        }

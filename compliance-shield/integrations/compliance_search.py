"""
Compliance-aware search layer built on top of CrustDataClient.

Builds jurisdiction-specific queries, handles geolocation mapping,
and uses Gemini to summarize raw HTML into actionable compliance guidance.
"""

import json
import os
import time
from typing import Optional

import google.generativeai as genai

from .crustdata import CrustDataClient

JURISDICTION_CONFIG = {
    "gdpr": {
        "name": "GDPR (EU General Data Protection Regulation)",
        "geolocation": "GB",
        "search_terms": [
            "GDPR",
            "EU data protection",
            "European Data Protection Board",
        ],
        "regulatory_bodies": ["edpb.europa.eu", "gdpr.eu", "ico.org.uk"],
    },
    "dpdp": {
        "name": "DPDP Act (India Digital Personal Data Protection)",
        "geolocation": "IN",
        "search_terms": [
            "DPDP Act",
            "India data protection",
            "Digital Personal Data Protection Act",
        ],
        "regulatory_bodies": ["meity.gov.in"],
    },
    "hipaa": {
        "name": "HIPAA (US Health Insurance Portability and Accountability Act)",
        "geolocation": "US",
        "search_terms": [
            "HIPAA",
            "health data privacy",
            "HHS enforcement",
            "protected health information",
        ],
        "regulatory_bodies": ["hhs.gov", "hipaajournal.com"],
    },
    "soc2": {
        "name": "SOC 2 (Service Organization Control 2)",
        "geolocation": "US",
        "search_terms": [
            "SOC 2 compliance",
            "SOC 2 audit",
            "AICPA trust services criteria",
        ],
        "regulatory_bodies": ["aicpa.org"],
    },
}


class ComplianceSearchEngine:
    """
    High-level compliance intelligence engine.

    Combines CrustData search APIs with Gemini summarization to deliver
    actionable compliance information from jurisdiction-specific queries.
    """

    def __init__(
        self,
        crustdata_client: Optional[CrustDataClient] = None,
        gemini_model: Optional[genai.GenerativeModel] = None,
    ):
        self.client = crustdata_client or CrustDataClient()

        if gemini_model:
            self.model = gemini_model
        else:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
            self.model = genai.GenerativeModel("gemini-2.0-flash")

        self._cache: dict[str, tuple[float, any]] = {}
        self._cache_ttl = 300  # 5 minutes

    def _get_cached(self, key: str):
        if key in self._cache:
            ts, value = self._cache[key]
            if time.time() - ts < self._cache_ttl:
                return value
            del self._cache[key]
        return None

    def _set_cached(self, key: str, value):
        self._cache[key] = (time.time(), value)

    def _build_jurisdiction_query(
        self, jurisdictions: list[str], topic: Optional[str] = None
    ) -> list[tuple[str, str]]:
        """
        Build (query_string, geolocation) pairs for each jurisdiction.
        Returns a list so callers can search each jurisdiction separately.
        """
        queries = []
        for j in jurisdictions:
            config = JURISDICTION_CONFIG.get(j.lower())
            if not config:
                continue
            base_term = config["search_terms"][0]
            query = f"{base_term} {topic}" if topic else base_term
            queries.append((query, config["geolocation"]))
        return queries

    async def search_compliance_news(
        self,
        jurisdictions: list[str],
        topic: Optional[str] = None,
    ) -> list[dict]:
        """
        Search for latest compliance news across given jurisdictions.

        Returns a flat list of results with jurisdiction tag added.
        """
        cache_key = f"news:{','.join(sorted(jurisdictions))}:{topic}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        all_results = []
        queries = self._build_jurisdiction_query(jurisdictions, topic)

        for query_text, geo in queries:
            news_query = f"{query_text} enforcement OR update OR regulation"
            try:
                response = await self.client.search_news(
                    query=news_query, geolocation=geo
                )
                if response.get("success") and response.get("results"):
                    for r in response["results"]:
                        r["jurisdiction"] = query_text.split()[0]
                    all_results.extend(response["results"])
            except Exception as e:
                all_results.append(
                    {"error": str(e), "jurisdiction": query_text.split()[0]}
                )

        self._set_cached(cache_key, all_results)
        return all_results

    async def search_compliance_web(
        self,
        query: str,
        jurisdictions: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Free-form web search scoped to compliance topics.

        If jurisdictions are provided, the query is augmented with
        jurisdiction-specific terms and searched with matching geolocation.
        """
        if not jurisdictions:
            response = await self.client.search_web(query=f"{query} compliance")
            return response.get("results", [])

        all_results = []
        for j in jurisdictions:
            config = JURISDICTION_CONFIG.get(j.lower())
            if not config:
                continue
            augmented = f"{config['search_terms'][0]} {query}"
            try:
                response = await self.client.search_web(
                    query=augmented, geolocation=config["geolocation"]
                )
                if response.get("success") and response.get("results"):
                    for r in response["results"]:
                        r["jurisdiction"] = j.upper()
                    all_results.extend(response["results"])
            except Exception as e:
                all_results.append({"error": str(e), "jurisdiction": j.upper()})

        return all_results

    async def fetch_and_summarize(self, urls: list[str]) -> list[dict]:
        """
        Fetch full page content from URLs and use Gemini to extract
        compliance-relevant information.
        """
        fetched = await self.client.web_fetch(urls)
        summaries = []

        for page in fetched:
            if not page.get("success"):
                summaries.append(
                    {
                        "url": page.get("url", "unknown"),
                        "error": page.get("error", "Failed to fetch"),
                    }
                )
                continue

            content = page.get("content", "")
            # Truncate very large pages to fit Gemini context
            if len(content) > 50000:
                content = content[:50000] + "\n[...truncated...]"

            prompt = f"""Extract compliance-relevant information from this webpage.
Focus on: regulatory requirements, obligations, deadlines, penalties, and implementation guidance.
Return a structured summary with sections: Key Requirements, Obligations, Penalties, Implementation Guidance.
If the page is not compliance-related, say so briefly.

Page title: {page.get('pageTitle', 'Unknown')}
URL: {page.get('url', '')}

Content:
{content}"""

            try:
                response = self.model.generate_content(prompt)
                summaries.append(
                    {
                        "url": page.get("url"),
                        "title": page.get("pageTitle"),
                        "compliance_summary": response.text,
                    }
                )
            except Exception as e:
                summaries.append(
                    {
                        "url": page.get("url"),
                        "title": page.get("pageTitle"),
                        "error": f"Gemini summarization failed: {e}",
                    }
                )

        return summaries

    async def get_regulatory_updates(
        self,
        jurisdictions: list[str],
        days: int = 30,
    ) -> dict:
        """
        Get recent regulatory changes for given jurisdictions.

        Searches news from the last N days and uses Gemini to produce
        a severity-rated digest of what's changed.
        """
        now = int(time.time())
        start_ts = now - (days * 86400)

        cache_key = f"updates:{','.join(sorted(jurisdictions))}:{days}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        all_news: list[dict] = []
        for j in jurisdictions:
            config = JURISDICTION_CONFIG.get(j.lower())
            if not config:
                continue
            query = f"{config['search_terms'][0]} new regulation OR amendment OR enforcement action OR fine OR update"
            try:
                response = await self.client.search_news(
                    query=query,
                    geolocation=config["geolocation"],
                    start_date=start_ts,
                    end_date=now,
                )
                if response.get("success") and response.get("results"):
                    for r in response["results"]:
                        r["jurisdiction"] = j.upper()
                    all_news.extend(response["results"])
            except Exception:
                pass

        if not all_news:
            result = {
                "jurisdictions": jurisdictions,
                "period_days": days,
                "updates": [],
                "digest": "No regulatory updates found for the specified period.",
            }
            self._set_cached(cache_key, result)
            return result

        news_text = "\n".join(
            f"- [{r.get('jurisdiction')}] {r.get('title', '')} — {r.get('snippet', '')}"
            for r in all_news[:20]  # cap at 20 items for Gemini context
        )

        prompt = f"""You are a compliance analyst. Analyze these recent regulatory news items and produce a digest.

For each significant update, provide:
1. Jurisdiction (GDPR/DPDP/HIPAA/SOC2)
2. What changed
3. Impact severity (critical/high/medium/low)
4. Action required for software developers

News items from the last {days} days:
{news_text}

Return as a JSON array of objects with keys: jurisdiction, change, severity, action_required.
Return ONLY the JSON array, no other text."""

        try:
            response = self.model.generate_content(prompt)
            digest_text = response.text.strip()
            # Try to parse as JSON, fall back to raw text
            if digest_text.startswith("["):
                digest = json.loads(digest_text)
            elif "```json" in digest_text:
                json_str = digest_text.split("```json")[1].split("```")[0].strip()
                digest = json.loads(json_str)
            elif "```" in digest_text:
                json_str = digest_text.split("```")[1].split("```")[0].strip()
                digest = json.loads(json_str)
            else:
                digest = digest_text
        except (json.JSONDecodeError, IndexError):
            digest = digest_text

        result = {
            "jurisdictions": jurisdictions,
            "period_days": days,
            "raw_news": all_news[:20],
            "digest": digest,
        }
        self._set_cached(cache_key, result)
        return result

    async def ask_compliance_question(
        self,
        question: str,
        jurisdictions: Optional[list[str]] = None,
    ) -> dict:
        """
        Use CrustData's AI search mode to get a synthesized answer
        to a compliance question. Falls back to web search + Gemini
        if AI mode returns no results.
        """
        if jurisdictions:
            jurisdiction_names = []
            geo = "US"
            for j in jurisdictions:
                config = JURISDICTION_CONFIG.get(j.lower())
                if config:
                    jurisdiction_names.append(config["search_terms"][0])
                    geo = config["geolocation"]
            prefix = " ".join(jurisdiction_names)
            full_question = f"{prefix} {question}"
        else:
            full_question = f"compliance regulation {question}"
            geo = "US"

        try:
            response = await self.client.search_ai(
                query=full_question, geolocation=geo
            )
            if response.get("success") and response.get("results"):
                return {
                    "question": question,
                    "jurisdictions": jurisdictions or [],
                    "source": "crustdata_ai",
                    "results": response["results"],
                }
        except Exception:
            pass

        # Fallback: web search + Gemini summarization
        try:
            web_results = await self.client.search_web(
                query=full_question, geolocation=geo
            )
            if web_results.get("success") and web_results.get("results"):
                snippets = "\n".join(
                    f"- {r.get('title', '')}: {r.get('snippet', '')}"
                    for r in web_results["results"][:10]
                )
                prompt = f"""Based on these search results, answer this compliance question concisely:

Question: {question}
Jurisdictions: {', '.join(jurisdictions or ['general'])}

Search results:
{snippets}

Provide a clear, actionable answer with specific requirements and recommendations."""

                gemini_resp = self.model.generate_content(prompt)
                return {
                    "question": question,
                    "jurisdictions": jurisdictions or [],
                    "source": "web_search_with_gemini",
                    "answer": gemini_resp.text,
                    "sources": [
                        {"title": r.get("title"), "url": r.get("url")}
                        for r in web_results["results"][:5]
                    ],
                }
        except Exception as e:
            return {
                "question": question,
                "jurisdictions": jurisdictions or [],
                "error": f"Search failed: {e}",
            }

        return {
            "question": question,
            "jurisdictions": jurisdictions or [],
            "error": "No results found from either AI or web search.",
        }

"""
CrustData compliance MCP tools.

Usage in server.py:
    from integrations import register_crustdata_tools
    register_crustdata_tools(mcp)

This registers 5 tools on the MCP server for real-time compliance intelligence.
"""

import json
from typing import Optional

from .compliance_search import ComplianceSearchEngine

_engine: Optional[ComplianceSearchEngine] = None


def _get_engine() -> ComplianceSearchEngine:
    global _engine
    if _engine is None:
        _engine = ComplianceSearchEngine()
    return _engine


def register_crustdata_tools(mcp) -> None:
    """
    Register all CrustData compliance tools on the given MCP server instance.

    Tools registered:
      1. search_compliance_news  - Latest regulatory news by jurisdiction
      2. search_compliance_web   - Free-form compliance web search
      3. fetch_regulation_content - Fetch & summarize regulatory URLs
      4. get_regulatory_updates  - Digest of recent regulatory changes
      5. ask_compliance_question - AI-powered compliance Q&A
    """

    @mcp.tool()
    async def search_compliance_news(
        jurisdictions: list[str],
        topic: str = "",
    ) -> str:
        """Search for the latest compliance and regulatory news.

        Uses CrustData's news search to find recent enforcement actions,
        regulatory updates, fines, and compliance-related news articles
        for the specified jurisdictions.

        Args:
            jurisdictions: List of jurisdiction codes to search.
                           Valid values: 'gdpr', 'dpdp', 'hipaa', 'soc2'
            topic: Optional topic to narrow the search (e.g. 'data breach',
                   'encryption requirements', 'consent management')

        Returns:
            JSON array of news results with title, url, snippet, and jurisdiction.
        """
        engine = _get_engine()
        results = await engine.search_compliance_news(
            jurisdictions=jurisdictions,
            topic=topic if topic else None,
        )
        return json.dumps(results, indent=2)

    @mcp.tool()
    async def search_compliance_web(
        query: str,
        jurisdictions: list[str] = None,
    ) -> str:
        """Search the web for compliance regulations, guidance, and best practices.

        Performs a web search scoped to compliance topics. When jurisdictions
        are provided, queries are augmented with jurisdiction-specific terms
        and geo-targeted for relevance.

        Args:
            query: The compliance topic to search for (e.g. 'cookie consent
                   implementation', 'data encryption requirements',
                   'breach notification procedure')
            jurisdictions: Optional list of jurisdiction codes to scope the search.
                           Valid values: 'gdpr', 'dpdp', 'hipaa', 'soc2'

        Returns:
            JSON array of web results with title, url, snippet, and jurisdiction.
        """
        engine = _get_engine()
        results = await engine.search_compliance_web(
            query=query,
            jurisdictions=jurisdictions,
        )
        return json.dumps(results, indent=2)

    @mcp.tool()
    async def fetch_regulation_content(urls: list[str]) -> str:
        """Fetch full content from compliance-related URLs and summarize them.

        Retrieves the HTML content of regulatory body websites, legal guidance
        documents, or compliance articles, then uses AI to extract and summarize
        the compliance-relevant information into actionable guidance.

        Args:
            urls: List of URLs to fetch and summarize (max 10).
                  Should be regulatory or compliance-related pages
                  (e.g. from gdpr.eu, hhs.gov, ico.org.uk).

        Returns:
            JSON array of summaries, each with url, title, and
            compliance_summary containing: Key Requirements, Obligations,
            Penalties, and Implementation Guidance.
        """
        engine = _get_engine()
        summaries = await engine.fetch_and_summarize(urls=urls)
        return json.dumps(summaries, indent=2)

    @mcp.tool()
    async def get_regulatory_updates(
        jurisdictions: list[str],
        days: int = 30,
    ) -> str:
        """Get a digest of recent regulatory changes and enforcement actions.

        Searches compliance news from the last N days for each jurisdiction,
        then produces a severity-rated digest of what changed and what
        developers need to do about it.

        Args:
            jurisdictions: List of jurisdiction codes to check.
                           Valid values: 'gdpr', 'dpdp', 'hipaa', 'soc2'
            days: Number of days to look back (default: 30, max recommended: 90)

        Returns:
            JSON object with 'digest' (array of updates, each with jurisdiction,
            change description, severity, and action_required) and 'raw_news'
            (the underlying news articles).
        """
        engine = _get_engine()
        result = await engine.get_regulatory_updates(
            jurisdictions=jurisdictions,
            days=days,
        )
        return json.dumps(result, indent=2, default=str)

    @mcp.tool()
    async def ask_compliance_question(
        question: str,
        jurisdictions: list[str] = None,
    ) -> str:
        """Ask a compliance question and get an AI-synthesized answer.

        Uses CrustData's AI search to get a direct answer to compliance
        questions. Falls back to web search with Gemini summarization
        if AI search is unavailable.

        Best for quick questions like:
        - "What are the GDPR requirements for cookie consent?"
        - "How long do I have to report a HIPAA breach?"
        - "What data must be stored in India under DPDP?"
        - "What are SOC 2 requirements for access logging?"

        Args:
            question: The compliance question to answer.
            jurisdictions: Optional list of jurisdiction codes for context.
                           Valid values: 'gdpr', 'dpdp', 'hipaa', 'soc2'

        Returns:
            JSON object with the answer, source (crustdata_ai or
            web_search_with_gemini), and source URLs where applicable.
        """
        engine = _get_engine()
        result = await engine.ask_compliance_question(
            question=question,
            jurisdictions=jurisdictions,
        )
        return json.dumps(result, indent=2)

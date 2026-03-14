"""
Async client for CrustData's Web Search and Web Fetch APIs.

Endpoints used:
  - POST /screener/web-search  (1 credit/query, 10 RPM)
  - POST /screener/web-fetch   (1 credit/URL, max 10 URLs)

Auth: Authorization: Token <CRUSTDATA_API_TOKEN>
"""

import asyncio
import os
import time
from typing import Optional

import httpx

CRUSTDATA_BASE_URL = "https://api.crustdata.com"
MAX_RPM = 10
MIN_REQUEST_INTERVAL = 60.0 / MAX_RPM  # 6 seconds between requests


class CrustDataClient:
    """Thin async wrapper around CrustData Web Search & Web Fetch APIs."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("CRUSTDATA_API_TOKEN", "")
        if not self.token:
            raise ValueError(
                "CRUSTDATA_API_TOKEN is required. "
                "Set it as an environment variable or pass it to CrustDataClient()."
            )
        self._headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }
        self._last_request_time: float = 0.0

    async def _throttle(self) -> None:
        """Simple throttle to stay under CrustData's 10 RPM limit."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            await asyncio.sleep(MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.monotonic()

    async def web_search(
        self,
        query: str,
        sources: Optional[list[str]] = None,
        geolocation: Optional[str] = None,
        site: Optional[str] = None,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        fetch_content: bool = False,
    ) -> dict:
        """
        Search the web via CrustData.

        Args:
            query: Search text (max 1000 chars).
            sources: Filter by source type. Valid values:
                     'web', 'news', 'ai', 'social',
                     'scholar-articles', 'scholar-articles-enriched', 'scholar-author'
            geolocation: ISO 3166-1 alpha-2 country code (e.g. 'US', 'GB', 'IN').
            site: Restrict results to a domain (e.g. 'gdpr.eu').
            start_date: Unix timestamp for date range start.
            end_date: Unix timestamp for date range end.
            fetch_content: If True, fetches full HTML for each result URL.

        Returns:
            Dict with 'success', 'results' (list of {title, url, snippet, position}),
            'metadata', and optionally 'contents' when fetch_content=True.
        """
        await self._throttle()

        url = f"{CRUSTDATA_BASE_URL}/screener/web-search"
        if fetch_content:
            url += "?fetch_content=true"

        payload: dict = {"query": query}
        if sources:
            payload["sources"] = sources
        if geolocation:
            payload["geolocation"] = geolocation
        if site:
            payload["site"] = site
        if start_date is not None:
            payload["startDate"] = start_date
        if end_date is not None:
            payload["endDate"] = end_date

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=self._headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def web_fetch(self, urls: list[str]) -> list[dict]:
        """
        Fetch full HTML content from up to 10 URLs.

        Args:
            urls: List of URLs (max 10) with http:// or https:// prefix.

        Returns:
            List of dicts, each with 'success', 'url', 'timestamp',
            'pageTitle', and 'content' (HTML string).
        """
        if not urls:
            return []

        await self._throttle()

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{CRUSTDATA_BASE_URL}/screener/web-fetch",
                headers=self._headers,
                json={"urls": urls[:10]},
            )
            resp.raise_for_status()
            return resp.json()

    async def search_news(
        self,
        query: str,
        geolocation: Optional[str] = None,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
    ) -> dict:
        """Convenience: search only news sources."""
        return await self.web_search(
            query=query,
            sources=["news"],
            geolocation=geolocation,
            start_date=start_date,
            end_date=end_date,
        )

    async def search_web(
        self,
        query: str,
        geolocation: Optional[str] = None,
        site: Optional[str] = None,
    ) -> dict:
        """Convenience: search only web sources."""
        return await self.web_search(
            query=query,
            sources=["web"],
            geolocation=geolocation,
            site=site,
        )

    async def search_ai(self, query: str, geolocation: str = "US") -> dict:
        """Convenience: use Google AI Mode for synthesized answers."""
        return await self.web_search(
            query=query,
            sources=["ai"],
            geolocation=geolocation,
        )

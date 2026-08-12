"""Evidence retrieval — pluggable providers with DuckDuckGo fallback."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

import httpx

from app.core.config import get_settings
from app.core.enums import EvidenceType
from app.evidence.reliability import extract_domain, score_domain

logger = logging.getLogger(__name__)


@dataclass
class RawEvidence:
    url: str | None
    title: str | None
    domain: str | None
    snippet: str | None
    relevance_score: float
    evidence_type: EvidenceType = EvidenceType.NEUTRAL
    source_reliability_score: float = 50.0


class EvidenceRetriever:
    """
    Collect external evidence for a claim.

    Priority:
    1) configured provider (serper/tavily) when keys exist
    2) DuckDuckGo free search fallback (no key)
    """

    async def retrieve(self, claim: str) -> list[RawEvidence]:
        settings = get_settings()
        max_results = settings.evidence_max_results

        try:
            if settings.evidence_provider == "serper" and settings.serper_api_key:
                return await self._serper(claim, max_results)
            if settings.evidence_provider == "tavily" and settings.tavily_api_key:
                return await self._tavily(claim, max_results)
            return await self._duckduckgo(claim, max_results)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Evidence retrieval failed: %s", exc)
            return []

    async def _serper(self, claim: str, max_results: int) -> list[RawEvidence]:
        settings = get_settings()
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": settings.serper_api_key},
                json={"q": claim, "num": max_results},
            )
            response.raise_for_status()
            data = response.json()
        organic = data.get("organic", [])[:max_results]
        return [self._from_hit(item.get("link"), item.get("title"), item.get("snippet"), i)
                for i, item in enumerate(organic)]

    async def _tavily(self, claim: str, max_results: int) -> list[RawEvidence]:
        settings = get_settings()
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.tavily_api_key,
                    "query": claim,
                    "max_results": max_results,
                },
            )
            response.raise_for_status()
            data = response.json()
        results = data.get("results", [])[:max_results]
        return [
            self._from_hit(item.get("url"), item.get("title"), item.get("content"), i)
            for i, item in enumerate(results)
        ]

    async def _duckduckgo(self, claim: str, max_results: int) -> list[RawEvidence]:
        """Key-free fallback using duckduckgo-search package."""
        queries = [
            claim,
            f"{claim} news official source",
            f"\"{claim[:120]}\"",
        ]

        def _search() -> list[dict]:
            from ddgs import DDGS

            collected: list[dict] = []
            seen_urls: set[str] = set()
            with DDGS() as ddgs:
                for query in queries:
                    try:
                        for item in ddgs.text(query, max_results=max_results):
                            url = item.get("href") or item.get("link") or item.get("url")
                            if not url or url in seen_urls:
                                continue
                            # Drop low-value dictionary / translator noise.
                            domain = (extract_domain(url) or "").lower()
                            if any(
                                bad in domain
                                for bad in (
                                    "dictionary.",
                                    "cambridge.org",
                                    "merriam-webster",
                                    "translate.google",
                                    "wikipedia.org/wiki/Help:",
                                )
                            ):
                                continue
                            seen_urls.add(url)
                            collected.append(item)
                            if len(collected) >= max_results:
                                return collected
                    except Exception:  # noqa: BLE001
                        continue
            return collected

        try:
            hits = await asyncio.to_thread(_search)
        except Exception:
            def _search_legacy() -> list[dict]:
                from duckduckgo_search import DDGS

                with DDGS() as ddgs:
                    return list(ddgs.text(claim, max_results=max_results))

            hits = await asyncio.to_thread(_search_legacy)

        evidence: list[RawEvidence] = []
        for i, item in enumerate(hits[:max_results]):
            evidence.append(
                self._from_hit(
                    item.get("href") or item.get("link") or item.get("url"),
                    item.get("title"),
                    item.get("body") or item.get("snippet"),
                    i,
                )
            )
        return evidence

    def _from_hit(
        self,
        url: str | None,
        title: str | None,
        snippet: str | None,
        rank: int,
    ) -> RawEvidence:
        domain = extract_domain(url)
        # Simple rank-based relevance prior (re-ranked later).
        relevance = max(0.35, 1.0 - (rank * 0.08))
        return RawEvidence(
            url=url,
            title=title,
            domain=domain,
            snippet=snippet,
            relevance_score=relevance * 100.0,
            evidence_type=EvidenceType.NEUTRAL,
            source_reliability_score=score_domain(domain),
        )


def unique_domains(items: list[RawEvidence]) -> int:
    return len({e.domain for e in items if e.domain})

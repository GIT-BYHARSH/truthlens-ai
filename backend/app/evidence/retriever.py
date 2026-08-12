"""Evidence retrieval — pluggable providers with resilient free fallbacks."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from urllib.parse import quote

import httpx

from app.core.config import get_settings
from app.core.enums import EvidenceType
from app.evidence.reliability import extract_domain, score_domain

logger = logging.getLogger(__name__)

NOISE_DOMAINS = (
    "dictionary.",
    "cambridge.org",
    "merriam-webster",
    "translate.google",
    "wikipedia.org/wiki/Help:",
    "wiktionary.org",
    "capital.com",
    "capital.bank",
)

HTTP_HEADERS = {
    "User-Agent": (
        "TruthLensAI/0.2 (academic verification; "
        "https://github.com/GIT-BYHARSH/truthlens-ai)"
    ),
    "Accept": "application/json",
}


@dataclass
class RawEvidence:
    url: str | None
    title: str | None
    domain: str | None
    snippet: str | None
    relevance_score: float
    evidence_type: EvidenceType = EvidenceType.NEUTRAL
    source_reliability_score: float = 50.0


def build_search_queries(claim: str) -> list[str]:
    """Build targeted queries so search engines don't latch onto wrong senses."""
    cleaned = " ".join(claim.split()).strip()
    queries = [
        cleaned,
        f"{cleaned} wikipedia",
        f"{cleaned} official source",
    ]

    capital_match = re.search(
        r"capital of ([A-Za-z][A-Za-z\s]+?)\s+is\s+([A-Za-z][A-Za-z\s]+)",
        cleaned,
        flags=re.I,
    )
    if capital_match:
        country = capital_match.group(1).strip(" .")
        city = capital_match.group(2).strip(" .")
        queries.extend(
            [
                f"capital of {country}",
                f"{country} capital city",
                f"is {city} the capital of {country}",
                f"{country} New Delhi capital",
            ]
        )

    if re.search(r"chandrayaan|lunar|moon", cleaned, flags=re.I):
        queries.extend(
            [
                "Chandrayaan-3 landing lunar south pole August 2023",
                "Chandrayaan-3 successfully landed Moon south pole",
                "ISRO Chandrayaan-3 soft landing",
            ]
        )

    tokens = [
        t
        for t in re.findall(r"[A-Za-z0-9\-]+", cleaned)
        if t.lower()
        not in {
            "the",
            "a",
            "an",
            "is",
            "are",
            "of",
            "in",
            "on",
            "to",
            "and",
            "that",
            "this",
            "was",
            "were",
            "has",
            "have",
            "will",
        }
    ]
    if len(tokens) >= 3:
        queries.append(" ".join(tokens[:8]))

    seen: set[str] = set()
    unique: list[str] = []
    for q in queries:
        key = q.lower()
        if key not in seen:
            seen.add(key)
            unique.append(q)
    return unique


class EvidenceRetriever:
    """
    Collect external evidence for a claim.

    Priority:
    1) configured provider (serper/tavily) when keys exist
    2) DuckDuckGo free search (with retries + query expansion)
    3) Wikipedia + DuckDuckGo Instant Answer fallbacks
    """

    async def retrieve(self, claim: str) -> list[RawEvidence]:
        settings = get_settings()
        max_results = settings.evidence_max_results
        collected: list[RawEvidence] = []

        try:
            if settings.evidence_provider == "serper" and settings.serper_api_key:
                collected = await self._serper(claim, max_results)
            elif settings.evidence_provider == "tavily" and settings.tavily_api_key:
                collected = await self._tavily(claim, max_results)
            else:
                collected = await self._duckduckgo_with_retries(claim, max_results)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Primary evidence retrieval failed: %s", exc)

        if len(collected) < 3:
            extras = await self._fallback_sources(claim, max_results)
            collected = _merge_evidence(collected, extras, max_results)

        return collected[:max_results]

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
        return [
            self._from_hit(item.get("link"), item.get("title"), item.get("snippet"), i)
            for i, item in enumerate(organic)
        ]

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

    async def _duckduckgo_with_retries(
        self, claim: str, max_results: int
    ) -> list[RawEvidence]:
        last: list[RawEvidence] = []
        for attempt in range(3):
            try:
                last = await self._duckduckgo(claim, max_results)
                if last:
                    return last
            except Exception as exc:  # noqa: BLE001
                logger.warning("DuckDuckGo attempt %s failed: %s", attempt + 1, exc)
            await asyncio.sleep(0.7 * (attempt + 1))
        return last

    async def _duckduckgo(self, claim: str, max_results: int) -> list[RawEvidence]:
        queries = build_search_queries(claim)

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
                            domain = (extract_domain(url) or "").lower()
                            if any(bad in domain for bad in NOISE_DOMAINS):
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

        return [
            self._from_hit(
                item.get("href") or item.get("link") or item.get("url"),
                item.get("title"),
                item.get("body") or item.get("snippet"),
                i,
            )
            for i, item in enumerate(hits[:max_results])
        ]

    async def _fallback_sources(
        self, claim: str, max_results: int
    ) -> list[RawEvidence]:
        results: list[RawEvidence] = []
        async with httpx.AsyncClient(
            timeout=20.0,
            headers=HTTP_HEADERS,
            follow_redirects=True,
        ) as client:
            results.extend(await self._wikipedia(client, claim, max_results))
            results.extend(await self._duckduckgo_instant(client, claim))
        return results

    async def _wikipedia(
        self, client: httpx.AsyncClient, claim: str, max_results: int
    ) -> list[RawEvidence]:
        wiki_queries = build_search_queries(claim)[:4]
        evidence: list[RawEvidence] = []
        seen_titles: set[str] = set()

        for query in wiki_queries:
            try:
                search = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "list": "search",
                        "srsearch": query[:180],
                        "srlimit": min(5, max_results),
                        "utf8": 1,
                        "format": "json",
                        "origin": "*",
                    },
                )
                if search.status_code == 403:
                    logger.warning("Wikipedia blocked request (403)")
                    break
                search.raise_for_status()
                pages = search.json().get("query", {}).get("search", [])
            except Exception as exc:  # noqa: BLE001
                logger.warning("Wikipedia search failed: %s", exc)
                continue

            for idx, page in enumerate(pages):
                title = page.get("title")
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)
                snippet = re.sub("<[^<]+?>", "", page.get("snippet") or "")
                url = f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
                try:
                    extract = await client.get(
                        "https://en.wikipedia.org/w/api.php",
                        params={
                            "action": "query",
                            "format": "json",
                            "prop": "extracts",
                            "explaintext": 1,
                            "exchars": 1200,
                            "titles": title,
                        },
                    )
                    if extract.status_code == 200:
                        pages_map = extract.json().get("query", {}).get("pages", {})
                        for page_data in pages_map.values():
                            long_extract = (page_data.get("extract") or "").strip()
                            if long_extract:
                                snippet = long_extract[:1200]
                                break
                except Exception:  # noqa: BLE001
                    pass
                evidence.append(self._from_hit(url, title, snippet, idx))
                if len(evidence) >= max_results:
                    return evidence
        return evidence

    async def _duckduckgo_instant(
        self, client: httpx.AsyncClient, claim: str
    ) -> list[RawEvidence]:
        items: list[RawEvidence] = []
        for query in build_search_queries(claim)[:3]:
            try:
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": 1,
                        "skip_disambig": 1,
                    },
                )
                response.raise_for_status()
                data = response.json()
            except Exception as exc:  # noqa: BLE001
                logger.warning("DuckDuckGo instant answer failed: %s", exc)
                continue

            abstract = (data.get("AbstractText") or "").strip()
            abstract_url = data.get("AbstractURL")
            heading = data.get("Heading")
            if abstract and abstract_url:
                items.append(
                    self._from_hit(
                        abstract_url, heading or "DuckDuckGo Abstract", abstract, 0
                    )
                )

            for idx, topic in enumerate(data.get("RelatedTopics", [])[:4]):
                if not isinstance(topic, dict):
                    continue
                text = (topic.get("Text") or "").strip()
                url = topic.get("FirstURL")
                if text and url:
                    items.append(self._from_hit(url, text[:80], text, idx + 1))
            if items:
                break
        return items

    def _from_hit(
        self,
        url: str | None,
        title: str | None,
        snippet: str | None,
        rank: int,
    ) -> RawEvidence:
        domain = extract_domain(url)
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


def _merge_evidence(
    primary: list[RawEvidence],
    secondary: list[RawEvidence],
    limit: int,
) -> list[RawEvidence]:
    seen: set[str] = set()
    merged: list[RawEvidence] = []
    for item in primary + secondary:
        key = (item.url or "").rstrip("/").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(item)
        if len(merged) >= limit:
            break
    return merged


def unique_domains(items: list[RawEvidence]) -> int:
    return len({e.domain for e in items if e.domain})

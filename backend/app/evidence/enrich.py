"""Evidence enrichment and claim-aware ranking helpers."""

from __future__ import annotations

import logging
import re
from urllib.parse import quote, unquote

import httpx

from app.core.enums import EvidenceType
from app.evidence.reliability import extract_domain, score_domain
from app.evidence.retriever import RawEvidence

logger = logging.getLogger(__name__)

HTTP_HEADERS = {
    "User-Agent": (
        "TruthLensAI/0.2 (academic verification; "
        "https://github.com/GIT-BYHARSH/truthlens-ai)"
    ),
    "Accept": "application/json,text/plain,*/*",
}

OUTCOME_TERMS = {
    "landed",
    "landing",
    "successfully",
    "success",
    "touched",
    "soft",
    "august",
    "2023",
    "south",
    "pole",
}


def claim_tokens(claim: str) -> set[str]:
    stop = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "of",
        "in",
        "on",
        "to",
        "and",
        "that",
        "this",
        "near",
        "with",
        "for",
        "by",
    }
    return {
        t.lower()
        for t in re.findall(r"[A-Za-z0-9\-]+", claim)
        if len(t) > 2 and t.lower() not in stop
    }


def keyword_overlap_score(claim: str, item: RawEvidence) -> float:
    tokens = claim_tokens(claim)
    if not tokens:
        return 0.0
    blob = f"{item.title or ''} {item.snippet or ''} {item.domain or ''}".lower()
    hits = sum(1 for t in tokens if t in blob)
    base = 100.0 * (hits / max(1, len(tokens)))
    outcome_hits = sum(1 for t in OUTCOME_TERMS if t in blob)
    return min(100.0, base + outcome_hits * 4.0)


def rank_by_claim_relevance(claim: str, items: list[RawEvidence]) -> list[RawEvidence]:
    """Boost items whose title/snippet overlap the claim tokens and outcome facts."""
    scored: list[tuple[float, RawEvidence]] = []
    for item in items:
        overlap = keyword_overlap_score(claim, item)
        base = item.relevance_score or 0.0
        item.relevance_score = max(base, overlap)
        score = (
            overlap * 0.55
            + (item.source_reliability_score or 0.0) * 0.30
            + base * 0.15
        )
        scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored]


async def enrich_evidence_snippets(
    items: list[RawEvidence],
    claim: str,
    limit: int = 6,
) -> list[RawEvidence]:
    """
    Expand Wikipedia snippets with long plain-text extracts so Gemini sees
    outcome/date/location sentences (REST summaries are often too short).
    """
    async with httpx.AsyncClient(
        timeout=15.0, headers=HTTP_HEADERS, follow_redirects=True
    ) as client:
        wiki_extra = await _wikipedia_claim_extract(client, claim)
        if wiki_extra:
            items = _merge_unique(items, [wiki_extra])

        for item in items[:limit]:
            domain = (item.domain or extract_domain(item.url) or "").lower()
            current = (item.snippet or "").strip()
            try:
                if "wikipedia.org" in domain and item.url:
                    title = _wikipedia_title_from_url(item.url)
                    if title:
                        extract = await _wikipedia_long_extract(client, title)
                        if extract and _is_better_snippet(claim, current, extract):
                            item.snippet = extract[:1200]
                elif item.url and len(current) < 160:
                    # Only keep HTML peek if it improves claim/outcome overlap.
                    page = await client.get(item.url)
                    if page.status_code == 200 and "text/html" in page.headers.get(
                        "content-type", ""
                    ):
                        text = _visible_text(page.text)[:1200]
                        if _is_better_snippet(claim, current, text):
                            item.snippet = text
            except Exception as exc:  # noqa: BLE001
                logger.debug("Snippet enrichment failed for %s: %s", item.url, exc)

    return rank_by_claim_relevance(claim, items)


def _is_better_snippet(claim: str, old: str, new: str) -> bool:
    if not new or len(new.strip()) < 40:
        return False
    old_item = RawEvidence(
        url=None,
        title=None,
        domain=None,
        snippet=old,
        relevance_score=0.0,
    )
    new_item = RawEvidence(
        url=None,
        title=None,
        domain=None,
        snippet=new,
        relevance_score=0.0,
    )
    old_score = keyword_overlap_score(claim, old_item)
    new_score = keyword_overlap_score(claim, new_item)
    # Prefer longer factual extracts when overlap is at least as good.
    return new_score > old_score or (
        new_score >= old_score and len(new) > len(old) + 80
    )


async def _wikipedia_claim_extract(
    client: httpx.AsyncClient, claim: str
) -> RawEvidence | None:
    """Pull the best Wikipedia page extract for the claim entity."""
    queries = [claim]
    if re.search(r"chandrayaan", claim, flags=re.I):
        queries = ["Chandrayaan-3", claim]
    try:
        for query in queries:
            search = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query[:180],
                    "srlimit": 3,
                    "utf8": 1,
                    "format": "json",
                },
            )
            if search.status_code != 200:
                continue
            pages = search.json().get("query", {}).get("search", [])
            for page in pages:
                title = page.get("title")
                if not title:
                    continue
                extract = await _wikipedia_long_extract(client, title)
                if not extract:
                    continue
                url = f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
                domain = "en.wikipedia.org"
                return RawEvidence(
                    url=url,
                    title=title,
                    domain=domain,
                    snippet=extract[:1200],
                    relevance_score=95.0,
                    evidence_type=EvidenceType.NEUTRAL,
                    source_reliability_score=score_domain(domain),
                )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Wikipedia claim extract failed: %s", exc)
    return None


async def _wikipedia_long_extract(
    client: httpx.AsyncClient, title: str
) -> str | None:
    response = await client.get(
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
    if response.status_code != 200:
        return None
    pages = response.json().get("query", {}).get("pages", {})
    for page in pages.values():
        extract = (page.get("extract") or "").strip()
        if extract:
            return extract
    return None


def _merge_unique(
    items: list[RawEvidence], extras: list[RawEvidence]
) -> list[RawEvidence]:
    seen = {(e.url or "").lower() for e in items if e.url}
    merged = list(items)
    for extra in extras:
        key = (extra.url or "").lower()
        if key and key in seen:
            # Replace existing wiki snippet with longer extract when better.
            for item in merged:
                if (item.url or "").lower() == key and len(extra.snippet or "") > len(
                    item.snippet or ""
                ):
                    item.snippet = extra.snippet
            continue
        if key:
            seen.add(key)
        merged.insert(0, extra)
    return merged


def _wikipedia_title_from_url(url: str) -> str | None:
    marker = "/wiki/"
    if marker not in url:
        return None
    title = url.split(marker, 1)[1]
    title = title.split("#", 1)[0].split("?", 1)[0]
    return unquote(title).replace("_", " ")


def _visible_text(html: str) -> str:
    cleaned = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    cleaned = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", cleaned)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()

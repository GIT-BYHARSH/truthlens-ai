"""Transparent source reliability heuristics (not LLM opinions)."""

from urllib.parse import urlparse


OFFICIAL_SUFFIXES = (
    ".gov",
    ".gov.in",
    ".nic.in",
    ".edu",
    ".ac.in",
    ".who.int",
    ".un.org",
    ".europa.eu",
)

REPUTABLE_NEWS = {
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "bbc.co.uk",
    "npr.org",
    "thehindu.com",
    "indianexpress.com",
    "nytimes.com",
    "theguardian.com",
    "nature.com",
    "science.org",
    "who.int",
}

AGGREGATORS = {
    "wikipedia.org",
    "medium.com",
    "blogspot.com",
    "wordpress.com",
    "substack.com",
}

LOW_TRUST = {
    "bit.ly",
    "t.co",
    "tinyurl.com",
}


def extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        host = urlparse(url).netloc.lower()
    except Exception:  # noqa: BLE001
        return None
    if host.startswith("www."):
        host = host[4:]
    return host or None


def score_domain(domain: str | None) -> float:
    """Return 0-100 reliability prior for a domain."""
    if not domain:
        return 35.0

    if any(domain.endswith(suffix) or domain == suffix.lstrip(".") for suffix in OFFICIAL_SUFFIXES):
        return 92.0
    if domain in REPUTABLE_NEWS or any(domain.endswith("." + d) for d in REPUTABLE_NEWS):
        return 82.0
    if domain in AGGREGATORS or any(domain.endswith("." + d) for d in AGGREGATORS):
        return 58.0
    if domain in LOW_TRUST:
        return 20.0
    if domain.endswith(".org"):
        return 68.0
    if domain.endswith(".com") or domain.endswith(".in"):
        return 55.0
    return 45.0

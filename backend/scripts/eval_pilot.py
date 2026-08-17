"""
Pilot evaluation: Gemini-only baseline vs TruthLens (evidence + structured Gemini + scores).

Usage (from backend/):
  .\\.venv\\Scripts\\python -m scripts.eval_pilot

Outputs:
  ../datasets/pilot/results_pilot.json
  Console accuracy / insufficient-rate summary for Sem-7 paper Table.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

# Ensure backend root is on path when run as module.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT.parent / ".env")
load_dotenv(ROOT / ".env")

from app.ai.gemini import GeminiClient
from app.core.config import get_settings
from app.evidence.enrich import enrich_evidence_snippets, rank_by_claim_relevance
from app.evidence.retriever import EvidenceRetriever
from app.scoring.confidence import compute_confidence
from app.scoring.credibility import compute_credibility
from app.services.signals import (
    apply_gemini_labels,
    build_confidence_inputs,
    build_credibility_inputs,
)

CLAIMS_PATH = ROOT.parent / "datasets" / "pilot" / "claims.json"
OUT_PATH = ROOT.parent / "datasets" / "pilot" / "results_pilot.json"

LABEL_MAP = {
    "SUPPORTED": "SUPPORTED",
    "REFUTED": "REFUTED",
    "PARTIALLY_SUPPORTED": "SUPPORTED",  # soft map for pilot accuracy
    "INSUFFICIENT_EVIDENCE": "NEI",
    "UNVERIFIED": "NEI",
    "NEI": "NEI",
}


def normalize_gold(label: str) -> str:
    return LABEL_MAP.get(label.upper(), label.upper())


def normalize_pred(label: str | None) -> str:
    if not label:
        return "NEI"
    return LABEL_MAP.get(label.upper(), "NEI")


async def gemini_only_baseline(client: GeminiClient, claim: str) -> dict:
    """Faculty 'Fake/Real' style baseline: claim only, no evidence retrieval."""
    started = time.perf_counter()
    assert client._client is not None
    prompt = (
        "You are a Fake/Real style claim classifier.\n"
        "Given ONLY the claim (no external evidence), return JSON with keys:\n"
        'verdict (SUPPORTED|REFUTED|NEI), model_confidence (0..1), reason (short).\n'
        "Use your parametric knowledge. Do not say NEI unless truly unknown.\n"
        f"CLAIM: {claim}"
    )
    from app.ai.gemini import _parse_json_payload
    from google.genai import types
    from app.core.config import get_settings

    settings = get_settings()
    model = settings.gemini_model or "gemini-3.5-flash"

    def _raw() -> str:
        response = client._client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini baseline returned empty response")
        return text

    raw = await asyncio.to_thread(_raw)
    try:
        data = _parse_json_payload(raw)
    except Exception:
        # Salvage verdict token if JSON is slightly malformed.
        up = raw.upper()
        verdict = "NEI"
        if "REFUTED" in up:
            verdict = "REFUTED"
        elif "SUPPORTED" in up:
            verdict = "SUPPORTED"
        data = {"verdict": verdict, "model_confidence": 0.5, "reason": raw[:200]}
    verdict = str(data.get("verdict", "NEI")).upper()
    if verdict in {"INSUFFICIENT_EVIDENCE", "UNVERIFIED"}:
        verdict = "NEI"
    return {
        "system": "gemini_only",
        "verdict": verdict,
        "model_confidence": float(data.get("model_confidence") or 0),
        "credibility": None,
        "confidence": None,
        "risk": None,
        "evidence_count": 0,
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "reason": data.get("reason"),
    }


async def truthlens_system(
    client: GeminiClient,
    retriever: EvidenceRetriever,
    claim: str,
    enrich: bool = True,
) -> dict:
    started = time.perf_counter()
    evidence = await retriever.retrieve(claim)
    if evidence:
        evidence = rank_by_claim_relevance(claim, evidence)
        if enrich:
            evidence = await enrich_evidence_snippets(evidence, claim=claim, limit=6)

    payload = [
        {
            "url": e.url,
            "title": e.title,
            "domain": e.domain,
            "snippet": (e.snippet or "")[:900],
            "source_reliability_score": e.source_reliability_score,
        }
        for e in evidence
    ]
    gemini = await client.analyze_claim_with_evidence(claim, payload)
    evidence = apply_gemini_labels(evidence, gemini)
    cred_in = build_credibility_inputs(evidence, gemini)
    conf_in = build_confidence_inputs(evidence, gemini)
    credibility, _ = compute_credibility(cred_in)
    confidence, _ = compute_confidence(conf_in)

    return {
        "system": "truthlens" if enrich else "truthlens_no_enrich",
        "verdict": gemini.verdict,
        "model_confidence": gemini.model_confidence,
        "credibility": round(credibility, 2),
        "confidence": round(confidence, 2),
        "risk": None,
        "evidence_count": len(evidence),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "reason": gemini.reasoning_summary,
    }


def summarize(rows: list[dict]) -> dict:
    by_system: dict[str, list[dict]] = {}
    for row in rows:
        by_system.setdefault(row["system"], []).append(row)

    summary = {}
    for system, items in by_system.items():
        correct = 0
        nei = 0
        for item in items:
            pred = normalize_pred(item["pred_verdict"])
            gold = normalize_gold(item["gold_label"])
            # Map NEI gold rarely; treat NEI pred specially
            if pred == "NEI":
                nei += 1
            if pred == gold or (
                gold == "REFUTED" and pred == "REFUTED"
            ) or (gold == "SUPPORTED" and pred == "SUPPORTED"):
                if pred == gold:
                    correct += 1
        n = len(items)
        summary[system] = {
            "n": n,
            "accuracy": round(correct / n, 3) if n else 0.0,
            "insufficient_or_nei_rate": round(nei / n, 3) if n else 0.0,
            "avg_latency_ms": int(sum(i["latency_ms"] for i in items) / n) if n else 0,
        }
    return summary


async def main() -> None:
    claims = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    client = GeminiClient()
    if not client.configured:
        raise SystemExit("GEMINI_API_KEY missing in .env")
    retriever = EvidenceRetriever()

    rows: list[dict] = []
    for item in claims:
        claim = item["claim"]
        gold = item["gold_label"]
        print(f"\n=== {item['id']}: {claim[:70]}...")

        try:
            base = await gemini_only_baseline(client, claim)
        except Exception as exc:  # noqa: BLE001
            print(f"  gemini_only FAIL: {exc}")
            base = {
                "system": "gemini_only",
                "verdict": "NEI",
                "model_confidence": 0,
                "credibility": None,
                "confidence": None,
                "risk": None,
                "evidence_count": 0,
                "latency_ms": 0,
                "reason": str(exc),
            }
        print(f"  gemini_only -> {base['verdict']}")
        rows.append(
            {
                "id": item["id"],
                "claim": claim,
                "gold_label": gold,
                "system": "gemini_only",
                "pred_verdict": base["verdict"],
                **{k: v for k, v in base.items() if k not in {"system", "verdict"}},
            }
        )

        try:
            full = await truthlens_system(client, retriever, claim, enrich=True)
        except Exception as exc:  # noqa: BLE001
            print(f"  truthlens FAIL: {exc}")
            full = {
                "system": "truthlens",
                "verdict": "INSUFFICIENT_EVIDENCE",
                "model_confidence": 0,
                "credibility": None,
                "confidence": None,
                "risk": None,
                "evidence_count": 0,
                "latency_ms": 0,
                "reason": str(exc),
            }
        print(
            f"  truthlens   -> {full['verdict']} "
            f"(cred={full['credibility']}, conf={full['confidence']}, ev={full['evidence_count']})"
        )
        rows.append(
            {
                "id": item["id"],
                "claim": claim,
                "gold_label": gold,
                "system": "truthlens",
                "pred_verdict": full["verdict"],
                **{k: v for k, v in full.items() if k not in {"system", "verdict"}},
            }
        )

    summary = summarize(rows)
    out = {"summary": summary, "rows": rows}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n===== PILOT SUMMARY =====")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())

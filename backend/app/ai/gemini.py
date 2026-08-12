"""Gemini structured-output client with schema validation and retries."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.schemas.gemini import GeminiVerificationResult

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """
You are a verification reasoning component inside TruthLens AI.
You do NOT decide final credibility, confidence, risk, or user actions.
Those are computed by backend engines.

Given a claim and retrieved evidence snippets, return ONLY valid JSON matching the schema.
Rules:
- Use ONLY the provided evidence. Never invent URLs.
- If evidence clearly supports the claim -> SUPPORTED
- If evidence clearly contradicts the claim -> REFUTED
- If mixed -> PARTIALLY_SUPPORTED
- If evidence is empty/too weak -> INSUFFICIENT_EVIDENCE
- Be conservative, but do not refuse to refute an obviously contradicted claim when evidence is present.
- Keep reasoning_summary short and auditable. No hidden chain-of-thought.
""".strip()


class GeminiClient:
    """Structured-output client. Never treat free text as ground truth."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: genai.Client | None = None
        if self.configured:
            self._client = genai.Client(api_key=self.settings.gemini_api_key)

    @property
    def configured(self) -> bool:
        return bool(self.settings.gemini_api_key)

    async def analyze_claim_with_evidence(
        self,
        claim_text: str,
        evidence: list[dict[str, Any]],
    ) -> GeminiVerificationResult:
        if not self.configured or self._client is None:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        payload = {
            "task": "structured_claim_verification",
            "claim_text": claim_text,
            "evidence_count": len(evidence),
            "evidence": evidence,
            "allowed_verdicts": [
                "SUPPORTED",
                "REFUTED",
                "PARTIALLY_SUPPORTED",
                "UNVERIFIED",
                "INSUFFICIENT_EVIDENCE",
            ],
            "output_schema": {
                "claim_normalized": "string",
                "claim_category": "general|health|finance|civic|tech|science|other",
                "verdict": "one of allowed_verdicts",
                "model_confidence": "float 0..1",
                "claim_summary": "string",
                "reasoning_summary": "short auditable summary, no hidden chain-of-thought",
                "supporting_points": ["string"],
                "contradicting_points": ["string"],
                "uncertainties": ["string"],
                "evidence_labels": [
                    {
                        "url": "string|null",
                        "title": "string|null",
                        "label": "support|contradict|neutral",
                        "relevance": "float 0..1",
                        "rationale": "string",
                    }
                ],
                "category_sensitivity": "float 0..100",
            },
        }

        prompt = (
            "Analyze the claim using ONLY the provided evidence list.\n"
            "If evidence_count is 0, return INSUFFICIENT_EVIDENCE.\n"
            f"INPUT_JSON:\n{json.dumps(payload, ensure_ascii=True)}"
        )

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                raw_text = await asyncio.wait_for(
                    asyncio.to_thread(self._generate_once, prompt),
                    timeout=max(45, self.settings.gemini_timeout_seconds),
                )
                data = _parse_json_payload(raw_text)
                return GeminiVerificationResult.model_validate(data)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("Gemini attempt %s failed: %s", attempt + 1, exc)
                await asyncio.sleep(0.8 * (attempt + 1))

        raise RuntimeError(f"Gemini request failed after retries: {last_error}")

    def _generate_once(self, prompt: str) -> str:
        assert self._client is not None
        models_to_try = [
            self.settings.gemini_model,
            "gemini-3.5-flash",
            "gemini-3.6-flash",
            "gemini-flash-latest",
            "gemini-3-flash-preview",
        ]
        seen: set[str] = set()
        candidates: list[str] = []
        for name in models_to_try:
            if name and name not in seen:
                seen.add(name)
                candidates.append(name)

        last_error: Exception | None = None
        for model_name in candidates:
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.1,
                        response_mime_type="application/json",
                    ),
                )
                text = (response.text or "").strip()
                if not text:
                    raise RuntimeError("Gemini returned empty response")
                if model_name != self.settings.gemini_model:
                    logger.warning("Fell back to Gemini model %s", model_name)
                return text
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("Gemini model %s failed: %s", model_name, exc)
                continue
        raise RuntimeError(f"All Gemini models failed: {last_error}")


def _parse_json_payload(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, flags=re.S | re.I)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        # Attempt to salvage the first JSON object if extra text exists.
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(text[start : end + 1])
        else:
            raise RuntimeError("Gemini returned non-JSON output") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Gemini JSON root must be an object")
    return data

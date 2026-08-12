"""Gemini structured-output client with schema validation."""

from __future__ import annotations

import asyncio
import json
import logging
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
Be conservative: if evidence is weak/missing, use INSUFFICIENT_EVIDENCE or UNVERIFIED.
Never invent URLs or fabricate evidence that was not provided.
Do not claim absolute truth. Use evidence-based language.
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
            f"INPUT_JSON:\n{json.dumps(payload, ensure_ascii=True)}"
        )

        def _call() -> str:
            assert self._client is not None
            models_to_try = [
                self.settings.gemini_model,
                "gemini-3.5-flash",
                "gemini-3.6-flash",
                "gemini-flash-latest",
                "gemini-3-flash-preview",
                "gemini-2.5-flash",
            ]
            # Preserve order, drop duplicates
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
                            temperature=0.2,
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
            raise RuntimeError(f"Gemini request failed: {last_error}")

        try:
            raw_text = await asyncio.wait_for(
                asyncio.to_thread(_call),
                timeout=self.settings.gemini_timeout_seconds,
            )
        except TimeoutError as exc:
            raise RuntimeError("Gemini request timed out") from exc
        except Exception as exc:  # noqa: BLE001
            logger.exception("Gemini call failed")
            raise RuntimeError(f"Gemini request failed: {exc}") from exc

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Gemini returned non-JSON output") from exc

        try:
            return GeminiVerificationResult.model_validate(data)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Gemini JSON failed schema validation: {exc}") from exc

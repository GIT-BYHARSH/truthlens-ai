"""Verification pipeline orchestration."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.ai.gemini import GeminiClient
from app.core.enums import (
    EvidenceType,
    InputType,
    PipelineStatus,
    SystemEventType,
    Verdict,
)
from app.evidence.ranker import rank_evidence
from app.evidence.retriever import EvidenceRetriever, RawEvidence
from app.models.evidence import EvidenceItem
from app.models.ocr import OcrArtifact
from app.models.verification import Verification
from app.ocr.service import OcrService
from app.recommendations.engine import recommend_action
from app.risk.engine import RiskInputs, compute_risk
from app.schemas.common import ExplanationOut
from app.scoring.confidence import compute_confidence
from app.scoring.credibility import compute_credibility
from app.services.events import log_event
from app.services.signals import (
    apply_gemini_labels,
    build_confidence_inputs,
    build_credibility_inputs,
)

@dataclass
class PipelineResult:
    status: PipelineStatus
    verification_id: uuid.UUID | None = None
    verdict: Verdict | None = None
    claim: str | None = None
    message: str = ""
    errors: list[str] = field(default_factory=list)


class VerificationPipeline:
    """
    Ordered stages (do not collapse into a single Gemini call):

    validate → preprocess → claim normalize → evidence
    → multimodal verify → contradiction/support → explain → score
    → confidence → risk → recommend → persist
    """

    def __init__(self) -> None:
        self.gemini = GeminiClient()
        self.retriever = EvidenceRetriever()
        self.ocr = OcrService(languages=["en"], gpu=False)

    async def run_text(
        self,
        db: AsyncSession,
        text: str,
        session_id: str | None = None,
    ) -> PipelineResult:
        started = time.perf_counter()
        cleaned = " ".join((text or "").split()).strip()
        if len(cleaned) < 8:
            return PipelineResult(
                status=PipelineStatus.FAILED,
                message="Input text is too short.",
                errors=["validation_fail"],
            )

        verification = Verification(
            id=uuid.uuid4(),
            session_id=session_id,
            input_type=InputType.TEXT.value,
            original_input_ref=cleaned[:500],
            extracted_text=cleaned,
            pipeline_status=PipelineStatus.PROCESSING.value,
        )
        db.add(verification)
        await db.flush()

        errors: list[str] = []
        evidence: list[RawEvidence] = []

        try:
            evidence = await self.retriever.retrieve(cleaned)
            if not evidence:
                await log_event(
                    db,
                    SystemEventType.EVIDENCE_FAIL.value,
                    "Evidence retrieval returned no results",
                    verification.id,
                )
                errors.append("evidence_empty")
        except Exception as exc:  # noqa: BLE001
            await log_event(
                db,
                SystemEventType.EVIDENCE_FAIL.value,
                str(exc),
                verification.id,
            )
            errors.append("evidence_fail")

        evidence_payload = [
            {
                "url": e.url,
                "title": e.title,
                "domain": e.domain,
                "snippet": e.snippet,
                "source_reliability_score": e.source_reliability_score,
            }
            for e in evidence
        ]

        try:
            if not self.gemini.configured:
                raise RuntimeError("GEMINI_API_KEY missing")
            gemini = await self.gemini.analyze_claim_with_evidence(
                cleaned, evidence_payload
            )
        except Exception as exc:  # noqa: BLE001
            await log_event(
                db,
                SystemEventType.GEMINI_FAIL.value,
                str(exc),
                verification.id,
            )
            # Conservative fallback when model fails but we still want a report.
            from app.schemas.gemini import GeminiVerificationResult

            gemini = GeminiVerificationResult(
                claim_normalized=cleaned[:500],
                claim_category="general",
                verdict=Verdict.INSUFFICIENT_EVIDENCE,
                model_confidence=0.35,
                claim_summary=cleaned[:280],
                reasoning_summary=(
                    "Model reasoning unavailable or invalid. "
                    "System defaulted to insufficient evidence."
                ),
                supporting_points=[],
                contradicting_points=[],
                uncertainties=["Gemini analysis failed or returned invalid JSON."],
                evidence_labels=[],
                category_sensitivity=40.0,
            )
            errors.append("gemini_fail")

        evidence = apply_gemini_labels(evidence, gemini)
        evidence = rank_evidence(evidence)

        cred_inputs = build_credibility_inputs(evidence, gemini)
        conf_inputs = build_confidence_inputs(evidence, gemini)
        credibility, cred_rationale = compute_credibility(cred_inputs)
        confidence, conf_rationale = compute_confidence(conf_inputs)

        # If claim is refuted, credibility should reflect poor support for the claim.
        if gemini.verdict == Verdict.REFUTED:
            credibility = min(credibility, 35.0)
            cred_rationale += " Adjusted downward because verdict is REFUTED."

        avg_source = (
            sum(e.source_reliability_score for e in evidence) / len(evidence)
            if evidence
            else 25.0
        )
        contradiction_intensity = min(
            100.0,
            len([e for e in evidence if e.evidence_type == EvidenceType.CONTRADICT])
            * 22.0,
        )
        risk_score, risk_level, risk_rationale = compute_risk(
            RiskInputs(
                credibility_score=credibility,
                confidence_score=confidence,
                contradiction_intensity=contradiction_intensity,
                source_reliability=avg_source,
                category_sensitivity=gemini.category_sensitivity,
                verdict=gemini.verdict,
            )
        )
        recommendation = recommend_action(gemini.verdict, risk_level, confidence)

        explanation = ExplanationOut(
            claim_summary=gemini.claim_summary or gemini.claim_normalized,
            verdict_rationale=gemini.reasoning_summary,
            key_evidence=[
                (e.title or e.domain or e.url or "source")
                for e in evidence[:5]
            ],
            supporting_points=gemini.supporting_points,
            contradicting_points=gemini.contradicting_points,
            source_reasoning=(
                f"Average source reliability prior: {avg_source:.1f}/100 "
                f"across {len(evidence)} evidence items "
                f"({len({e.domain for e in evidence if e.domain})} domains)."
            ),
            uncertainties=gemini.uncertainties,
            credibility_rationale=cred_rationale,
            confidence_rationale=conf_rationale + " " + risk_rationale,
            recommended_action=recommendation.text,
        )

        verification.claim_normalized = gemini.claim_normalized
        verification.claim_category = gemini.claim_category
        verification.verdict = gemini.verdict.value
        verification.credibility_score = round(credibility, 2)
        verification.confidence_score = round(confidence, 2)
        verification.risk_level = risk_level.value
        verification.risk_score = round(risk_score, 2)
        verification.recommendation_code = recommendation.code
        verification.recommendation_text = recommendation.text
        verification.explanation_json = explanation.model_dump()
        verification.pipeline_status = PipelineStatus.COMPLETED.value
        verification.error_codes = errors or None
        verification.processing_ms = int((time.perf_counter() - started) * 1000)

        for idx, item in enumerate(evidence, start=1):
            db.add(
                EvidenceItem(
                    verification_id=verification.id,
                    url=item.url,
                    title=item.title,
                    domain=item.domain,
                    evidence_type=item.evidence_type.value,
                    relevance_score=item.relevance_score,
                    snippet=item.snippet,
                    source_reliability_score=item.source_reliability_score,
                    rank_position=idx,
                )
            )

        await db.commit()

        return PipelineResult(
            status=PipelineStatus.COMPLETED,
            verification_id=verification.id,
            verdict=gemini.verdict,
            claim=gemini.claim_normalized,
            message="Verification completed.",
            errors=errors,
        )

    async def run_image(
        self,
        db: AsyncSession,
        image_path: str,
        session_id: str | None = None,
    ) -> PipelineResult:
        """
        Image → EasyOCR text extraction → shared verification pipeline.
        OCR extracts text only; it does not prove authenticity.
        """
        try:
            ocr = await self.ocr.extract_text(image_path)
        except Exception as exc:  # noqa: BLE001
            await log_event(db, SystemEventType.OCR_FAIL.value, str(exc))
            await db.commit()
            return PipelineResult(
                status=PipelineStatus.FAILED,
                message=f"OCR failed: {exc}",
                errors=["ocr_fail"],
            )

        if len(ocr.text.strip()) < 8:
            await log_event(
                db,
                SystemEventType.OCR_FAIL.value,
                "OCR returned insufficient text for claim verification",
            )
            await db.commit()
            return PipelineResult(
                status=PipelineStatus.FAILED,
                message=(
                    "Could not extract enough text from the image. "
                    "Try a clearer screenshot with readable claim text."
                ),
                errors=["ocr_empty"],
            )

        claim_text = (
            "Claim text extracted from uploaded image via OCR "
            "(OCR does not authenticate the image):\n"
            f"{ocr.text.strip()}"
        )
        result = await self.run_text(db, claim_text, session_id=session_id)
        if result.verification_id:
            row = await db.get(Verification, result.verification_id)
            if row:
                row.input_type = InputType.IMAGE.value
                row.original_input_ref = image_path
                row.extracted_text = ocr.text.strip()
                db.add(
                    OcrArtifact(
                        verification_id=row.id,
                        image_path=image_path,
                        image_hash=ocr.image_hash,
                        ocr_text=ocr.text,
                        ocr_confidence=ocr.confidence,
                        engine_meta=ocr.engine_meta,
                    )
                )
                await db.commit()
        return result

    async def run_url(
        self,
        db: AsyncSession,
        url: str,
        session_id: str | None = None,
    ) -> PipelineResult:
        import httpx

        cleaned = (url or "").strip()
        if not cleaned.startswith(("http://", "https://")):
            return PipelineResult(
                status=PipelineStatus.FAILED,
                message="URL must start with http:// or https://",
                errors=["validation_fail"],
            )

        extracted = cleaned
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(
                    cleaned,
                    headers={"User-Agent": "TruthLensAI/0.1 (academic-verification)"},
                )
                response.raise_for_status()
                html = response.text
            title = _extract_title(html)
            text_bits = _extract_visible_text(html)
            extracted = f"URL: {cleaned}\nTitle: {title}\nContent: {text_bits[:3500]}"
        except Exception as exc:  # noqa: BLE001
            await log_event(db, SystemEventType.URL_FETCH_FAIL.value, str(exc))
            # Still verify using the URL string as claim context.
            extracted = f"URL submitted for verification: {cleaned}"

        result = await self.run_text(db, extracted, session_id=session_id)
        if result.verification_id:
            row = await db.get(Verification, result.verification_id)
            if row:
                row.input_type = InputType.URL.value
                row.original_input_ref = cleaned
                await db.commit()
        return result

    async def get_report(
        self, db: AsyncSession, verification_id: uuid.UUID
    ) -> Verification | None:
        result = await db.execute(
            select(Verification)
            .where(Verification.id == verification_id)
            .options(selectinload(Verification.evidence_items))
        )
        return result.scalar_one_or_none()


def _extract_title(html: str) -> str:
    import re

    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()[:300]


def _extract_visible_text(html: str) -> str:
    import re

    cleaned = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    cleaned = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", cleaned)
    cleaned = re.sub(r"(?is)<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def supported_input_types() -> list[InputType]:
    return [InputType.TEXT, InputType.IMAGE, InputType.URL]

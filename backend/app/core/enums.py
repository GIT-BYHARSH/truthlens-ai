"""Shared enums and constants."""

from enum import StrEnum


class InputType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    URL = "url"
    DOCUMENT = "document"  # extensible; not MVP


class Verdict(StrEnum):
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNVERIFIED = "UNVERIFIED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvidenceType(StrEnum):
    SUPPORT = "support"
    CONTRADICT = "contradict"
    NEUTRAL = "neutral"


class PipelineStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SystemEventType(StrEnum):
    OCR_FAIL = "ocr_fail"
    GEMINI_FAIL = "gemini_fail"
    EVIDENCE_FAIL = "evidence_fail"
    VALIDATION_FAIL = "validation_fail"
    URL_FETCH_FAIL = "url_fetch_fail"
    PIPELINE_FAIL = "pipeline_fail"
    INFO = "info"

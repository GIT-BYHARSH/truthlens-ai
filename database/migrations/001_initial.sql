-- TruthLens AI initial schema (PostgreSQL)
-- Prefer app startup create_all / Alembic; this file documents the canonical DDL.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(64),
    input_type VARCHAR(32) NOT NULL,
    original_input_ref TEXT,
    extracted_text TEXT,
    claim_normalized TEXT,
    claim_category VARCHAR(64),
    verdict VARCHAR(64),
    credibility_score DOUBLE PRECISION,
    confidence_score DOUBLE PRECISION,
    risk_level VARCHAR(32),
    risk_score DOUBLE PRECISION,
    recommendation_code VARCHAR(64),
    recommendation_text TEXT,
    explanation_json JSONB,
    pipeline_status VARCHAR(32) NOT NULL DEFAULT 'pending',
    error_codes JSONB,
    processing_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_verifications_session_id ON verifications (session_id);
CREATE INDEX IF NOT EXISTS ix_verifications_input_type ON verifications (input_type);
CREATE INDEX IF NOT EXISTS ix_verifications_verdict ON verifications (verdict);
CREATE INDEX IF NOT EXISTS ix_verifications_risk_level ON verifications (risk_level);
CREATE INDEX IF NOT EXISTS ix_verifications_pipeline_status ON verifications (pipeline_status);

CREATE TABLE IF NOT EXISTS evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id UUID NOT NULL REFERENCES verifications (id) ON DELETE CASCADE,
    url TEXT,
    title TEXT,
    domain VARCHAR(255),
    published_at TIMESTAMPTZ,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    evidence_type VARCHAR(32) NOT NULL,
    relevance_score DOUBLE PRECISION,
    snippet TEXT,
    source_reliability_score DOUBLE PRECISION,
    rank_position INTEGER
);

CREATE INDEX IF NOT EXISTS ix_evidence_verification_id ON evidence_items (verification_id);
CREATE INDEX IF NOT EXISTS ix_evidence_domain ON evidence_items (domain);
CREATE INDEX IF NOT EXISTS ix_evidence_type ON evidence_items (evidence_type);

CREATE TABLE IF NOT EXISTS ocr_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id UUID NOT NULL REFERENCES verifications (id) ON DELETE CASCADE,
    image_path TEXT,
    image_hash TEXT,
    ocr_text TEXT,
    ocr_confidence DOUBLE PRECISION,
    engine_meta JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ocr_verification_id ON ocr_artifacts (verification_id);

CREATE TABLE IF NOT EXISTS system_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(64) NOT NULL,
    verification_id UUID REFERENCES verifications (id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_events_type ON system_events (event_type);
CREATE INDEX IF NOT EXISTS ix_events_verification_id ON system_events (verification_id);

"""Helpers for storing uploaded verification images."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import get_settings

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
}


async def save_upload_image(file: UploadFile) -> Path:
    settings = get_settings()
    content_type = (file.content_type or "").lower()
    suffix = ALLOWED_IMAGE_TYPES.get(content_type)
    if suffix is None:
        # Fallback to filename extension when browser omits content-type.
        name = (file.filename or "").lower()
        for ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp"):
            if name.endswith(ext):
                suffix = ".jpg" if ext == ".jpeg" else ext
                break
    if suffix is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Use JPG, PNG, WEBP, or BMP.",
        )

    raw = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if not raw:
        raise HTTPException(status_code=400, detail="Empty image upload.")
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Image exceeds {settings.max_upload_mb} MB limit.",
        )

    upload_root = Path(settings.upload_dir)
    if not upload_root.is_absolute():
        # Prefer project-root uploads/ when running from backend/
        candidate = Path.cwd().parent / settings.upload_dir
        upload_root = candidate if candidate.exists() else Path.cwd() / settings.upload_dir
    upload_root.mkdir(parents=True, exist_ok=True)

    dest = upload_root / f"{uuid.uuid4().hex}{suffix}"
    dest.write_bytes(raw)
    return dest

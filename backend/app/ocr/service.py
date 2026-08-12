"""EasyOCR service — extracts text only; does not prove image authenticity."""

from __future__ import annotations

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class OcrResult:
    text: str
    confidence: float | None
    engine_meta: dict
    image_hash: str


class OcrService:
    """
    Lazy-loaded EasyOCR reader (CPU by default).
    First call may download model weights and take longer.
    """

    def __init__(self, languages: list[str] | None = None, gpu: bool = False) -> None:
        self.languages = languages or ["en"]
        self.gpu = gpu

    async def extract_text(self, image_path: str) -> OcrResult:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image_hash = _file_sha256(path)

        def _run() -> tuple[str, float | None, dict]:
            reader = _get_reader(tuple(self.languages), self.gpu)
            # detail=1 returns (bbox, text, conf)
            raw = reader.readtext(str(path), detail=1, paragraph=False)
            texts: list[str] = []
            confs: list[float] = []
            for item in raw:
                if len(item) < 3:
                    continue
                text = str(item[1]).strip()
                conf = float(item[2])
                if text:
                    texts.append(text)
                    confs.append(conf)
            joined = " ".join(texts).strip()
            avg_conf = (sum(confs) / len(confs)) if confs else None
            meta = {
                "engine": "easyocr",
                "languages": list(self.languages),
                "gpu": self.gpu,
                "line_count": len(texts),
                "note": "OCR extracts embedded text; it does not authenticate the image.",
            }
            return joined, avg_conf, meta

        try:
            text, confidence, meta = await asyncio.to_thread(_run)
        except Exception as exc:  # noqa: BLE001
            logger.exception("EasyOCR failed")
            raise RuntimeError(f"OCR failed: {exc}") from exc

        return OcrResult(
            text=text,
            confidence=confidence,
            engine_meta=meta,
            image_hash=image_hash,
        )


@lru_cache(maxsize=2)
def _get_reader(languages: tuple[str, ...], gpu: bool):
    import easyocr

    logger.info("Initializing EasyOCR reader languages=%s gpu=%s", languages, gpu)
    # verbose=False avoids Unicode progress-bar crashes on Windows cp1252 consoles.
    return easyocr.Reader(list(languages), gpu=gpu, verbose=False)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

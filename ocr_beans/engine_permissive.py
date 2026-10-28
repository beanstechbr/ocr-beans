"""
ocr_beans/engine_permissive.py
------------------------------
Motor OCR 100% permissivo (sem PyMuPDF/AGPL).

Dependências diretas (todas permissivas):
    - pypdfium2  (Apache/BSD)  -> render + texto nativo
    - pypdf      (BSD)         -> fallback de texto nativo
    - pytesseract(Apache)      -> OCR primário
    - Pillow     (HPND)        -> manipulação de imagens
    - rapidocr_onnxruntime (Apache/ONNX) -> OCR de contingência (CPU)

Python 3.11+

Gerado por megacoder (kimi-k2.7-code) e corrigido/validado por execução.
"""

from __future__ import annotations

import atexit
import io
from pathlib import Path
from typing import Any

import pypdfium2 as pdfium
from pypdf import PdfReader

try:
    import pytesseract
    _TESSERACT_AVAILABLE = True
except Exception:  # pragma: no cover
    pytesseract = None  # type: ignore
    _TESSERACT_AVAILABLE = False

try:
    from rapidocr_onnxruntime import RapidOCR
    _RAPIDOCR_AVAILABLE = True
except Exception:  # pragma: no cover
    RapidOCR = None  # type: ignore
    _RAPIDOCR_AVAILABLE = False

_LEGAL_WORDS = frozenset({
    "artigo", "contrato", "processo", "lei", "decreto", "sentença", "sentenca",
    "acordo", "parte", "reclamante", "requerente", "autor", "réu", "reu",
    "testemunha", "documento", "assinatura", "notificação", "notificacao",
    "ofício", "oficio", "despacho", "decisão", "decisao", "julgamento",
    "tribunal", "juiz", "advogado", "procurador", "trabalhista", "cível",
    "civel", "criminal", "federal", "estadual", "municipal", "constituição",
    "constituicao", "regulamento", "normativo", "portaria", "resolução",
    "resolucao", "vara", "comarca", "autos", "recurso", "agravo", "liminar",
})

_RAPIDOCR_ENGINE: Any | None = None


def _normalize_text(text: str | None) -> str:
    if not text:
        return ""
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def _get_rapidocr_engine() -> Any:
    global _RAPIDOCR_ENGINE
    if _RAPIDOCR_ENGINE is None and _RAPIDOCR_AVAILABLE:
        _RAPIDOCR_ENGINE = RapidOCR()
    return _RAPIDOCR_ENGINE


def _ocr_rapidocr_pil(img) -> str:
    if not _RAPIDOCR_AVAILABLE:
        return ""
    try:
        engine = _get_rapidocr_engine()
        import numpy as np
        result, _ = engine(np.array(img.convert("RGB")))
        if not result:
            return ""
        return "\n".join(str(item[1]) for item in result if item[1])
    except Exception:  # pragma: no cover
        return ""


def texto_legivel(text: str) -> bool:
    """Heurística: decide se o texto nativo já é legível (sem OCR)."""
    if not isinstance(text, str):
        return False
    text = _normalize_text(text)
    if len(text) < 10:
        return False
    alpha = sum(1 for c in text if c.isalpha())
    ls = sum(1 for c in text if c.isalpha() or c.isspace())
    if alpha < 10 or ls / len(text) < 0.55 or alpha / len(text) < 0.35:
        return False
    lower = text.lower()
    tem_legal = any(p in lower for p in _LEGAL_WORDS)
    return tem_legal or alpha / len(text) >= 0.50


def ocr_pagina_pil(img, lang: str = "por", psm: int = 6) -> str:
    """OCR numa PIL Image: Tesseract primeiro, RapidOCR como contingência."""
    if img is None:
        return ""
    if _TESSERACT_AVAILABLE:
        try:
            raw = pytesseract.image_to_string(img, lang=lang, config=f"--psm {psm}")
            return _normalize_text(raw)
        except Exception:  # pragma: no cover
            pass
    return _ocr_rapidocr_pil(img)


def render_pagina_pil(pdfium_page, dpi: int = 300):
    """Renderiza página pypdfium2 para PIL Image no DPI desejado."""
    bitmap = pdfium_page.render(scale=dpi / 72.0)
    return bitmap.to_pil()


def extrair_texto_nativo(page) -> str:
    """Texto nativo via pypdfium2; sem fallback aqui (ver processar_pdf)."""
    try:
        return _normalize_text(page.get_textpage().get_text_range())
    except Exception:  # pragma: no cover
        return ""


def _native_text_pypdf(reader, idx: int) -> str:
    if reader is None:
        return ""
    try:
        return _normalize_text(reader.pages[idx].extract_text() or "")
    except Exception:  # pragma: no cover
        return ""


def processar_pdf(
    pdf_path: str | Path,
    dpi: int = 300,
    lang: str = "por",
    pages: list[int] | None = None,
) -> dict:
    """
    Processa um PDF página a página com roteamento:
      texto nativo legível -> source "native"; senão -> source "ocr".
    pages: lista 1-based; None = todas.
    """
    pdf_path = Path(pdf_path)
    doc = pdfium.PdfDocument(str(pdf_path))
    try:
        reader = None
        try:
            reader = PdfReader(str(pdf_path))
        except Exception:  # pragma: no cover
            pass

        total_pages = len(doc)
        page_indices = range(total_pages) if pages is None else [
            p - 1 for p in pages if 1 <= p <= total_pages
        ]

        result_pages = []
        ocr_count = 0
        text_count = 0

        for idx in page_indices:
            page = doc[idx]
            native = extrair_texto_nativo(page)
            if not native and reader is not None:
                native = _native_text_pypdf(reader, idx)

            if native and texto_legivel(native):
                content, source = native, "native"
                text_count += 1
            else:
                img = render_pagina_pil(page, dpi=dpi)
                content = ocr_pagina_pil(img, lang=lang)
                source = "ocr"
                ocr_count += 1

            result_pages.append({"number": idx + 1, "source": source, "content": content})

        return {
            "path": str(pdf_path),
            "total_pages": total_pages,
            "ocr_pages": ocr_count,
            "text_pages": text_count,
            "pages": result_pages,
        }
    finally:
        doc.close()


def check_legibility(pdf_path: str | Path) -> dict:
    """Diagnóstico: o PDF tem texto nativo legível (sem rodar OCR)?"""
    pdf_path = Path(pdf_path)
    doc = pdfium.PdfDocument(str(pdf_path))
    try:
        reader = None
        try:
            reader = PdfReader(str(pdf_path))
        except Exception:  # pragma: no cover
            pass

        total_pages = len(doc)
        sample_parts: list[str] = []
        legible = False
        for idx in range(min(total_pages, 5)):
            text = extrair_texto_nativo(doc[idx])
            if not text and reader is not None:
                text = _native_text_pypdf(reader, idx)
            sample_parts.append(text)
            if texto_legivel(text):
                legible = True
                break

        sample_text = "\n".join(sample_parts).strip()[:2000]
        reason = (
            "Texto nativo legível detectado no PDF."
            if legible
            else "Nenhum texto nativo legível detectado; provável necessidade de OCR."
        )
        return {
            "legible": legible,
            "total_pages": total_pages,
            "sample_text": sample_text,
            "reason": reason,
        }
    finally:
        doc.close()


def health() -> dict:
    """Estado e licença de cada engine (todos permissivos, sem AGPL)."""
    info: dict[str, Any] = {}
    info["pypdfium2"] = {"available": True, "license": "BSD-3-Clause / Apache-2.0"}
    try:
        import pypdf
        info["pypdf"] = {"available": True, "license": "BSD-3-Clause",
                         "version": getattr(pypdf, "__version__", "unknown")}
    except Exception as exc:
        info["pypdf"] = {"available": False, "license": "BSD-3-Clause", "error": str(exc)}
    try:
        if _TESSERACT_AVAILABLE:
            info["tesseract"] = {"available": True, "license": "Apache-2.0",
                                 "version": str(pytesseract.get_tesseract_version())}
        else:
            raise RuntimeError("pytesseract não instalado")
    except Exception as exc:
        info["tesseract"] = {"available": False, "license": "Apache-2.0", "error": str(exc)}
    info["rapidocr_onnxruntime"] = (
        {"available": True, "license": "Apache-2.0 / ONNX"}
        if _RAPIDOCR_AVAILABLE
        else {"available": False, "license": "Apache-2.0 / ONNX", "error": "não instalado"}
    )
    return info


def _cleanup() -> None:
    global _RAPIDOCR_ENGINE
    _RAPIDOCR_ENGINE = None


atexit.register(_cleanup)

__all__ = [
    "texto_legivel", "ocr_pagina_pil", "render_pagina_pil", "extrair_texto_nativo",
    "processar_pdf", "check_legibility", "health",
]

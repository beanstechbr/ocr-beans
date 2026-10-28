"""
ocr_code.py
Módulo conector unificado de OCR para LLMs (GPT/Claude/MCP).
Roda 100% em CPU, sem dependência de GPU.

Gerado por megacoder (kimi-k2.7-code) e validado por execução.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Union

import pytesseract
from PIL import Image

# PyMuPDF
import pymupdf as fitz  # noqa

# ------------------------------------------------------------------------------
# Constantes / configuração
# ------------------------------------------------------------------------------
_TESSERACT_CONF_THRESHOLD = 0.70  # 70%
_NATIVE_LEGAL_WORDS = {
    "processo", "autor", "reu", "réu", "julgamento", "tribunal", "justiça",
    "justica", "direito", "lei", "sentença", "sentenca", "honorarios",
    "honorários", "advogado", "advogada", "parte", "requerente", "requerido",
    "execucao", "execução", "ação", "acao", "demanda", "juiz", "juiza",
    "vara", "comarca", "autos", "embargos", "apelacao", "apelação", "agravo",
    "recurso", "despacho", "decisao", "decisão", "liminar", "mandado",
    "seguranca", "segurança",
}

# Lazy-loaded RapidOCR
_RAPIDOCR_ENGINE: Any = None
_RAPIDOCR_CHECKED: bool = False


# ------------------------------------------------------------------------------
# Dataclasses
# ------------------------------------------------------------------------------
@dataclass
class PageResult:
    page_number: int
    engine: str
    text: str
    confidence: float
    latency_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OCRResult:
    total_pages: int
    engines_used: List[str]
    full_text: str
    pages: List[PageResult]
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ------------------------------------------------------------------------------
# Heurísticas e utilitários
# ------------------------------------------------------------------------------
def _texto_legivel(text: str) -> bool:
    """
    Heurística para decidir se o texto nativo extraído do PDF é legível.
    Combina proporção de letras/espaços e presença de vocabulário jurídico
    comum em português.
    """
    if not text:
        return False

    text = text.strip()
    if len(text) < 10:
        return False

    letras_espacos = sum(1 for c in text if c.isalpha() or c.isspace())
    proporcao = letras_espacos / len(text)

    palavras = set(re.findall(r"\w+", text.lower()))
    tem_legal = bool(palavras & _NATIVE_LEGAL_WORDS)

    if proporcao >= 0.80 and len(text) > 100:
        return True

    return proporcao >= 0.65 and tem_legal


def _parse_page_selection(
    total_pages: int,
    pages: Optional[Union[int, str, List[int]]],
) -> List[int]:
    """
    Converte especificação de páginas (1-based) em índices 0-based.
    Aceita: None, int, list[int], str tipo '1-3,5,7'.
    """
    if pages is None:
        return list(range(total_pages))

    if isinstance(pages, int):
        pages = [pages]

    indices: set[int] = set()
    if isinstance(pages, str):
        for parte in pages.split(","):
            parte = parte.strip()
            if not parte:
                continue
            if "-" in parte:
                inicio, fim = parte.split("-", 1)
                inicio = int(inicio.strip())
                fim = int(fim.strip())
                indices.update(range(inicio - 1, fim))
            else:
                indices.add(int(parte) - 1)
    else:
        # list[int] já vem 1-based
        for p in pages:
            try:
                indices.add(int(p) - 1)
            except Exception:
                continue

    return sorted(i for i in indices if 0 <= i < total_pages)


def _render_page(page: fitz.Page, dpi: int = 300) -> Image.Image:
    """Renderiza uma página de PDF em PIL.Image RGB."""
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=mat)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


# ------------------------------------------------------------------------------
# Engines OCR
# ------------------------------------------------------------------------------
def _get_rapidocr() -> Optional[Any]:
    """
    Carrega o RapidOCR de forma lazy. Retorna None se a biblioteca não
    estiver instalada ou falhar a inicialização.
    """
    global _RAPIDOCR_ENGINE, _RAPIDOCR_CHECKED  # noqa
    if _RAPIDOCR_CHECKED:
        return _RAPIDOCR_ENGINE

    try:
        from rapidocr_onnxruntime import RapidOCR  # type: ignore

        _RAPIDOCR_ENGINE = RapidOCR()
    except Exception:
        _RAPIDOCR_ENGINE = None
    finally:
        _RAPIDOCR_CHECKED = True

    return _RAPIDOCR_ENGINE


def _tesseract_ocr_page(
    image: Image.Image,
    lang: str = "por",
    psm: int = 6,
) -> tuple[str, float, str]:
    """
    Executa Tesseract OCR em uma imagem e retorna (texto, confiança, engine).
    A confiança é a média dos valores de confiança por palavra (0-1).
    Levanta RuntimeError se o binário do Tesseract não for encontrado.
    """
    try:
        config = f"--psm {psm}"
        data = pytesseract.image_to_data(
            image,
            lang=lang,
            config=config,
            output_type=pytesseract.Output.DICT,
        )
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract OCR não encontrado. "
            "Instale o pacote 'tesseract-ocr' e adicione-o ao PATH."
        ) from exc

    confidences: List[int] = []
    words: List[str] = []

    for i, word in enumerate(data["text"]):
        word = word.strip()
        if not word:
            continue
        try:
            conf = int(data["conf"][i])
        except (ValueError, TypeError):
            continue
        if conf >= 0:
            confidences.append(conf)
            words.append(word)

    text = " ".join(words)
    confidence = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0
    return text, max(0.0, min(1.0, confidence)), "tesseract"


def _rapidocr_page(image: Image.Image, lang: str = "por") -> tuple[str, float, Optional[str]]:
    """
    Executa RapidOCR em uma imagem. Retorna (texto, confiança, engine).
    Se RapidOCR não estiver disponível, retorna engine=None.
    """
    engine = _get_rapidocr()
    if engine is None:
        return "", 0.0, None

    import numpy as np

    arr = np.array(image)
    try:
        result, _ = engine(arr)
    except Exception:
        return "", 0.0, None

    if not result:
        return "", 0.0, "rapidocr"

    words: List[str] = []
    confidences: List[float] = []

    for item in result:
        # Formato esperado: [box, text, confidence]
        if not isinstance(item, (list, tuple)) or len(item) < 3:
            continue
        _, txt, conf = item
        words.append(str(txt))
        try:
            confidences.append(float(conf))
        except (ValueError, TypeError):
            continue

    text = " ".join(words)
    confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return text, max(0.0, min(1.0, confidence)), "rapidocr"


# ------------------------------------------------------------------------------
# API pública
# ------------------------------------------------------------------------------
def ocr_image(
    path: Union[str, os.PathLike],
    lang: str = "por",
    psm: int = 6,
) -> Dict[str, Any]:
    """
    OCR em uma única imagem usando Tesseract.
    Retorna dict com 'text', 'confidence' e 'engine'.
    Levanta RuntimeError se o Tesseract não estiver instalado.
    """
    image = Image.open(path).convert("RGB")
    text, confidence, engine = _tesseract_ocr_page(image, lang=lang, psm=psm)
    return {
        "text": text,
        "confidence": confidence,
        "engine": engine,
    }


def analyze_pdf(path: Union[str, os.PathLike]) -> Dict[str, Any]:
    """
    Diagnóstico de PDF sem realizar OCR.
    Retorna metadados e informações por página (texto nativo, imagens,
    dimensões, tipo estimado).
    """
    doc = fitz.open(path)
    try:
        total = doc.page_count
        pages_info: List[Dict[str, Any]] = []

        for idx in range(total):
            page = doc[idx]
            text = page.get_text()
            images = page.get_images(full=True)
            rect = page.rect

            has_text = bool(text.strip())
            has_image = len(images) > 0

            if has_text and not has_image:
                estimated = "text"
            elif has_image and not has_text:
                estimated = "image"
            else:
                estimated = "mixed"

            pages_info.append(
                {
                    "page_number": idx + 1,
                    "width": rect.width,
                    "height": rect.height,
                    "has_text": has_text,
                    "has_image": has_image,
                    "image_count": len(images),
                    "text_length": len(text),
                    "estimated_type": estimated,
                }
            )

        return {
            "path": str(path),
            "total_pages": total,
            "pages": pages_info,
        }
    finally:
        doc.close()


def health() -> Dict[str, Any]:
    """
    Verifica quais engines estão disponíveis e suas versões.
    """
    info: Dict[str, Any] = {
        "pymupdf": False,
        "tesseract": False,
        "rapidocr": False,
        "versions": {},
    }

    try:
        info["pymupdf"] = True
        info["versions"]["pymupdf"] = getattr(fitz, "version", "unknown")
    except Exception:
        pass

    try:
        version = pytesseract.get_tesseract_version()
        info["tesseract"] = True
        info["versions"]["tesseract"] = str(version)
    except Exception:
        pass

    try:
        import rapidocr_onnxruntime  # type: ignore

        info["rapidocr"] = True
        info["versions"]["rapidocr"] = getattr(
            rapidocr_onnxruntime, "__version__", "unknown"
        )
    except Exception:
        pass

    return info


def ocr_pdf(
    path: Union[str, os.PathLike],
    lang: str = "por",
    dpi: int = 300,
    pages: Optional[Union[int, str, List[int]]] = None,
    force_engine: Optional[str] = None,
) -> OCRResult:
    """
    Executa OCR em um PDF com roteamento automático por página.

    Engines:
        - 'auto' (padrão): texto nativo legível -> PyMuPDF;
          scan limpo -> Tesseract; fonte corrompida/scan complexo ou
          confiança Tesseract < 70% -> RapidOCR.
        - 'tesseract': força Tesseract.
        - 'rapidocr': força RapidOCR (fallback para Tesseract se indisponível).

    :param path: caminho do PDF.
    :param lang: idioma para o Tesseract (padrão 'por').
    :param dpi: resolução de renderização das páginas.
    :param pages: páginas a processar (1-based). None = todas.
    :param force_engine: 'auto', 'tesseract' ou 'rapidocr'.
    :return: OCRResult.
    """
    if force_engine not in (None, "auto", "tesseract", "rapidocr"):
        raise ValueError(
            "force_engine deve ser 'auto', 'tesseract' ou 'rapidocr'."
        )

    doc = fitz.open(path)
    try:
        total_pages = doc.page_count
        page_indices = _parse_page_selection(total_pages, pages)

        results: List[PageResult] = []
        warnings: List[str] = []
        engines_used: set[str] = set()
        rapid_unavailable_warned = False

        for idx in page_indices:
            start = time.perf_counter()
            page = doc[idx]
            engine = ""
            text = ""
            confidence = 0.0

            try:
                selected = force_engine or "auto"

                if selected == "auto":
                    native_text = page.get_text()
                    if _texto_legivel(native_text):
                        engine = "native"
                        text = native_text
                        confidence = 1.0
                    else:
                        img = _render_page(page, dpi)
                        text, confidence, engine = _tesseract_ocr_page(
                            img, lang=lang
                        )
                        if confidence < _TESSERACT_CONF_THRESHOLD or not text.strip():
                            rapid_text, rapid_conf, rapid_engine = _rapidocr_page(
                                img, lang=lang
                            )
                            if rapid_engine is None:
                                if not rapid_unavailable_warned:
                                    warnings.append(
                                        "RapidOCR não está instalado/disponível; "
                                        "mantendo resultado do Tesseract."
                                    )
                                    rapid_unavailable_warned = True
                            elif rapid_text.strip():
                                text, confidence, engine = (
                                    rapid_text,
                                    rapid_conf,
                                    rapid_engine,
                                )

                elif selected == "tesseract":
                    img = _render_page(page, dpi)
                    text, confidence, engine = _tesseract_ocr_page(img, lang=lang)

                elif selected == "rapidocr":
                    img = _render_page(page, dpi)
                    text, confidence, engine = _rapidocr_page(img, lang=lang)
                    if engine is None:
                        warnings.append(
                            "RapidOCR não está instalado/disponível; "
                            "fallback para Tesseract."
                        )
                        text, confidence, engine = _tesseract_ocr_page(
                            img, lang=lang
                        )

            except RuntimeError:
                raise
            except Exception as exc:
                warnings.append(f"Página {idx + 1}: {exc}")

            latency = (time.perf_counter() - start) * 1000.0
            results.append(
                PageResult(
                    page_number=idx + 1,
                    engine=engine or "error",
                    text=text,
                    confidence=confidence,
                    latency_ms=round(latency, 2),
                )
            )
            if engine:
                engines_used.add(engine)

        full_text = "\n\n".join(p.text for p in results)

        return OCRResult(
            total_pages=total_pages,
            engines_used=sorted(engines_used),
            full_text=full_text,
            pages=results,
            warnings=warnings,
        )
    finally:
        doc.close()


# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Conector unificado de OCR para PDFs jurídicos."
    )
    parser.add_argument("arquivo", help="Caminho do arquivo PDF.")
    parser.add_argument(
        "--engine",
        choices=["auto", "tesseract", "rapidocr"],
        default="auto",
        help="Engine de OCR (padrão: auto).",
    )
    parser.add_argument(
        "--pages",
        type=str,
        default=None,
        help="Páginas a processar, ex: '1-3,5,7-9'. Padrão: todas.",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="por",
        help="Idioma do Tesseract (padrão: por).",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI para renderização das páginas (padrão: 300).",
    )

    args = parser.parse_args()

    result = ocr_pdf(
        args.arquivo,
        lang=args.lang,
        dpi=args.dpi,
        pages=args.pages,
        force_engine=args.engine,
    )

    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

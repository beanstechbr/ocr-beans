"""
ocr_beans/backend.py
--------------------
Seleciona o motor de processamento por variável de ambiente.

    OCR_BEANS_ENGINE=pymupdf     (padrão — melhor qualidade, AGPL)
    OCR_BEANS_ENGINE=permissive  (100% permissivo, distribuível comercialmente)

Todas as interfaces (API, MCP, CLI) devem importar daqui, nunca de
core/convert diretamente, para que a troca de motor seja transparente.
"""

from __future__ import annotations

import os

ENGINE = os.environ.get("OCR_BEANS_ENGINE", "pymupdf").strip().lower()
if ENGINE not in ("pymupdf", "permissive"):
    ENGINE = "pymupdf"

if ENGINE == "permissive":
    from . import convert_permissive as _convert
    from . import engine_permissive as _core
else:
    from . import convert as _convert
    from . import core as _core


def _abrir_saida_texto(path: str, mode: str = "w"):
    """Abre arquivo de saída com validação inline: sem '..' nem nulos, pasta existente."""
    if not path or "\x00" in path or ".." in path.replace("\\", "/").split("/"):
        raise ValueError(f"Caminho inválido: {path!r}")
    resolved = os.path.realpath(os.path.expanduser(path))
    if "r" in mode:
        if not os.path.isfile(resolved):
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    else:
        parent = os.path.dirname(resolved)
        if not parent or not os.path.isdir(parent):
            raise ValueError(f"Diretório de saída não existe: {path}")
    return open(resolved, mode, encoding="utf-8" if "b" not in mode else None)


def motor_ativo() -> dict:
    """Descreve o motor em uso (para health/diagnóstico)."""
    return {
        "engine": ENGINE,
        "agpl_free": ENGINE == "permissive",
        "descricao": (
            "pypdfium2 + pypdf + Tesseract + RapidOCR (100% permissivo)"
            if ENGINE == "permissive"
            else "PyMuPDF + Tesseract (AGPL — ver docs/LICENSE-NOTES.md)"
        ),
    }


# --------------------------------------------------------------------------- #
# OCR / extração
# --------------------------------------------------------------------------- #
def processar_pdf(pdf_path, dpi=300, lang="por", progress_callback=None, pages=None):
    if ENGINE == "permissive":
        return _core.processar_pdf(pdf_path, dpi=dpi, lang=lang, pages=pages)
    return _core.processar_pdf(pdf_path, dpi=dpi, lang=lang,
                               progress_callback=progress_callback)


def processar_paginas(pdf_path, page_range, dpi=300, lang="por"):
    if ENGINE == "permissive":
        from .core import _parse_page_range  # parser puro, sem motor
        pages = _parse_page_range(page_range)
        r = _core.processar_pdf(pdf_path, dpi=dpi, lang=lang, pages=pages)
        return {
            "path": r["path"],
            "total_pages": r["total_pages"],
            "requested_pages": sorted(pages),
            "pages": r["pages"],
        }
    return _core.processar_paginas(pdf_path, page_range, dpi=dpi, lang=lang)


def check_legibility(pdf_path):
    return _core.check_legibility(pdf_path)


def ocr_imagem(image_path, lang="por", psm=6, pre_processar=True):
    if ENGINE == "permissive":
        from PIL import Image
        img = Image.open(image_path)
        try:
            img.load()
            if img.mode not in ("L", "RGB"):
                img = img.convert("RGB")
            w, h = img.size
            text = _core.ocr_pagina_pil(img, lang=lang, psm=psm)
        finally:
            img.close()
        return {"path": image_path, "width": w, "height": h, "lang": lang,
                "content": text.strip()}
    return _core.ocr_imagem(image_path, lang=lang, psm=psm, pre_processar=pre_processar)


def texto_legivel(text):
    return _core.texto_legivel(text)


def health_motor():
    if ENGINE == "permissive":
        return _core.health()
    from .core import tesseract_disponivel, idiomas_disponiveis
    return {
        "engine": ENGINE,
        "tesseract": tesseract_disponivel(),
        "idiomas": idiomas_disponiveis(),
    }


# --------------------------------------------------------------------------- #
# Conversões
# --------------------------------------------------------------------------- #
def juntar_pdfs(pdf_paths, output_path):
    return _convert.juntar_pdfs(pdf_paths, output_path)


def dividir_pdf(pdf_path, output_path, pages):
    return _convert.dividir_pdf(pdf_path, output_path, pages)


def rotacionar_pdf(pdf_path, output_path, graus=90, pages=None):
    return _convert.rotacionar_pdf(pdf_path, output_path, graus=graus, pages=pages)


def comprimir_pdf(pdf_path, output_path, qualidade_imagem=60, dpi_imagem=150):
    if ENGINE == "permissive":
        return _convert.comprimir_pdf(pdf_path, output_path,
                                      qualidade_imagem=qualidade_imagem)
    return _convert.comprimir_pdf(pdf_path, output_path,
                                  qualidade_imagem=qualidade_imagem, dpi_imagem=dpi_imagem)


def pdf_para_imagens(pdf_path, output_zip, dpi=200, fmt="png", pages=None):
    return _convert.pdf_para_imagens(pdf_path, output_zip, dpi=dpi, fmt=fmt, pages=pages)


def imagens_para_pdf(image_paths, output_path):
    return _convert.imagens_para_pdf(image_paths, output_path)


def extrair_imagens_pdf(pdf_path, output_zip):
    return _convert.extrair_imagens_pdf(pdf_path, output_zip)


def pdf_para_docx(pdf_path, output_path, pages=None):
    return _convert.pdf_para_docx(pdf_path, output_path, pages=pages)


def adicionar_marca_dagua(pdf_path, output_path, texto, opacidade=0.15, tamanho=48, angulo=45):
    if ENGINE == "permissive":
        return _convert.adicionar_marca_dagua(pdf_path, output_path, texto,
                                              opacidade=opacidade)
    return _convert.adicionar_marca_dagua(pdf_path, output_path, texto,
                                          opacidade=opacidade, tamanho=tamanho, angulo=angulo)


def pdf_para_txt(pdf_path, output_path, dpi=300, lang="por"):
    if ENGINE == "permissive":
        r = _core.processar_pdf(pdf_path, dpi=dpi, lang=lang)
        lines = []
        for page in r["pages"]:
            lines.append(f"\n{'=' * 70}")
            lines.append(f"PÁGINA {page['number']} ({page['source']})")
            lines.append(f"{'=' * 70}")
            lines.append(page["content"])
        with _abrir_saida_texto(output_path, "w") as f:
            f.write("\n".join(lines))
        return {
            "output": os.path.realpath(output_path),
            "total_pages": r["total_pages"],
            "ocr_pages": r["ocr_pages"],
            "text_pages": r["text_pages"],
        }
    return _convert.pdf_para_txt(pdf_path, output_path, dpi=dpi, lang=lang)

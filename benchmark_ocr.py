#!/usr/bin/env python3
"""
benchmark_ocr.py

Benchmark production-grade de OCR para PDFs jurídicos brasileiros.
Compara o texto nativo do PDF (ground-truth) contra o texto extraído
por engines OCR sobre imagens renderizadas das páginas.

Gerado por megacoder (kimi-k2.7-code) e validado por execução.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import string
import time
import unicodedata
import warnings
from dataclasses import asdict, dataclass
from typing import List

import pymupdf as fitz  # PyMuPDF
import jiwer
import pytesseract
from PIL import Image


# ------------------------------------------------------------------------------
# Configuração global de idioma (usada pelas funções de OCR)
# ------------------------------------------------------------------------------
_LANG: str = "por"


def set_ocr_lang(lang: str) -> None:
    global _LANG
    _LANG = lang


# ------------------------------------------------------------------------------
# Normalização de texto
# ------------------------------------------------------------------------------
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


def normalize_text(text: str) -> str:
    """
    Normaliza o texto para comparação de conteúdo:
    - lowercase
    - remove acentos (NFKD + filtra combining chars)
    - remove pontuação
    - colapsa espaços
    """
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))
    text = " ".join(text.split())
    return text


# ------------------------------------------------------------------------------
# Engines OCR
# ------------------------------------------------------------------------------
def ocr_tesseract(img: Image.Image) -> str:
    """OCR via Tesseract."""
    return pytesseract.image_to_string(img, lang=_LANG)


# Lazy-load do RapidOCR
_rapidocr_engine = None


def ocr_rapidocr(img: Image.Image) -> str:
    """OCR via RapidOCR (CPU / ONNX)."""
    global _rapidocr_engine
    if _rapidocr_engine is None:
        try:
            from rapidocr_onnxruntime import RapidOCR

            _rapidocr_engine = RapidOCR()
        except Exception as exc:  # pragma: no cover
            warnings.warn(f"RapidOCR não pôde ser carregado: {exc}", stacklevel=2)
            return ""

    try:
        import numpy as np

        arr = np.array(img)
        result, _ = _rapidocr_engine(arr)
        if not result:
            return ""
        # RapidOCR retorna lista de [box, texto, score]
        return "\n".join(line[1] for line in result)
    except Exception as exc:  # pragma: no cover
        warnings.warn(f"RapidOCR falhou: {exc}", stacklevel=2)
        return ""


# ------------------------------------------------------------------------------
# Estruturas de dados
# ------------------------------------------------------------------------------
@dataclass
class PageMetric:
    doc: str
    page: int
    engine: str
    cer: float
    wer: float
    latency_ms: float


@dataclass
class EngineSummary:
    engine: str
    mean_cer: float
    mean_wer: float
    mean_latency_ms: float
    pages: int


@dataclass
class BenchmarkReport:
    summaries: List[EngineSummary]
    pages: List[PageMetric]
    generated_at: str

    def to_markdown(self) -> str:
        lines = [
            "# Benchmark OCR - Relatório",
            f"Gerado em: {self.generated_at}",
            "",
            "## Resumo por Engine",
            "| Engine | Páginas | CER Médio | WER Médio | Latência Média (ms) |",
            "|--------|--------:|----------:|----------:|--------------------:|",
        ]
        for s in self.summaries:
            lines.append(
                f"| {s.engine} | {s.pages} | {s.mean_cer:.4f} | {s.mean_wer:.4f} | {s.mean_latency_ms:.2f} |"
            )

        lines.extend([
            "",
            "## Métricas por Página",
            "| Documento | Página | Engine | CER | WER | Latência (ms) |",
            "|-----------|-------:|--------|----:|----:|--------------:|",
        ])
        for p in self.pages:
            lines.append(
                f"| {os.path.basename(p.doc)} | {p.page} | {p.engine} | {p.cer:.4f} | {p.wer:.4f} | {p.latency_ms:.2f} |"
            )

        return "\n".join(lines)

    def save_json(self, path: str) -> None:
        with _abrir_saida_texto(path) as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------------------------
# Benchmark principal
# ------------------------------------------------------------------------------
def run_benchmark(
    pdf_paths: list[str],
    engines: list[str],
    pages_per_doc: int = 3,
    dpi: int = 300,
    lang: str = "por",
) -> BenchmarkReport:
    """
    Renderiza páginas de PDFs como imagens, executa os engines OCR e compara
    com o texto nativo do PDF usando CER e WER.
    """
    set_ocr_lang(lang)

    supported = {"tesseract", "rapidocr"}
    invalid = set(engines) - supported
    if invalid:
        raise ValueError(f"Engines inválidas: {invalid}. Suportadas: {supported}")

    engine_funcs = {
        "tesseract": ocr_tesseract,
        "rapidocr": ocr_rapidocr,
    }

    pages_metrics: List[PageMetric] = []

    for pdf_path in pdf_paths:
        if not os.path.exists(pdf_path):
            warnings.warn(f"Arquivo não encontrado: {pdf_path}", stacklevel=2)
            continue

        try:
            doc = fitz.open(pdf_path)
        except Exception as exc:
            warnings.warn(f"Erro ao abrir {pdf_path}: {exc}", stacklevel=2)
            continue

        num_pages = min(pages_per_doc, len(doc))

        for page_idx in range(num_pages):
            page = doc[page_idx]
            native_text = page.get_text()
            stripped_native = native_text.strip()

            if len(stripped_native) < 30:
                continue

            norm_reference = normalize_text(native_text)
            if not norm_reference:
                continue

            # Renderiza a página como imagem
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            mode = "RGB" if pix.n == 3 else "RGBA"
            img = Image.frombytes(mode, (pix.width, pix.height), pix.samples).convert("RGB")

            for engine_name in engines:
                ocr_func = engine_funcs[engine_name]

                start = time.perf_counter()
                ocr_raw = ocr_func(img)
                elapsed = time.perf_counter() - start

                norm_ocr = normalize_text(ocr_raw)

                try:
                    cer = float(jiwer.cer(norm_reference, norm_ocr))
                    wer = float(jiwer.wer(norm_reference, norm_ocr))
                except Exception as exc:
                    warnings.warn(f"Erro ao calcular métricas: {exc}", stacklevel=2)
                    cer, wer = 1.0, 1.0

                latency_ms = elapsed * 1000

                metric = PageMetric(
                    doc=pdf_path,
                    page=page_idx + 1,
                    engine=engine_name,
                    cer=cer,
                    wer=wer,
                    latency_ms=latency_ms,
                )
                pages_metrics.append(metric)

                print(
                    f"[{os.path.basename(pdf_path)}] Página {page_idx + 1} | "
                    f"Engine: {engine_name} | CER: {cer:.4f}"
                )

        doc.close()

    # Agregação por engine
    summaries: List[EngineSummary] = []
    for engine_name in engines:
        engine_pages = [p for p in pages_metrics if p.engine == engine_name]
        if engine_pages:
            mean_cer = sum(p.cer for p in engine_pages) / len(engine_pages)
            mean_wer = sum(p.wer for p in engine_pages) / len(engine_pages)
            mean_latency = sum(p.latency_ms for p in engine_pages) / len(engine_pages)
        else:
            mean_cer = mean_wer = mean_latency = 0.0

        summaries.append(
            EngineSummary(
                engine=engine_name,
                mean_cer=mean_cer,
                mean_wer=mean_wer,
                mean_latency_ms=mean_latency,
                pages=len(engine_pages),
            )
        )

    return BenchmarkReport(
        summaries=summaries,
        pages=pages_metrics,
        generated_at=datetime.datetime.now().isoformat(),
    )


# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark de OCR para PDFs jurídicos brasileiros."
    )
    parser.add_argument("pdfs", nargs="+", help="Caminhos para os arquivos PDF.")
    parser.add_argument(
        "--pages", type=int, default=3, help="Número de páginas por documento."
    )
    parser.add_argument(
        "--dpi", type=int, default=300, help="DPI para renderização das páginas."
    )
    parser.add_argument(
        "--lang", type=str, default="por", help="Código de idioma para o Tesseract."
    )
    parser.add_argument(
        "--engines",
        nargs="+",
        default=["tesseract", "rapidocr"],
        help="Engines a avaliar.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="benchmark_ocr_report.json",
        help="Arquivo JSON de saída.",
    )

    args = parser.parse_args()

    report = run_benchmark(
        pdf_paths=args.pdfs,
        engines=args.engines,
        pages_per_doc=args.pages,
        dpi=args.dpi,
        lang=args.lang,
    )

    print("\n" + report.to_markdown())
    report.save_json(args.output)
    print(f"\nRelatório salvo em: {args.output}")


if __name__ == "__main__":
    main()

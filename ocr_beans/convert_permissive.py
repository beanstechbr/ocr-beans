# ocr_beans/convert_permissive.py
# Módulo drop-in de conversões de PDF sem dependências de copyleft restritivo.
#
# Licenças das bibliotecas utilizadas:
#   - pypdf:        BSD-3-Clause
#   - pypdfium2:    Apache-2.0 / BSD-3-Clause (pdfium)
#   - pikepdf:      MPL-2.0
#   - Pillow (PIL): HPND
#   - img2pdf:      LGPL-3.0+
#   - reportlab:    BSD-3-Clause
#   - python-docx:  MIT
#
# Não utiliza PyMuPDF (AGPL) nem pdf2docx.

from __future__ import annotations

import io
import math
import os
import tempfile
import zipfile

import img2pdf
import pikepdf
import pypdfium2 as pdfium
from docx import Document
from docx.shared import Inches
from PIL import Image
from pikepdf import PdfImage
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


# --------------------------------------------------------------------------- #
# Validação de caminhos (inline junto ao I/O)
# --------------------------------------------------------------------------- #
def _open_saida(path: str, mode: str):
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
            os.makedirs(parent, exist_ok=True)
    return open(resolved, mode)


def _validar_entrada(caminho: str, ext: str | None = None) -> None:
    if not isinstance(caminho, str) or not caminho:
        raise ValueError("Caminho inválido.")
    if ".." in caminho.replace("\\", "/").split("/"):
        raise ValueError("Caminho contém '..' (path traversal não é permitido).")
    if ext is not None and not caminho.lower().endswith(ext.lower()):
        raise ValueError(f"Arquivo deve ter extensão {ext}.")
    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")


def _validar_saida(caminho: str, ext: str) -> None:
    if not isinstance(caminho, str) or not caminho:
        raise ValueError("Caminho inválido.")
    if ".." in caminho.replace("\\", "/").split("/"):
        raise ValueError("Caminho contém '..' (path traversal não é permitido).")
    if not caminho.lower().endswith(ext.lower()):
        raise ValueError(f"Arquivo deve ter extensão {ext}.")


def _validar_paginas(paginas: list[int], total: int) -> None:
    if not paginas:
        raise ValueError("A lista de páginas não pode ser vazia.")
    for p in paginas:
        if not isinstance(p, int) or p < 1 or p > total:
            raise ValueError(f"Página {p} fora do intervalo válido (1..{total}).")


# --------------------------------------------------------------------------- #
# Funções públicas
# --------------------------------------------------------------------------- #
def juntar_pdfs(pdf_paths: list[str], output_path: str) -> str:
    """Junta uma lista de PDFs em um único arquivo."""
    if not pdf_paths:
        raise ValueError("A lista de PDFs está vazia.")
    _validar_saida(output_path, ".pdf")

    writer = PdfWriter()
    for caminho in pdf_paths:
        _validar_entrada(caminho, ".pdf")
        for pagina in PdfReader(caminho).pages:
            writer.add_page(pagina)

    with _open_saida(output_path, "wb") as f:
        writer.write(f)
    return os.path.realpath(output_path)


def dividir_pdf(pdf_path: str, output_path: str, pages: list[int]) -> str:
    """Cria um novo PDF contendo apenas as páginas informadas (1-based)."""
    _validar_entrada(pdf_path, ".pdf")
    _validar_saida(output_path, ".pdf")

    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    _validar_paginas(pages, total)

    writer = PdfWriter()
    for p in pages:
        writer.add_page(reader.pages[p - 1])

    with _open_saida(output_path, "wb") as f:
        writer.write(f)
    return os.path.realpath(output_path)


def rotacionar_pdf(
    pdf_path: str,
    output_path: str,
    graus: int = 90,
    pages: list[int] | None = None,
) -> str:
    """Rotaciona páginas do PDF em 90°, 180° ou 270°."""
    if graus not in (90, 180, 270):
        raise ValueError("A rotação deve ser 90, 180 ou 270 graus.")
    _validar_entrada(pdf_path, ".pdf")
    _validar_saida(output_path, ".pdf")

    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    if pages is not None:
        _validar_paginas(pages, total)

    writer = PdfWriter()
    for i, pagina in enumerate(reader.pages):
        if pages is None or (i + 1) in pages:
            pagina = pagina.rotate(graus)
        writer.add_page(pagina)

    with _open_saida(output_path, "wb") as f:
        writer.write(f)
    return os.path.realpath(output_path)


def comprimir_pdf(
    pdf_path: str,
    output_path: str,
    qualidade_imagem: int = 60,
) -> dict:
    """Recomprime imagens do PDF e regrava streams, retornando estatísticas."""
    _validar_entrada(pdf_path, ".pdf")
    _validar_saida(output_path, ".pdf")

    if not 1 <= qualidade_imagem <= 100:
        raise ValueError("A qualidade da imagem deve estar entre 1 e 100.")

    tamanho_original = os.path.getsize(pdf_path)
    pdf = pikepdf.Pdf.open(pdf_path)

    MAX_DIM = 2048
    MAX_PIXELS = 4_000_000

    for pagina in pdf.pages:
        recursos = pagina.get("/Resources")
        if not recursos:
            continue
        xobjects = recursos.get("/XObject")
        if not xobjects:
            continue

        for nome, obj in xobjects.items():
            try:
                if obj.get("/Subtype") != pikepdf.Name("/Image"):
                    continue
                if obj.get("/ImageMask") == 1:
                    continue

                pil_image = PdfImage(obj).as_pil_image()
                largura, altura = pil_image.size

                pixels = largura * altura
                max_dim = max(largura, altura)
                escala = 1.0
                if max_dim > MAX_DIM:
                    escala = min(escala, MAX_DIM / max_dim)
                if pixels > MAX_PIXELS:
                    escala = min(escala, math.sqrt(MAX_PIXELS / pixels))

                if escala < 1.0:
                    novo_tamanho = (
                        max(1, int(largura * escala)),
                        max(1, int(altura * escala)),
                    )
                    pil_image = pil_image.resize(novo_tamanho, Image.Resampling.LANCZOS)

                if pil_image.mode in ("RGBA", "LA", "P", "1"):
                    pil_image = pil_image.convert("RGB")

                buf = io.BytesIO()
                pil_image.save(buf, format="JPEG", quality=qualidade_imagem, optimize=True)
                jpeg_bytes = buf.getvalue()

                try:
                    dados_originais = obj.read_bytes()
                except Exception:
                    dados_originais = b""

                if escala >= 1.0 and len(jpeg_bytes) >= len(dados_originais):
                    continue

                obj.write_bytes(jpeg_bytes)
                obj["/Filter"] = pikepdf.Name("/DCTDecode")
                obj["/ColorSpace"] = pikepdf.Name("/DeviceRGB")
                obj["/BitsPerComponent"] = 8

                for chave in (
                    "/DecodeParms", "/Decode", "/Mask", "/SMask", "/Intent",
                    "/Interpolate", "/Name", "/StructParent", "/OC",
                ):
                    if chave in obj:
                        del obj[chave]
            except Exception:
                continue

    pdf.save(
        os.path.realpath(output_path),
        object_stream_mode=pikepdf.ObjectStreamMode.preserve,
        compress_streams=True,
    )

    tamanho_final = os.path.getsize(output_path)
    reducao = round((1 - tamanho_final / tamanho_original) * 100, 2)

    return {
        "output": os.path.realpath(output_path),
        "tamanho_original": tamanho_original,
        "tamanho_final": tamanho_final,
        "reducao_pct": reducao,
    }


def pdf_para_imagens(
    pdf_path: str,
    output_zip: str,
    dpi: int = 200,
    fmt: str = "png",
    pages: list[int] | None = None,
) -> str:
    """Renderiza páginas do PDF em imagens e empacota em ZIP."""
    _validar_entrada(pdf_path, ".pdf")
    _validar_saida(output_zip, ".zip")

    fmt = fmt.lower()
    if fmt not in {"png", "jpeg", "jpg", "tiff", "bmp", "webp"}:
        raise ValueError(f"Formato de imagem não suportado: {fmt}")

    formato_pil = "JPEG" if fmt in ("jpg", "jpeg") else fmt.upper()
    extensao = "jpg" if fmt in ("jpg", "jpeg") else fmt

    pdf = pdfium.PdfDocument(pdf_path)
    total = len(pdf)
    if pages is None:
        indices = list(range(total))
    else:
        _validar_paginas(pages, total)
        indices = [p - 1 for p in pages]

    with _open_saida(output_zip, "wb") as raw:
        with zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as zf:
            for idx in indices:
                bitmap = pdf[idx].render(scale=dpi / 72.0)
                imagem = bitmap.to_pil()
                buf = io.BytesIO()
                imagem.save(buf, format=formato_pil)
                zf.writestr(f"page_{idx + 1:04d}.{extensao}", buf.getvalue())
    pdf.close()
    return os.path.realpath(output_zip)


def imagens_para_pdf(image_paths: list[str], output_path: str) -> str:
    """Converte uma lista de imagens em PDF, normalizando para RGB."""
    if not image_paths:
        raise ValueError("A lista de imagens está vazia.")
    _validar_saida(output_path, ".pdf")

    arquivos_temp: list[str] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i, caminho in enumerate(image_paths):
            _validar_entrada(caminho)
            with Image.open(caminho) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                temp_path = os.path.join(tmpdir, f"{i:04d}.jpg")
                img.save(temp_path, "JPEG", quality=95)
                arquivos_temp.append(temp_path)

        with _open_saida(output_path, "wb") as f:
            img2pdf.convert(arquivos_temp, outputstream=f)

    return os.path.realpath(output_path)


def extrair_imagens_pdf(pdf_path: str, output_zip: str) -> dict:
    """Extrai as imagens embutidas do PDF e empacota em ZIP."""
    _validar_entrada(pdf_path, ".pdf")
    _validar_saida(output_zip, ".zip")

    reader = PdfReader(pdf_path)
    imagens_extraidas: list[str] = []

    with _open_saida(output_zip, "wb") as raw:
        with zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as zf:
            nomes_vistos: set[str] = set()
            for i, pagina in enumerate(reader.pages):
                for imagem in pagina.images:
                    try:
                        pil_image = imagem.image
                    except Exception:
                        continue

                    filtro = getattr(imagem, "filter", None)
                    nome_filtro = str(filtro).upper() if filtro else ""
                    if "DCT" in nome_filtro:
                        ext = "jpg"
                    elif "JPX" in nome_filtro:
                        ext = "jp2"
                    elif "CCITT" in nome_filtro:
                        ext = "tiff"
                    else:
                        ext = "png"

                    buf = io.BytesIO()
                    if ext == "jpg":
                        pil_image.convert("RGB").save(buf, "JPEG", quality=95)
                    elif ext == "jp2":
                        pil_image.save(buf, "JPEG2000")
                    elif ext == "tiff":
                        pil_image.save(buf, "TIFF")
                    else:
                        pil_image.save(buf, "PNG")

                    nome_base = getattr(imagem, "name", "img") or "img"
                    nome_seguro = "".join(
                        c if c.isalnum() or c in ("_", "-") else "_" for c in nome_base
                    )
                    nome_arquivo = f"page_{i + 1:04d}_{nome_seguro}.{ext}"
                    contador = 1
                    while nome_arquivo in nomes_vistos:
                        nome_arquivo = f"page_{i + 1:04d}_{nome_seguro}_{contador}.{ext}"
                        contador += 1
                    nomes_vistos.add(nome_arquivo)
                    zf.writestr(nome_arquivo, buf.getvalue())
                    imagens_extraidas.append(nome_arquivo)

    return {
        "output": os.path.realpath(output_zip),
        "imagens": imagens_extraidas,
    }


def pdf_para_docx(
    pdf_path: str,
    output_path: str,
    pages: list[int] | None = None,
) -> str:
    """Converte PDF para DOCX: texto nativo; páginas sem texto vão como imagem."""
    _validar_entrada(pdf_path, ".pdf")
    _validar_saida(output_path, ".docx")

    pdf = pdfium.PdfDocument(pdf_path)
    total = len(pdf)
    if pages is None:
        indices = list(range(total))
    else:
        _validar_paginas(pages, total)
        indices = [p - 1 for p in pages]

    doc = Document()
    for pos, idx in enumerate(indices):
        pagina = pdf[idx]
        texto = pagina.get_textpage().get_text_range()

        if texto and texto.strip():
            for linha in texto.splitlines():
                doc.add_paragraph(linha)
        else:
            imagem = pagina.render(scale=150 / 72.0).to_pil()
            buf = io.BytesIO()
            imagem.save(buf, format="PNG")
            buf.seek(0)
            doc.add_picture(buf, width=Inches(6.5))

        if pos < len(indices) - 1:
            doc.add_page_break()

    doc.save(os.path.realpath(output_path))
    pdf.close()
    return os.path.realpath(output_path)


def adicionar_marca_dagua(
    pdf_path: str,
    output_path: str,
    texto: str,
    opacidade: float = 0.15,
) -> str:
    """Adiciona uma marca d'água textual em todas as páginas do PDF."""
    _validar_entrada(pdf_path, ".pdf")
    _validar_saida(output_path, ".pdf")

    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("O texto da marca d'água não pode ser vazio.")
    if not 0 <= opacidade <= 1:
        raise ValueError("A opacidade deve estar entre 0 e 1.")

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for pagina in reader.pages:
        largura = float(pagina.mediabox.width)
        altura = float(pagina.mediabox.height)

        pacote = io.BytesIO()
        c = canvas.Canvas(pacote, pagesize=(largura, altura))
        tamanho_fonte = min(largura, altura) * 0.08
        c.setFont("Helvetica", tamanho_fonte)
        c.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacidade)
        c.saveState()
        c.translate(largura / 2, altura / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, texto)
        c.restoreState()
        c.save()

        pacote.seek(0)
        overlay = PdfReader(pacote).pages[0]
        pagina.merge_page(overlay)
        writer.add_page(pagina)

    with _open_saida(output_path, "wb") as f:
        writer.write(f)
    return os.path.realpath(output_path)

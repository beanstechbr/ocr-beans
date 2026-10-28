"""
test_api_suite.py
Suite de testes production-grade para a API REST do OCR Beans.
Gerada por megacoder (kimi-k2.7-code) e validada por execucao.
"""

import io
import zipfile
from pathlib import Path

import pytest
import requests
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_URL = "http://127.0.0.1:8080"
TIMEOUT = 60


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def base_url() -> str:
    """Verifica se a API está disponível antes de executar os testes."""
    url = BASE_URL
    try:
        response = requests.get(f"{url}/api/health", timeout=5)
        response.raise_for_status()
    except requests.RequestException as exc:
        pytest.skip(f"OCR Beans API indisponível em {url}: {exc}")
    return url


@pytest.fixture(scope="function")
def sample_text() -> str:
    return "OCR Beans Test"


def _generate_pdf(path: Path, text: str, pages: int = 1) -> Path:
    pdf_path = path / "sample.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    for i in range(pages):
        c.drawString(100, height - 100, f"{text} - page {i + 1}")
        c.showPage()
    c.save()
    return pdf_path


def _generate_png(path: Path, text: str) -> Path:
    img_path = path / "sample.png"
    img = Image.new("RGB", (800, 200), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 60)
    except Exception:
        font = ImageFont.load_default()
    draw.text((50, 70), text, fill="black", font=font)
    img.save(img_path, "PNG")
    return img_path


@pytest.fixture(scope="function")
def pdf_file(tmp_path: Path, sample_text: str) -> Path:
    return _generate_pdf(tmp_path, sample_text, pages=1)


@pytest.fixture(scope="function")
def multi_page_pdf(tmp_path: Path, sample_text: str) -> Path:
    return _generate_pdf(tmp_path, sample_text, pages=2)


@pytest.fixture(scope="function")
def png_file(tmp_path: Path, sample_text: str) -> Path:
    return _generate_png(tmp_path, sample_text)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _assert_valid_pdf(content: bytes) -> None:
    assert content.startswith(b"%PDF"), "O conteúdo não começa com %PDF"
    reader = PdfReader(io.BytesIO(content))
    assert len(reader.pages) >= 1, "PDF gerado não possui páginas"


def _assert_valid_zip(content: bytes) -> None:
    buffer = io.BytesIO(content)
    assert zipfile.is_zipfile(buffer), "O conteúdo não é um ZIP válido"
    with zipfile.ZipFile(buffer) as zf:
        assert len(zf.namelist()) > 0, "ZIP está vazio"


def _mime(filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return "application/pdf"
    if filename.lower().endswith(".png"):
        return "image/png"
    return "application/octet-stream"


# --------------------------------------------------------------------------- #
# Testes de caminho feliz
# --------------------------------------------------------------------------- #
def test_health(base_url: str) -> None:
    response = requests.get(f"{base_url}/api/health", timeout=TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    for key in ("status", "versao", "tesseract", "idiomas"):
        assert key in data


def test_tools(base_url: str) -> None:
    response = requests.get(f"{base_url}/api/tools", timeout=TIMEOUT)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "catalogo" in data or len(data) > 0


def test_ocr_pdf(base_url: str, pdf_file: Path) -> None:
    with open(pdf_file, "rb") as f:
        response = requests.post(
            f"{base_url}/api/ocr/pdf",
            files={"file": (pdf_file.name, f, _mime(pdf_file.name))},
            data={"dpi": 300, "lang": "por"},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith("text/plain")
    assert "BEANS" in response.text.upper() or "OCR" in response.text.upper()


def test_ocr_image(base_url: str, png_file: Path) -> None:
    with open(png_file, "rb") as f:
        response = requests.post(
            f"{base_url}/api/ocr/image",
            files={"file": (png_file.name, f, _mime(png_file.name))},
            data={"lang": "por", "psm": 6},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    data = response.json()
    for key in ("arquivo", "largura", "altura", "idioma", "texto"):
        assert key in data
    assert data["texto"].strip() != ""


def test_check(base_url: str, pdf_file: Path) -> None:
    with open(pdf_file, "rb") as f:
        response = requests.post(
            f"{base_url}/api/check",
            files={"file": (pdf_file.name, f, _mime(pdf_file.name))},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    data = response.json()
    for key in ("legible", "total_pages", "sample_text", "reason"):
        assert key in data
    assert isinstance(data["legible"], bool)
    assert isinstance(data["total_pages"], int)


def test_convert_merge(base_url: str, tmp_path: Path, pdf_file: Path) -> None:
    second_pdf = _generate_pdf(tmp_path, "Second PDF", pages=1)
    with open(pdf_file, "rb") as f1, open(second_pdf, "rb") as f2:
        files = [
            ("files", (pdf_file.name, f1, _mime(pdf_file.name))),
            ("files", (second_pdf.name, f2, _mime(second_pdf.name))),
        ]
        response = requests.post(
            f"{base_url}/api/convert/merge", files=files, timeout=TIMEOUT
        )
    assert response.status_code == 200
    _assert_valid_pdf(response.content)


def test_convert_split(base_url: str, multi_page_pdf: Path) -> None:
    with open(multi_page_pdf, "rb") as f:
        response = requests.post(
            f"{base_url}/api/convert/split",
            files={"file": (multi_page_pdf.name, f, _mime(multi_page_pdf.name))},
            data={"pages": "1-2"},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    _assert_valid_pdf(response.content)


def test_convert_compress(base_url: str, multi_page_pdf: Path) -> None:
    with open(multi_page_pdf, "rb") as f:
        response = requests.post(
            f"{base_url}/api/convert/compress",
            files={"file": (multi_page_pdf.name, f, _mime(multi_page_pdf.name))},
            data={"qualidade": 60},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    assert "X-Reducao-Pct" in response.headers
    _assert_valid_pdf(response.content)


def test_convert_rotate(base_url: str, multi_page_pdf: Path) -> None:
    with open(multi_page_pdf, "rb") as f:
        response = requests.post(
            f"{base_url}/api/convert/rotate",
            files={"file": (multi_page_pdf.name, f, _mime(multi_page_pdf.name))},
            data={"graus": 90, "pages": "1"},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    _assert_valid_pdf(response.content)


def test_convert_watermark(base_url: str, multi_page_pdf: Path) -> None:
    with open(multi_page_pdf, "rb") as f:
        response = requests.post(
            f"{base_url}/api/convert/watermark",
            files={"file": (multi_page_pdf.name, f, _mime(multi_page_pdf.name))},
            data={"texto": "Confidencial"},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    _assert_valid_pdf(response.content)


def test_convert_pdf_to_images(base_url: str, multi_page_pdf: Path) -> None:
    with open(multi_page_pdf, "rb") as f:
        response = requests.post(
            f"{base_url}/api/convert/pdf-to-images",
            files={"file": (multi_page_pdf.name, f, _mime(multi_page_pdf.name))},
            data={"dpi": 200, "fmt": "png", "pages": "1"},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    _assert_valid_zip(response.content)


def test_convert_images_to_pdf(base_url: str, tmp_path: Path, png_file: Path) -> None:
    second_png = _generate_png(tmp_path, "Imagem 2")
    with open(png_file, "rb") as f1, open(second_png, "rb") as f2:
        files = [
            ("files", (png_file.name, f1, _mime(png_file.name))),
            ("files", (second_png.name, f2, _mime(second_png.name))),
        ]
        response = requests.post(
            f"{base_url}/api/convert/images-to-pdf", files=files, timeout=TIMEOUT
        )
    assert response.status_code == 200
    _assert_valid_pdf(response.content)


def test_convert_pdf_to_docx(base_url: str, multi_page_pdf: Path) -> None:
    with open(multi_page_pdf, "rb") as f:
        response = requests.post(
            f"{base_url}/api/convert/pdf-to-docx",
            files={"file": (multi_page_pdf.name, f, _mime(multi_page_pdf.name))},
            data={"pages": "1"},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    buffer = io.BytesIO(response.content)
    assert zipfile.is_zipfile(buffer), "DOCX não é um ZIP válido"
    with zipfile.ZipFile(buffer) as zf:
        assert "word/document.xml" in zf.namelist()


def test_convert_extract_images(base_url: str, multi_page_pdf: Path) -> None:
    with open(multi_page_pdf, "rb") as f:
        response = requests.post(
            f"{base_url}/api/convert/extract-images",
            files={"file": (multi_page_pdf.name, f, _mime(multi_page_pdf.name))},
            timeout=TIMEOUT,
        )
    assert response.status_code == 200
    content_type = response.headers.get("Content-Type", "")
    if content_type.startswith("application/zip"):
        _assert_valid_zip(response.content)
    else:
        data = response.json()
        assert "imagens" in data
        assert isinstance(data["imagens"], int)


# --------------------------------------------------------------------------- #
# Testes de erro
# --------------------------------------------------------------------------- #
def test_split_invalid_pages_returns_422(base_url: str, multi_page_pdf: Path) -> None:
    with open(multi_page_pdf, "rb") as f:
        response = requests.post(
            f"{base_url}/api/convert/split",
            files={"file": (multi_page_pdf.name, f, _mime(multi_page_pdf.name))},
            data={"pages": "invalid"},
            timeout=TIMEOUT,
        )
    assert response.status_code == 422


def test_ocr_image_invalid_format_returns_422(base_url: str, pdf_file: Path) -> None:
    with open(pdf_file, "rb") as f:
        response = requests.post(
            f"{base_url}/api/ocr/image",
            files={"file": (pdf_file.name, f, _mime(pdf_file.name))},
            data={"lang": "por", "psm": 6},
            timeout=TIMEOUT,
        )
    assert response.status_code == 422


def test_empty_file_returns_error(base_url: str) -> None:
    response = requests.post(
        f"{base_url}/api/ocr/image",
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
        data={"lang": "por", "psm": 6},
        timeout=TIMEOUT,
    )
    assert response.status_code in (400, 422)

# OCR Beans

**OCR de PDFs judiciais brasileiros e imagens + suíte de conversão de PDF — via MCP, CLI, API web e app desktop.**

PDFs de tribunais brasileiros (TJ-SP, TRT, STJ) frequentemente usam fontes proprietárias que nenhuma IA consegue ler. O OCR Beans detecta automaticamente essas fontes corrompidas e aplica OCR quando necessário — transformando documentos ilegíveis em texto limpo que qualquer agente AI pode usar.

## O que está incluído

| Interface | Uso | Público |
|-----------|-----|---------|
| **API Web** | `ocr-beans-api` — UI estilo iLovePDF + REST em `/api/*` | Programas e humanos |
| **MCP Server** | `ocr-beans-mcp` — tools para Claude Code / agentes AI | Agentes AI |
| **CLI** | `ocr-beans <comando>` — terminal | Scripts e automação |
| **App Desktop** | `ocr_beans_app.py` — GUI (Windows/macOS/Linux) | Usuário final |

## Funcionalidades

### OCR (o diferencial)
- **PDF → Texto** com detecção automática de fonte corrompida (heurística para português jurídico)
- **Imagem → Texto** (PNG, JPG, TIFF, BMP, WEBP, GIF)
- **Diagnóstico rápido** (`check`): diz se o PDF precisa de OCR em < 1s, sem processar

### Conversões de PDF (estilo iLovePDF, mas via API/CLI)
- Imagens → PDF
- PDF → Imagens (zip com PNG/JPG por página)
- PDF → Word (DOCX editável)
- Juntar PDFs (merge)
- Dividir / extrair páginas
- Comprimir PDF (recompacta imagens embutidas — testado: −33,6% em contrato real)
- Girar páginas (90/180/270)
- Marca d'água de texto
- Extrair imagens embutidas

## Instalação rápida

**Linux (Debian/Ubuntu):**
```bash
sudo apt install tesseract-ocr tesseract-ocr-por
pip install -r requirements.txt   # ou: pip install .
```

**macOS:**
```bash
brew install tesseract tesseract-lang
pip install -r requirements.txt
```

**Windows:**
1. Instale o Tesseract: https://github.com/UB-Mannheim/tesseract/wiki (marque "Portuguese")
2. `pip install -r requirements.txt`

Instruções detalhadas por SO: [docs/INSTALACAO.md](docs/INSTALACAO.md)

## Uso rápido

### API Web (humano + programas)

```bash
ocr-beans-api --port 8080
# ou: python -m ocr_beans.api --port 8080
```

- UI web (clicar e arrastar): http://localhost:8080/
- Documentação interativa (Swagger): http://localhost:8080/docs
- Integração programática: [docs/API.md](docs/API.md)

```bash
# Exemplo: extrair texto de um PDF judicial via curl
curl -F "file=@processo.pdf" http://localhost:8080/api/ocr/pdf -o processo.txt

# Exemplo: OCR de uma imagem
curl -F "file=@scan.png" http://localhost:8080/api/ocr/image
```

### CLI

```bash
ocr-beans pdf processo.pdf                    # extrai texto (OCR automático)
ocr-beans imagem scan.png                     # OCR de imagem
ocr-beans check processo.pdf                  # diagnóstico: precisa de OCR?
ocr-beans juntar a.pdf b.pdf -o merged.pdf
ocr-beans dividir doc.pdf --paginas 1-3,7 -o parte.pdf
ocr-beans comprimir doc.pdf -o pequeno.pdf --qualidade 60
ocr-beans girar doc.pdf --graus 90 -o girado.pdf
ocr-beans marca-dagua doc.pdf --texto CONFIDENCIAL -o marcado.pdf
ocr-beans pdf-para-imagens doc.pdf -o pags.zip --dpi 200
ocr-beans imagens-para-pdf f1.png f2.jpg -o saida.pdf
ocr-beans pdf-para-docx doc.pdf -o saida.docx
ocr-beans extrair-imagens doc.pdf -o imagens.zip
```

Referência completa: [docs/CLI.md](docs/CLI.md)

### MCP Server (Claude Code / agentes AI)

Adicione ao seu `~/.claude.json` (seção `mcpServers`):

```json
{
  "ocr-beans": {
    "type": "stdio",
    "command": "python",
    "args": ["/caminho/para/OCR Beans/ocr_beans/mcp_server.py"]
  }
}
```

Tools disponíveis: `ocr_pdf`, `ocr_page`, `ocr_image`, `check_legibility`, `batch_ocr`.
Detalhes: [docs/MCP.md](docs/MCP.md)

### App Desktop (GUI)

```bash
python ocr_beans_app.py
```

Aceita PDFs **e imagens**. Para gerar o executável Windows com Tesseract embutido: `python -m PyInstaller "OCR Beans.spec" --noconfirm`.

## Deploy (Docker / Cloud)

```bash
docker build -t ocr-beans .
docker run -p 8080:8080 ocr-beans        # API web + REST
```

O container sobe a API. Para modo MCP remoto (streamable-http):
```bash
docker run -p 8080:8080 ocr-beans python -m ocr_beans.mcp_server --remote
```

### GCP Cloud Run

```bash
gcloud run deploy ocr-beans \
  --source . \
  --region southamerica-east1 \
  --no-allow-unauthenticated \
  --memory 2Gi --cpu 2 --timeout 300
```

## Segurança

- **Path traversal**: caminhos com `..` rejeitados; uploads confinados ao diretório temporário
- **Upload**: limite de 200MB por arquivo (configurável via `OCR_BEANS_MAX_UPLOAD_MB`)
- **DPI**: limitado a 150–400 (evita OOM)
- **Batch**: máximo 50 arquivos por operação
- **Pages**: máximo 100 páginas por request no MCP

Para deploy público, coloque autenticação na frente (IAM no GCP, ALB auth na AWS, ou reverse proxy com auth).

## Arquitetura

```
ocr_beans/
├── __init__.py       # Versão
├── core.py           # Motor OCR multiplataforma (PDF + imagem, detecção de fonte corrompida)
├── convert.py        # Conversões PDF (merge, split, compress, watermark, docx...)
├── security.py       # Validações de input
├── mcp_server.py     # MCP server (5 tools, stdio + HTTP, SDK 1.x e 2.x)
├── api.py            # API FastAPI (REST + web UI)
├── webui.py          # UI web embutida (single-page)
└── cli.py            # CLI unificado
```

**Dependências principais:**
- PyMuPDF — extração de texto nativo e renderização
- Tesseract (pytesseract) — OCR quando texto nativo é corrompido
- pypdf / img2pdf / pdf2docx — conversões
- FastAPI + uvicorn — API web
- MCP SDK — protocolo com agentes AI

## Limitações conhecidas

- Tesseract é excelente em texto corrido limpo (~99%), mas perde estrutura em tabelas
  multiculunares e pode falhar em timbres. Roadmap: motor VLM opcional (Surya/PaddleOCR-VL).
- PDF → DOCX funciona melhor em PDFs com texto nativo; scans viram imagem no DOCX.

## Licença

BeansTech 2026. Open-source (licença a definir).

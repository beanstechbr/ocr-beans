# Conector OCR Beans — Claude, GPT e Copilot

O OCR Beans expõe o mesmo motor de OCR/conversão por **três padrões de conector**,
para plugar nos principais agentes de IA.

## Pré-requisito

O servidor precisa estar no ar:

```bash
ocr-beans-api --port 8080          # ou: systemctl --user start ocr-beans-api
```

- OpenAPI (gerado automaticamente): http://localhost:8080/openapi.json
- Swagger interativo: http://localhost:8080/docs

---

## 1. Claude (MCP) — o mais completo

O MCP server tem **14 tools** e funciona via stdio (local) ou HTTP (remoto).

`~/.claude.json` (seção `mcpServers`):

```json
{
  "ocr-beans": {
    "type": "stdio",
    "command": "python3",
    "args": ["/mnt/sda1/D1/OCR Beans/ocr_beans/mcp_server.py"]
  }
}
```

Tools: `ocr_pdf`, `ocr_page`, `ocr_image`, `check_legibility`, `batch_ocr`,
`pdf_merge`, `pdf_split`, `pdf_compress`, `pdf_rotate`, `pdf_watermark`,
`pdf_to_images`, `images_to_pdf`, `pdf_to_docx`, `pdf_extract_images`.

---

## 2. GPT (OpenAI) — via Actions / plugin manifest

O arquivo [`connector/ai-plugin.json`](./ai-plugin.json) é o manifest. A API de
verdade é o `openapi.json` que o FastAPI gera sozinho.

Em um GPT customizado (ChatGPT → Explore GPTs → Create → Actions), importe a spec:

```
http://localhost:8080/openapi.json
```

ou aponte o manifest `ai-plugin.json` (que referencia o openapi.json).

> Para uso fora da sua máquina, suba a API num host acessível e troque
> `localhost:8080` pela URL real (com auth na frente).

---

## 3. Copilot (Microsoft) — declarative agent / plugin

O arquivo [`connector/copilot-plugin.json`](./copilot-plugin.json) descreve as 12
ações sobre a API REST. Importe-o como *declarative agent* / plugin de API no
Copilot Studio ou no manifest do seu agente.

---

## Autenticação

Todos os manifests assumem `auth: none` (uso local). Para expor publicamente,
coloque um proxy com autenticação (OAuth2/API key) na frente e ajuste `auth` no
manifest correspondente.

## Privacidade

Processamento 100% local: os arquivos vão apenas para a API desta máquina.

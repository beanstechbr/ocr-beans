# Licenças e o risco AGPL

## O problema

O motor principal (`ocr_beans/core.py`, `convert.py`) usa **PyMuPDF**, cuja licença é
**AGPL-3.0 / comercial (Artifex)**.

Isso importa se você quiser **vender ou distribuir o OCR Beans como produto fechado**
(plugin/conector pago para Claude, GPT, Copilot, ou licença on-prem B2B):

- **AGPL** exige que qualquer trabalho derivado distribuído — incluindo uso via rede
  (SaaS/API) — seja também AGPL, com código-fonte aberto.
- Um plugin/conector comercial fechado que linka PyMuPDF **viola a AGPL** sem uma
  licença comercial paga da Artifex.

## As duas saídas

### Opção A — Licenciar a Artifex (recomendada para produto comercial)

Comprar a licença comercial da Artifex para o PyMuPDF. Mantém o motor atual (que é o
mais maduro para PDF judicial) sem mudança de código. Custo anual por produto/projeto.

### Opção B — Motor permissivo (sem custo de licença)

O módulo **`ocr_beans/engine_permissive.py`** é um backend drop-in 100% permissivo:

| Componente | Função | Licença |
|---|---|---|
| pypdfium2 | render + texto nativo | BSD-3-Clause / Apache-2.0 |
| pypdf | fallback de texto nativo | BSD-3-Clause |
| Tesseract (pytesseract) | OCR | Apache-2.0 |
| Pillow | imagem | HPND (permissiva) |
| rapidocr_onnxruntime | OCR SOTA (CPU) | Apache-2.0 |

Nenhum componente é copyleft — pode distribuir fechado, vender, integrar em plugin
comercial.

**Status:** validado por execução (texto nativo e OCR funcionando em PDFs reais).

**Trade-off honesto:** pypdfium2/pypdf extraem texto nativo de forma um pouco diferente
do PyMuPDF em PDFs com fontes corrompidas — o motor permissivo pode divergir em casos
de borda. O `convert.py` (compressão, marca d'água, etc.) ainda usa PyMuPDF e precisaria
de reescrita equivalente para uma distribuição 100% permissiva.

## Recomendação

- **Uso interno / open-source (AGPL ok):** mantenha PyMuPDF.
- **Produto comercial fechado:** licencie a Artifex (Opção A) para manter a qualidade,
  ou invista na migração completa para o motor permissivo (Opção B) começando por
  `engine_permissive.py`.

> Este documento é informativo e não substitui aconselhamento jurídico.

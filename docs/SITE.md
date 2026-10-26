# O Site — passo a passo

Acesse **http://localhost:8080/** (o serviço `ocr-beans-api` sobe sozinho no boot).

## Estrutura da página

1. **Barra superior** — marca ocr*beans*, atalhos (Ferramentas, Como funciona), botão **API REST ↗** e indicador de status do processamento (bolinha verde = pronto).
2. **Hero** — proposta do produto, ilustração do fluxo (documento → OCR → texto extraído) e botão "Explorar ferramentas".
3. **Faixa de métricas** — 12 ferramentas, 100% local, OCR automático, REST + MCP.
4. **Ferramentas** — aviso de privacidade, **filtros por categoria** (Todas / OCR e texto / Converter / Organizar / Otimizar), **busca** (tolerante a acentos e plural/singular) e os 12 cartões.
5. **Como funciona** — o fluxo em 3 passos.
6. **CTA final** — exemplo de chamada da API e link da documentação.
7. **Rodapé** — marca, ano e link da API.

## Usando qualquer ferramenta (passo a passo)

1. **Encontre a ferramenta** — filtre por categoria ou busque pelo nome (ex.: "juntar", "imagem", "word").
2. **Clique no cartão** — abre a janela da ferramenta com título, descrição e nota de privacidade.
3. **Envie os arquivos** — arraste para a área tracejada ou clique em "selecione no seu dispositivo". Cada arquivo vira uma linha da lista com **número de ordem**, tamanho e botões ↑ ↓ × (em ferramentas de múltiplos arquivos, a ordem da lista é a ordem do resultado — ex.: Juntar PDFs, Imagens → PDF).
4. **Ajuste as opções** quando existirem:
   - *PDF → Texto*: idioma do OCR (por / por+eng / eng) e DPI (200/300/400)
   - *Imagem → Texto*: idioma e segmentação (bloco / automática / texto esparso)
   - *PDF → Imagens*: formato (PNG/JPG), DPI e páginas (ex.: `1-3,7`)
   - *PDF → Word*: páginas
   - *Dividir*: páginas (obrigatório)
   - *Girar*: 90/180/270 graus + páginas
   - *Comprimir*: qualidade 40/60/75 (menor = arquivo menor)
   - *Marca d'água*: texto livre (obrigatório)
5. **Clique em "Processar arquivo"**. Um spinner indica o andamento; é possível **Cancelar** a qualquer momento.
6. **Resultado**:
   - Conversões: **download automático** + botão "Baixar novamente"
   - *Imagem → Texto*: texto na tela com botão **Copiar texto**
   - *Diagnosticar PDF*: veredito (Precisa de OCR: Sim/Não), nº de páginas, motivo e amostra do texto
7. **"Processar outro arquivo"** limpa a janela para uma nova operação.
8. Erros aparecem em vermelho com a causa (página inválida, formato não suportado, arquivo acima de 200 MB etc.).

## Dialog "API REST"

O botão **API REST ↗** (ou "Conhecer a API") abre a documentação resumida: exemplo de `GET /api/health`, exemplos `curl` copiáveis, tabela das 12 rotas com seus campos, regras de resposta (arquivo binário com `Content-Disposition`, JSON para diagnóstico/erros) e limites. Links para o Swagger interativo (`/docs`) e o catálogo (`/api/tools`).

## Privacidade

Processamento 100% local: os arquivos vão apenas para o servidor desta máquina, são gravados em diretório temporário descartável e o resultado volta como download. Nada é enviado a serviços externos.

## Atalhos úteis

| Ação | Onde |
|------|------|
| Swagger interativo | `/docs` |
| Saúde do serviço | `GET /api/health` |
| Catálogo de endpoints | `GET /api/tools` |
| Logs do serviço | `journalctl --user -u ocr-beans-api -f` |

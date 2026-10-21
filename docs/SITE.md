# O Site — passo a passo

Acesse **http://localhost:8080/** (o serviço `ocr-beans-api` sobe sozinho no boot).

## Estrutura da página

1. **Barra superior** — logo, atalhos para Ferramentas, Como funciona e **API REST ↗** (documentação interativa Swagger em `/docs`, para integrar por programa).
2. **Cabeçalho (hero)** — proposta do produto e indicadores: 12 ferramentas, processamento 100% local, diagnóstico em <1s, API REST.
3. **Ferramentas em 3 grupos:**
   - **OCR inteligente** — PDF → Texto (OCR), Imagem → Texto (OCR), Diagnosticar PDF
   - **Converter** — Imagens → PDF, PDF → Imagens, PDF → Word, Extrair imagens do PDF
   - **Organizar e editar** — Juntar PDFs, Dividir/Extrair páginas, Comprimir PDF, Girar PDF, Marca d'água
4. **Como funciona** — o fluxo em 3 passos.
5. **Rodapé** — nota de privacidade (nada sai da máquina) e link da API.

## Usando qualquer ferramenta (passo a passo)

1. **Clique no cartão** da ferramenta desejada. Abre-se uma janela (modal) com título, descrição e área de envio.
2. **Envie o(s) arquivo(s)**: arraste para a área tracejada ou clique para abrir o seletor. Ferramentas como *Juntar PDFs* e *Imagens → PDF* aceitam vários arquivos — a ordem de seleção é a ordem do resultado.
3. **Confira a lista** — cada arquivo aparece como um chip com nome e tamanho.
4. **Ajuste as opções** quando existirem:
   - *Comprimir PDF*: qualidade 40/60/75 (menor = arquivo menor)
   - *Dividir*: páginas como `1-3,7`
   - *Girar*: 90/180/270 graus
   - *Marca d'água*: texto livre
   - *PDF → Imagens*: DPI (150/200/300) e formato (PNG/JPG)
5. **Clique em Processar**. Uma barra de progresso animada indica trabalho em andamento. PDFs grandes com OCR podem levar alguns minutos (~1,2s por página escaneada).
6. **Resultado**:
   - Conversões retornam **download automático** do arquivo processado.
   - *Imagem → Texto* e *Diagnosticar PDF* retornam **JSON na tela** (texto extraído / diagnóstico).
7. **Erros** aparecem em vermelho com a mensagem (ex.: página inválida, formato não suportado, arquivo acima de 200 MB).
8. **Voltar** (←) ou clicar fora da janela retorna à lista de ferramentas.

## Privacidade

Os arquivos são enviados apenas para o servidor local (sua máquina), processados em
diretório temporário que é descartado, e o resultado volta como download. Nenhum dado
vai para a nuvem ou terceiros.

## Atalhos úteis

| Ação | Onde |
|------|------|
| Documentação interativa da API | `/docs` (Swagger) |
| Saúde do serviço | `GET /api/health` |
| Catálogo de endpoints | `GET /api/tools` |
| Logs do serviço | `journalctl --user -u ocr-beans-api -f` |

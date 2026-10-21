"""
OCR Beans - Interface web embutida (single-page, sem dependências externas).
Servida pela API em GET /.
"""

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OCR Beans — Suite profissional de OCR e PDF</title>
<style>
  :root{
    --brand:#0f6b3a; --brand-2:#0a4f2b; --accent:#16a34a;
    --ink:#0f172a; --muted:#64748b; --line:#e2e8f0;
    --bg:#f8fafc; --card:#ffffff; --radius:14px;
  }
  *{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',system-ui,-apple-system,sans-serif}
  body{background:var(--bg);color:var(--ink)}
  a{color:inherit}

  /* ---------- Header ---------- */
  .topbar{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.92);
    backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
  .topbar-inner{max-width:1120px;margin:0 auto;padding:14px 24px;display:flex;
    align-items:center;gap:12px}
  .logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:1.15rem}
  .logo-mark{width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,var(--brand),var(--accent));
    display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px}
  .topbar nav{margin-left:auto;display:flex;gap:22px;font-size:.9rem;color:var(--muted)}
  .topbar nav a{text-decoration:none}
  .topbar nav a:hover{color:var(--brand)}
  .badge-api{background:var(--brand);color:#fff;padding:6px 14px;border-radius:8px;
    font-size:.85rem;font-weight:600;text-decoration:none}
  .badge-api:hover{background:var(--brand-2)}

  /* ---------- Hero ---------- */
  .hero{max-width:1120px;margin:0 auto;padding:56px 24px 36px;text-align:center}
  .hero h1{font-size:2.5rem;letter-spacing:-.02em;line-height:1.15}
  .hero h1 span{color:var(--brand)}
  .hero p{max-width:640px;margin:16px auto 0;color:var(--muted);font-size:1.08rem;line-height:1.6}
  .hero-stats{display:flex;gap:36px;justify-content:center;margin-top:28px;flex-wrap:wrap}
  .stat{text-align:center}
  .stat b{display:block;font-size:1.5rem;color:var(--brand)}
  .stat span{font-size:.82rem;color:var(--muted)}

  /* ---------- Sections ---------- */
  .wrap{max-width:1120px;margin:0 auto;padding:0 24px}
  .secao{margin:36px 0}
  .secao h2{font-size:.85rem;text-transform:uppercase;letter-spacing:.12em;
    color:var(--muted);margin-bottom:14px;display:flex;align-items:center;gap:10px}
  .secao h2::after{content:"";flex:1;height:1px;background:var(--line)}

  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
    padding:20px;cursor:pointer;transition:all .18s ease;position:relative}
  .card:hover{border-color:var(--accent);box-shadow:0 8px 24px rgba(15,107,58,.10);
    transform:translateY(-2px)}
  .card .icone{width:42px;height:42px;border-radius:10px;background:#ecfdf5;
    display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:12px}
  .card h3{font-size:.98rem;font-weight:600;margin-bottom:5px}
  .card p{font-size:.82rem;color:var(--muted);line-height:1.45}

  /* ---------- Como funciona ---------- */
  .steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
  .step{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px}
  .step .num{width:28px;height:28px;border-radius:50%;background:var(--brand);color:#fff;
    display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;margin-bottom:10px}
  .step h4{font-size:.92rem;margin-bottom:6px}
  .step p{font-size:.82rem;color:var(--muted);line-height:1.5}

  /* ---------- Painel de trabalho ---------- */
  #painel{display:none;position:fixed;inset:0;background:rgba(15,23,42,.55);
    z-index:100;overflow:auto;padding:40px 16px}
  .modal{max-width:680px;margin:0 auto;background:#fff;border-radius:18px;
    box-shadow:0 24px 64px rgba(0,0,0,.25);overflow:hidden}
  .modal-head{background:linear-gradient(135deg,var(--brand),var(--brand-2));
    color:#fff;padding:22px 28px}
  .modal-head h2{font-size:1.25rem}
  .modal-head p{opacity:.85;font-size:.88rem;margin-top:4px}
  .modal-body{padding:24px 28px}
  .voltar{background:rgba(255,255,255,.15);border:0;color:#fff;padding:6px 14px;
    border-radius:8px;cursor:pointer;font-size:.85rem;margin-bottom:14px}
  .voltar:hover{background:rgba(255,255,255,.28)}
  .drop{border:2px dashed #cbd5e1;border-radius:12px;padding:38px 20px;text-align:center;
    color:var(--muted);cursor:pointer;transition:all .15s;background:#f8fafc}
  .drop:hover,.drop.over{border-color:var(--accent);background:#ecfdf5;color:var(--brand)}
  .drop b{color:var(--brand)}
  #lista-arqs{margin:12px 0;display:flex;flex-direction:column;gap:6px}
  .arquivo-chip{display:flex;align-items:center;gap:8px;background:#f1f5f9;
    border-radius:8px;padding:8px 12px;font-size:.85rem}
  .arquivo-chip span{margin-left:auto;color:var(--muted);font-size:.78rem}
  .campo{margin-bottom:14px}
  .campo label{display:block;font-size:.84rem;font-weight:600;margin-bottom:6px;color:#334155}
  .campo input,.campo select{width:100%;padding:10px 12px;border:1px solid var(--line);
    border-radius:9px;font-size:.92rem;background:#fff}
  .campo input:focus,.campo select:focus{outline:2px solid var(--accent);border-color:transparent}
  button.acao{background:var(--brand);color:#fff;border:0;padding:14px 26px;border-radius:10px;
    font-size:1rem;font-weight:600;cursor:pointer;width:100%;transition:background .15s}
  button.acao:hover:not(:disabled){background:var(--brand-2)}
  button.acao:disabled{background:#94a3b8;cursor:wait}
  #status{margin-top:16px;font-size:.88rem;white-space:pre-wrap;border-radius:10px;display:none;padding:14px}
  #status.erro{display:block;color:#b91c1c;background:#fef2f2}
  #status.ok{display:block;color:#166534;background:#f0fdf4}
  #status.trabalhando{display:block;color:#075985;background:#f0f9ff}

  .barra{height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;margin-top:14px;display:none}
  .barra div{height:100%;width:40%;background:var(--accent);border-radius:3px;
    animation:indet 1.2s infinite ease-in-out}
  @keyframes indet{0%{margin-left:-40%}100%{margin-left:100%}}

  footer{border-top:1px solid var(--line);margin-top:56px;padding:28px 24px;text-align:center;
    color:var(--muted);font-size:.82rem}
  footer b{color:var(--ink)}
</style>
</head>
<body>

<header class="topbar">
  <div class="topbar-inner">
    <div class="logo"><div class="logo-mark">☕</div> OCR Beans</div>
    <nav>
      <a href="#ferramentas">Ferramentas</a>
      <a href="#como-funciona">Como funciona</a>
      <a href="/docs" target="_blank" class="badge-api">API REST ↗</a>
    </nav>
  </div>
</header>

<section class="hero">
  <h1>OCR e ferramentas de PDF,<br><span>direto na sua máquina</span></h1>
  <p>Extraia texto de PDFs judiciais com fontes corrompidas, leia imagens e converta
     documentos — tudo local, privado e também disponível via API REST para os seus programas.</p>
  <div class="hero-stats">
    <div class="stat"><b>12</b><span>ferramentas</span></div>
    <div class="stat"><b>100%</b><span>local &amp; privado</span></div>
    <div class="stat"><b>&lt;1s</b><span>diagnóstico de PDF</span></div>
    <div class="stat"><b>REST</b><span>API para integração</span></div>
  </div>
</section>

<main class="wrap" id="ferramentas">
  <div class="secao">
    <h2>OCR inteligente</h2>
    <div class="grid" id="grid-ocr"></div>
  </div>
  <div class="secao">
    <h2>Converter</h2>
    <div class="grid" id="grid-converter"></div>
  </div>
  <div class="secao">
    <h2>Organizar e editar</h2>
    <div class="grid" id="grid-editar"></div>
  </div>
</main>

<section class="wrap secao" id="como-funciona">
  <h2>Como funciona</h2>
  <div class="steps">
    <div class="step"><div class="num">1</div><h4>Escolha a ferramenta</h4>
      <p>Clique em um cartão: OCR de PDF ou imagem, juntar, dividir, comprimir e mais.</p></div>
    <div class="step"><div class="num">2</div><h4>Envie os arquivos</h4>
      <p>Arraste para a área de envio ou clique para selecionar. Tudo é processado localmente.</p></div>
    <div class="step"><div class="num">3</div><h4>Baixe o resultado</h4>
      <p>O arquivo processado é baixado automaticamente. Nada fica armazenado no servidor.</p></div>
  </div>
</section>

<div id="painel">
  <div class="modal">
    <div class="modal-head">
      <button class="voltar" onclick="fechar()">← Voltar</button>
      <h2 id="p-titulo"></h2>
      <p id="p-desc"></p>
    </div>
    <div class="modal-body">
      <div class="drop" id="drop">Arraste arquivo(s) aqui<br>ou <b>clique para selecionar</b></div>
      <input type="file" id="file" style="display:none" multiple>
      <div id="lista-arqs"></div>
      <div id="opcoes"></div>
      <button class="acao" id="btn" onclick="executar()">Processar</button>
      <div class="barra" id="barra"><div></div></div>
      <div id="status"></div>
    </div>
  </div>
</div>

<footer>
  <b>OCR Beans</b> · BeansTech 2026 · Processamento 100% local —
  nenhum arquivo sai da sua máquina · <a href="/docs">Documentação da API</a>
</footer>

<script>
const TOOLS = [
 // ---- OCR ----
 {cat:'ocr', id:'ocr-pdf', icone:'📄', titulo:'PDF → Texto (OCR)',
  desc:'Extrai texto de PDF com OCR automático para fontes corrompidas e páginas escaneadas.',
  accept:'.pdf', multiple:false, endpoint:'/api/ocr/pdf'},
 {cat:'ocr', id:'ocr-img', icone:'🖼️', titulo:'Imagem → Texto (OCR)',
  desc:'Lê texto de PNG, JPG, TIFF, WEBP e outros formatos de imagem.',
  accept:'.png,.jpg,.jpeg,.tif,.tiff,.bmp,.webp', multiple:false, endpoint:'/api/ocr/image'},
 {cat:'ocr', id:'check', icone:'🩺', titulo:'Diagnosticar PDF',
  desc:'Detecta em segundos se o PDF tem fonte corrompida e precisa de OCR.',
  accept:'.pdf', multiple:false, endpoint:'/api/check'},
 // ---- Converter ----
 {cat:'converter', id:'img2pdf', icone:'🗂️', titulo:'Imagens → PDF',
  desc:'Junta várias imagens em um único PDF, na ordem escolhida.',
  accept:'.png,.jpg,.jpeg,.tif,.tiff,.bmp,.webp', multiple:true, endpoint:'/api/convert/images-to-pdf'},
 {cat:'converter', id:'pdf2img', icone:'🎞️', titulo:'PDF → Imagens',
  desc:'Renderiza páginas do PDF como PNG ou JPG (arquivo zip).',
  accept:'.pdf', multiple:false, endpoint:'/api/convert/pdf-to-images',
  opcoes:[{nome:'dpi',label:'Resolução (DPI)',tipo:'select',valores:['150','200','300'],padrao:'200'},
          {nome:'fmt',label:'Formato',tipo:'select',valores:['png','jpg'],padrao:'png'}]},
 {cat:'converter', id:'pdf2docx', icone:'📝', titulo:'PDF → Word',
  desc:'Converte PDF para DOCX editável, preservando a formatação.',
  accept:'.pdf', multiple:false, endpoint:'/api/convert/pdf-to-docx'},
 {cat:'converter', id:'extract-img', icone:'🗃️', titulo:'Extrair imagens do PDF',
  desc:'Baixa todas as imagens embutidas no documento (zip).',
  accept:'.pdf', multiple:false, endpoint:'/api/convert/extract-images'},
 // ---- Organizar e editar ----
 {cat:'editar', id:'merge', icone:'🔗', titulo:'Juntar PDFs',
  desc:'Combina vários PDFs em um só, na ordem selecionada.',
  accept:'.pdf', multiple:true, endpoint:'/api/convert/merge'},
 {cat:'editar', id:'split', icone:'✂️', titulo:'Dividir / Extrair páginas',
  desc:'Extrai páginas específicas do PDF (ex.: 1-3,7).',
  accept:'.pdf', multiple:false, endpoint:'/api/convert/split',
  opcoes:[{nome:'pages',label:'Páginas (ex: 1-3,7)',tipo:'text',padrao:'1'}]},
 {cat:'editar', id:'compress', icone:'🗜️', titulo:'Comprimir PDF',
  desc:'Reduz o tamanho do arquivo recompactando imagens embutidas.',
  accept:'.pdf', multiple:false, endpoint:'/api/convert/compress',
  opcoes:[{nome:'qualidade',label:'Qualidade das imagens',tipo:'select',
           valores:['40 (máxima compressão)','60 (equilibrada)','75 (alta qualidade)'],padrao:'60 (equilibrada)'}]},
 {cat:'editar', id:'rotate', icone:'🔄', titulo:'Girar PDF',
  desc:'Rotaciona páginas em 90, 180 ou 270 graus.',
  accept:'.pdf', multiple:false, endpoint:'/api/convert/rotate',
  opcoes:[{nome:'graus',label:'Graus',tipo:'select',valores:['90','180','270'],padrao:'90'}]},
 {cat:'editar', id:'watermark', icone:'💧', titulo:'Marca d’água',
  desc:'Aplica um texto diagonal em todas as páginas do documento.',
  accept:'.pdf', multiple:false, endpoint:'/api/convert/watermark',
  opcoes:[{nome:'texto',label:'Texto da marca d’água',tipo:'text',padrao:'CONFIDENCIAL'}]},
];

let toolAtual = null;
const painel = document.getElementById('painel');
const fileInput = document.getElementById('file');
const drop = document.getElementById('drop');

TOOLS.forEach(t => {
  const el = document.createElement('div');
  el.className = 'card';
  el.innerHTML = `<div class="icone">${t.icone}</div><h3>${t.titulo}</h3><p>${t.desc}</p>`;
  el.onclick = () => abrir(t);
  document.getElementById('grid-' + t.cat).appendChild(el);
});

function abrir(t) {
  toolAtual = t;
  document.getElementById('p-titulo').textContent = t.titulo;
  document.getElementById('p-desc').textContent = t.desc;
  fileInput.value = ''; fileInput.multiple = t.multiple; fileInput.accept = t.accept;
  document.getElementById('lista-arqs').innerHTML = '';
  const st = document.getElementById('status'); st.textContent=''; st.className='';
  const op = document.getElementById('opcoes'); op.innerHTML = '';
  (t.opcoes || []).forEach(o => {
    const div = document.createElement('div'); div.className = 'campo';
    const label = document.createElement('label'); label.textContent = o.label; div.appendChild(label);
    if (o.tipo === 'select') {
      const sel = document.createElement('select'); sel.id = 'opt-' + o.nome;
      o.valores.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v.split(' ')[0]; opt.textContent = v;
        if (v.startsWith(o.padrao.split(' ')[0])) opt.selected = true;
        sel.appendChild(opt);
      });
      div.appendChild(sel);
    } else {
      const inp = document.createElement('input'); inp.id = 'opt-' + o.nome; inp.value = o.padrao;
      div.appendChild(inp);
    }
    op.appendChild(div);
  });
  painel.style.display = 'block';
  document.body.style.overflow = 'hidden';
}
function fechar(){ painel.style.display='none'; document.body.style.overflow=''; toolAtual = null; }
painel.onclick = e => { if (e.target === painel) fechar(); };

drop.onclick = () => fileInput.click();
drop.ondragover = e => { e.preventDefault(); drop.classList.add('over'); };
drop.ondragleave = () => drop.classList.remove('over');
drop.ondrop = e => { e.preventDefault(); drop.classList.remove('over'); fileInput.files = e.dataTransfer.files; listar(); };
fileInput.onchange = listar;
function listar() {
  const box = document.getElementById('lista-arqs');
  box.innerHTML = '';
  [...fileInput.files].forEach(f => {
    const kb = f.size > 1048576 ? (f.size/1048576).toFixed(1)+' MB' : (f.size/1024).toFixed(0)+' KB';
    const chip = document.createElement('div');
    chip.className = 'arquivo-chip';
    chip.innerHTML = `📎 ${f.name}<span>${kb}</span>`;
    box.appendChild(chip);
  });
}

async function executar() {
  const st = document.getElementById('status');
  const btn = document.getElementById('btn');
  const barra = document.getElementById('barra');
  if (!fileInput.files.length) {
    st.className = 'erro'; st.textContent = 'Selecione ao menos um arquivo.'; return;
  }
  const fd = new FormData();
  if (toolAtual.multiple) { [...fileInput.files].forEach(f => fd.append('files', f)); }
  else { fd.append('file', fileInput.files[0]); }
  (toolAtual.opcoes || []).forEach(o =>
    fd.append(o.nome, document.getElementById('opt-' + o.nome).value));

  btn.disabled = true; barra.style.display = 'block';
  st.className = 'trabalhando'; st.textContent = 'Processando… arquivos grandes podem levar alguns minutos.';
  try {
    const resp = await fetch(toolAtual.endpoint, { method: 'POST', body: fd });
    if (!resp.ok) {
      let msg = 'Erro ' + resp.status;
      try { const j = await resp.json(); msg = j.detail || msg; } catch(e) {}
      throw new Error(msg);
    }
    const ctype = resp.headers.get('content-type') || '';
    if (ctype.includes('application/json')) {
      const j = await resp.json();
      st.className = 'ok'; st.textContent = JSON.stringify(j, null, 2);
    } else {
      const blob = await resp.blob();
      const cd = resp.headers.get('content-disposition') || '';
      const m = cd.match(/filename\*?=(?:utf-8'')?"?([^";]+)"?/i);
      const nome = m ? decodeURIComponent(m[1]) : 'resultado';
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = nome; a.click();
      st.className = 'ok'; st.textContent = '✔ Pronto! Download iniciado: ' + nome;
    }
  } catch (e) {
    st.className = 'erro'; st.textContent = '✘ ' + e.message;
  } finally { btn.disabled = false; barra.style.display = 'none'; }
}
</script>
</body>
</html>
"""

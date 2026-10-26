"""
OCR Beans - Interface web embutida (single-page, sem dependências externas).
Servida pela API em GET /. Design: tema café (creme/terracota/serif).
"""

INDEX_HTML = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#f8f5ef">
<meta name="description" content="OCR Beans: 12 ferramentas para PDFs e imagens, com OCR automático e API REST. Processamento 100% local.">
<title>OCR Beans — PDFs, sem complicar.</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' rx='10' fill='%23f8f5ef'/%3E%3Cpath d='M9 13h20v11a10 10 0 0 1-20 0zM29 15h3a4 4 0 0 1 0 8h-3M7 35h25' fill='none' stroke='%23b65e3c' stroke-width='3'/%3E%3C/svg%3E">
<style>
:root{--cream:#f8f5ef;--espresso:#29231f;--rust:#b65e3c;--rust-dark:#934627;--sage:#74836b;--sage-light:#e8ede3;--muted:#736c63;--line:#ded8ce;--paper:#fffdf9;--serif:Georgia,'Times New Roman',serif;--sans:'Segoe UI',Arial,sans-serif;--mono:'Courier New',monospace}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:30px}
body{margin:0;background:var(--cream);color:var(--espresso);font-family:var(--sans);font-size:15px;line-height:1.6;-webkit-font-smoothing:antialiased}
button,input,select,textarea{font:inherit}button{cursor:pointer;color:inherit;background:none;border:0}
a{color:inherit;text-decoration:none}
button:disabled{cursor:not-allowed;opacity:.55}
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid var(--rust);outline-offset:3px}
h1,h2,h3,p{margin-top:0}h1,h2{font-family:var(--serif);font-weight:400;letter-spacing:-.045em;line-height:1.09}
h3{font-weight:600}em{font-weight:400}svg{flex-shrink:0}
.wrap{width:min(1180px,calc(100% - 64px));margin-inline:auto}
[hidden]{display:none!important}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}

/* ---------- Header ---------- */
.site-header{min-height:96px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);gap:24px}
.brand{display:flex;gap:12px;align-items:center;font-size:29px;font-weight:600;letter-spacing:-1.2px;line-height:1}
.cup-logo{width:36px;height:42px;color:var(--rust)}
.brand-beans{color:var(--rust);font-weight:400}
.brand small{display:block;margin-top:9px;font-size:8px;letter-spacing:2.7px;font-weight:600;color:var(--muted)}
nav{display:flex;align-items:center;gap:32px}
nav a,.nav-api{font-size:13px;padding:9px 0}
nav a:hover,.nav-api:hover{color:var(--rust)}
.nav-api span{margin-left:5px}
.header-note{font-size:11px;color:var(--muted);display:flex;align-items:center;gap:8px}
.status-dot{display:inline-block;width:7px;height:7px;background:var(--sage);border-radius:50%;flex-shrink:0}
.status-dot.offline{background:var(--rust)}

/* ---------- Hero ---------- */
.hero{display:grid;grid-template-columns:1.16fr 1fr;align-items:center;gap:20px;padding-top:72px;padding-bottom:64px}
.eyebrow{font-size:10px;font-weight:600;letter-spacing:2px;line-height:1.5;margin-bottom:24px}
.hero .eyebrow{display:flex;align-items:center;gap:10px;color:var(--rust)}
.tiny-bean{width:11px;height:16px;border:1.5px solid var(--rust);border-radius:60%;transform:rotate(35deg);position:relative;display:inline-block}
.tiny-bean:after{content:'';position:absolute;left:4px;top:1px;height:11px;border-left:1px solid var(--rust);transform:rotate(-14deg)}
h1{font-size:clamp(44px,4.9vw,66px);margin-bottom:27px}
h1 em{color:var(--rust)}
.hero-description{max-width:415px;font-size:14px;line-height:1.9;color:var(--muted);margin-bottom:31px}
.hero-actions{display:flex;gap:27px;align-items:center}
.button{display:inline-flex;justify-content:center;align-items:center;gap:22px;min-height:49px;padding:12px 22px;border:1px solid transparent;border-radius:5px;font-size:12px;font-weight:600;line-height:1.5;transition:background .18s,transform .18s;cursor:pointer}
.button:hover{transform:translateY(-2px)}
.primary{background:var(--rust);color:#fffdf9}.primary:hover{background:var(--rust-dark)}
.secondary{background:transparent;border-color:var(--line);color:var(--espresso)}.secondary:hover{background:#eee9df}
.text-button{padding:8px 0;display:inline-flex;align-items:center;gap:12px;font-size:12px;font-weight:600}
.text-button:hover{color:var(--rust)}
.text-button.small{font-size:11px}
.hero-footnote{display:flex;align-items:center;gap:7px;font-size:10px;color:var(--muted);margin:24px 0 0}
.hero-footnote svg{width:16px;height:16px;color:var(--sage)}

/* hero art */
.hero-art{position:relative;height:437px;min-width:0}
.art-orbit{position:absolute;top:14px;left:9%;width:365px;height:365px;border:1px solid #e7dfd3;border-radius:50%}
.art-orbit:after{content:'';position:absolute;inset:25px;border:1px dashed #e7dfd3;border-radius:50%}
.art-note{position:absolute;right:0;top:4px;color:#91867a;font-family:var(--mono);font-size:8px;letter-spacing:1px;transform:rotate(7deg);line-height:1.8}
.paper{position:absolute;width:260px;height:321px;left:24%;top:39px;background:var(--paper);border:1px solid #ded6c8;box-shadow:0 18px 26px -16px #54412b27;border-radius:3px}
.paper-back{transform:rotate(-13deg);left:15%;top:58px;background:#e9e6da}
.paper-middle{transform:rotate(9deg);left:30%;top:37px;background:#f0ebdf}
.paper-label{display:block;margin:22px;font-family:var(--mono);font-size:7px;color:#a19380;letter-spacing:1.5px}
.paper-lines{margin:70px 25px;height:100px;background:repeating-linear-gradient(to bottom,transparent 0,transparent 10px,#d3ccbc 10px,#d3ccbc 12px);opacity:.5}
.paper-front{transform:rotate(-4deg);padding:23px}
.document-top{display:flex;align-items:center;gap:12px;padding-bottom:18px;border-bottom:1px solid var(--line)}
.document-top svg{width:24px;height:30px;color:var(--rust)}
.document-top span{font-family:var(--serif);font-size:15px}
.document-top small{display:block;font-family:var(--mono);font-size:6px;letter-spacing:1px;margin-top:3px;color:var(--muted)}
.scan-box{margin-top:24px;border:1px solid #b65e3c50;background:#b65e3c05;padding:15px 10px;position:relative}
.scan-box span{font-family:var(--serif);font-size:11px}
.scan-box i{position:absolute;width:7px;height:7px;border:solid var(--rust)}
.scan-box i:nth-of-type(1){top:-2px;left:-2px;border-width:2px 0 0 2px}
.scan-box i:nth-of-type(2){top:-2px;right:-2px;border-width:2px 2px 0 0}
.scan-box i:nth-of-type(3){bottom:-2px;left:-2px;border-width:0 0 2px 2px}
.scan-box i:nth-of-type(4){bottom:-2px;right:-2px;border-width:0 2px 2px 0}
.document-lines{margin-top:21px}
.document-lines i{display:block;height:4px;background:#e3ded5;margin:10px 0}
.document-lines i:nth-child(2){width:85%}.document-lines i:nth-child(3){width:60%}
.ocr-stamp{position:absolute;right:24px;bottom:45px;transform:rotate(-11deg);border:2px solid var(--sage);color:var(--sage);padding:4px 11px;font-family:var(--serif);font-size:23px;line-height:1;text-align:center;opacity:.85}
.ocr-stamp span{display:block;font-family:var(--mono);font-size:6px;letter-spacing:1px;margin-top:5px}
.paper-bottom{position:absolute;bottom:19px;left:23px;right:23px;display:flex;justify-content:space-between;color:#a09689;font-family:var(--mono);font-size:6px;letter-spacing:1.1px}
.extraction-card{position:absolute;left:9%;top:301px;display:flex;align-items:center;gap:12px;min-width:320px;padding:17px;background:var(--paper);border:1px solid #ddd5c6;border-radius:7px;box-shadow:0 12px 36px -18px #55463155;transform:rotate(2deg)}
.extract-icon{background:var(--sage-light);color:#59674f;font-family:var(--serif);font-size:21px;display:grid;place-items:center;width:41px;height:41px;border-radius:5px}
.extraction-label{color:var(--sage);font-size:7px;letter-spacing:1.4px;font-weight:600}
.extraction-card p{font-family:var(--serif);font-size:12px;margin:3px 0 0}
.extract-check{margin-left:auto;color:var(--sage);border:1px solid #c8d1be;border-radius:50%;width:18px;height:18px;display:grid;place-items:center;font-size:10px}
.art-caption{position:absolute;bottom:14px;left:27%;font-family:var(--mono);font-size:7px;color:var(--muted);letter-spacing:1.4px}
.art-caption span{margin-left:14px;color:var(--rust);font-size:19px}

/* ---------- Metrics ---------- */
.metrics{border-block:1px solid var(--line);display:grid;grid-template-columns:repeat(4,1fr);padding-block:30px}
.metrics>div{padding-inline:33px;border-left:1px solid var(--line)}
.metrics>div:first-child{border:0;padding-left:0}
.metrics strong{display:block;font-family:var(--serif);font-size:25px;font-weight:400;letter-spacing:-.7px;line-height:1.4}
.metrics span{font-size:10px;color:var(--muted)}

/* ---------- Tools ---------- */
.tool-section{padding-top:72px;padding-bottom:70px}
.section-heading{display:flex;justify-content:space-between;align-items:end;gap:25px;margin-bottom:33px}
.section-heading .eyebrow{color:var(--rust);margin-bottom:17px}
.section-heading h2{font-size:41px;margin-bottom:0}
.section-heading>p{font-size:12px;color:var(--muted);line-height:1.9;margin:0 0 5px}
.privacy-notice{display:flex;align-items:center;gap:13px;border:1px solid #d4dacd;background:#eef0e9;padding:14px 17px;border-radius:5px;margin-bottom:29px}
.privacy-notice svg{width:22px;height:22px;color:#607054}
.privacy-notice p{font-size:11px;line-height:1.8;color:#536049;margin:0}
.privacy-notice strong{font-weight:600;margin-right:5px}
.privacy-download{display:inline-flex;align-items:center;gap:10px;font-size:11px;font-weight:600;color:#4d6041;text-decoration:underline;text-underline-offset:3px;white-space:nowrap}
.privacy-download:hover{color:var(--rust)}
.tool-controls{display:flex;justify-content:space-between;gap:20px;align-items:center;margin-bottom:27px}
.filters{display:flex;gap:4px;flex-wrap:wrap}
.filter{border:1px solid transparent;border-radius:5px;font-size:11px;padding:9px 12px;min-height:37px;color:var(--muted)}
.filter.active{background:var(--espresso);color:var(--cream)}
.filter:not(.active):hover{background:#eee8dd;color:var(--espresso)}
.filter span{font-size:9px;opacity:.6;margin-left:6px}
.search-box{display:flex;gap:9px;align-items:center;border:1px solid var(--line);border-radius:5px;padding:9px 12px;background:var(--paper)}
.search-box svg{width:15px;height:15px;color:var(--muted)}
.search-box input{border:0;outline:0;background:transparent;min-width:0;width:150px;font-size:11px;color:var(--espresso)}
.tool-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.tool-card{display:flex;flex-direction:column;position:relative;background:var(--paper);border:1px solid var(--line);border-radius:7px;padding:24px;min-height:210px;transition:border-color .18s,box-shadow .18s,transform .18s}
.tool-card:hover{border-color:#bfb2a2;box-shadow:0 7px 20px -14px #5c473c70;transform:translateY(-3px)}
.card-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}
.tool-icon{display:grid;place-items:center;width:39px;height:39px;color:var(--rust);background:#f6ebe4;border-radius:7px;font-size:19px}
.category-ocr .tool-icon{background:var(--sage-light);color:#66785a}
.category-organize .tool-icon{background:#eeebe4;color:#82725d}
.category-optimize .tool-icon{background:#f3e8e8;color:#8d5b5b}
.card-tag{font-family:var(--mono);color:#9a8e7f;font-size:8px;letter-spacing:1px}
.tool-card h3{font-size:15px;letter-spacing:-.2px;margin:0 0 8px}
.tool-card p{font-size:11px;line-height:1.8;color:var(--muted);margin:0 0 23px}
.tool-card button{border-top:1px solid #eee8de;width:100%;text-align:left;display:flex;justify-content:space-between;align-items:center;padding:13px 0 0;margin-top:auto;color:var(--rust);font-size:10px;font-weight:600}
.tool-card button:after{content:'';position:absolute;inset:0;border-radius:7px}
.tool-card button span{font-size:17px;line-height:1}
.tools-bottom{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-top:23px;color:var(--muted)}
.tools-bottom p{display:flex;align-items:center;gap:8px;font-size:10px;margin:0}
.empty-tools{text-align:center;padding:45px 20px;border:1px dashed var(--line);border-radius:7px}
.empty-tools h3{font-family:var(--serif);font-size:25px;font-weight:400}
.empty-tools p{font-size:13px;color:var(--muted)}

/* ---------- How ---------- */
.how-section{border-block:1px solid var(--line);background:#f1ede5;padding-block:64px}
.how-section .section-heading h2{font-size:36px}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:52px;margin-top:44px}
.step-number{font-family:var(--serif);font-size:34px;color:#b0a38f;font-style:italic;line-height:1}
.steps h3{font-size:14px;margin:19px 0 10px}
.steps p{font-size:11px;color:var(--muted);line-height:1.9;max-width:285px;margin:0}

/* ---------- CTA ---------- */
.bottom-cta{display:grid;grid-template-columns:1.1fr 1fr;gap:65px;margin-top:72px;margin-bottom:55px;padding:49px 55px;background:var(--espresso);color:var(--cream);border-radius:9px}
.bottom-cta .eyebrow{color:#c8b19b;font-size:8px;margin-bottom:21px}
.bottom-cta h2{font-size:42px;margin-bottom:20px}
.bottom-cta h2 em{color:#d99b79}
.bottom-cta p{max-width:370px;font-size:12px;line-height:1.9;color:#c1b7ab;margin-bottom:25px}
.light{background:var(--cream);color:var(--espresso)}.light:hover{background:#e8dfd1}
.api-teaser{border-left:1px solid #50473e;padding-left:43px;align-self:center}
.code-eyebrow{display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:8px;letter-spacing:1px;color:#b8ada0}
.api-teaser pre{font-size:11px;line-height:1.9;font-family:var(--mono);margin-block:21px;white-space:pre-wrap}
.code-muted{color:#a39787;font-size:9px}
.code-orange{color:#dba383}.code-sage{color:#b1c2a1}.code-cream{color:#e0d8c8}
.api-teaser .text-button{color:#e0d8c8;font-size:10px}
.api-teaser .text-button:hover{color:#d99b79}

/* ---------- Footer ---------- */
.site-footer{display:flex;justify-content:space-between;gap:20px;align-items:center;border-top:1px solid var(--line);padding-block:25px 35px}
.footer-brand{font-size:20px;font-weight:600;letter-spacing:-.8px}
.footer-brand>span:first-of-type{font-weight:400;color:var(--rust)}
.footer-tagline{display:inline-block;font-size:10px;font-weight:400;color:var(--muted);margin-left:23px}
.site-footer>div{display:flex;align-items:center;gap:26px;color:var(--muted);font-size:10px}

/* ---------- Dialogs ---------- */
dialog{color:var(--espresso);border:1px solid var(--line);background:var(--cream);border-radius:12px;width:min(700px,calc(100% - 32px));max-height:calc(100dvh - 48px);padding:30px 34px;box-shadow:0 28px 100px #21180e40;overscroll-behavior:contain}
dialog::backdrop{background:#211b17a8;backdrop-filter:blur(4px)}
body:has(dialog[open]){overflow:hidden}
.dialog-header{display:flex;align-items:start;justify-content:space-between;gap:15px;margin-bottom:12px}
.dialog-header .eyebrow{font-size:9px;color:var(--rust);margin-bottom:9px}
.dialog-header h2{font-size:32px;margin:0}
.icon-button{min-width:38px;height:38px;display:grid;place-items:center;background:transparent;border:1px solid var(--line);border-radius:50%;font-size:25px;line-height:1}
.icon-button:hover{background:#ebe4d9}
.workspace-description{font-size:13px;color:var(--muted);margin-bottom:14px}
.workspace-privacy{font-size:10px;line-height:1.8;background:var(--sage-light);color:#54624a;border-radius:4px;padding:10px 13px;margin-bottom:20px}
.drop-zone{display:flex;align-items:center;flex-direction:column;gap:5px;text-align:center;padding:26px 16px;border:1.5px dashed #c9bbab;border-radius:7px;background:var(--paper);cursor:pointer;transition:background .15s,border-color .15s}
.drop-zone:hover,.drop-zone.dragging{background:#f6ebe4;border-color:var(--rust)}
.drop-zone svg{width:30px;height:30px;color:var(--rust);margin-bottom:6px}
.drop-zone strong{font-size:14px;font-weight:500}
.drop-zone span{font-size:12px;color:var(--muted)}
.drop-zone b{font-weight:500;color:var(--rust);text-decoration:underline;text-underline-offset:3px}
.drop-zone small{font-size:10px;color:var(--muted);margin-top:4px}
.file-input{position:absolute;opacity:0;width:1px;height:1px}
.upload-limits{font-size:10px;text-align:center;color:var(--muted);margin:9px 0 14px}
.file-list{list-style:none;padding:0;margin:0}
.file-row{display:flex;gap:10px;align-items:center;padding:11px 0;border-bottom:1px solid var(--line)}
.file-order{font-family:var(--mono);font-size:10px;color:var(--rust);min-width:20px}
.file-info{flex:1;min-width:0}
.file-name{display:block;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.file-size{font-size:10px;color:var(--muted)}
.file-row-controls{display:flex;gap:4px}
.file-row-controls button{width:30px;height:30px;border:1px solid var(--line);background:var(--paper);border-radius:4px;font-size:13px}
.file-row-controls button:hover:not(:disabled){background:#eee5d9}
.file-total{font-size:10px;color:var(--muted);margin:9px 0 16px}
.options-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:17px}
.options-grid label{display:flex;flex-direction:column;gap:6px;font-size:12px}
.options-grid select,.options-grid input{width:100%;min-height:42px;padding:9px 10px;background:var(--paper);border:1px solid #cec5b8;border-radius:5px;color:var(--espresso)}
.options-grid .option-wide{grid-column:1/-1}
.option-help{font-size:10px;color:var(--muted);line-height:1.6}
.tool-caveat{font-size:10px;line-height:1.8;color:var(--muted);margin:18px 0 0}
.workspace-actions{display:flex;justify-content:flex-end;gap:12px;margin-top:22px}
.message{padding:12px 14px;margin-top:16px;border-radius:5px;font-size:12px}
.error{background:#f9e8e2;border:1px solid #dfb4a4;color:#8d391f}
.processing{display:flex;align-items:center;gap:14px;padding:20px 16px;background:#efe9df;border-radius:6px;margin-top:18px}
.processing strong{font-size:13px}
.processing p{font-size:11px;color:var(--muted);margin:3px 0 0}
.spinner{display:inline-block;width:25px;height:25px;border:2px solid #d0c0af;border-top-color:var(--rust);border-radius:50%;animation:spin 1s linear infinite;flex-shrink:0}
@keyframes spin{to{transform:rotate(360deg)}}
.result-panel{margin-top:20px;padding:20px;background:var(--paper);border:1px solid #d2d9c8;border-radius:7px}
.result-panel h3{font-family:var(--serif);font-size:25px;font-weight:400;margin:0 0 7px}
.result-panel p{font-size:12px;color:var(--muted)}
.result-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:17px}
.result-actions .button{min-height:42px;font-size:11px;padding:10px 16px;gap:12px}
#text-preview-label{display:block;font-size:12px;margin-top:14px}
#text-preview{display:block;width:100%;margin-top:8px;resize:vertical;background:var(--cream);border:1px solid var(--line);border-radius:4px;padding:12px;font-family:var(--mono);font-size:11px;line-height:1.7}
.diagnosis-list{display:grid;grid-template-columns:minmax(110px,1fr) 2fr;font-size:12px;margin:15px 0}
.diagnosis-list dt,.diagnosis-list dd{margin:0;padding:8px 0;border-bottom:1px solid var(--line);overflow-wrap:anywhere}
.diagnosis-list dt{color:var(--muted);padding-right:10px}
.diagnosis-details{font-family:var(--mono);font-size:11px;line-height:1.7;white-space:pre-wrap;overflow-wrap:anywhere;background:var(--cream);padding:12px;max-height:270px;overflow:auto;border-radius:4px}

/* API dialog */
.api-dialog{width:min(810px,calc(100% - 32px))}
.api-dialog>p,.api-dialog section p{font-size:12px;color:var(--muted);line-height:1.9}
.api-dialog h3{font-size:15px;margin:25px 0 12px}
.api-links{display:flex;gap:10px;flex-wrap:wrap;margin-block:20px}
.api-links .button{font-size:11px}
.api-dialog pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:18px;background:var(--espresso);color:var(--cream);border-radius:5px;font-size:11px;line-height:1.8;overflow:auto;font-family:var(--mono)}
.api-dialog .api-note{font-size:10px;color:var(--muted)}
.code-block{position:relative;margin-block:16px}
.code-block pre{padding-top:47px}
.code-copy{position:absolute;top:9px;right:10px;font-size:10px;color:#e7ded1;border:1px solid #62574a;border-radius:4px;background:#3a322b;padding:4px 9px;cursor:pointer}
.code-copy:hover{background:#504136}
.api-table-wrap{overflow:auto}
.api-table{width:100%;border-collapse:collapse;text-align:left;font-size:11px;min-width:460px}
.api-table th{font-weight:600;background:#eee7dc}
.api-table td,.api-table th{padding:11px;border-bottom:1px solid var(--line);vertical-align:top}
.api-table td:first-child{font-family:var(--mono);color:var(--rust);white-space:nowrap}
.api-table td:last-child{font-family:var(--mono);font-size:10px;overflow-wrap:anywhere}

@media(max-width:1050px){
  .hero{grid-template-columns:1.15fr 1fr;padding-top:56px;padding-bottom:52px}
  h1{font-size:clamp(39px,5.2vw,54px)}
  .hero-art{transform:scale(.87);transform-origin:center right;margin-left:-30px}
  .metrics>div{padding-inline:20px}
  .bottom-cta{gap:35px;padding:40px}
  .api-teaser{padding-left:30px}
}
@media(max-width:820px){
  .wrap{width:calc(100% - 40px)}
  .header-note{display:none}
  .hero{grid-template-columns:1fr;gap:25px}
  .hero-art{width:440px;max-width:100%;justify-self:center;transform:scale(.93);transform-origin:center;height:400px;margin:0}
  .metrics{grid-template-columns:repeat(2,1fr)}
  .metrics>div{padding:19px 15px;border-left:0}
  .metrics>div:nth-child(even){border-left:1px solid var(--line)}
  .metrics>div:nth-child(n+3){border-top:1px solid var(--line)}
  .section-heading{flex-direction:column;align-items:start;gap:16px}
  .section-heading h2{font-size:34px}
  .tool-controls{flex-direction:column;align-items:stretch;gap:13px}
  .search-box input{width:100%}
  .tool-grid{grid-template-columns:1fr 1fr}
  .steps{grid-template-columns:1fr;gap:24px}
  .bottom-cta{grid-template-columns:1fr;padding:32px}
  .bottom-cta h2{font-size:34px}
  .api-teaser{border-left:0;border-top:1px solid #50473e;padding:25px 0 0}
  .site-footer{align-items:start;flex-direction:column}
  dialog{padding:22px 18px}
  .options-grid{grid-template-columns:1fr}
}
@media(max-width:480px){.tool-grid{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*:before,*:after{animation:none!important;transition:none!important}}
</style>
</head>
<body>

<header class="site-header wrap">
  <a class="brand" href="#inicio" aria-label="OCR Beans, início"><svg class="cup-logo" viewBox="0 0 44 44" fill="none" aria-hidden="true"><path d="M8 15h24v12c0 7-5 11-12 11S8 34 8 27V15Z" stroke="currentColor" stroke-width="2.2"/><path d="M32 18h3a5 5 0 0 1 0 10h-3M5 41h31M15 10c-4-4 4-5 0-9M23 10c-4-4 4-5 0-9" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg><span>ocr<span class="brand-beans">beans</span><small>BY BEANSTECH</small></span></a>
  <nav aria-label="Navegação principal">
    <a href="#ferramentas">Ferramentas</a>
    <a href="#como-funciona">Como funciona</a>
    <button class="nav-api" data-api>API REST <span aria-hidden="true">↗</span></button>
  </nav>
  <span class="header-note" role="status"><span class="status-dot offline" id="mode-dot"></span><span id="mode-badge">Verificando…</span></span>
</header>

<main id="inicio">
  <section class="hero wrap">
    <div class="hero-copy">
      <p class="eyebrow"><span class="tiny-bean" aria-hidden="true"></span> SEU PDF. DO SEU JEITO.</p>
      <h1>OCR e ferramentas<br>de PDF, <em>sem</em><br><em>complicar.</em></h1>
      <p class="hero-description">Transforme documentos em possibilidades. Extraia textos de PDFs judiciais e imagens, organize páginas e converta arquivos — com a simplicidade de um bom café.</p>
      <div class="hero-actions">
        <a class="button primary" href="#ferramentas">Explorar ferramentas <span aria-hidden="true">↘</span></a>
        <button class="text-button" data-api>Conhecer a API <span aria-hidden="true">↗</span></button>
      </div>
      <p class="hero-footnote"><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="m10 2 6 3v5c0 4-6 7-6 7s-6-3-6-7V5l6-3Z" stroke="currentColor" stroke-width="1.4"/><path d="m7 9 2 2 4-4" stroke="currentColor" stroke-width="1.4"/></svg> Processamento 100% local. Nenhum arquivo sai da sua máquina.</p>
    </div>
    <div class="hero-art" aria-hidden="true">
      <div class="art-orbit"></div>
      <span class="art-note">MENOS TRABALHO MANUAL.<br>MAIS TEMPO PARA UM CAFÉ.</span>
      <div class="paper paper-back"><div class="paper-lines"></div></div>
      <div class="paper paper-middle"><span class="paper-label">DOCUMENTO ORIGINAL</span><div class="paper-lines"></div></div>
      <div class="paper paper-front">
        <div class="document-top"><svg viewBox="0 0 36 40" fill="none"><path d="M5 2h18l9 9v27H5V2Z M23 2v10h9" stroke="currentColor" stroke-width="1.5"/><path d="M11 21h15M11 27h15M11 32h9" stroke="currentColor" stroke-width="1.5"/></svg><span>petição.pdf<small>PRONTO PARA TRANSFORMAR</small></span></div>
        <div class="scan-box"><span>Deixe a burocracia no papel.</span><i></i><i></i><i></i><i></i></div>
        <div class="document-lines"><i></i><i></i><i></i></div>
        <div class="ocr-stamp">OCR<span>RECONHECIDO</span></div>
        <div class="paper-bottom"><span>01 / 03</span><span>OCR BEANS</span></div>
      </div>
      <div class="extraction-card"><span class="extract-icon">Aa</span><div><span class="extraction-label">TEXTO EXTRAÍDO</span><p>“Deixe a burocracia no papel.”</p></div><span class="extract-check">✓</span></div>
      <span class="art-caption">DO PAPEL ÀS POSSIBILIDADES <span>↗</span></span>
    </div>
  </section>

  <section class="metrics wrap" aria-label="Recursos do OCR Beans">
    <div><strong>12</strong><span>ferramentas, um só lugar</span></div>
    <div><strong>100% local</strong><span>privacidade por desenho</span></div>
    <div><strong>OCR automático</strong><span>fontes corrompidas detectadas</span></div>
    <div><strong>REST + MCP</strong><span>integre ao seu fluxo ou agente</span></div>
  </section>

  <section class="tool-section wrap" id="ferramentas">
    <div class="section-heading">
      <div><p class="eyebrow">A CAIXA DE FERRAMENTAS</p><h2>Um bom resultado.<br>Sem passos a mais.</h2></div>
      <p>Do documento escaneado ao arquivo organizado.<br>Escolha o que você precisa fazer.</p>
    </div>
    <div class="privacy-notice">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="2" stroke="currentColor" stroke-width="1.6"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3" stroke="currentColor" stroke-width="1.6"/></svg>
      <p><strong>Transparência em primeiro lugar.</strong> Os arquivos são processados nesta máquina, em diretório temporário que é descartado ao fim. Nada é enviado a serviços externos ou guardado para outra sessão.</p>
      <a class="privacy-download" href="/docs" target="_blank" rel="noopener">Documentação da API <span aria-hidden="true">↗</span></a>
    </div>
    <div class="tool-controls">
      <div class="filters" role="group" aria-label="Filtrar ferramentas por categoria">
        <button class="filter active" data-category="all">Todas <span>12</span></button>
        <button class="filter" data-category="ocr">OCR e texto</button>
        <button class="filter" data-category="convert">Converter</button>
        <button class="filter" data-category="organize">Organizar</button>
        <button class="filter" data-category="optimize">Otimizar</button>
      </div>
      <label class="search-box"><svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" stroke="currentColor" stroke-width="1.5"/><path d="m13 13 4 4" stroke="currentColor" stroke-width="1.5"/></svg><span class="sr-only">Buscar ferramentas</span><input id="tool-search" type="search" placeholder="Buscar ferramenta…" autocomplete="off"></label>
    </div>
    <div class="tool-grid" id="tool-grid"></div>
    <div id="empty-tools" class="empty-tools" hidden><h3>Nenhuma ferramenta por aqui.</h3><p>Tente buscar “PDF”, “imagem” ou escolher outra categoria.</p><button class="button secondary" id="clear-search">Limpar busca e filtros</button></div>
    <div class="tools-bottom"><p><span class="status-dot" id="service-dot"></span><span id="service-status" role="status">Verificando ambiente de processamento…</span></p><button class="text-button small" id="retry-status">Verificar novamente <span aria-hidden="true">↻</span></button></div>
  </section>

  <section class="how-section" id="como-funciona">
    <div class="wrap">
      <div class="section-heading">
        <div><p class="eyebrow">SIMPLES, DO INÍCIO AO FIM</p><h2>Três passos.<br>O resto é com a gente.</h2></div>
        <p>Sem cadastro, sem labirintos.<br>Um fluxo que respeita o seu tempo.</p>
      </div>
      <div class="steps">
        <article><span class="step-number">01</span><h3>Escolha a ferramenta</h3><p>Encontre a transformação que seu documento precisa. Cada ferramenta tem um propósito claro.</p></article>
        <article><span class="step-number">02</span><h3>Adicione seus arquivos</h3><p>Arraste os arquivos, ajuste as opções e organize a ordem. Você tem o controle antes de começar.</p></article>
        <article><span class="step-number">03</span><h3>Baixe o resultado</h3><p>Receba o arquivo pronto ou copie o texto extraído. Sem histórico salvo, sem etapas desnecessárias.</p></article>
      </div>
    </div>
  </section>

  <section class="bottom-cta wrap">
    <div>
      <p class="eyebrow">UM CAFÉ. UM PDF. TUDO RESOLVIDO.</p>
      <h2>Menos burocracia.<br><em>Mais possibilidades.</em></h2>
      <p>Use as ferramentas ou leve o OCR Beans para o seu fluxo de trabalho com a API REST e o servidor MCP.</p>
      <a class="button light" href="#ferramentas">Começar com um arquivo <span aria-hidden="true">↗</span></a>
    </div>
    <div class="api-teaser">
      <span class="code-eyebrow"><span class="status-dot"></span> FEITO PARA SE INTEGRAR</span>
      <pre><code><span class="code-muted">// Seu fluxo, com menos trabalho manual</span>
<span class="code-orange">POST</span> /api/ocr/pdf

-F <span class="code-sage">file</span>=@peticao.pdf
-F <span class="code-sage">lang</span>=<span class="code-cream">por</span> -F <span class="code-sage">dpi</span>=<span class="code-cream">300</span></code></pre>
      <button class="text-button" data-api>Explorar documentação <span aria-hidden="true">↗</span></button>
    </div>
  </section>
</main>

<footer class="site-footer wrap">
  <a class="footer-brand" href="#inicio">ocr<span>beans</span><span class="footer-tagline">Documentos leves. Rotina também.</span></a>
  <div><span>© 2026 BeansTech</span><button class="text-button small" data-api>API e documentação <span aria-hidden="true">↗</span></button></div>
</footer>

<!-- ===== Dialog: ferramenta ===== -->
<dialog id="tool-dialog" aria-labelledby="workspace-title">
  <div class="dialog-header">
    <div><p class="eyebrow" id="workspace-category">FERRAMENTA</p><h2 id="workspace-title"></h2></div>
    <button class="icon-button dialog-close" aria-label="Fechar ferramenta">×</button>
  </div>
  <p class="workspace-description" id="workspace-description"></p>
  <p class="workspace-privacy">Os arquivos são processados nesta máquina, em diretório temporário descartado após a resposta. Nada é enviado a serviços externos.</p>
  <form id="tool-form" novalidate>
    <div id="upload-workspace">
      <label class="drop-zone" id="drop-zone" for="file-input">
        <svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><path d="M16 22V5m-6 6 6-6 6 6M5 21v7h22v-7" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <strong>Arraste seus arquivos aqui</strong>
        <span>ou <b>selecione no seu dispositivo</b></span>
        <small id="upload-hint"></small>
      </label>
      <input id="file-input" class="file-input" type="file">
      <p class="upload-limits">Até 200 MB por arquivo · máximo de 50 arquivos</p>
      <ol id="file-list" class="file-list" aria-label="Arquivos selecionados"></ol>
      <p id="file-total" class="file-total"></p>
      <div class="options-grid" id="tool-options"></div>
      <p class="tool-caveat" id="tool-caveat"></p>
    </div>
    <div class="message error" id="tool-error" role="alert" hidden></div>
    <div class="processing" id="processing" role="status" aria-live="polite" hidden>
      <span class="spinner" aria-hidden="true"></span>
      <div><strong>Processando seus arquivos…</strong><p>O tempo depende do tamanho e do conteúdo. PDFs grandes com OCR podem levar alguns minutos.</p></div>
    </div>
    <div class="result-panel" id="result-panel" hidden>
      <h3>Seu resultado está pronto.</h3>
      <p id="result-summary" role="status"></p>
      <div id="diagnosis-result"></div>
      <label id="text-preview-label" hidden>Texto extraído<textarea id="text-preview" readonly rows="8" spellcheck="false"></textarea></label>
      <div class="result-actions">
        <a class="button primary" id="download-result" download hidden>Baixar novamente <span aria-hidden="true">↓</span></a>
        <button class="button secondary" id="copy-text" type="button" hidden>Copiar texto</button>
        <button class="text-button" id="new-process" type="button">Processar outro arquivo <span aria-hidden="true">↻</span></button>
      </div>
      <p id="copy-feedback" role="status" class="tool-caveat"></p>
    </div>
    <div class="workspace-actions">
      <button class="button secondary" id="cancel-process" type="button" hidden>Cancelar</button>
      <button class="button primary" id="submit-tool" type="submit">Processar arquivo <span aria-hidden="true">↗</span></button>
    </div>
  </form>
</dialog>

<!-- ===== Dialog: API ===== -->
<dialog class="api-dialog" id="api-dialog" aria-labelledby="api-title">
  <div class="dialog-header">
    <div><p class="eyebrow">PARA QUEM CONSTRÓI</p><h2 id="api-title">Seu fluxo. Nossa API.</h2></div>
    <button class="icon-button dialog-close" aria-label="Fechar documentação">×</button>
  </div>
  <p>As mesmas 12 ferramentas, por HTTP. Envie arquivos em <code>multipart/form-data</code> e receba o resultado diretamente. Documentação interativa (Swagger) em <a href="/docs" target="_blank" rel="noopener" style="text-decoration:underline">/docs</a>.</p>
  <div class="api-links">
    <a class="button secondary" href="/docs" target="_blank" rel="noopener">Swagger interativo ↗</a>
    <a class="button secondary" href="/api/tools" target="_blank" rel="noopener">Catálogo de endpoints ↗</a>
  </div>
  <h3>1. Consulte o ambiente</h3>
  <pre><code>GET /api/health

{
  "status": "ok",
  "versao": "2.1.0",
  "tesseract": true,
  "idiomas": ["eng", "osd", "por"]
}</code></pre>
  <h3>2. Envie os arquivos e as opções</h3>
  <p>Campo <code>file</code> para um arquivo, <code>files</code> repetido para vários. Opções como campos do formulário.</p>
  <div class="code-block"><button class="code-copy" type="button" data-copy="curl -X POST http://127.0.0.1:8080/api/ocr/pdf -F &quot;file=@documento.pdf&quot; -F &quot;lang=por&quot; --output texto.txt">Copiar exemplo</button><pre><code>curl -X POST http://127.0.0.1:8080/api/ocr/pdf \
  -F "file=@documento.pdf" \
  -F "lang=por" \
  --output texto-extraido.txt</code></pre></div>
  <div class="code-block"><button class="code-copy" type="button" data-copy="curl -X POST http://127.0.0.1:8080/api/convert/merge -F &quot;files=@primeiro.pdf&quot; -F &quot;files=@segundo.pdf&quot; --output unidos.pdf">Copiar exemplo</button><pre><code>curl -X POST http://127.0.0.1:8080/api/convert/merge \
  -F "files=@primeiro.pdf" \
  -F "files=@segundo.pdf" \
  --output documentos-unidos.pdf</code></pre></div>
  <h3>Ferramentas e opções</h3>
  <div class="api-table-wrap"><table class="api-table"><thead><tr><th>Rota</th><th>Campos do formulário</th></tr></thead><tbody id="api-tools-table"></tbody></table></div>
  <h3>3. Receba o resultado</h3>
  <p>Conversões retornam arquivos com nome em <code>Content-Disposition</code> (o download é automático na interface). OCR de imagem e diagnóstico retornam JSON. Erros retornam JSON com <code>detail</code> e código HTTP (413 tamanho, 422 inválido, 500 interno).</p>
  <p class="api-note">Limites: 200 MB por arquivo, 50 arquivos por requisição, 500 páginas por range. Sem autenticação embutida — para expor publicamente, coloque um proxy com auth na frente.</p>
  <p id="api-copy-feedback" role="status" class="tool-caveat"></p>
</dialog>

<script>
"use strict";

/* ============ Catálogo de ferramentas ============ */
const ICONS = {
  pdf:'📄', img:'🖼️', diag:'🩺', conv:'🗂️', frames:'🎞️', word:'📝',
  box:'🗃️', merge:'🔗', split:'✂️', press:'🗜️', spin:'🔄', drop:'💧'
};
const CATS = { ocr:'OCR E TEXTO', convert:'CONVERTER', organize:'ORGANIZAR', optimize:'OTIMIZAR' };

const TOOLS = [
 { id:'pdf-ocr', cat:'ocr', icon:ICONS.pdf, tag:'PDF · TXT',
   titulo:'PDF → Texto (OCR)',
   desc:'Extrai o texto do PDF. Detecta fontes corrompidas de tribunais e aplica OCR automático por página.',
   endpoint:'/api/ocr/pdf', accept:'.pdf', multiple:false,
   options:[
     {nome:'lang', label:'Idioma do OCR', tipo:'select', valores:['por','por+eng','eng'], padrao:'por'},
     {nome:'dpi', label:'Resolução OCR (DPI)', tipo:'select', valores:['200','300','400'], padrao:'300'},
   ],
   caveat:'Páginas com texto nativo são extraídas sem OCR (instantâneo). OCR só entra em páginas com fonte corrompida ou imagem.' },
 { id:'image-ocr', cat:'ocr', icon:ICONS.img, tag:'IMAGEM · TEXTO',
   titulo:'Imagem → Texto (OCR)',
   desc:'Lê texto de PNG, JPG, TIFF, WEBP e BMP. O texto aparece na tela, pronto para copiar.',
   endpoint:'/api/ocr/image', accept:'.png,.jpg,.jpeg,.tif,.tiff,.bmp,.webp', multiple:false,
   options:[
     {nome:'lang', label:'Idioma do OCR', tipo:'select', valores:['por','por+eng','eng'], padrao:'por'},
     {nome:'psm', label:'Segmentação', tipo:'select', valores:['6 (bloco uniforme)','3 (automática)','11 (texto esparso)'], padrao:'6 (bloco uniforme)'},
   ],
   result:'json' },
 { id:'diagnose', cat:'ocr', icon:ICONS.diag, tag:'PDF · DIAGNÓSTICO',
   titulo:'Diagnosticar PDF',
   desc:'Detecta em menos de um segundo se o PDF tem fonte corrompida e vai precisar de OCR.',
   endpoint:'/api/check', accept:'.pdf', multiple:false, options:[],
   result:'diagnosis',
   caveat:'Não faz OCR — apenas analisa a primeira página. Ideal para verificar um lote antes de processar.' },
 { id:'images-pdf', cat:'convert', icon:ICONS.conv, tag:'IMAGEM · PDF',
   titulo:'Imagens → PDF',
   desc:'Junta várias imagens em um único PDF, uma página por imagem, na ordem que você definir.',
   endpoint:'/api/convert/images-to-pdf', accept:'.png,.jpg,.jpeg,.tif,.tiff,.bmp,.webp', multiple:true, options:[],
   caveat:'A ordem dos arquivos na lista define a ordem das páginas. Use as setas para reorganizar.' },
 { id:'pdf-images', cat:'convert', icon:ICONS.frames, tag:'PDF · IMAGENS',
   titulo:'PDF → Imagens',
   desc:'Renderiza as páginas do PDF como imagens PNG ou JPG e entrega tudo em um arquivo zip.',
   endpoint:'/api/convert/pdf-to-images', accept:'.pdf', multiple:false,
   options:[
     {nome:'fmt', label:'Formato', tipo:'select', valores:['png','jpg'], padrao:'png'},
     {nome:'dpi', label:'Resolução (DPI)', tipo:'select', valores:['150','200','300'], padrao:'200'},
     {nome:'pages', label:'Páginas (ex: 1-3,7 — vazio = todas)', tipo:'text', padrao:'', wide:true},
   ] },
 { id:'pdf-word', cat:'convert', icon:ICONS.word, tag:'PDF · DOCX',
   titulo:'PDF → Word',
   desc:'Converte o PDF em documento Word editável, preservando a formatação do texto.',
   endpoint:'/api/convert/pdf-to-docx', accept:'.pdf', multiple:false,
   options:[{nome:'pages', label:'Páginas (ex: 1-5 — vazio = todas)', tipo:'text', padrao:'', wide:true}],
   caveat:'Funciona melhor em PDFs com texto nativo. Em scans, o DOCX conterá imagens das páginas.' },
 { id:'extract-images', cat:'convert', icon:ICONS.box, tag:'PDF · IMAGENS',
   titulo:'Extrair imagens do PDF',
   desc:'Baixa todas as imagens embutidas no documento, na resolução original, em um zip.',
   endpoint:'/api/convert/extract-images', accept:'.pdf', multiple:false, options:[],
   result:'maybe-json' },
 { id:'merge', cat:'organize', icon:ICONS.merge, tag:'PDF · JUNTAR',
   titulo:'Juntar PDFs',
   desc:'Combina dois ou mais PDFs em um só, exatamente na ordem da lista.',
   endpoint:'/api/convert/merge', accept:'.pdf', multiple:true, min:2, options:[],
   caveat:'A ordem dos arquivos na lista define a ordem das páginas no resultado.' },
 { id:'split', cat:'organize', icon:ICONS.split, tag:'PDF · DIVIDIR',
   titulo:'Dividir / Extrair páginas',
   desc:'Extrai páginas específicas do PDF para um novo documento (ex.: 1-3,7).',
   endpoint:'/api/convert/split', accept:'.pdf', multiple:false,
   options:[{nome:'pages', label:'Páginas (ex: 1-3,7)', tipo:'text', padrao:'1', required:true, wide:true}] },
 { id:'rotate', cat:'organize', icon:ICONS.spin, tag:'PDF · GIRAR',
   titulo:'Girar PDF',
   desc:'Rotaciona páginas em 90, 180 ou 270 graus — todas ou só as que você indicar.',
   endpoint:'/api/convert/rotate', accept:'.pdf', multiple:false,
   options:[
     {nome:'graus', label:'Rotação', tipo:'select', valores:['90','180','270'], padrao:'90'},
     {nome:'pages', label:'Páginas (vazio = todas)', tipo:'text', padrao:''},
   ] },
 { id:'compress', cat:'optimize', icon:ICONS.press, tag:'PDF · COMPRIMIR',
   titulo:'Comprimir PDF',
   desc:'Reduz o tamanho do arquivo recompactando as imagens embutidas. Ideal para envio por e-mail.',
   endpoint:'/api/convert/compress', accept:'.pdf', multiple:false,
   options:[{nome:'qualidade', label:'Qualidade das imagens', tipo:'select',
             valores:['40 (máxima compressão)','60 (equilibrada)','75 (alta qualidade)'], padrao:'60 (equilibrada)'}],
   caveat:'PDFs só de texto comprimem pouco — o ganho vem das imagens. O cabeçalho informa a redução obtida.' },
 { id:'watermark', cat:'optimize', icon:ICONS.drop, tag:'PDF · MARCA',
   titulo:'Marca d’água',
   desc:'Aplica um texto diagonal em todas as páginas — CONFIDENCIAL, CÓPIA, URGENTE…',
   endpoint:'/api/convert/watermark', accept:'.pdf', multiple:false,
   options:[{nome:'texto', label:'Texto da marca d’água', tipo:'text', padrao:'CONFIDENCIAL', required:true, wide:true}] },
];

/* ============ Estado ============ */
let toolAtual = null;
let arquivos = [];
let resultadoBlob = null;
let resultadoUrl = null;

const $ = id => document.getElementById(id);
const toolDialog = $('tool-dialog'), apiDialog = $('api-dialog');
const fileInput = $('file-input'), dropZone = $('drop-zone');

/* ============ Grid + filtros + busca ============ */
// Normaliza para a busca: sem acentos, sem plural simples, "imagem"~"imagens" (m/n final)
function singularizar(s) {
  return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/\b(\w{4,})s\b/g, '$1')
    .replace(/m\b/g, 'n');
}
function renderGrid() {
  const grid = $('tool-grid');
  grid.innerHTML = '';
  TOOLS.forEach(t => {
    const card = document.createElement('div');
    card.className = 'tool-card category-' + t.cat;
    card.dataset.cat = t.cat;
    card.dataset.search = singularizar(t.titulo + ' ' + t.desc + ' ' + t.tag);
    card.innerHTML = `
      <div class="card-top"><span class="tool-icon">${t.icon}</span><span class="card-tag">${t.tag}</span></div>
      <h3>${t.titulo}</h3>
      <p>${t.desc}</p>
      <button type="button">Abrir ferramenta <span aria-hidden="true">→</span></button>`;
    card.querySelector('button').onclick = () => abrirTool(t);
    grid.appendChild(card);
  });
}
function aplicarFiltros() {
  const cat = document.querySelector('.filter.active').dataset.category;
  const q = singularizar($('tool-search').value.trim());
  let visiveis = 0;
  document.querySelectorAll('.tool-card').forEach(c => {
    const ok = (cat === 'all' || c.dataset.cat === cat) && (!q || c.dataset.search.includes(q));
    c.style.display = ok ? '' : 'none';
    if (ok) visiveis++;
  });
  $('empty-tools').hidden = visiveis > 0;
}
document.querySelectorAll('.filter').forEach(b => b.onclick = () => {
  document.querySelectorAll('.filter').forEach(x => x.classList.remove('active'));
  b.classList.add('active'); aplicarFiltros();
});
$('tool-search').oninput = aplicarFiltros;
$('clear-search').onclick = () => {
  $('tool-search').value = '';
  document.querySelectorAll('.filter').forEach(b => b.classList.toggle('active', b.dataset.category === 'all'));
  aplicarFiltros();
};

/* ============ Dialog da ferramenta ============ */
function abrirTool(t) {
  toolAtual = t; arquivos = [];
  resultadoBlob = null;
  if (resultadoUrl) { URL.revokeObjectURL(resultadoUrl); resultadoUrl = null; }
  $('workspace-category').textContent = CATS[t.cat];
  $('workspace-title').textContent = t.titulo;
  $('workspace-description').textContent = t.desc;
  $('upload-hint').textContent = t.multiple
    ? 'Vários arquivos — a ordem da lista define o resultado'
    : 'Um arquivo: ' + t.accept.replace(/\./g, '').toUpperCase();
  fileInput.accept = t.accept; fileInput.multiple = !!t.multiple; fileInput.value = '';
  $('tool-caveat').textContent = t.caveat || '';
  $('tool-error').hidden = true;
  $('result-panel').hidden = true;
  $('processing').hidden = true;
  $('upload-workspace').hidden = false;
  $('submit-tool').hidden = false;
  $('cancel-process').hidden = true;
  renderOpcoes(t);
  renderArquivos();
  toolDialog.showModal();
}

function renderOpcoes(t) {
  const box = $('tool-options'); box.innerHTML = '';
  (t.options || []).forEach(o => {
    const label = document.createElement('label');
    if (o.wide) label.className = 'option-wide';
    label.textContent = o.label;
    let el;
    if (o.tipo === 'select') {
      el = document.createElement('select');
      o.valores.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v.split(' ')[0]; opt.textContent = v;
        if (v === o.padrao) opt.selected = true;
        el.appendChild(opt);
      });
    } else {
      el = document.createElement('input');
      el.value = o.padrao || '';
      if (o.required) el.required = true;
    }
    el.id = 'opt-' + o.nome;
    label.appendChild(el);
    box.appendChild(label);
  });
}

/* ============ Arquivos ============ */
function fmtSize(n) { return n > 1048576 ? (n/1048576).toFixed(1)+' MB' : Math.max(1,Math.round(n/1024))+' KB'; }

function adicionarArquivos(lista) {
  for (const f of lista) {
    if (!toolAtual.multiple) arquivos = [];
    arquivos.push(f);
    if (!toolAtual.multiple) break;
  }
  renderArquivos();
}

function renderArquivos() {
  const ol = $('file-list'); ol.innerHTML = '';
  let total = 0;
  arquivos.forEach((f, i) => {
    total += f.size;
    const li = document.createElement('li');
    li.className = 'file-row';
    li.innerHTML = `
      <span class="file-order">${String(i+1).padStart(2,'0')}</span>
      <div class="file-info"><span class="file-name">${f.name}</span><span class="file-size">${fmtSize(f.size)}</span></div>
      <span class="file-row-controls">
        ${toolAtual.multiple ? `<button type="button" data-up="${i}" ${i===0?'disabled':''} aria-label="Mover para cima">↑</button>
        <button type="button" data-down="${i}" ${i===arquivos.length-1?'disabled':''} aria-label="Mover para baixo">↓</button>` : ''}
        <button type="button" data-del="${i}" aria-label="Remover arquivo">×</button>
      </span>`;
    ol.appendChild(li);
  });
  ol.querySelectorAll('[data-del]').forEach(b => b.onclick = () => { arquivos.splice(+b.dataset.del, 1); renderArquivos(); });
  ol.querySelectorAll('[data-up]').forEach(b => b.onclick = () => { const i=+b.dataset.up; [arquivos[i-1],arquivos[i]]=[arquivos[i],arquivos[i-1]]; renderArquivos(); });
  ol.querySelectorAll('[data-down]').forEach(b => b.onclick = () => { const i=+b.dataset.down; [arquivos[i+1],arquivos[i]]=[arquivos[i],arquivos[i+1]]; renderArquivos(); });
  $('file-total').textContent = arquivos.length ? `${arquivos.length} arquivo(s) · ${fmtSize(total)}` : '';
}

dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragging'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragging'));
dropZone.addEventListener('drop', e => { e.preventDefault(); dropZone.classList.remove('dragging'); adicionarArquivos(e.dataTransfer.files); });
fileInput.addEventListener('change', () => { adicionarArquivos(fileInput.files); fileInput.value=''; });

/* ============ Envio ============ */
function mostrarErro(msg) { const e=$('tool-error'); e.textContent = msg; e.hidden = false; }

$('tool-form').addEventListener('submit', async e => {
  e.preventDefault();
  $('tool-error').hidden = true;
  if (!arquivos.length) return mostrarErro('Selecione ao menos um arquivo.');
  if (toolAtual.min && arquivos.length < toolAtual.min) return mostrarErro(`Esta ferramenta precisa de ao menos ${toolAtual.min} arquivos.`);

  const fd = new FormData();
  if (toolAtual.multiple) arquivos.forEach(f => fd.append('files', f));
  else fd.append('file', arquivos[0]);
  (toolAtual.options || []).forEach(o => {
    const el = $('opt-' + o.nome);
    if (el) fd.append(o.nome, el.value.split(' ')[0]);
  });

  $('processing').hidden = false;
  $('submit-tool').hidden = true;
  $('cancel-process').hidden = false;
  $('result-panel').hidden = true;

  const ctrl = new AbortController();
  $('cancel-process').onclick = () => ctrl.abort();

  try {
    const resp = await fetch(toolAtual.endpoint, { method:'POST', body:fd, signal:ctrl.signal });
    if (!resp.ok) {
      let msg = 'Erro ' + resp.status;
      try { const j = await resp.json(); msg = j.detail || msg; } catch(_) {}
      throw new Error(msg);
    }
    const ctype = resp.headers.get('content-type') || '';
    if (ctype.includes('application/json')) {
      mostrarResultadoJson(await resp.json());
    } else {
      const blob = await resp.blob();
      const cd = resp.headers.get('content-disposition') || '';
      const m = cd.match(/filename\*?=(?:utf-8'')?"?([^";]+)"?/i);
      const nome = m ? decodeURIComponent(m[1]) : 'resultado';
      const extra = resp.headers.get('x-reducao-pct') ? ` (−${resp.headers.get('x-reducao-pct')}%)` : '';
      mostrarResultadoArquivo(blob, nome, extra);
    }
  } catch (err) {
    if (err.name === 'AbortError') mostrarErro('Processamento cancelado.');
    else mostrarErro(err.message);
  } finally {
    $('processing').hidden = true;
    $('submit-tool').hidden = false;
    $('cancel-process').hidden = true;
  }
});

function mostrarResultadoArquivo(blob, nome) {
  resultadoBlob = blob;
  resultadoUrl = URL.createObjectURL(blob);
  const a = $('download-result');
  a.href = resultadoUrl; a.download = nome; a.hidden = false;
  $('copy-text').hidden = true;
  $('text-preview-label').hidden = true;
  $('diagnosis-result').innerHTML = '';
  $('result-summary').textContent = `${nome} · ${fmtSize(blob.size)}`;
  $('result-panel').hidden = false;
  $('upload-workspace').hidden = true;
  a.click(); // download automático
}

function mostrarResultadoJson(j) {
  $('download-result').hidden = true;
  $('diagnosis-result').innerHTML = '';
  let texto = j.texto || j.text || '';
  if (texto) {
    $('text-preview-label').hidden = false;
    $('text-preview').value = texto;
    $('copy-text').hidden = false;
    $('result-summary').textContent = `${j.arquivo || 'imagem'} · ${j.largura||''}×${j.altura||''} · idioma ${j.idioma||j.idioma||'-'}`;
  } else {
    $('text-preview-label').hidden = true;
    $('copy-text').hidden = true;
    // diagnóstico
    const dl = document.createElement('dl'); dl.className = 'diagnosis-list';
    const add = (k,v) => { dl.innerHTML += `<dt>${k}</dt><dd>${v}</dd>`; };
    add('Precisa de OCR', j.legible === false ? '<b style="color:#8d391f">Sim</b>' : '<b style="color:#536049">Não</b>');
    add('Páginas', j.total_pages ?? '-');
    add('Motivo', j.reason || '-');
    if (j.sample_text) {
      const det = document.createElement('pre'); det.className = 'diagnosis-details';
      det.textContent = j.sample_text;
      dl.appendChild(det);
    }
    $('diagnosis-result').appendChild(dl);
    $('result-summary').textContent = 'Diagnóstico concluído.';
  }
  if (j.imagens === 0) { $('result-summary').textContent = 'Este PDF não contém imagens embutidas.'; }
  $('result-panel').hidden = false;
  $('upload-workspace').hidden = true;
}

$('copy-text').onclick = async () => {
  await navigator.clipboard.writeText($('text-preview').value);
  $('copy-feedback').textContent = 'Texto copiado para a área de transferência.';
  setTimeout(() => $('copy-feedback').textContent = '', 3000);
};

$('new-process').onclick = () => {
  arquivos = []; renderArquivos();
  $('result-panel').hidden = true;
  $('upload-workspace').hidden = false;
  $('text-preview-label').hidden = true;
  $('diagnosis-result').innerHTML = '';
};

/* ============ Fechar dialogs ============ */
document.querySelectorAll('.dialog-close').forEach(b => b.onclick = () => b.closest('dialog').close());
[toolDialog, apiDialog].forEach(d => d.addEventListener('click', e => {
  const r = d.getBoundingClientRect();
  if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) d.close();
}));

/* ============ Dialog da API ============ */
document.querySelectorAll('[data-api]').forEach(b => b.onclick = () => {
  const tb = $('api-tools-table'); tb.innerHTML = '';
  TOOLS.forEach(t => {
    const campos = ['file(s)', ...(t.options||[]).map(o => o.nome)].join(', ');
    tb.innerHTML += `<tr><td>${t.endpoint}</td><td>${campos}</td></tr>`;
  });
  apiDialog.showModal();
});
document.querySelectorAll('.code-copy').forEach(b => b.onclick = async () => {
  await navigator.clipboard.writeText(b.dataset.copy);
  $('api-copy-feedback').textContent = 'Exemplo copiado.';
  setTimeout(() => $('api-copy-feedback').textContent = '', 3000);
});

/* ============ Status do serviço ============ */
async function verificarStatus() {
  const dot = $('service-dot'), txt = $('service-status');
  const mdot = $('mode-dot'), mbadge = $('mode-badge');
  try {
    const r = await fetch('/api/health');
    if (!r.ok) throw 0;
    const j = await r.json();
    const langs = (j.idiomas || []).join(', ');
    dot.className = 'status-dot';
    txt.textContent = `Ambiente pronto — OCR ${j.tesseract ? 'ativo' : 'indisponível'} · idiomas: ${langs}`;
    mdot.className = 'status-dot';
    mbadge.textContent = 'Processamento local ativo';
  } catch(_) {
    dot.className = 'status-dot offline';
    txt.textContent = 'Servidor de processamento indisponível no momento.';
    mdot.className = 'status-dot offline';
    mbadge.textContent = 'Offline';
  }
}
$('retry-status').onclick = verificarStatus;

renderGrid();
aplicarFiltros();
verificarStatus();
</script>
</body>
</html>
"""

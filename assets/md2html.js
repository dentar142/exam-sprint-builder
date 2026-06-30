#!/usr/bin/env node
/* exam-sprint-builder · md2html.js
   Offline Markdown -> self-contained HTML converter (zero dependencies).

   Usage:
     node md2html.js <in.md> <out.html> [--title "T"] [--theme warm]

   Options:
     --title T     Page title (default: frontmatter `title:`, else input filename).
     --theme NAME  Token set: warm (default) | dark-tech.
     -h, --help    Show this help.

   Emits ONE self-contained .html: inline CSS + JS, no CDN, no ES imports,
   opens by double-click via file://. Light/dark share the localStorage key
   'esb-theme' with an anti-flash inline head script. Includes a sticky sidebar
   TOC with scrollspy.

   Supported Markdown: ATX headings, GFM tables, fenced code, Obsidian callouts
   (`> [!type]` and collapsible `> [!type]-`), ordered/unordered lists, **bold**,
   `inline code`, [[wikilinks]], [text](url) links, --- horizontal rules, and
   YAML frontmatter. Code spans are protected with private-use-area sentinels
   (U+E000 / U+E001) so their contents are never re-parsed as Markdown. Those
   characters are invisible in editors but load-bearing — do not delete them. */

const fs = require('fs');
const path = require('path');

/* ---------- Minimal Markdown -> HTML (offline, dependency-free) ---------- */
const PUA0 = String.fromCharCode(0xE000), PUA1 = String.fromCharCode(0xE001);
function escapeHtml(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function inline(t){
  const codes=[];
  t=t.replace(/`([^`]+)`/g,(m,c)=>{codes.push(c);return PUA0+(codes.length-1)+PUA1;});
  t=escapeHtml(t);
  t=t.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
  t=t.replace(/\[\[([^\]]+)\]\]/g,(m,x)=>'<span class="wl">'+escapeHtml(x.split('|').pop().replace(/^[★\s]+/,''))+'</span>');
  t=t.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2">$1</a>');
  t=t.replace(new RegExp(PUA0+'(\\d+)'+PUA1,'g'),(m,i)=>'<code>'+escapeHtml(codes[+i])+'</code>');
  return t;
}
const CLABEL={important:'重要',warning:'注意',tip:'提示',note:'笔记',example:'例',question:'自测',abstract:'摘要',summary:'小结',danger:'危险',info:'说明'};
const usedIds={};
function slug(txt){let s=txt.replace(/<[^>]+>/g,'').replace(/[`*]/g,'').trim().replace(/\s+/g,'-').replace(/[^\w一-龥-]/g,'').slice(0,40)||'h';
  if(usedIds[s]!=null){usedIds[s]++;s=s+'-'+usedIds[s];}else usedIds[s]=0;return s;}
function renderTable(rows){
  const cells=r=>r.trim().replace(/^\|/,'').replace(/\|$/,'').split('|').map(c=>c.trim());
  const head=cells(rows[0]),body=rows.slice(2).map(cells);
  let h='<table><thead><tr>'+head.map(c=>'<th>'+inline(c)+'</th>').join('')+'</tr></thead><tbody>';
  body.forEach(r=>h+='<tr>'+r.map(c=>'<td>'+inline(c)+'</td>').join('')+'</tr>');
  return h+'</tbody></table>';
}
function renderList(lines){
  const ordered=/^\s*\d+\./.test(lines[0]);const tag=ordered?'ol':'ul';let h='<'+tag+'>';
  for(const line of lines){const m=line.match(/^\s*(?:[-*]|\d+\.)\s+(.*)$/);
    if(m)h+='<li>'+inline(m[1])+'</li>';else h+=' '+inline(line.trim());}
  return h+'</'+tag+'>';
}
function renderCallout(lines){
  const first=lines[0]||'';const m=first.match(/^\[!(\w+)\]([-+]?)\s*(.*)$/);
  let type='note',title='',collapse=false,body;
  if(m){type=m[1].toLowerCase();collapse=m[2]==='-';title=m[3].trim();body=lines.slice(1);}else body=lines;
  const inner=renderBlocks(body);const label=title||CLABEL[type]||type;
  if(collapse)return '<details class="callout c-'+type+'"><summary>'+inline(label)+'</summary><div class="cbody">'+inner+'</div></details>';
  return '<div class="callout c-'+type+'"><div class="ctitle">'+inline(label)+'</div><div class="cbody">'+inner+'</div></div>';
}
function renderBlocks(lines){
  let html='',i=0;
  const stop=/^(#{1,6}\s|```|>\s?|\||---+\s*$|\s*(?:[-*]|\d+\.)\s)/;
  while(i<lines.length){
    const line=lines[i];
    if(/^\s*$/.test(line)){i++;continue;}
    let m=line.match(/^```(\w*)/);
    if(m){const lang=m[1];i++;const code=[];while(i<lines.length&&!/^```/.test(lines[i])){code.push(lines[i]);i++;}i++;
      html+='<pre'+(lang?' data-lang="'+lang+'"':'')+'><code>'+escapeHtml(code.join('\n'))+'</code></pre>';continue;}
    m=line.match(/^(#{1,6})\s+(.*)$/);
    if(m){const lv=m[1].length,txt=m[2],id=slug(txt);html+='<h'+lv+' id="'+id+'">'+inline(txt)+'</h'+lv+'>';i++;continue;}
    if(/^---+\s*$/.test(line)){html+='<hr>';i++;continue;}
    if(/^>\s?/.test(line)){const bq=[];while(i<lines.length&&/^>\s?/.test(lines[i])){bq.push(lines[i].replace(/^>\s?/,''));i++;}html+=renderCallout(bq);continue;}
    if(/^\|.*\|/.test(line)&&i+1<lines.length&&/^\|?[\s:|-]+$/.test(lines[i+1])&&lines[i+1].includes('-')){
      const tbl=[];while(i<lines.length&&/\|/.test(lines[i])&&!/^\s*$/.test(lines[i])){tbl.push(lines[i]);i++;}html+=renderTable(tbl);continue;}
    if(/^\s*(?:[-*]|\d+\.)\s+/.test(line)){const list=[];
      while(i<lines.length&&(/^\s*(?:[-*]|\d+\.)\s+/.test(lines[i])||/^\s{2,}\S/.test(lines[i]))){list.push(lines[i]);i++;}html+=renderList(list);continue;}
    const para=[];while(i<lines.length&&!/^\s*$/.test(lines[i])&&!stop.test(lines[i])){para.push(lines[i]);i++;}
    if(para.length)html+='<p>'+inline(para.join(' '))+'</p>';else i++;
  }
  return html;
}
function convert(md){
  md=md.replace(/\r\n/g,'\n');
  let title='';
  const fm=md.match(/^---\n([\s\S]*?)\n---\n/);
  if(fm){const t=fm[1].match(/title:\s*(.+)/);if(t)title=t[1].trim().replace(/^["']|["']$/g,'');md=md.slice(fm[0].length);}
  Object.keys(usedIds).forEach(k=>delete usedIds[k]);
  const body=renderBlocks(md.split('\n'));
  // TOC: h1/h2/h3
  const toc=[];const re=/<h([123]) id="([^"]+)">([\s\S]*?)<\/h\1>/g;let mm;
  while((mm=re.exec(body))){toc.push({lv:+mm[1],id:mm[2],txt:mm[3].replace(/<[^>]+>/g,'')});}
  return {title,body,toc};
}

/* ---------- Theme token sets (light + dark variable blocks) ----------
   Add a theme by pasting a {light, dark} block from references/themes.md. */
const THEMES={
  warm:{
    light:"--bg:#f6efe3;--surface:#fffaf2;--surface-2:#f3ebdc;--ink:#4a3b2c;--ink-soft:#6f5e4c;--ink-faint:#9b8a76;--line:#e3d6c0;--brand:#c0612f;--brand-2:#b9892f;--ok:#5b7c52;--ok-bg:#dde7d2;--warn:#b0552c;--warn-bg:#f3d9cb;--tip-bg:#f5ead2;--code-bg:#2f2722;--code-ink:#f3e7d6;--chip:#ecd9c2;--shadow:0 6px 22px rgba(90,64,40,.10),0 2px 6px rgba(90,64,40,.06);",
    dark:"--bg:#211b15;--surface:#2b2219;--surface-2:#332820;--ink:#f0e3d0;--ink-soft:#d4c3ac;--ink-faint:#a7937a;--line:#4a3c2d;--brand:#e8915a;--brand-2:#e6b85c;--ok:#9cc081;--ok-bg:#2f3a26;--warn:#e8a06a;--warn-bg:#3e2a1d;--tip-bg:#3a2e1d;--code-bg:#15110d;--code-ink:#f0e0c8;--chip:#3a2d20;--shadow:0 8px 28px rgba(0,0,0,.45),0 2px 8px rgba(0,0,0,.3);"
  },
  'dark-tech':{
    light:"--bg:#eef2f7;--surface:#ffffff;--surface-2:#e4e9f0;--ink:#1b2330;--ink-soft:#45526a;--ink-faint:#7c8aa0;--line:#d2dae6;--brand:#2563eb;--brand-2:#0891b2;--ok:#0f766e;--ok-bg:#d6f0ec;--warn:#b45309;--warn-bg:#fdecd2;--tip-bg:#e2ecfb;--code-bg:#0f172a;--code-ink:#e2e8f0;--chip:#dde6f2;--shadow:0 6px 22px rgba(30,41,59,.10),0 2px 6px rgba(30,41,59,.06);",
    dark:"--bg:#0b1120;--surface:#111a2e;--surface-2:#1b2742;--ink:#e6edf6;--ink-soft:#a9b6cc;--ink-faint:#6b7a94;--line:#26344f;--brand:#5b9dff;--brand-2:#22d3ee;--ok:#34d399;--ok-bg:#0f2e2a;--warn:#fbbf24;--warn-bg:#3a2a12;--tip-bg:#13233f;--code-bg:#060b16;--code-ink:#d6e2f2;--chip:#1d2b46;--shadow:0 10px 30px rgba(0,0,0,.55),0 2px 10px rgba(0,0,0,.4);"
  }
};

/* ---------- Self-contained page template (sidebar TOC · light/dark · file://) ---------- */
function page({title,body,toc,theme}){
const tk=THEMES[theme]||THEMES.warm;
const tocHtml=toc.filter(t=>t.lv<=3).map(t=>`<a href="#${t.id}" class="lv${t.lv}" data-id="${t.id}">${t.txt}</a>`).join('');
const safeTitle=escapeHtml(title);
return `<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${safeTitle}</title>
<script>(function(){try{var t=localStorage.getItem('esb-theme');if(!t)t=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>
<style>
:root,[data-theme="light"]{${tk.light}}
[data-theme="dark"]{${tk.dark}}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);font-family:"Microsoft YaHei","PingFang SC","Segoe UI",system-ui,sans-serif;line-height:1.75;font-size:15.5px;-webkit-font-smoothing:antialiased}
.bar{position:sticky;top:0;z-index:30;background:color-mix(in srgb,var(--bg) 90%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);display:flex;align-items:center;gap:10px;padding:11px 18px}
.bar h1{font-family:"Noto Serif SC","Songti SC",Georgia,serif;font-size:1.08rem;margin:0;flex:1;color:var(--ink)}
.bar h1 b{color:var(--brand)}
.tbtn{cursor:pointer;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:6px 13px;font-size:.82rem}
.tbtn:hover{border-color:var(--brand)}
.menu{display:none;cursor:pointer;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:8px;padding:6px 11px}
.layout{display:grid;grid-template-columns:266px 1fr;max-width:1180px;margin:0 auto;gap:0}
.toc{position:sticky;top:54px;align-self:start;height:calc(100vh - 54px);overflow:auto;padding:18px 10px 40px 18px;border-right:1px solid var(--line)}
.toc a{display:block;color:var(--ink-soft);text-decoration:none;font-size:.86rem;padding:4px 9px;border-radius:7px;border-left:2px solid transparent;line-height:1.4}
.toc a:hover{background:var(--surface-2)}
.toc a.lv1{font-weight:700;color:var(--ink);margin-top:6px}
.toc a.lv2{padding-left:14px}
.toc a.lv3{padding-left:26px;font-size:.8rem;color:var(--ink-faint)}
.toc a.active{color:var(--brand);border-left-color:var(--brand);background:var(--surface-2)}
.content{padding:18px 30px 80px;min-width:0;max-width:860px}
.content h1{font-family:"Noto Serif SC","Songti SC",Georgia,serif;font-size:1.7rem;border-bottom:2px solid var(--line);padding-bottom:10px;scroll-margin-top:64px}
.content h2{font-family:"Noto Serif SC","Songti SC",serif;font-size:1.3rem;margin-top:30px;padding-left:11px;border-left:4px solid var(--brand);scroll-margin-top:64px}
.content h3{font-size:1.08rem;color:var(--brand);margin-top:22px;scroll-margin-top:64px}
.content h4{font-size:.98rem;margin-top:18px;scroll-margin-top:64px}
a{color:var(--brand)} .wl{color:var(--brand-2);border-bottom:1px dashed var(--brand-2)}
code{font-family:"Cascadia Code","Consolas",monospace;background:var(--surface-2);color:var(--brand);padding:.06em .4em;border-radius:5px;font-size:.9em}
pre{background:var(--code-bg);color:var(--code-ink);border-radius:12px;padding:16px 18px;overflow:auto;line-height:1.55;font-size:13.5px;box-shadow:var(--shadow);position:relative}
pre code{background:none;color:inherit;padding:0;font-family:"Cascadia Code","Consolas",monospace}
pre[data-lang]::before{content:attr(data-lang);position:absolute;top:0;right:0;font-size:.66rem;color:var(--code-ink);opacity:.55;background:rgba(255,255,255,.07);padding:2px 8px;border-radius:0 12px 0 8px;text-transform:uppercase}
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:.92rem;background:var(--surface);border-radius:10px;overflow:hidden;box-shadow:var(--shadow)}
th,td{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top}
th{background:var(--surface-2);color:var(--brand)}
hr{border:none;border-top:1px solid var(--line);margin:26px 0}
ul,ol{padding-left:24px}li{margin:4px 0}
.callout{border-left:4px solid var(--brand);background:var(--tip-bg);border-radius:9px;padding:11px 15px;margin:15px 0}
.callout .ctitle{font-weight:700;color:var(--brand);margin-bottom:5px}
.callout .cbody>:first-child{margin-top:0}.callout .cbody>:last-child{margin-bottom:0}
.c-warning,.c-danger{border-color:var(--warn);background:var(--warn-bg)}.c-warning .ctitle,.c-danger .ctitle{color:var(--warn)}
.c-example,.c-question,.c-note,.c-summary,.c-abstract{border-color:var(--ok);background:var(--ok-bg)}.c-example .ctitle,.c-question .ctitle,.c-note .ctitle,.c-summary .ctitle,.c-abstract .ctitle{color:var(--ok)}
details.callout{padding:0}details.callout summary{cursor:pointer;font-weight:700;color:var(--ok);padding:11px 15px;list-style:none}
details.callout summary::-webkit-details-marker{display:none}
details.callout summary::before{content:"▸ ";color:var(--ok)}details.callout[open] summary::before{content:"▾ "}
details.callout .cbody{padding:0 15px 12px}
.content>:first-child{margin-top:6px}
@media(max-width:820px){.layout{grid-template-columns:1fr}.toc{display:none;position:fixed;top:50px;left:0;width:84%;max-width:320px;height:calc(100vh - 50px);background:var(--surface);z-index:40;box-shadow:var(--shadow);border-right:1px solid var(--line)}.toc.open{display:block}.menu{display:inline-block}.content{padding:16px 16px 70px}}
@media print{.bar,.toc,.menu,.tbtn{display:none!important}.layout{display:block;max-width:none}.content{max-width:none;padding:0}pre,table{box-shadow:none}@page{size:A4;margin:16mm}}
</style></head>
<body>
<div class="bar"><button class="menu" id="menu">☰ 目录</button><h1>${safeTitle.replace(/·/,'<b>·</b>')}</h1><button class="tbtn" id="tbtn">🌙 暗色</button></div>
<div class="layout">
  <nav class="toc" id="toc">${tocHtml}</nav>
  <main class="content" id="content">${body}</main>
</div>
<script>
function applyTheme(t){document.documentElement.setAttribute('data-theme',t);var b=document.getElementById('tbtn');if(b)b.textContent=t==='dark'?'☀ 亮色':'🌙 暗色';try{localStorage.setItem('esb-theme',t);}catch(e){}}
document.getElementById('tbtn').onclick=function(){applyTheme((document.documentElement.getAttribute('data-theme')||'light')==='dark'?'light':'dark');};
applyTheme(document.documentElement.getAttribute('data-theme')||'light');
var menu=document.getElementById('menu'),toc=document.getElementById('toc');
if(menu)menu.onclick=function(){toc.classList.toggle('open');};
toc.querySelectorAll('a').forEach(function(a){a.onclick=function(){toc.classList.remove('open');};});
// scrollspy
var links={};toc.querySelectorAll('a').forEach(function(a){links[a.dataset.id]=a;});
var heads=[].slice.call(document.querySelectorAll('#content h1,#content h2,#content h3'));
var obs=new IntersectionObserver(function(ents){ents.forEach(function(e){if(e.isIntersecting){var id=e.target.id;Object.values(links).forEach(function(x){x.classList.remove('active');});if(links[id]){links[id].classList.add('active');links[id].scrollIntoView({block:'nearest'});}}});},{rootMargin:'-60px 0px -70% 0px'});
heads.forEach(function(h){if(h.id)obs.observe(h);});
</script>
</body></html>`;
}

/* ---------- CLI ---------- */
function parseArgs(argv){
  const out={_:[]};
  for(let i=0;i<argv.length;i++){
    const a=argv[i];
    if(a==='--title'){out.title=argv[++i];}
    else if(a.startsWith('--title=')){out.title=a.slice(8);}
    else if(a==='--theme'){out.theme=argv[++i];}
    else if(a.startsWith('--theme=')){out.theme=a.slice(8);}
    else if(a==='-h'||a==='--help'){out.help=true;}
    else out._.push(a);
  }
  return out;
}
function usage(){
  console.log('Usage: node md2html.js <in.md> <out.html> [--title "T"] [--theme warm|dark-tech]');
}
function main(){
  const args=parseArgs(process.argv.slice(2));
  if(args.help){usage();process.exit(0);}
  if(args._.length<2){console.error('Error: need <in.md> and <out.html>.');usage();process.exit(1);}
  const [inPath,outPath]=args._;
  const theme=(args.theme||'warm').toLowerCase();
  if(!THEMES[theme]){console.error('Warning: unknown theme "'+theme+'", using "warm". Known: '+Object.keys(THEMES).join(', '));}
  const md=fs.readFileSync(inPath,'utf8');
  const r=convert(md);
  const title=args.title||r.title||path.basename(inPath).replace(/\.[^.]+$/,'');
  const html=page({title,body:r.body,toc:r.toc,theme});
  fs.writeFileSync(outPath,html,'utf8');
  const external=/(https?:)?\/\/(cdn|unpkg|jsdelivr|googleapis)/i.test(html);
  console.log(path.basename(outPath),'| title:',title,'| theme:',THEMES[theme]?theme:'warm','| TOC:',r.toc.length,'| bytes:',Buffer.byteLength(html,'utf8'),'| external-links:',external);
}

if(require.main===module){main();}
module.exports={convert,page,THEMES};

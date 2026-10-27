"""Selector de idioma (español / inglés, con banderas) y de modo noche / día.
  * El idioma se guarda en localStorage (codex_lang); si no hay, se usa el del navegador.  Cambiarlo recarga la página.
  * El tema se guarda en localStorage (codex_theme: light / dark); si no hay, manda el del sistema.  Cambiarlo es inmediato.
  * t() traduce: tools/i18n.py envuelve en cada build los textos en español de los scripts; el diccionario sale de tools/i18n_en.json
    y el del HTML fijo de tools/i18n_static.json.
Backup: src.before_patch49.html."""
import shutil

shutil.copy('src.html', 'src.before_patch49.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


# ---- 1. idioma y tema antes de que se dibuje nada ----
rep("<title>Aleister's Codex</title>", """<title>Aleister's Codex</title>
<script>(function(){var d=document.documentElement,L='',T='';try{L=localStorage.getItem('codex_lang')||'';T=localStorage.getItem('codex_theme')||'';}catch(e){}
if(L!=='es'&&L!=='en')L=((navigator.language||'es').toLowerCase().indexOf('es')===0)?'es':'en';
d.lang=L; if(T==='light'||T==='dark')d.setAttribute('data-theme',T);})();</script>""")

# ---- 2. núcleo de traducción, lo primero del script principal ----
rep("<script>\nconst CARDS = {};", r"""<script>
/* ---------- idioma ---------- */
const LANG = document.documentElement.lang==='en' ? 'en' : 'es';
const LOC = LANG==='en' ? 'en-US' : 'es-AR';
const EN = /*__I18NEN__*/{};          // español -> inglés (lo completa tools/i18n.py en cada build)
const EN_ST = /*__I18NST__*/{};       // HTML fijo: texto o HTML interno -> inglés
function t(a){
  if(Array.isArray(a)&&a.raw){                      // plantilla etiquetada: t`...${x}...`
    const v=Array.prototype.slice.call(arguments,1);
    if(LANG==='en'){
      let key=a.raw[0]; for(let i=1;i<a.raw.length;i++) key+='{'+(i-1)+'}'+a.raw[i];
      const r=EN[key]; if(r!==undefined) return r.replace(/\{(\d+)\}/g,(m,i)=>v[+i]);
    }
    let o=a[0]; for(let i=1;i<a.length;i++) o+=v[i-1]+a[i]; return o;
  }
  return LANG==='en'&&EN[a]!==undefined ? EN[a] : a;
}
function i18nStatic(){
  if(LANG!=='en') return;
  const norm=x=>x.replace(/\s+/g,' ').trim();
  document.querySelectorAll('footer li').forEach(li=>{ const k=norm(li.innerHTML); if(EN_ST[k]) li.innerHTML=EN_ST[k]; });
  const root=document.querySelector('.wrap')||document.body, w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT), nodes=[];
  for(let n;(n=w.nextNode());) nodes.push(n);
  nodes.forEach(n=>{ const p=n.parentElement; if(!p||p.closest('#app,#pv,#toast,footer li,script,style')) return;
    const k=norm(n.nodeValue); if(k&&EN_ST[k]){ const raw=n.nodeValue.trim(); n.nodeValue=n.nodeValue.replace(raw,()=>EN_ST[k]); } });
  document.querySelectorAll('[aria-label],[title],[placeholder]').forEach(el=>{ for(const a of ['aria-label','title','placeholder']){ const v=el.getAttribute(a); if(v&&EN_ST[norm(v)]) el.setAttribute(a,EN_ST[norm(v)]); } });
  const md=document.querySelector('meta[name=description]'); if(md&&EN_ST[norm(md.content)]) md.content=EN_ST[norm(md.content)];
}
/* ---------- tema noche / día ---------- */
const curTheme=()=>{ const a=document.documentElement.getAttribute('data-theme'); return a==='dark'||a==='light'?a:(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'); };
function setTheme(x){ document.documentElement.setAttribute('data-theme',x); try{ localStorage.setItem('codex_theme',x); }catch(e){} syncPrefs(); }
function setLang(x){ try{ localStorage.setItem('codex_lang',x); }catch(e){} location.reload(); }
function syncPrefs(){
  document.querySelectorAll('[data-lang]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.lang===LANG)));
  const b=document.querySelector('[data-theme-toggle]'); if(!b) return;
  const dark=curTheme()==='dark'; b.dataset.cur=dark?'dark':'light';
  const lbl=dark?t('Cambiar a modo día'):t('Cambiar a modo noche'); b.setAttribute('aria-label',lbl); b.title=lbl;
}
const CARDS = {};""")

# ---- 3. los controles en el encabezado ----
rep('  <div class="asof" id="asof"></div>', '''  <div class="asof" id="asof"></div>
  <div class="prefs" role="group" aria-label="Preferencias">
    <div class="langsw" role="group" aria-label="Idioma">
      <button class="lg" data-lang="es" aria-pressed="false" title="Español" aria-label="Español"><svg viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#c60b1e"/><rect y="5" width="30" height="10" fill="#ffc400"/></svg></button>
      <button class="lg" data-lang="en" aria-pressed="false" title="English" aria-label="English"><svg viewBox="0 0 60 40" aria-hidden="true"><clipPath id="fl-s"><path d="M0,0 v40 h60 v-40 z"/></clipPath><clipPath id="fl-t"><path d="M30,20 h30 v20 z v20 h-30 z h-30 v-20 z v-20 h30 z"/></clipPath><g clip-path="url(#fl-s)"><path d="M0,0 v40 h60 v-40 z" fill="#012169"/><path d="M0,0 L60,40 M60,0 L0,40" stroke="#fff" stroke-width="8"/><path d="M0,0 L60,40 M60,0 L0,40" clip-path="url(#fl-t)" stroke="#c8102e" stroke-width="5"/><path d="M30,0 v40 M0,20 h60" stroke="#fff" stroke-width="13"/><path d="M30,0 v40 M0,20 h60" stroke="#c8102e" stroke-width="8"/></g></svg></button>
    </div>
    <button class="themebtn" data-theme-toggle="1" data-cur="dark" aria-label="Cambiar a modo noche" title="Cambiar a modo noche">
      <svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.4M12 19.1v2.4M2.5 12h2.4M19.1 12h2.4M5.3 5.3l1.7 1.7M17 17l1.7 1.7M18.7 5.3L17 7M7 17l-1.7 1.7"/></svg>
      <svg class="moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5z"/></svg>
    </button>
  </div>''')

# ---- 4. se activan al cargar ----
rep("const h=location.hash.slice(1); if(MODES[h]) mode=h;", "i18nStatic(); syncPrefs();\nconst h=location.hash.slice(1); if(MODES[h]) mode=h;")

# ---- 5. clics ----
rep("  const d=b.dataset;\n", "  const d=b.dataset;\n  if(d.lang){ if(d.lang!==LANG) setLang(d.lang); return; }\n  if(d.themeToggle){ setTheme(curTheme()==='dark'?'light':'dark'); return; }\n")

# ---- 6. números y fechas según el idioma ----
s = s.replace("toLocaleString('es-AR')", "toLocaleString(LOC)")
rep("const fmtNum = n => n==null ? '' : n.toLocaleString(LOC);", "const fmtNum = n => n==null ? '' : n.toLocaleString(LOC);")
rep("const fmt=n=>n.toFixed(1).replace('.',',')+'%';", "const fmt=n=>n.toFixed(1).replace('.',LANG==='en'?'.':',')+'%';")
rep("const dmy=d=>{ if(!d) return ''; const [y,m,dd]=d.split('-'); return `${dd}/${m}/${y}`; };",
    "const dmy=d=>{ if(!d) return ''; const [y,m,dd]=d.split('-'); return LANG==='en'?`${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][+m-1]} ${+dd}, ${y}`:`${dd}/${m}/${y}`; };")

# ---- 7. lógica que miraba el texto en español: tiene que reconocer también el inglés ----
rep("/victoria/.test(x)?'w':/top 4/.test(x)?'t':/(banlist|puntos) actual/.test(x)?'u':''", "/victoria|\\bwins?\\b/.test(x)?'w':/top 4/.test(x)?'t':/(banlist|puntos) actual|current (banlist|points)/.test(x)?'u':''")
rep("if(/^Importé/.test(DK.msg)) DK.modal=null;", "if(/^(Importé|Imported)/.test(DK.msg)) DK.modal=null;")
rep("/^#\\s*(c[oó]mo funciona|notas?)\\b/i", "/^#\\s*(c[oó]mo funciona|how it works|notas?|notes?)\\b/i")

# ---- 8. estilos ----
css = '''/* idioma y modo noche / día */
.prefs{position:absolute;top:0;right:0;display:flex;gap:var(--s2);align-items:center;z-index:6;max-width:none!important}
.langsw{display:flex;gap:4px;padding:4px;border-radius:99px;border:1px solid var(--line2);background:color-mix(in srgb,var(--surface) 78%,transparent);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
.lg{display:grid;place-items:center;width:40px;height:28px;padding:0;border-radius:99px;border:2px solid transparent;background:none;cursor:pointer;opacity:.55;transition:opacity .15s,border-color .15s,transform .15s}
.lg svg{width:26px;height:18px;border-radius:4px;box-shadow:0 0 0 1px rgba(0,0,0,.25)}
.lg:hover{opacity:.9;transform:translateY(-1px)}
.lg[aria-pressed="true"]{opacity:1;border-color:var(--accent);box-shadow:0 0 14px -4px var(--accent)}
.themebtn{display:grid;place-items:center;width:42px;height:42px;padding:0;border-radius:50%;border:1px solid var(--line2);background:color-mix(in srgb,var(--surface) 78%,transparent);color:var(--fg);cursor:pointer;-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);transition:border-color .15s,box-shadow .15s,transform .2s}
.themebtn:hover{border-color:var(--accent);box-shadow:0 0 16px -4px var(--accent);transform:rotate(12deg)}
.themebtn svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;grid-area:1/1}
.themebtn[data-cur="dark"] .sun{display:none}
.themebtn[data-cur="light"] .moon{display:none}
.themebtn[data-cur="dark"] .moon{color:var(--accent2)}
.themebtn[data-cur="light"] .sun{color:#d98a00}
@media(max-width:760px){.prefs{position:static;justify-content:flex-start;margin-top:var(--s2)}}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 49 ok')

"""Gate: modernización (app instalable, sin conexión, búsqueda al instante, cartas guardadas, accesibilidad).  Desde la raíz:  python tests/check_pwa.py

  1. manifest: JSON válido, íconos con el tamaño que dicen, start_url, todo listado en files.json (lo que no está ahí no se publica)
  2. página: manifest, theme-color, apple-touch-icon, JSON-LD que parsea (WebSite + SearchAction hacia ?mode=search), enlace "saltar al contenido", botón de búsqueda, sin pedidos a Google Fonts
  3. fuentes propias: cada url() de @font-face existe y está en files.json
  4. service worker en node con caché y fetch simulados: navegación y data/ primero la red y, sin red, lo guardado; art/ lo guardado y se refresca; otros dominios no se tocan; activate borra cachés de versiones viejas
  5. atajos: "/" y Ctrl/Cmd+K abren la búsqueda salvo escribiendo en un campo
  6. cartas guardadas (favGet/favToggle) en node con localStorage falso, también con datos rotos y sin localStorage
  7. esqueletos de carga, prefers-reduced-motion/-data y foco visible
"""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


src = open('src.html', encoding='utf-8').read()
page = open('index.html', encoding='utf-8').read()
files = {f['path'] for f in json.load(open('files.json', encoding='utf-8'))}

# 1. manifest
man = json.load(open('manifest.webmanifest', encoding='utf-8'))
ok(man.get('display') == 'standalone' and man.get('start_url') and man.get('name') and man.get('theme_color'), 'manifest: nombre, start_url, display standalone y color')
try:
    from PIL import Image
    good = True
    for ic in man['icons']:
        w, h = Image.open(ic['src']).size
        good &= ('%dx%d' % (w, h)) == ic['sizes']
    ok(good and {i['purpose'] for i in man['icons']} >= {'any', 'maskable'}, 'manifest: los íconos existen, miden lo que dicen y hay uno maskable')
except Exception as e:
    ok(False, 'manifest: íconos (%s)' % e)
ok(all(p in files for p in ['manifest.webmanifest', 'sw.js', 'art/icon-180.png'] + [i['src'] for i in man['icons']]), 'files.json lista manifest, sw.js y los íconos (si no, no se publican)')

# 2. página
ok('<link rel="manifest" href="manifest.webmanifest">' in page and 'name="theme-color"' in page and 'rel="apple-touch-icon"' in page, 'página: manifest, theme-color y apple-touch-icon')
m = re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
try:
    ld = json.loads(m.group(1))
    ok(ld['@type'] == 'WebSite' and ld['potentialAction']['@type'] == 'SearchAction' and '?mode=search&q={search_term_string}' in ld['potentialAction']['target']['urlTemplate'], 'JSON-LD válido: WebSite con SearchAction hacia ?mode=search')
except Exception as e:
    ok(False, 'JSON-LD no parsea en la página construida (el traductor no debe tocarlo): %s' % e)
ok('class="skip" href="#app"' in page and 'class="themebtn srchbtn"' in page and 'aria-keyshortcuts="/ Control+K"' in page, 'enlace saltar al contenido y botón de búsqueda en la barra')
ok('fonts.googleapis.com' not in page and 'fonts.gstatic.com' not in page, 'la página no pide nada a Google Fonts')
ok("navigator.serviceWorker.register('sw.js?v='" in page, 'se registra sw.js con la versión del build')

# 3. fuentes
urls = re.findall(r"@font-face\{[^}]*?url\(([^)]+)\)", page)
ok(len(urls) >= 6 and all(os.path.isfile(u) and u in files for u in urls), '%d @font-face locales: archivos presentes y publicados' % len(urls))

# 4. service worker
js = r"""
const fs=require('fs'); const code=fs.readFileSync('sw.js','utf8');
const listeners={}; const store={};
class Resp{constructor(b,ok=true){this.b=b;this.ok=ok;} clone(){return new Resp(this.b,this.ok);} static error(){return new Resp('ERR',false);} }
const mk=name=>({ m:new Map(), async match(r){return this.m.get(typeof r==='string'?r:r.url);}, async put(r,v){this.m.set(typeof r==='string'?r:r.url,v);}, async addAll(){} });
const cs={};
const caches={ async open(n){return cs[n]||(cs[n]=mk(n));}, async keys(){return Object.keys(cs);}, async delete(n){delete cs[n];return true;} };
let net={}, down=false;
const fetchFn=async r=>{ if(down) throw new Error('offline'); return new Resp(net[r.url]||'net:'+r.url); };
const self_={location:{href:'https://x.test/sw.js?v=V2',origin:'https://x.test'},addEventListener:(t,f)=>listeners[t]=f,skipWaiting(){},clients:{claim(){}}};
new Function('self','caches','fetch','Response','URL','location',code)(self_,caches,fetchFn,Resp,URL,self_.location);
const out=[]; const T=(n,c)=>out.push((c?'ok ':'FAIL ')+n);
const ev=(url,mode='no-cors',method='GET',hdr={})=>{ let res; const e={request:{url,mode,method,headers:{has:k=>!!hdr[k]}},respondWith(p){res=p;}}; listeners.fetch(e); return res; };
(async()=>{
  cs['codex-shell-OLD']=mk(); cs['codex-data-OLD']=mk(); cs['codex-static-1']=mk(); cs['otro']=mk();
  let w; listeners.activate({waitUntil:p=>w=p}); await w;
  T('activate borra cachés viejos de codex y deja lo ajeno y lo estático', !cs['codex-shell-OLD']&&!cs['codex-data-OLD']&&cs['codex-static-1']&&cs['otro']);
  T('se versiona con ?v= de la dirección', JSON.stringify(Object.keys(cs)).indexOf('OLD')<0);
  T('otro dominio: no se intercepta', ev('https://images.ygoprodeck.com/a.jpg')===undefined);
  T('POST: no se intercepta', ev('https://x.test/data/a.js','no-cors','POST')===undefined);
  let r=await ev('https://x.test/','navigate'); T('navegación con red: va a la red', r.b==='net:https://x.test/');
  down=true; r=await ev('https://x.test/','navigate'); T('navegación sin red: devuelve lo guardado', r.b==='net:https://x.test/');
  down=false; r=await ev('https://x.test/data/es.js'); T('data con red: red', r.b==='net:https://x.test/data/es.js');
  net['https://x.test/data/es.js']='nuevo'; r=await ev('https://x.test/data/es.js'); T('data con red: siempre lo más nuevo', r.b==='nuevo');
  down=true; r=await ev('https://x.test/data/es.js'); T('data sin red: lo último guardado', r.b==='nuevo');
  r=await ev('https://x.test/data/nunca.js'); T('data sin red y sin copia: error, no se cuelga', r.ok===false);
  down=false; r=await ev('https://x.test/art/a.png'); T('art 1ª vez: red', r.b==='net:https://x.test/art/a.png');
  down=true; r=await ev('https://x.test/art/a.png'); T('art sin red: guardado', r.b==='net:https://x.test/art/a.png');
  r=await ev('https://x.test/art/font-figtree-latin.woff2'); T('fuente sin copia y sin red: error limpio', r.ok===false);
  console.log(out.join('\n')); process.exit(out.some(x=>x.startsWith('FAIL'))?1:0);
})();
"""
p = subprocess.run(['node', '-e', js], capture_output=True, text=True, encoding='utf-8')
for ln in p.stdout.strip().splitlines():
    ok(ln.startswith('ok '), 'sw: ' + ln[3:].strip() if ln.startswith('ok ') else 'sw: ' + ln[5:])
if p.returncode != 0 and not p.stdout.strip():
    ok(False, 'sw: node falló: ' + p.stderr[:300])

# 5. atajos
ok("(k==='/'&&!typing&&!e.ctrlKey&&!e.metaKey)||(k==='k'&&(e.ctrlKey||e.metaKey))" in src and 'function openSearch()' in src, 'atajos: "/" (si no se escribe en un campo) y Ctrl/Cmd+K')

# 6. cartas guardadas
fm = re.search(r"const FAVK=.*?\nfunction favToggle\(n\)\{.*?\n", src, re.S).group(0)
js2 = r"""
const store={}; global.localStorage={getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=v;}};
""" + fm + r"""
const T=(n,c)=>console.log((c?'ok ':'FAIL ')+n);
T('vacío al inicio', favGet().length===0);
T('guardar devuelve true y la carta queda primera', favToggle('A')===true && favToggle('B')===true && favGet()[0]==='B' && favHas('A'));
T('quitar devuelve false', favToggle('A')===false && !favHas('A') && favGet().length===1);
store['codex_fav']='{roto'; T('datos rotos no rompen: lista vacía', favGet().length===0);
store['codex_fav']='[1,"x",null]'; T('solo textos', JSON.stringify(favGet())==='["x"]');
for(let i=0;i<250;i++) favToggle('c'+i); T('tope de 200', favGet().length===200);
global.localStorage={getItem(){throw new Error('x')},setItem(){throw new Error('x')}}; T('sin localStorage no lanza', favGet().length===0 && favToggle('z')===true);
"""
p = subprocess.run(['node', '-e', js2], capture_output=True, text=True, encoding='utf-8')
for ln in p.stdout.strip().splitlines():
    ok(ln.startswith('ok '), 'favoritas: ' + ln[3:])
if p.returncode != 0:
    ok(False, 'favoritas: node falló: ' + p.stderr[:300])
ok("data-fav=" in src and 'favBlock()' in src and "if(d.fav){ favToggle(d.fav); render(); return; }" in src, 'favoritas: botón en la carta, lista en Buscar y manejador de clic')

# 7. CSS
ok('.lede.sk{' in src and 'prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important' in src and 'prefers-reduced-data:reduce' in src and ':focus-visible{outline:2px solid var(--accent)' in src, 'esqueletos de carga, reduced-motion global, reduced-data y foco visible')
ok(src.count('<p class="lede">Cargando…</p>') == 0, 'ningún "Cargando…" suelto: todos usan el esqueleto')
ok('document.startViewTransition' in src and 'announce(' in src, 'transición entre secciones y anuncio para lectores de pantalla')

ok(".dock.compact.dhide{transform:translateY(-112%)}" in src and "el.contains(document.activeElement)" in src and "color-mix(in srgb,var(--surface) 97%,transparent)" in src, 'barra fija de escritorio: fondo casi opaco y se esconde al bajar (no con el foco dentro ni en el móvil)')
m = re.search(r'@media\(min-width:761px\)\{\s*\.dock\.compact::before.*?\n\}\n', src, re.S)
ok(m is not None and m.group(0).count('{') == m.group(0).count('}'), 'barra fija: todas las reglas nuevas van dentro de @media(min-width:761px), el móvil no cambia')

# 8. capa visual 2026
vis = src[src.index('/* ---- Capa visual 2026'):src.index('</style>', src.index('/* ---- Capa visual 2026'))]
ok('aurora' not in page.replace('Maurora','') and '--aur' not in vis, 'visual: sin aurora de fondo (se quitó: quedaba mal)')
ok('@media(hover:hover) and (pointer:fine){' in vis and vis.count('@media(hover:hover) and (pointer:fine)') == 1 and 'conic-gradient(from 200deg' in vis and '.deck:not([open]){' in vis, 'visual: brillo del mouse solo con mouse y solo en mazos cerrados (en uno abierto, con 50 cartas, repintaba todo)')
ok("matchMedia('(hover:hover) and (pointer:fine)')" in src and "e.pointerType!=='mouse'" in src and 'requestAnimationFrame(()=>{ tk=0; const x=ev' in src, 'visual: el JS de puntero solo corre con mouse y escribe una vez por cuadro')
ok('.bigcard.tilt' not in src and 'perspective:900px' not in src, 'visual: sin tilt 3D en la carta (frenaba la página)')

ok('animation-timeline' not in vis and '@keyframes' not in vis and 'infinite' not in vis, 'visual: sin animaciones continuas ni revelado por scroll (una capa animada sobre un mazo abierto de 3800 px frenaba la página)')
print('failed:', len(fails))
sys.exit(1 if fails else 0)

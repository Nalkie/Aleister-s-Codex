"""Gate: página «Fuentes y licencia» y enlaces «Reportar un error» (item 9).  Run from the project root:  python tests/check_about.py

  1. la ruta ?mode=about abre la vista 'abt' (la regla real de rutas, en node) y vuelve a armarse igual; la vista no tiene pestaña y el render no se rompe por eso
  2. el pie trae los dos botones; el handler abre reportUrl en una pestaña nueva con noopener
  3. reportUrl (función real, en node): apunta a issues/new del repositorio, la página actual va codificada en el cuerpo, 'idea' cambia el formulario, nada personal
  4. viewAbout (función real, en node): cada fuente tiene enlace https, la licencia CC BY-SA 4.0 de Yugipedia con el aviso de modificación y ShareAlike, la marca de Konami, y no dice banish/banear
  5. toda fuente de datos que cita el pie «Fuentes y límites» con enlace propio aparece en la tabla (no queda una fuente sin acreditar)
  6. el idioma: tools/i18n_en.json trae los textos de esta vista
"""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


def node(js):
    f = os.path.join(tempfile.mkdtemp(), 't.js')
    open(f, 'w', encoding='utf-8').write(js)
    r = subprocess.run(['node', f], capture_output=True, text=True, encoding='utf-8')
    return (json.loads(r.stdout) if r.returncode == 0 else None), r.stderr[:300]


src = open('src.html', encoding='utf-8').read().replace('\r\n', '\n')

# 1. ruta
rm = re.search(r'const ROUTE_MODES=.*?function routeBuild\(st\)\{.*?\n\}\n', src, re.S)
ok(bool(rm), 'src.html trae el bloque de rutas')
if rm:
    js = (r"const slug=s=>String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-');" + '\n' + rm.group(0) + '''
const r=routeParse('?mode=about'), o={name:r.name,mode:r.mode,back:routeBuild({mode:'abt',tcgf:'',view:'meta',deck:''}),other:routeParse('?mode=glossary').mode};
console.log(JSON.stringify(o));''')
    o, err = node(js)
    ok(o is not None, 'las rutas corren en node %s' % err)
    if o:
        ok(o['name'] == 'about' and o['mode'] == 'abt', '?mode=about -> vista abt')
        ok(o['back'] == '?mode=about', 'la vista abt se vuelve a escribir como ?mode=about (%s)' % o['back'])
        ok(o['other'] == 'glos', 'las demás rutas siguen igual')
ok("abt:['Fuentes y licencia',viewAbout]" in src and 'id="tab-abt"' not in src, 'abt está en MODES y no tiene pestaña')
ok("const t=$('#tab-'+m); if(t) t.setAttribute('aria-selected'" in src, 'render() no falla por la falta de pestaña de abt')

# 2. pie y handler
foot = src[src.index('<footer>'):src.index('</footer>')]
ok('data-gomode="abt">Fuentes y licencia</button>' in foot and 'data-report="1">Reportar un error</button>' in foot, 'el pie trae «Fuentes y licencia» y «Reportar un error»')
ok(re.search(r"if\(d\.report!==undefined\)\{ window\.open\(reportUrl\(d\.report\),'_blank','noopener'\); return; \}", src), 'el handler abre reportUrl en pestaña nueva con noopener')

# 3 y 4. funciones reales
m = re.search(r"const REPO=.*?\nfunction rouCopy\(\)", src, re.S)
ph = re.search(r'const pageHead=.*?\n', src).group(0)
ok(bool(m), 'src.html trae reportUrl y viewAbout')
if m:
    body = m.group(0)[:-len('function rouCopy()')]
    js = '''let mode='glos'; const MODES={glos:['Glosario'],abt:['Fuentes y licencia']}; const document={title:'Glosario y reglas'};
function pageShareUrl(){ return 'https://x.test/app/p/glossary-hand-trap'; }
%s
%s
const u=new URL(reportUrl('1')), v=new URL(reportUrl('idea')), html=viewAbout();
console.log(JSON.stringify({u:u.origin+u.pathname,t:u.searchParams.get('title'),b:u.searchParams.get('body'),vt:v.searchParams.get('title'),vb:v.searchParams.get('body'),html,repo:REPO}));''' % (ph, body)
    o, err = node(js)
    ok(o is not None, 'reportUrl y viewAbout corren en node %s' % err)
    if o:
        ok(o['u'] == 'https://github.com/Nalkie/Aleister-s-Codex/issues/new', 'reportUrl apunta a issues/new del repositorio')
        ok(o['t'].startswith('Error en: ') and 'Página: https://x.test/app/p/glossary-hand-trap' in o['b'] and 'Sección: Glosario' in o['b'] and '**Qué está mal**' in o['b'], 'el aviso de error lleva la página actual y la sección en el cuerpo')
        ok(o['vt'].startswith('Sugerencia') and '**Qué te gustaría ver**' in o['vb'] and 'Qué está mal' not in o['vb'], 'la sugerencia usa su propio formulario')
        ok(not re.search(r'@|mail|token|password', o['b'] + o['vb'], re.I), 'el aviso no lleva datos personales')
        h = o['html']
        links = re.findall(r'<a href="(https?://[^"]+)" target="_blank" rel="noopener noreferrer"', h)
        ok(len(links) >= 10 and all(l.startswith('https://') for l in links), 'cada fuente tiene enlace https con rel noopener (%d)' % len(links))
        ok('CC BY-SA 4.0' in h and 'creativecommons.org/licenses/by-sa/4.0/' in h and 'ShareAlike' in h and 'modificación' in h and 'Yugipedia' in h, 'acredita a Yugipedia con CC BY-SA 4.0, ShareAlike y el aviso de modificación')
        ok('Autor: Bespresso' in h and '(Bespresso) con un enlace' in h and re.search(r'github.com/Nalkie/Aleister-s-Codex/blob/main/LICENSE"[^>]*>MIT</a>', h), 'la página nombra al autor (Bespresso), lo pide en la atribución y enlaza la licencia MIT del código')
        ok('Konami' in h and 'marcas' in h and 'sin fines de lucro' in h, 'trae el aviso de marcas de Konami y de proyecto de fans')
        ok('data-report="1"' in h and 'data-report="idea"' in h, 'la página trae los botones de reporte y de sugerencia')
        ok(not re.search(r'banish|banear|banee', re.sub(r'<[^>]+>', ' ', h), re.I), 'sin banish/banear (en español se dice desterrar)')
        ok('<table class="abt-t">' in h and h.count('<tr>') == 13, 'tabla de fuentes: una fila por fuente (12) y su cabecera')
        ok(all(x in h for x in ('db.ygoresources.com', 'wsrv.nl', 'TCGplayer, Cardmarket, eBay, CoolStuffInc, Amazon', 'ygoprodeck.com')), 'la tabla acredita nombres en español (YGOResources), precios (las cinco tiendas del pie) y el proxy wsrv.nl')
        ok(re.search(r"textos originales y el historial de la banlist derivado de Yugipedia se comparten con la licencia <a href=\"https://creativecommons.org/licenses/by-sa/4.0/\"[^>]*>CC BY-SA 4.0</a>", h) and 'pertenece a sus dueños y no entra en esa licencia' in h and 'tiers, precios y recetas' in h, 'declara CC BY-SA 4.0 solo para los textos originales y el historial derivado de Yugipedia, con atribución, cambios y misma licencia, y deja fuera todo lo demás (cartas, imágenes, marcas, tiers, precios, recetas)')
        ok('El copyright de lo que se toma de cada una de estas páginas pertenece a sus dueños' in h and 'no reclama derechos' in h and 'API' not in re.sub(r'<[^>]+>', ' ', h) and 'condiciones propias' not in h and 'sin licencia declarada' not in h, 'la página dice que el copyright de lo tomado de cada fuente es de sus dueños, sin entrar en APIs ni condiciones de cada sitio')
        ok('href="https://forms.gle/7oeRKZ7M77ahZL6L6" target="_blank" rel="noopener noreferrer">Formulario de contacto' in h, 'la página trae el formulario de contacto (Google Forms) con rel noopener')
        # 5. toda fuente de datos que el pie enlaza está en la tabla
        hosts = set(re.findall(r'https?://(?:www\.)?([a-z0-9.-]+)/', ' '.join(re.findall(r'href="(https?://[^"]+)"', foot))))
        tbl = set(re.findall(r'https?://(?:www\.)?([a-z0-9.-]+)/', ' '.join(links)))
        skip = {'roadoftheking.com', 'ygorganization.com', 'creativecommons.org'}   # informes y licencias puntuales, no fuentes de datos
        miss = sorted(x for x in hosts if x not in tbl and x not in skip)
        ok(not miss, 'toda fuente de datos que enlaza el pie está en la tabla %s' % miss)

# el formulario: con CONTACT_FORM puesto, aparece el enlace https
if m:
    o2, err = node(js.replace("const CONTACT_FORM='https://forms.gle/7oeRKZ7M77ahZL6L6';", "const CONTACT_FORM='https://forms.example.test/f/abc';"))
    ok(o2 is not None and 'href="https://forms.example.test/f/abc" target="_blank" rel="noopener noreferrer">Formulario de contacto' in o2['html'], 'el enlace sigue a CONTACT_FORM: con otra dirección puesta, aparece «Formulario de contacto» con rel noopener')
cf = re.search(r"const CONTACT_FORM='([^']*)';", src)
ok(cf is not None and cf.group(1).startswith('https://'), 'CONTACT_FORM está vacío o es una dirección https')

ref = open('tools/refresh.py', encoding='utf-8').read()
ok('tests/check_form_live.py' in ref and 'tests/check_about.py' in ref and os.path.isfile('tests/check_form_live.py'), 'refresh.py corre este gate y el chequeo en vivo del formulario (que solo avisa)')

lic = open('LICENSE', encoding='utf-8').read() if os.path.isfile('LICENSE') else ''
ok(lic.startswith('MIT License') and 'Copyright (c) 2026 Bespresso' in lic and 'CC BY-SA 4.0' in lic, 'LICENSE: MIT, titular Bespresso, y aclara que cubre solo el código (textos y datos van con CC BY-SA 4.0)')
ok("open('tools/pr.py', encoding='utf-8').read().count(\"'LICENSE'\") == 1", 'tools/pr.py copia LICENSE al PR')

# 6. idioma
en = json.load(open('tools/i18n_en.json', encoding='utf-8'))
ok('Fuentes y licencia' in en and 'Código y datos en GitHub' in en and any(k.startswith('\n    <div class="abt-s"><h3>Fuentes') for k in en), 'i18n_en.json trae los textos de la vista')
print('failed:', len(fails))
sys.exit(1 if fails else 0)

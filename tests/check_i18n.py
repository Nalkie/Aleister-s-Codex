"""Gate test del selector de idioma (español / inglés) y de modo noche / día.  Sin red.  Run from the project root:  python tests/check_i18n.py

Qué comprueba
  * Todo texto en español de los scripts tiene traducción (tools/i18n.py lo envuelve con __t en cada build) y todas las traducciones conservan
    marcadores {n}, etiquetas HTML, entidades y espacios.
  * Todo texto del HTML fijo (encabezado, menú, pie) tiene su traducción.
  * La función __t de la página hace lo que dice: en español devuelve el original; en inglés traduce plantillas y cadenas, rellena los
    marcadores y, si falta una entrada, devuelve el español (la página nunca queda rota).  PL() pone los puestos de torneo en inglés.
  * El índice trae los selectores (banderas y modo noche / día) y el script que fija idioma y tema antes de dibujar.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'tools')
import i18n, i18n_check

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


# ---- cobertura e integridad del diccionario ----
src = open('src.html', encoding='utf-8').read().replace('/*__GUIDEX__*/', open('tools/guide_extra.js', encoding='utf-8').read())
wrapped, keys, _ = i18n.wrap_page(src)
en = i18n.load_dict()
missing = [k for k in keys if k not in en]
check(not missing, 'every Spanish text in the scripts has an English translation (%d texts%s)' % (len(keys), ', missing: ' + repr(missing[:3]) if missing else ''))
bad = [k for k, v in en.items() if i18n_check.problems(k, v)]
check(not bad, 'every translation keeps its {n} markers, HTML tags, entities and edge spaces%s' % ((': ' + repr(bad[:2])) if bad else ''))
unused = [k for k in en if k not in set(keys)]
check(len(unused) <= 40, 'the dictionary has no pile of stale entries (%d unused)' % len(unused))

# ---- HTML fijo ----
st = json.load(open('tools/i18n_static.json', encoding='utf-8'))
html = src[src.rindex('</style>') + 8: src.index('<script', src.rindex('</style>'))]
norm = lambda x: re.sub(r'\s+', ' ', x).strip()
foot = html[html.index('<footer'):]
lis = [norm(m.group(1)) for m in re.finditer(r'<li>(.*?)</li>', foot, re.S)]
check(all(k in st for k in lis), 'every footer paragraph has its English version (%d)' % len(lis))
for t in ('Qué se juega hoy', 'Buscador de cartas', 'Cajas y sets', 'Obtención en Duel Links', 'Guía', 'Eventos', 'Fuentes y límites', 'Preferencias', 'Idioma'):
    check(any(k.startswith(t) for k in st), 'static text translated: %s' % t)

# ---- la función de traducción de la página ----
page = open('index.html', encoding='utf-8').read()
check('function __t(a){' in page and 'const LANG = document.documentElement.lang' in page, 'index.html carries the translation function')
node = 'node'
core = re.search(r'function PL\(p\)\{.*?\n\}\nfunction __t\(a\)\{.*?\n\}\n', page, re.S)
check(bool(core), 'PL() and __t() found in index.html')
if core:
    harness = r'''
const results = [];
function run(LANG, EN) {
  const fn = new Function('LANG', 'EN', %s + '; return {PL, __t};');
  return fn(LANG, EN);
}
const EN = {'Hola {0}': 'Hello {0}', '{0} de {1} cartas': '{0} of {1} cards', 'mazo': 'deck', '<b>{0}</b> victorias': '<b>{0}</b> wins'};
const es = run('es', EN), en = run('en', EN);
const tag = (f, ...a) => f(...a);
results.push(es.__t('mazo') === 'mazo');
results.push(en.__t('mazo') === 'deck');
results.push(en.__t('desconocido') === 'desconocido');
results.push(en.__t`Hola ${'Ana'}` === 'Hello Ana');
results.push(es.__t`Hola ${'Ana'}` === 'Hola Ana');
results.push(en.__t`${3} de ${5} cartas` === '3 of 5 cards');
results.push(en.__t`<b>${7}</b> victorias` === '<b>7</b> wins');
results.push(en.__t`algo sin entrada ${1} y ${2}` === 'algo sin entrada 1 y 2');
results.push(en.PL('1.º puesto') === '1st place' && en.PL('2.º puesto') === '2nd place' && en.PL('3.º puesto') === '3rd place' && en.PL('11.º puesto') === '11th place');
results.push(en.PL('Top 4') === 'Top 4' && es.PL('2.º puesto') === '2.º puesto');
console.log(JSON.stringify(results));
''' % json.dumps(core.group(0))
    r = subprocess.run([node, '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['ES: identity on strings', 'EN: string lookup', 'EN: missing entry falls back to Spanish', 'EN: tagged template fills markers', 'ES: tagged template identity',
              'EN: markers can change order of meaning', 'EN: keeps markup in templates', 'EN: missing template falls back with values filled', 'PL ordinals', 'PL leaves other texts alone']
    check(len(res) == len(labels), 'node ran the translation harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:120]))
    for ok, lab in zip(res, labels):
        check(ok, '__t: ' + lab)

# ---- selectores ----
check('data-lang="es"' in page and 'data-lang="en"' in page, 'language selector with both flags')
check('data-theme-toggle' in page and "localStorage.getItem('codex_theme')" in page and "localStorage.getItem('codex_lang')" in page, 'night/day toggle and saved preferences')
check(page.index("localStorage.getItem('codex_lang')") < page.index('<style>'), 'language and theme are set before anything is drawn (no flash)')
check('--i-tools' in page and 'html[lang="en"]' in page, 'CSS labels follow the language')

print('failed:', len(fails))
sys.exit(1 if fails else 0)

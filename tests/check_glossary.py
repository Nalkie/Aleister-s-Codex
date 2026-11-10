"""Gate test del glosario (src/glossary/*.json -> data/glossary.js y la pestaña Glosario).  Sin red.  Run from the project root:  python tests/check_glossary.py

Outcome: cualquiera puede buscar un término del juego, leerlo en español o inglés y compartir su enlace.
  * tools/glossary.py: el contrato se cumple (claves, 15-80 palabras, es != en, sin raya larga, "desterrar", see y cards válidos, mínimos)
  * data/glossary.js coincide con lo que se genera hoy, está en files.json y en dist/
  * La página: pestaña, modo, ruta (?mode=glossary&term=...), vista con búsqueda y categorías, enlaces reales, título por término
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import glossary

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


items = glossary.load()
bad = glossary.problems(items)
check(not bad, 'the glossary meets its contract (%d problems%s)' % (len(bad), ': ' + bad[0] if bad else ''))
check(len(items) >= glossary.MIN_TERMS, '%d terms (minimum %d)' % (len(items), glossary.MIN_TERMS))
txt = open('data/glossary.js', encoding='utf-8').read() if os.path.isfile('data/glossary.js') else ''
check(txt == '__load("glossary",' + json.dumps(glossary.build(items), ensure_ascii=False, separators=(',', ':')) + ');', 'data/glossary.js is what tools/glossary.py makes today (run it after editing src/glossary)')
check(sum(1 for x in items if x['cards']) >= 15, 'at least 15 terms show example cards')
refs = {r for x in items for r in x['see']}
check(len(refs) >= 40, 'the terms point to each other (%d are referenced)' % len(refs))
check(all(not re.search(r'  +', x[l][k]) for x in items for l in ('es', 'en') for k in ('term', 'def')), 'no double spaces in the texts')

src = open('src.html', encoding='utf-8').read()
check('id="tab-glos" data-mode="glos"' in src and "glos:['Glosario',viewGlossary]" in src and "glossary:['glos','']" in src, 'the Glossary tab, its mode and its route are wired')
check("loadData('glossary')" in src and 'function viewGlossary(' in src and 'id="gq"' in src and 'data-glcat' in src, 'the view loads its data lazily and has search and categories')
check('href="${glHref(x.s)}" data-glterm=' in src and 'a[data-glterm]' in src and 'function glPend(' in src, 'terms and related terms are real anchors that scroll to the term')
check("out.term=archSlug(q.get('term')||'')" in src and "q.set('term',st.term)" in src and 'glTitle()' in src, 'the route carries the term and the title shows it')
check('Se menciona en:' in src and 'function lk=' not in src and 'const lk=r=>' in src and 'ENG.scroll' in src, 'every term lists who mentions it, and an engine deep link scrolls to the opened engine')
check("normalize('NFD').replace(/[\u0300-\u036f]/g,'')" in src and 'function engBlock(' in src, 'search ignores accents (pendulo finds Péndulo) and an engine link scrolls to the engine block')
check("if(was==='glos'||was==='arq'||was==='lore')" in src, 'a card link from the glossary, a hub or the Lore scrolls to the card detail')
check('data-glretry' in src and 'GL.err' in src, 'a failed load shows a retry button')

files = [f['path'] for f in json.load(open('files.json', encoding='utf-8'))]
check('data/glossary.js' in files, 'data/glossary.js is listed in files.json')
if os.path.isdir('dist'):
    check(os.path.isfile('dist/data/glossary.js'), 'dist/ has data/glossary.js')

page = open('index.html', encoding='utf-8').read()
core = re.search(r'const ROUTE_MODES=.*?function routeBuild\(st\)\{.*?\n\}\n', page, re.S)
check(bool(core), 'the route helpers are in index.html')
if core:
    harness = r'''
const slug = s => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-');
%s
const t = [];
let r = routeParse('?mode=glossary&term=Hand-Trap');  t.push(r.mode==='glos' && r.name==='glossary' && r.term==='hand-trap');
r = routeParse('?mode=glossary&term=%%3Cb%%3E');  t.push(/^[a-z0-9-]*$/.test(r.term));
r = routeParse('?mode=tcg&term=x');  t.push(r.term==='');
t.push(routeBuild({mode:'glos',tcgf:'',view:'meta',deck:'',term:'cadena'})==='?mode=glossary&term=cadena');
t.push(routeBuild({mode:'glos',tcgf:'',view:'meta',deck:'',term:''})==='?mode=glossary');
t.push(routeName('glos','')==='glossary');
console.log(JSON.stringify(t));
''' % core.group(0)
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['glossary URL gives the term', 'term slug is sanitised', 'term= is ignored outside the glossary', 'term URL is written back', 'index URL has no term', 'routeName for the glossary']
    check(len(res) == len(labels), 'the route harness ran (%s)' % (r.stderr.strip()[:120] if r.stderr else 'ok'))
    for ok, l in zip(res, labels):
        check(ok, l)

print('\nfailed: %d' % len(fails))
sys.exit(1 if fails else 0)

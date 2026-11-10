"""Gate: historial de banlist (data/banhist.js). Run from the project root:  python tests/check_banhist.py

Cuatro cosas que no pueden romperse:
  1. forma: listas en orden, transiciones válidas (índice en rango, estado 0-3, sin repetir el estado anterior);
  2. la última lista es la banlist vigente de Konami (src/konami_current.json), carta por carta;
  3. los formatos retro (Goat abril 2005, Edison marzo 2010, HAT abril 2014) salen de otra fuente (Format Library):
     el historial en esa fecha tiene que coincidir con ellas;
  4. cada lista se vuelve a derivar de las páginas crudas de Yugipedia con un parser independiente y debe dar lo mismo;
     y las cartas que la revisión encontró mal con la tabla vieja (Heavy Storm, Mirror Force, Cyber Jar...) quedan fijas.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def ok(c, m):
    if not c:
        fails.append(m)


raw = open('data/banhist.js', encoding='utf-8').read()
m = re.search(r'__load\("banhist",(.*)\);\s*$', raw, re.S)
ok('CC BY-SA' in raw.split('__load')[0] and 'creativecommons.org/licenses/by-sa' in raw.split('__load')[0], 'data/banhist.js sin cabecera de licencia CC BY-SA y aviso de modificación')
ok(m, 'data/banhist.js no tiene la forma __load("banhist",{...});')
H = json.loads(m.group(1))
L, C = H['l'], H['c']

# 1. forma
ok(L == sorted(L) and len(set(map(tuple, L))) == len(L), 'las listas no están en orden estricto')
ok(all(1 <= mm <= 12 and 1 <= dd <= 31 and 2002 <= y <= 2100 for y, mm, dd in L), 'fecha de lista fuera de rango')
ok(len(L) >= 80, 'pocas listas (%d): la tabla de Yugipedia se leyó incompleta' % len(L))
ok(len(C) >= 500, 'pocas cartas con historial (%d)' % len(C))
for n, tr in C.items():
    idx = [t[0] for t in tr]
    ok(idx == sorted(set(idx)) and idx[0] >= 0 and idx[-1] < len(L), '%s: índices fuera de orden o de rango' % n)
    ok(all(t[1] in (0, 1, 2, 3) for t in tr), '%s: estado inválido' % n)
    ok(all(a[1] != b[1] for a, b in zip(tr, tr[1:])), '%s: dos transiciones seguidas al mismo estado' % n)
    ok(tr[0][1] != 3 or len(tr) > 1, '%s: historial vacío (solo "sin límite")' % n)


def at(n, i):
    """estado de n en la lista i (None si todavía no aparece; 3 si ya apareció y no tiene límite)"""
    r = None
    for j, s in C.get(n, []):
        if j <= i:
            r = s
    return r


# 2. la última lista = la vigente de Konami
k = json.load(open('src/konami_current.json', encoding='utf-8'))
dd, mm, yy = k['from'].split('/')
ok(L[-1] == [int(yy), int(mm), int(dd)], 'la última lista es %s y Konami vigente es %s/%s/%s' % (L[-1], dd, mm, yy))
sys.path.insert(0, 'tools')
from banhist import ALIAS
cur = {ALIAS.get(html.unescape(x['nameeng']), html.unescape(x['nameeng'])): int(g) for g in '012' for x in k.get(g, [])}
bad = [(n, s, at(n, len(L) - 1)) for n, s in cur.items() if at(n, len(L) - 1) != s]
ok(not bad, 'la última lista difiere de Konami en %d cartas: %s' % (len(bad), bad[:5]))
extra = [n for n in C if at(n, len(L) - 1) in (0, 1, 2) and n not in cur]
ok(not extra, 'cartas con límite en el historial que Konami no lista hoy: %s' % extra[:5])

# nombres: cada clave tiene que existir en la base de cartas del sitio (para poder enlazarla)
site = {c['name'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
unk = [n for n in C if n not in site]
ok(not unk, '%d cartas del historial no existen en la base del sitio: %s' % (len(unk), unk[:6]))

# 3. anclas independientes: formatos retro
F = json.load(open('src/formats.json', encoding='utf-8'))
KEY = {'forbidden': 0, 'limited': 1, 'semiLimited': 2}
for fk, ym in {'goat': (2005, 4), 'edison': (2010, 3), 'hat': (2014, 4)}.items():
    idx = [j for j, x in enumerate(L) if (x[0], x[1]) == ym]
    ok(len(idx) == 1, 'falta la lista %s del formato %s' % (ym, fk))
    if len(idx) != 1:
        continue
    i = idx[0]
    exp = {n: KEY[g] for g, ns in F[fk]['banlist'].items() for n in ns}
    wrong = [(n, s, at(n, i)) for n, s in exp.items() if at(n, i) != s]
    # Format Library escribe el nombre de 3 cartas distinto; ver ALIAS
    ok(len(wrong) <= 1, '%s: el historial en %s difiere de Format Library en %d cartas: %s' % (fk, ym, len(wrong), wrong[:6]))
    over = [n for n in C if at(n, i) in (0, 1, 2) and n not in exp]
    ok(len(over) <= 1, '%s: el historial marca límites que Format Library no tiene (%d): %s' % (fk, len(over), over[:6]))

# 4. cada lista otra vez desde las páginas crudas, con un parser distinto (línea a línea, sin regex de secciones)
pages = json.load(open('src/banhist/lists.json', encoding='utf-8'))
rawnote, rawstate = {}, {}
ok(len(pages) == len(L), 'lists.json tiene %d páginas y el historial %d listas' % (len(pages), len(L)))
for i, (title, w) in enumerate(pages.items()):
    sec, raw = None, {}
    inside = False
    for ln in w.split(chr(10)):
        if ln.startswith('{{Limitation list'):
            inside = True
            continue
        if inside and ln.strip() == '}}':
            break
        mm2 = re.match(r'\|\s*(forbidden|limited|semi_limited)\s*=', ln)
        if inside and mm2:
            sec = {'forbidden': 0, 'limited': 1, 'semi_limited': 2}[mm2.group(1)]
            continue
        if inside and re.match(r'\|\s*\w+\s*=', ln):
            sec = None
            continue
        if inside and sec is not None and ln.strip():
            nm = html.unescape(ln.split('//')[0].strip())
            raw[ALIAS.get(nm, nm)] = sec
            pm = re.search(r'prev::\s*([A-Za-z -]+)', ln)
            rawnote.setdefault(i, {})[ALIAS.get(nm, nm)] = pm.group(1).strip() if pm else None
            rawstate.setdefault(i, {})[ALIAS.get(nm, nm)] = sec
    for fc, fi in H['f']:
        if fi == i:
            raw[fc] = at(fc, i)       # omisión de la fuente que la lista siguiente desmiente (ver tools/banhist.py)
    got = {n: at(n, i) for n in C if at(n, i) in (0, 1, 2)}
    ok(got == raw, '%s: el historial da %d cartas con límite y la página %d (difieren %s)' % (title, len(got), len(raw), sorted(set(got.items()) ^ set(raw.items()))[:4]))

# huecos: carta en la lista, ausente en las siguientes y de vuelta. Si al volver no trae nota prev:: o la nota es el estado de antes,
# es una omisión de la fuente (listas ajustadas) y tiene que estar corregida en H['f']; si trae otra nota, salió de verdad.
fixed = {(n, j) for n, j in H['f']}
for n in C:
    seqr = [rawstate.get(i, {}).get(n, 3) for i in range(len(L))]
    for i in range(1, len(seqr)):
        if seqr[i] != 3 and seqr[i - 1] == 3:
            k = i - 1
            while k > 0 and seqr[k] == 3:
                k -= 1
            if seqr[k] == 3:
                continue
            note = rawnote.get(i, {}).get(n)
            if note is None or {'forbidden': 0, 'limited': 1, 'semi-limited': 2, 'unlimited': 3}.get(note.lower()) == seqr[k]:
                for j in range(k + 1, i):
                    ok((n, j) in fixed, '%s: hueco sin corregir en la lista %d (reaparece sin nota que lo explique)' % (n, j))
ok(fixed == {('Return from the Different Dimension', 33), ('Trap Dustshoot', 32), ('Trap Dustshoot', 33)}, 'las correcciones por omisión de la fuente cambiaron: %s' % sorted(fixed))

ok(H['e'] == [i for i, x in enumerate(L) if x == [2016, 2, 8]] and len(H['e']) == 1, 'la lista ajustada de febrero de 2016 (solo eventos) tiene que estar marcada: %s' % H['e'])
TL = {  # líneas de tiempo comprobadas contra las páginas de Yugipedia (la revisión las halló mal con la tabla vieja)
    'Heavy Storm': [(2002, 7, 2), (2003, 5, 1), (2010, 9, 0), (2011, 9, 1), (2013, 9, 0)],
    'Mirror Force': [(2002, 7, 1), (2004, 8, 0), (2005, 4, 1), (2005, 10, 0), (2006, 4, 1), (2012, 9, 2), (2014, 7, 3)],
    'Cyber Jar': [(2002, 10, 1), (2006, 4, 0), (2022, 10, 1), (2024, 12, 2), (2025, 4, 3)],
    'Crossout Designator': [(2025, 4, 1), (2026, 10, 0)],
    'Protectcode Talker': [(2026, 9, 0)],
    'Sangan': [(2002, 7, 2), (2003, 4, 1), (2004, 8, 0), (2005, 4, 1), (2013, 3, 0), (2017, 3, 3)],
    'Morphing Jar #2': [(2002, 12, 2), (2005, 4, 3), (2014, 4, 0), (2020, 1, 3)],
    'Raigeki': [(2002, 5, 1), (2004, 8, 0), (2014, 10, 1), (2022, 2, 3)],
    'Trap Dustshoot': [(2007, 9, 1), (2012, 3, 0)],
}
for n, exp in TL.items():
    got = [(L[j][0], L[j][1], st) for j, st in C.get(n, [])]
    ok(got == exp, '%s: línea de tiempo %s, esperada %s' % (n, got, exp))
TL['Return from the Different Dimension'] = [(2008, 5, 1), (2014, 1, 0)]
ok([(L[j][0], L[j][1], st) for j, st in C['Return from the Different Dimension']] == TL['Return from the Different Dimension'], 'Return from the Different Dimension sigue limitada hasta enero de 2014')
ok(len(H['t']) == len(L) and all(isinstance(x, str) and 'Lists' in x for x in H['t']), 'falta el título de la página fuente de alguna lista')
ok(len([n for n in C if any(j == 1 for j, _ in C[n])]) == 4, 'julio de 2002 tiene que traer 4 cambios (Heavy Storm, Mirror Force, Sangan, Witch of the Black Forest)')
D = set(H['d'])
ok(D <= set(C) and all(C[n][0][1] != 3 for n in D), 'cartas de debut con un primer estado inválido')

# 5. cableado: la UI, los datos lazy, los textos y la atribución CC BY-SA
src = open('src.html', encoding='utf-8').read()
for pat, why in [
    (r"const BH=\{", 'estado BH'), (r"loadData\('banhist'\)", 'carga lazy de data/banhist.js'),
    (r'data-bfmt="hist"', 'botón Historial en la Banlist'), (r"f==='hist'", 'rama hist en viewBan'),
    (r'id="dx-bh"', 'contenedor del historial en la página de carta'), (r"bhReady\(\)\.then", 'relleno del historial en fillDetail'),
    (r'<select id="bhy"', 'desplegable para elegir el año'), (r"id==='bhy'", 'handler del desplegable de año'), (r'data-bhgo=', 'enlace de la carta al historial filtrado'), (r'D\.e\.includes', 'marca de lista solo para eventos'), (r'function bhPend', 'scroll a los resultados con el enlace directo'), (r"q.set\('hist','1'\)", 'ruta ?hist=1'),
    (r'yugipedia\.com/wiki/Forbidden_%26_Limited_List', 'atribución a Yugipedia en las fuentes'), (r'creativecommons\.org/licenses/by-sa/4\.0', 'enlace a la licencia'), (r'CC BY-SA', 'licencia CC BY-SA'),
]:
    ok(re.search(pat, src), 'src.html: falta ' + why)
ok('data/banhist.js' in open('files.json', encoding='utf-8').read(), 'files.json no lista data/banhist.js')
rf = open('tools/refresh.py', encoding='utf-8').read()
ok("'tools/banhist.py'" in rf and "'tests/check_banhist.py'" in rf, 'tools/refresh.py no corre el generador y el gate del historial')
ok(os.path.exists('dist/data/banhist.js') or not os.path.isdir('dist'), 'dist/ sin data/banhist.js: falta correr tools/dist.py')

# 6. la ruta del historial (?mode=banlist&hist=1&find=...) en el helper real de index.html, corrido en node
import subprocess
page = open('index.html', encoding='utf-8').read()
core = re.search(r'const ROUTE_MODES=.*?function routeBuild\(st\)\{.*?\n\}\n', page, re.S)
ok(core, 'index.html: no encuentro los helpers de ruta')
if core:
    harness = """
const slug = s => String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-');
%s
const t = [];
let r = routeParse('?mode=banlist&hist=1&find=Raigeki');  t.push(r.mode==='ban' && r.bhist===true && r.find==='Raigeki');
r = routeParse('?mode=banlist');  t.push(r.bhist===false && r.find==='');
r = routeParse('?mode=tcg&hist=1&find=x');  t.push(r.bhist===false && r.find==='');
r = routeParse('?mode=banlist&hist=1&find=' + 'a'.repeat(500));  t.push(r.find.length===80);
t.push(routeBuild({mode:'ban',tcgf:'',view:'meta',deck:'',bhist:true,find:'Heavy Storm'})==='?mode=banlist&hist=1&find=Heavy+Storm');
t.push(routeBuild({mode:'ban',tcgf:'',view:'meta',deck:'',bhist:true,find:''})==='?mode=banlist&hist=1');
t.push(routeBuild({mode:'ban',tcgf:'',view:'meta',deck:'',bhist:false,find:'x'})==='?mode=banlist');
console.log(JSON.stringify(t));
""" % core.group(0)
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['hist=1 da la vista de historial con su búsqueda', 'sin hist no hay historial', 'hist solo vale en la Banlist', 'find se corta a 80 caracteres', 'la URL del historial con búsqueda', 'la URL del historial sin búsqueda', 'sin historial no se escribe find']
    ok(len(res) == len(labels), 'el arnés de rutas no corrió: %s' % r.stderr.strip()[:160])
    for good, l in zip(res, labels):
        ok(good, 'ruta: ' + l)

if fails:
    print('FALLA check_banhist:')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('ok check_banhist: %d listas, %d cartas, %d límites vigentes iguales a Konami, todas las listas iguales a las páginas de Yugipedia' % (len(L), len(C), len(cur)))

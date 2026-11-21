"""Gate: las figuras de la Guía (tablero, fases, cadena, esquemas de invocación) siguen alineadas con el texto que ilustran.  Run from the project root:  python tests/check_guide.py

Las figuras se dibujan por posición (GBASICS[i] ilustra el paso i de «Cómo se juega», SUMFIG[i] la invocación i): si alguien reordena
tools/guide_data.js / guide_extra.js sin mover la figura, la Guía mostraría el dibujo del Sincro bajo el texto del Link.  Este test lo atrapa.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


src = open('src.html', encoding='utf-8').read().replace('\r\n', '\n')
data = open('tools/guide_data.js', encoding='utf-8').read() + open('tools/guide_extra.js', encoding='utf-8').read()

# 1. pasos de «Cómo se juega»: la figura i va con el paso i
titles = re.findall(r"\{t:'([^']+)',p:'", data)
m = re.search(r"const GBASICS=\[([^\]]*)\]", src)
keys = re.findall(r"'(\w+)'", m.group(1)) if m else []
want = [('El objetivo', 'goal'), ('El tablero', 'board'), ('Un turno', 'turn'), ('Tipos de carta', 'ctypes'), ('Formas de invocar', 'summon'), ('Cadenas', 'chain')]
ok(len(keys) == len(want) and all(titles[i].startswith(t) and keys[i] == k for i, (t, k) in enumerate(want)), 'GBASICS: goal/board/turn/ctypes/summon/chain van con los pasos 1 a 6 de la guía (%s)' % keys)
ok(all(('  %s:' % k) in src or (' %s:()' % k) in src for k in keys), 'cada clave de GBASICS tiene su figura en GFIG')

# 2. invocaciones: SUMFIG[i] va con la invocación i
names = re.findall(r"\{n:'([^']*)',intro", data)
order = ['Invocaci', 'Ritual', 'Fusi', 'Sincro', 'Xyz', 'P', 'Link']
m = re.search(r"const SUMFIG=\[(.*?)\n\];", src, re.S)
n_fig = len(re.findall(r"^  \(\)=>", m.group(1), re.M)) if m else 0
ok(n_fig == 7 and len(names) >= 7 and all(names[i].startswith(p) for i, p in enumerate(order)) and names[5].endswith('ndulo'), 'SUMFIG: 7 esquemas, en el orden Normal, Ritual, Fusión, Sincro, Xyz, Péndulo, Link (%d figuras)' % n_fig)

# 3. cartas reales de la figura de tipos existen
ids = {r['name'] for r in json.load(open('src/ygo_all.json', encoding='utf-8'))}
ex = re.findall(r"\['([^']+)','(?:Monstruo|Hechizo|Trampa)'", src)
ok(len(ex) == 3 and all(e in ids for e in ex), 'las tres cartas de ejemplo (monstruo, hechizo, trampa) existen en la base: %s' % ex)

# 4. cada color de marco que se usa tiene su regla CSS
used = set(re.findall(r"gfc\('(\w+)'", src))
css = set(re.findall(r"\.gfc\.(\w+)", src))
ok(used and used <= css, 'todos los marcos usados (%s) tienen estilo' % ', '.join(sorted(used)))
used_s = set(re.findall(r"\['(\w\w)','[A-ZÁÉÍÓÚ][^']*'\]", src[src.index('const GFIG'):src.index('const GBASICS')]))
ok({'nm', 'ef', 'rit', 'fu', 'sy', 'xy', 'lk', 'pe'} <= set(re.findall(r"\.gfs\.(\w+)", src)), 'las ocho etiquetas de marco de monstruo tienen estilo')

# 5. el tablero: las 9 zonas están numeradas una vez en la leyenda y el dibujo
blk = src[src.index('board:()=>'):src.index('turn:()=>')]
leg = re.findall(r"\['(\w)',(\d),'", blk)
ok(sorted(int(n) for _, n in leg) == list(range(1, 10)), 'la leyenda del tablero numera las 9 zonas, una vez cada una')
ok(blk.count("z('m',1,c,2,'Monstruo')") == 1 and "c===2||c===6?8:2" in blk and "'Péndulo':'Hechizo'" in blk, 'el tablero tiene 5 zonas de monstruo y 5 de hechizo/trampa (las de los extremos son de Péndulo)')

# 6. la figura de fases: seis fases
t = src[src.index('turn:()=>'):src.index('ctypes:()=>')]
ok(len(re.findall(r"\['(?:Robar|Inicio|Principal 1|Batalla|Principal 2|Final)'", t)) == 6, 'la figura del turno lista las 6 fases en orden')

# 6b. cada celda del tablero lleva su nombre (se ve en escritorio) y su número (celular y leyenda)
ok(len(re.findall(r"z\('[a-z]',\d,[^)]*,'[^']+'\)", blk)) + blk.count("z(c===2||c===6?'p':'s'") >= 7 and 'data-t=' in blk and 'content:attr(data-t)' in src and 'content:attr(data-n)' in src, 'las celdas del tablero llevan nombre (escritorio) y número (celular)')
# 6c. el ejemplo real de Fusión existe en la base de cartas
fus = re.findall(r"'(Elemental HERO [A-Za-z ]+)'", src)
ok(len(set(fus)) == 3 and all(e in ids for e in fus), 'las tres cartas reales del ejemplo de Fusión existen: %s' % sorted(set(fus)))

# 6d. Sincro con cartas reales (Nivel 3 Tuner + Nivel 5 = Nivel 8) y Link con mini tablero
rows = {r['name']: r for r in json.load(open('src/ygo_all.json', encoding='utf-8'))}
js, cd, sd = rows.get('Junk Synchron'), rows.get('Cyber Dragon'), rows.get('Stardust Dragon')
ok(bool(js and cd and sd) and js['type'] == 'Tuner Monster' and js['level'] == 3 and cd['level'] == 5 and sd['type'] == 'Synchro Monster' and sd['level'] == 8 and js['level'] + cd['level'] == sd['level'], 'el ejemplo de Sincro es real: Junk Synchron (Tuner Nv3) + Cyber Dragon (Nv5) = Stardust Dragon (Nv8)')
lk = src[src.index('class="glkb"'):src.index('class="glkl"')]
ok(lk.count("'ptd'") == 2 and lk.count("'lkc',1") == 1 and lk.count("['',''") + lk.count("['','ptd'") == 4 and '.glz.ptd' in src, 'el mini tablero del Link: 5 zonas, el Link en el medio apunta a las 2 contiguas (2 flechas = Link-2)')

# 6e. Ritual real, Set de costado y cadena apilada
r = {x['name']: x for x in json.load(open('src/ygo_all.json', encoding='utf-8'))}
bl, bs, dm, ku = r.get('Black Luster Ritual'), r.get('Black Luster Soldier'), r.get('Dark Magician'), r.get('Kuriboh')
ok(bool(bl and bs and dm and ku) and bs['type'] == 'Ritual Monster' and bs['level'] == 8 and dm['level'] + ku['level'] == bs['level'] and 'total Levels equal 8 or more' in bl['desc'], 'el ejemplo de Ritual es real: Black Luster Ritual pide Niveles que sumen 8 o más; Dark Magician (7) + Kuriboh (1) = 8; Black Luster Soldier es Ritual Nv8')
ok('class="gdef"' in src and '.gdef .gfc{transform:rotate(90deg)' in src, 'el monstruo en Set se dibuja de costado (defensa)')
ok(src.count('<i class="s1">') == 1 and '.gstk .s3' in src and 'Se activan ↑' in src and 'Se resuelven ↓' in src, 'la cadena se dibuja como pila de tres cartas con el sentido de activación y de resolución')
ge = open('tools/guide_extra.js', encoding='utf-8').read()
ok('Cuenta como tu Invocación Normal del turno' in ge, 'el texto de la guía dice que poner un monstruo en Set gasta la Invocación Normal')

# 6f. el turno de ejemplo: las cuentas del daño y de los LP son ciertas
rr = {x['name']: x for x in json.load(open('src/ygo_all.json', encoding='utf-8'))}
ge_, bo_ = rr.get('Gemini Elf'), rr.get('Battle Ox')
ok(bool(ge_ and bo_) and ge_['level'] == 4 and ge_['atk'] - bo_['atk'] == 200 and 8000 - (ge_['atk'] - bo_['atk']) == 7800 and rr.get('Mirror Force', {}).get('type') == 'Trap Card', 'el turno de ejemplo es real: Gemini Elf (Nv4, ATK 1900) vence a Battle Ox (ATK 1700): 200 de daño, 8000 a 7800 LP')
ex = src[src.index('example:()=>'):src.index('};' + chr(10) + 'const GBASICS')]
ok(len(re.findall(r"\['(?:Robar|Inicio|Principal 1|Batalla|Principal 2|Final)','", ex)) == 6 and '[8000,7800,200]' in ex and "GBASICS[i]==='turn'?GFIG.example()" in src, 'el turno de ejemplo recorre las 6 fases en orden y cuelga del paso «Un turno»')

# 6g. la batalla de ejemplo: ATK/DEF reales y las cuentas del texto
dmg, ge2, bo2, gs2 = rr.get('Dark Magician'), rr.get('Gemini Elf'), rr.get('Battle Ox'), rr.get('Giant Soldier of Stone')
ok(dmg['atk'] == 2500 and ge2['atk'] == 1900 and dmg['atk'] - ge2['atk'] == 600 and bo2['def'] == 1000 and ge2['atk'] > bo2['def'] and gs2['def'] == 2000 and ge2['atk'] < gs2['def'] and gs2['def'] - ge2['atk'] == 100, 'la batalla de ejemplo es real: 2500 menos 1900 = 600; ATK 1900 mayor que DEF 1000 (se destruye); ATK 1900 menor que DEF 2000 (100 de daño a quien ataca)')
bt = src[src.index('battle:()=>'):src.index('};' + chr(10) + 'const GBASICS')]
ok(bt.count("',cd(") == 4 and 'ATK 2500' in bt and 'DEF 1000' in bt and 'DEF 2000' in bt and "GFIG.example()+GFIG.battle()" in src, 'la batalla tiene los 4 casos (ataque, defensa menor, defensa mayor, directo) y cuelga del paso «Un turno»')

# 6h. Invocaciones: mapa + ficha por invocación; Tipos de mazo: mapa + perfil por estilo
sm = re.search(r"const SUMMETA=\[(.*?)\];", src, re.S).group(1)
sm_rows = re.findall(r"\['(\w+)','([^']*)'", sm)
ok([c for c, _ in sm_rows] == ['nm', 'rit', 'fu', 'sy', 'xy', 'pe', 'lk'] and sm_rows[0][1].startswith('Normal') and sm_rows[1][1] == 'Ritual' and sm_rows[2][1].startswith('Fusi') and sm_rows[3][1] == 'Sincro' and sm_rows[4][1] == 'Xyz' and sm_rows[5][1].startswith('P') and sm_rows[6][1] == 'Link', 'SUMMETA sigue el orden de las invocaciones (Normal, Ritual, Fusión, Sincro, Xyz, Péndulo, Link) y su color de marco')
ok(all(('.gsm[data-fr=%s]' % c) in src and ('.gsmap.%s' % c) in src for c, _ in sm_rows) and "d.gsgo!==undefined" in src and 'id="gs-${gi}"' in src, 'cada invocación tiene su color, su ancla y el botón del mapa que lleva hasta ella')
tn = re.findall(r"\{n:'([^']+)',e:'", data)
ty = re.search(r"const TYMETA=\[(.*?)\];", src, re.S).group(1)
ty_rows = re.findall(r"\['([^']+)',(\d),(\d),(\d),(\d),'", ty)
names_in_code = re.search(r"const TYNAMES=\[(.*?)\];", src).group(1)
nm_code = re.findall(r"'([^']+)'", names_in_code)
ok(len(tn) >= 7 and len(ty_rows) == 7 and len(nm_code) == 7 and [x.split(' (')[0].split(' /')[0].lower() for x in tn[:7]][:2] == ['agresivo', 'combo'] and tn[5].startswith('OTK') and nm_code[5].startswith('OTK') and tn[6] == 'Toolbox', 'TYMETA y TYNAMES siguen el orden de los 7 tipos de mazo de la guía (%s)' % ', '.join(nm_code))
ok(all(c in ids for c, *_ in ty_rows) and all(1 <= int(v) <= 5 for _, *vs in ty_rows for v in vs), 'las 7 cartas de ejemplo de los estilos existen y las valoraciones están entre 1 y 5')
pts = {(int(v), int(i)) for _, v, i, *_ in ty_rows}
ok(len(pts) == 7, 'en el mapa velocidad/interacción cada estilo cae en un punto distinto (%d puntos)' % len(pts))
ok(ty_rows[0][1] == '5' and ty_rows[2][2] == '5' and ty_rows[5][2] == '1', 'el Agresivo es de los más rápidos, el Control de los más interactivos y el OTK de los menos interactivos')

# 6i. Xyz, Péndulo y Link: paso a paso en lenguaje llano, con hechos verificables
ss = re.search(r"const SUMSTEPS=\{(.*?)\};\nconst sumSteps", src, re.S)
blocks = re.findall(r"\n  (\d):\['([^']+)',\[(.*?)\]\]", ss.group(1), re.S) if ss else []
ok([b[0] for b in blocks] == ['4', '5', '6'] and all(len(re.findall(r"\n\s+'", "\n" + b[2])) == 4 for b in blocks), 'SUMSTEPS: Xyz (4), Péndulo (5) y Link (6) tienen su frase y cuatro pasos')
cards = {r['name']: r for r in json.load(open('src/ygo_all.json', encoding='utf-8'))}
ok('2 Level 4 monsters' in cards['Number 39: Utopia']['desc'] and 'detach 1 material' in cards['Number 39: Utopia']['desc'], 'Utopia pide 2 monstruos de Nivel 4 y gasta 1 material para negar un ataque, como dice la figura Xyz')
ok(cards['Link Spider']['type'] == 'Link Monster' and cards['Link Spider']['desc'].startswith('1 Normal Monster') and 'Special Summon 1 Level 4 or lower Normal Monster from your hand' in cards['Link Spider']['desc'] and cards['Dark Magician']['type'] == 'Normal Monster', 'Link Spider pide 1 monstruo Normal e invoca desde la mano a su zona; Dark Magician es Normal')
hand = [(4, 1), (6, 1), (8, 1), (2, 0), (10, 0)]
ok(all((3 < n < 9) == bool(e) for n, e in hand) and '[[4,1],[6,1],[8,1],[2,0],[10,0]]' in src, 'Péndulo con Escalas 3 y 9: entran los Niveles 4, 6 y 8; el 2 y el 10 quedan fuera')

# 6j. Principiantes: camino de inicio, test de estilo (cada estilo se puede alcanzar) y botón de siguiente paso
import itertools
qz = re.search(r"const QUIZ=\[(.*?)\n\];?\nconst quizRes|const QUIZ=\[(.*?)\]\]\]\];\nconst quizRes", src, re.S)
qtxt = src[src.index('const QUIZ=['):src.index('const quizRes')]
qs = re.findall(r"\['([^']+)',\[\[", qtxt)
opts = []
for blk in re.split(r"\n  \['", qtxt)[1:]:
    opts.append([list(map(int, w.split(','))) for w in re.findall(r"\[(\d,\d,\d,\d,\d,\d,\d)\]", blk)])
ok(len(opts) == 3 and [len(o) for o in opts] == [5, 3, 2], 'QUIZ: 3 preguntas con 5, 3 y 2 respuestas, 7 puntajes cada una (%s)' % [len(o) for o in opts])
winners = set()
for combo in itertools.product(*opts):
    sc = [sum(c[i] for c in combo) for i in range(7)]
    winners.add(sc.index(max(sc)))
ok(winners == set(range(7)), 'el test puede recomendar cada uno de los 7 estilos (alcanzables: %s)' % sorted(winners))
ok(all(('%s:[' % k) in src for k in ('basics', 'formats', 'summons', 'types', 'decks', 'cards')) and 'const GNEXT=' in src and "data-gomode=\"deck\"" in src and "GD.tab==='basics') body=`${gPath()}${gQuick()}" in src, 'camino de inicio y esencial en 30 segundos arriba de Cómo se juega; siguiente paso al final de cada pestaña')
ok("id=\"gt-${ti}\"" in src and 'd.gtgo!==undefined' in src and "id==='ggq'" in src, 'el test lleva al estilo recomendado y el glosario tiene buscador')

# 7. estilo del proyecto: sin rayas largas en el texto de las figuras
fig = src[src.index('/* ---------- Guía: figuras'):src.index('function viewGuide()')]
ok('—' not in fig, 'sin rayas largas en las figuras')

# 8. sin imágenes externas nuevas: solo las cartas reales (cardImg) y SVG/HTML propio
ok('<img' not in fig.replace('<img src="art/lv-star.png"', '') and 'http' not in fig, 'las figuras no cargan imágenes ni enlaces externos (solo la estrella de Nivel, que es un archivo propio)')

print('failed:', len(fails))
sys.exit(1 if fails else 0)

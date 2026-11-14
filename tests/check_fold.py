"""Gate: tiers plegables y listas de cartas populares cortas (navegación más corta).  Run from the project root:  python tests/check_fold.py

  1. cada tier («Tier 1», «Poco resultado», «Ganaron sin ser meta»...) es un <details class="tier"> con el encabezado como <summary>; ya no queda ningún <div class="tier">
  2. grouped() y tierBlock() (funciones reales, en node): solo el primer tier sale abierto; la cabecera cerrada muestra hasta 4 mazos y «+N»; lo que el usuario abrió o cerró (TOPEN) manda
  3. cardChips(cards, cap) (real, en node): muestra solo las primeras 'cap' cartas y el resto queda en «Ver N cartas más»; con pocas de más no se pliega
  4. el cableado: recordar lo que el usuario abre o cierra, y abrir un mazo por enlace (?deck=) abre también su tier; las tablas de «Cartas más usadas» también se pliegan
  5. el CSS: la lista de nombres se oculta con el tier abierto y en pantallas angostas, y hay foco visible en la cabecera
"""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


src = open('src.html', encoding='utf-8').read().replace('\r\n', '\n')

# 1. marcado
ok('<div class="tier ' not in src and src.count('<details class="tier ') == 1, 'ningún tier queda como <div>; todos salen de tierBlock (un solo <details class="tier">)')
ok(src.count('tierBlock(') == 4 and "tierBlock('t-n','★','Ganaron sin ser meta'" in src, 'tierBlock lo usan grouped(), «Ganaron sin ser meta» y la Guía (4 apariciones con su definición)')
ok('<summary class="tierhead">' in src and 'aria-hidden="true"></span></summary>' in src, 'la cabecera del tier es el <summary> (teclado y lector de pantalla gratis) y la flecha es decorativa')

# 2 y 3. funciones reales
m = re.search(r"const ROMAN=.*?\nconst fmt=", src, re.S)
c = re.search(r"const moreBox=.*?\n\}\n", src, re.S)
ct = re.search(r"const capTable=.*?\n", src)
ok(bool(m and c and ct), 'src.html trae grouped, tierBlock, moreBox, capTable y cardChips')
if m and c and ct:
    js = '''const TIERS={T1:['t-1','Tier 1','el más fuerte'],T2:['t-2','Tier 2','top cut'],T3:['t-3','Tier 3','a veces llega'],R:['t-r','Poco resultado','bajo'],N:['t-n','Sin tier','x']};
let mode='tcg', TCGF='adv', dlFormat='speed'; const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;'), thumb=n=>'', fmt=0;
%s
%s
const tbl=(h,r)=>'<table>'+r.join('')+'</table>', rowsA=Array.from({length:14},(_,i)=>'<tr>'+i+'</tr>'), rowsB=Array.from({length:7},(_,i)=>'<tr>'+i+'</tr>');
const decks=[{n:'A',tier:'T1'},{n:'B',tier:'T1'},{n:'C',tier:'T2'},{n:'D',tier:'T2'},{n:'E',tier:'T2'},{n:'F',tier:'T2'},{n:'G',tier:'T2'},{n:'H',tier:'T2'},{n:'I',tier:'T3'}];
const r1=grouped(decks,(d,i)=>'<i>'+d.n+'</i>');
TOPEN['tcg/adv|T2']=true; TOPEN['tcg/adv|T1']=false; const r2=grouped(decks,(d,i)=>'');
mode='dl'; const r3=grouped(decks.slice(8),(d,i)=>'');
const cards=Array.from({length:36},(_,i)=>['C'+i,50]), few=Array.from({length:13},(_,i)=>['C'+i,5]);
console.log(JSON.stringify({capA:capTable([],rowsA,5,'filas'),capB:capTable([],rowsB,5,'filas'),r1,r2,r3,big:cardChips(cards,12),few:cardChips(few,12),none:cardChips(cards)}));''' % (m.group(0)[:-len('const fmt=')], c.group(0))
    f = os.path.join(tempfile.mkdtemp(), 'fold.js')
    open(f, 'w', encoding='utf-8').write(js)
    r = subprocess.run(['node', f], capture_output=True, text=True, encoding='utf-8')
    o = json.loads(r.stdout) if r.returncode == 0 else None
    ok(o is not None, 'las funciones corren en node %s' % r.stderr[:300])
    if o:
        t1 = re.findall(r'<details class="tier (t-\w)"[^>]*?( open)?>', o['r1'])
        ok([x[0] for x in t1] == ['t-1', 't-2', 't-3'] and [bool(x[1]) for x in t1] == [True, False, False], 'solo el primer tier sale abierto (%s)' % t1)
        ok('<span class="tprev">A · B</span>' in o['r1'] and 'C · D · E · F +2' in o['r1'] and '2 mazos' in o['r1'] and '6 mazos' in o['r1'] and '1 mazo<' in o['r1'], 'la cabecera cerrada lista hasta 4 mazos y «+N», y cuenta bien (2, 6 y 1 mazo)')
        t2 = re.findall(r'<details class="tier (t-\w)"[^>]*?( open)?>', o['r2'])
        ok([bool(x[1]) for x in t2] == [False, True, False], 'lo que el usuario abrió o cerró (TOPEN) manda sobre el valor por defecto (%s)' % t2)
        ok('data-tk="dl/speed|T3"' in o['r3'] and ' open>' in o['r3'], 'el estado se guarda por vista y formato (clave dl/speed|T3) y el primer tier de otra vista sale abierto')
        n = lambda h: len(re.findall(r'class="cc"', h))
        ok(n(o['big']) == 36 and o['big'].count('<details class="more">') == 1 and 'Ver 24 cartas más' in o['big'] and o['big'].index('<details class="more">') > o['big'].index('data-card="C11"') and o['big'].index('data-card="C12"') > o['big'].index('<details class="more">'), 'con 36 cartas y tope 12: 12 a la vista y «Ver las 24 restantes» con las otras 24')
        ok(o['capA'].count('<tr>') == 14 and o['capA'].count('<details class="more">') == 1 and 'Ver 9 filas más' in o['capA'] and o['capB'].count('<details') == 0 and o['capB'].count('<tr>') == 7, 'capTable: 14 filas muestran 5 y pliegan 9; con 7 (cap+2) salen todas')
        ok('class="more"' not in o['few'] and n(o['few']) == 13, 'con una o dos cartas de más no se pliega (13 con tope 12 salen todas)')
        ok('class="more"' not in o['none'] and n(o['none']) == 36, 'sin tope (las cartas de cada mazo) no cambia nada')
        ok('class="mc">Mostrar menos</span>' in o['big'], 'el botón tiene su texto de «Mostrar menos» al abrirse')

# 4. cableado
ok("document.addEventListener('toggle',e=>{ const t=e.target; if(t&&t.matches&&t.matches('details.tier[data-tk]')) TOPEN[t.dataset.tk]=t.open; },true);" in src, 'se recuerda lo que el usuario abre o cierra (toggle no burbujea: escucha en captura)')
ok("el.open=true; const tr=el.closest('details.tier'); if(tr){ tr.open=true; TOPEN[tr.dataset.tk]=true; }" in src, 'abrir un mazo por enlace (?deck=) abre también su tier')
ok("return capTable(head,rows.map(row),8,'cartas');" in src and 'cardChips(usage,16)' in src, 'las tablas de «Cartas más usadas» (8 filas) y los chips (16) se pliegan')
ok('r.du.slice(0,6).map(' in src and 'class="tmore"' in src and 'r.du.length>6' in src, 'cada fila de «Cartas más usadas» lista 6 mazos y «+N» (el resto en el título y en la ficha de la carta): la columna de mazos era lo que más alto hacía la fila')
ok(src.count('enginesTable(TCG_ENGINES,8)') == 1 and src.count('enginesTable(TCG_ENGINES)') == 1 and 'enginesTable(DL_ENGINES,8)' in src and "return cap?capTable(head,rows,cap,'motores'):tbl(head,rows);" in src, '«Motores y arquetipos» de las vistas TCG y Duel Links muestra 8 filas y pliega el resto; la pestaña Engines («Combinaciones a mano») sigue completa')
ok("const cards=rs=>rs.length>14?gal(rs.slice(0,12))+moreBox(rs.length-12,gal(rs.slice(12)),'cartas'):gal(rs);" in src, '«Cartas recomendadas»: 12 cartas a la vista y el resto plegado (con 14 o menos salen todas)')

# 5. CSS
ok('.tier[open] > .tierhead .tprev{display:none}' in src and '@media(max-width:760px){.tprev{display:none}}' in src and '.tierhead:focus-visible{outline' in src, 'la lista de nombres se oculta con el tier abierto y en pantallas angostas, y la cabecera tiene foco visible')
ok('.more[open] .mo{display:none}' in src and '.more .mc{display:none}' in src, 'los textos de «Ver N cartas más» y «Mostrar menos» se alternan con CSS')
ok('.more > summary::after{content:"+"' in src and '.more[open] > summary::after{content:"−"}' in src, 'el botón de «Ver N … más» lleva + (cerrado) y el signo menos (abierto), como las demás cajas plegables')
ok('@media(max-width:520px){.recgal{grid-template-columns:repeat(3,minmax(0,1fr))' in src, '«Cartas recomendadas» usa 3 columnas en el celular (con 2, cada ficha medía unos 315 px de alto)')
ok("const ROUTE_VIEWS=['meta','recs','cost','staples','engines'];" in src and "['Cartas recomendadas','recs'],['Cuánto cuesta armarlo','cost']" in src and "${b('recs','Cartas recomendadas')}${b('cost','Cuánto cuesta armarlo')}" in src, 'los accesos directos de sección incluyen «Cartas recomendadas» y «Cuánto cuesta armarlo» (las secciones más largas de Duel Links)')

ok("<details class=\"gfold\"${gi===0?' open':''}><summary><h3>${esc(r)}</h3>" in src and '.gfold[open] > summary::after{content:"−"}' in src, 'Guia > Cartas clave: un desplegable por rol (el primero abierto) con su cantidad')

ok('.tier:not([open])::before{display:none}' in src and 'height:min(340px,100%)' in src, 'el halo de color del tier no se dibuja con el tier plegado y nunca pasa del alto del tier (si no, se derrama sobre los tiers y títulos de abajo)')

print('failed:', len(fails))
sys.exit(1 if fails else 0)

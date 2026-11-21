"""Gate: la página de Inicio y la barra separada en Herramientas / Explorar.  python tests/check_home.py

  1. la página abre en Inicio (no en TCG) y Inicio está en MODES, en las rutas y en la barra
  2. la barra tiene dos filas por intención: Cartas y mazos (9) y Aprender y descubrir (Inicio + 5)
  3. Inicio agrupa por lo que querés hacer (4 grupos con ilustración), una tarjeta por botón, y cada una abre un modo que existe
  4. el buscador de Inicio y el camino para principiantes están cableados; el título de Inicio es el del sitio solo
  5. en la página generada (index.html) y en inglés también está todo
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
ok("let mode='home';" in src and "home:['Página de inicio',viewHome]" in src and "home:['home','']" in src and "home:'home'" in src, 'abre en Inicio y Inicio está en MODES y en las rutas')

navs = re.findall(r'<nav class="tools" data-cat="(\w+)" role="tablist" aria-label="([^"]+)"[^>]*>(.*?)</nav>', src, re.S)
ok(len(navs) == 4, 'la barra tiene cuatro categorías con sus botones')
ids = {c: re.findall(r'id="tab-(\w+)" data-mode', body) for c, _, body in navs}
EXP = {'find': ['fnd', 'ex', 'sets', 'obt', 'ban'], 'build': ['arq', 'eng', 'rou', 'deck'], 'learn': ['guide', 'glos'], 'discover': ['lore', 'ser', 'ev']}
ok(ids == EXP, 'categorías Cartas, Mazos, Aprender, Descubrir con sus botones: %s' % ids)
cats = re.findall(r'<button class="cat" role="tab"( id="tab-home" data-mode="home"| data-cat="(\w+)")', src)
ok([c[1] for c in cats] == ['', 'find', 'build', 'learn', 'discover'] and 'id="tab-home" data-mode="home"' in cats[0][0], 'cinco chips arriba: Inicio y las cuatro categorías')
ok('.navbox .tools:not(.on){display:none}' in src and 'function navSync()' in src and 'if(d.cat){ NAVCAT=d.cat; navSync._pick=true; navSync(); return; }' in src, 'solo se ve la fila de la categoría activa; elegir un chip la cambia sin cambiar de sección')
R1 = EXP['find'] + EXP['build']; R2 = ['home'] + EXP['learn'] + EXP['discover']
ok(src.index('id="tab-eng"') < src.index('id="tab-rou"') < src.index('id="tab-deck"'), 'el orden Engines, Ruleta, Constructor se mantiene')

hg = re.search(r"const HGROUPS=\[(.*?)\];\nconst HOME_TOOLS", src, re.S)
ok(bool(hg), 'HGROUPS existe')
if hg:
    gids = re.findall(r"\['(learn|find|build|discover)','", hg.group(1))
    ok(gids == ['learn', 'find', 'build', 'discover'], 'cuatro grupos por intención: %s' % gids)
    cards = re.findall(r"\['(\w+)','([^']+)','([^']{20,})'\]", hg.group(1))
    keys = [c[0] for c in cards if c[0] in R1 + R2]
    ok(sorted(keys) == sorted(k for k in R1 + R2 if k != 'home'), 'hay una tarjeta por cada botón de la barra (menos Inicio), ni repetida ni faltante: %s' % sorted(keys))
    modes = re.search(r"const MODES = \{(.*?)\};\n", src, re.S).group(1)
    ok(all(("%s:['" % k) in modes for k in keys), 'cada tarjeta abre un modo que existe')
    ok(len(re.findall(r"HSVG\('0 0 120 90'", hg.group(1))) == 4, 'cada grupo trae su ilustración')
hs = re.search(r"const HSTEPS=\[(.*?)\];\nconst HGROUPS", src, re.S)
ok(bool(hs) and len(re.findall(r"HSVG\('0 0 64 48'", hs.group(1))) == 3, 'los tres pasos de «cómo usar la página» traen su ilustración')

ok("document.title=\"Aleister's Codex\"" in src and "if(mode==='home')" in src, 'el título de Inicio es el del sitio solo')
ok("id=\"hmform\"" in src and "e.target.id!=='hmform'" in src and "mode='fnd'" in src, 'el buscador de Inicio manda a Buscar en todo con lo escrito')
ok('data-gomode="guide"' in src and 'body.home .navbox{display:none}' not in src and 'navSync._pick' in src, 'camino para principiantes; la barra se ve también en Inicio (misma que en el resto, fila solo al elegir categoría)')
ok('--i-explore:"Aprender y descubrir"' in src and 'html[lang="en"]{--i-tools:"Cards and decks";--i-explore:"Learn and discover"' in src, 'la etiqueta del grupo Explorar sigue el idioma')

ok('<h1><a class="brand" href="?mode=home" data-goqs="?mode=home"' in src, 'el título de arriba es un enlace a Inicio (data-goqs, también con clic del medio)')

ok('const bhTile=' in src and 'const BH_CAP=innerWidth<=760?6:12' in src and 'class="bhmore"' in src and 'bhn s${st}' in src, 'el historial de Banlist muestra tarjetas con imagen, color por tipo de cambio, contadores en el título y «ver las restantes»')
ok('Con la Ruleta de decks o el Constructor. En cada mazo del tier list, el botón «Abrir en el constructor» lo carga ahí.' in src and 'data-todeck' in src, 'el paso 3 de Inicio aclara que cada mazo del tier list tiene «Abrir en el constructor»')

ok("const TIERS=[[100,999," in src and "grid(g,n=>CARDS[n][C.GEN]+' pts',BH_CAPG)" in src and '.bgrp.s4{--bc' in src, 'Genesys se separa en tramos de puntos (100, 50 a 99, 20 a 49, 11 a 19, 1 a 10), cada uno con su color y contador')
ok('<h3>${t}<em>${ns.length}</em></h3>' in src and "const grid=(names,label,cap=BH_CAP)" in src, 'todas las listas de Banlist usan franjas de color con contador y tarjetas con «ver las restantes»')
ok(src.index('class="navbox"') < src.index('<nav class="modes"') and 'dlabel' not in src, 'la barra por intención va primero y los modos de juego pasan a una franja compacta, sin título suelto encima')

ok('<b>Standard</b><small>TCG · Yu-Gi-Oh! Advanced</small>' in src and '>Advanced</button>${Object.entries(FMT_RETRO)' in src, 'el botón del juego principal dice «Standard» (con «TCG · Yu-Gi-Oh! Advanced» debajo) y en Banlist el formato TCG se llama «Advanced»')
ok(src.count('.mode small{display:block;font-size:.74rem}') == 1, 'los modos de juego muestran su descripción debajo del nombre, así se entiende que son modos')

ok('>Historial (Advanced)</button>' in src and 'Este historial es solo del formato <b>Advanced</b>' in src, 'el historial de Banlist aclara que es solo del formato Advanced (botón y aviso arriba)')
ok('.seg{display:flex;flex-wrap:wrap;gap:6px}' in src and src.index('.seg{display:flex;flex-wrap:wrap;gap:6px}') > src.index('h1{font-size:clamp(2rem,10vw,2.6rem)}'), 'los ajustes de móvil de selectores, Inicio y Banlist van al final de los estilos, después de todos los bloques móviles (si no, no los pisan)')

ok("const ENG_MODES=[['tcg','Advanced']," in src and 'Todos los arquetipos del formato Advanced' in src and 'Todos los arquetipos del TCG' not in src, 'Engines y Arquetipos llaman «Advanced» al formato principal (no «TCG»)')
ok('class="engpk"' in src and 'const engOpen=' in src and "contains('engpk')" in src, 'Engines: la galería de cartas de cada engine va plegada en móvil y recuerda lo que abriste')

ok('const GACC=' in src and src.count('GACC(')>=5 and "contains('gacc')" in src and '@media(min-width:761px){.gacc>summary{display:none}}' in src, 'Guía: esquemas, invocaciones y formatos van plegados en móvil (abiertos en escritorio) y recuerdan lo que abriste')

ok('const DKPAGE=innerWidth<=760?24:48' in src and 'limit:DKPAGE' in src and src.count('DK.limit=48')==0 and '.dkpick .gal,.dkdeck .gal{grid-template-columns:repeat(4,minmax(0,1fr))' in src, 'Constructor: en móvil el selector muestra de a 24 cartas en 4 columnas y la barra de botones se compacta')

ok('.cgrid{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}' in src and src.index('.cgrid{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}')>src.index('#dk-notes{height:84px}'), 'Arquetipos y demás listas de tarjetas van en 2 columnas en móvil (al final de los estilos)')

ok('const GLIC=' in src and 'class="gltiles"' in src and "GACC('gl'+c.id" in src and '.glc-campo{--gc' in src, 'Glosario: categorías con ilustración y color, encabezado por categoría y términos plegados en móvil')

ok('class="glcards"' in src and '.glcard{' in src and 'class="glcard"' in src, 'Glosario: cada término muestra sus cartas de ejemplo como imágenes')

ok('const GLFIG={}' in src and src.count('glSet(')>=30 and 'class="glf"' in src and 'GLFIG[x.s]?' in src, 'Glosario: cada término con gráfico lo muestra en lugar de cartas sueltas (tablero, fases, invocaciones, cadena, banlist...)')

ok("z('field',6,30,'F')" in src and "z('extra',6,56,'Ex')" in src and "z('f',3,1,2,'Campo')" in src and "z('x',6,1,3,'Extra Deck')" in src, 'Glosario y Guía: la Zona de Campo va arriba del Extra Deck (como en el tablero real)')
ok("glSet('desterrar',glBanish)" in src and "glSet('side-deck',glSide)" in src and "glSet('boca-arriba-abajo poner',glFaceCards)" in src and "cardImg('Dark Magician')" in src, 'Glosario: Desterrar no marca el Cementerio, Side Deck muestra 15 cartas y Boca arriba/abajo usa una carta real y su dorso')

ok('const glTx=' in src and 'const glTime=' in src and "'garnet':()=>" in src and 'class="gzp ' in src and 'Object.assign(GLFIG,{' in src, 'Glosario: ejemplos de texto con costo/efecto/objetivo, comparaciones y esquemas para los términos de efectos, formatos y jerga (incluido Garnet), con clases propias que no pisan las de la Guía')

ok(all(k in src for k in ["'activar-y-resolver':()=>", "'trampa-de-contraefecto':()=>", "'monstruo-trampa':()=>", "const glRot=", "const glBanish2=", "const glTuner="]) and 'art/cardback.jpg' in src and os.path.exists('art/cardback.jpg') and "cardImg('Man-Eater Bug')" in src, 'Glosario: control, desterrar, flip, poner, tuner, activar y resolver, contraefecto y monstruo trampa tienen su gráfico, y el dorso es la imagen real')

ok(all(os.path.exists('art/ic-%s.png' % n) for n in ['equipo', 'campo', 'rapido', 'ritual', 'continua', 'contraefecto']) and 'const glIc=' in src and 'const glIcs=' in src and 'glIcs(GLMAG' in src and "glIc('contraefecto')" in src and "glIc('rapido')" in src, 'Glosario y Guía: los tipos de Magia y Trampa muestran sus íconos oficiales (Equipo, Campo, Juego Rápido, Ritual, Continua, Contraefecto)')

ok('const glLinkZones=' in src and 'const glCrown=' in src and "'boss-monster':()=>" in src and "'invocacion-link':()=>" in src and "'flechas-link':()=>" in src and 'class="gllk"' in src and 'class="glz" viewBox' not in src, 'Glosario: Boss monster (corona sobre una carta real), Invocación Link (carta real) y Flechas Link (zonas enlazadas), con una clase propia que no pisa la .glz de la Guía')

ok('const lvTxt=' in src and 'function lvDom(' in src and src.count('.innerHTML=lvTxt(esc(d.d||')==4 and "lvDom(document.getElementById('app'))" in src and 'lvStars(lv,xyz)' in src and os.path.exists('art/lv-star.png'), 'Estrellas de Nivel: los textos de efecto, la ficha de la carta, la Guía y el Glosario muestran la estrella cada vez que dicen Nivel/Level/Rango/Rank y un número')

page = open('index.html', encoding='utf-8').read()
ok('const HOME_TOOLS=' in page and 'id="tab-home"' in page and "let mode='home'" in page, 'la página generada trae Inicio')
en = json.load(open('tools/i18n_en.json', encoding='utf-8'))
stt = json.load(open('tools/i18n_static.json', encoding='utf-8'))
ok(stt.get('Inicio') == 'Home' and en.get('Página de inicio') == 'Home', 'en inglés Inicio es Home (el botón y el nombre de la sección), no Standby')
ok(en.get('Inicio') == 'Standby', 'la fase «Inicio» de la Guía sigue siendo Standby (por eso la sección se llama «Página de inicio» por dentro)')
ok(all(k in en for k in ['Quiero aprender', 'Quiero descubrir']), 'los títulos de grupo tienen traducción')

print('\nfailed: %d' % len(fails))
sys.exit(1 if fails else 0)

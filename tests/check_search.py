"""Gate: búsqueda global y azar (pestaña "Buscar en todo").  Run from the project root:  python tests/check_search.py

  1. cableado: pestaña, MODES, rutas, handlers, redibujo de los cargadores lazy, gate en refresh.py, traducción estática
  2. rutas en node: ?mode=search&q=..., saneo (control, largo 60), build, routeName
  3. render y búsqueda en node con los datos reales de arquetipos, glosario, Lore, series y ruleta:
     cada grupo aparece con su consulta, todo resultado es un enlace real, "sin resultados" y "menos de 2 letras" se ven,
     el azar (fdPick) devuelve siempre un nombre válido en los extremos 0 y 0.999999 y nada si no hay datos
  4. los dos idiomas
"""
import glob, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


src = open('src.html', encoding='utf-8').read()
page = open('index.html', encoding='utf-8').read()

# 1. cableado
for pat, why in [
    (r'id="tab-fnd" data-mode="fnd"', 'pestaña Buscar en todo'), (r"fnd:\['Buscar en todo',viewFind\]", 'MODES.fnd'), (r'function viewFind\(', 'vista'),
    (r"search:\['fnd',''\]", 'ruta ?mode=search'), (r"fnd:'search'", 'ROUTE_OLD'), (r"id==='fq'", 'handler del cuadro de búsqueda'),
    (r'd\.fdrand', 'handler de los botones al azar'), (r'd\.fdmore', 'handler de Ver más'), (r'd\.fdretry', 'handler de reintentar'), (r'maxlength="60" placeholder', 'el cuadro limita el largo como la ruta'), (r"ARCH\.err=true; if\(mode==='arq'\|\|mode==='fnd'\)", 'si falla un conjunto, el buscador se redibuja'), (r'setSelectionRange\(a,z\)', 'el cursor se conserva al escribir'), (r'data-fdrand="card"', 'botón carta al azar'), (r'data-fdrand="arch"', 'botón arquetipo al azar'),
    (r"mode==='fnd'\?FD\.q\.trim\(\)", 'routeSync guarda la consulta'), (r"if\(r\.mode==='fnd'\) FD\.q=r\.q", 'routeFromUrl lee la consulta'),
    (r"'ser','fnd'\]\.includes\(mode\)", 'arquetipos recargan el buscador'), (r"mode==='arq'\|\|mode==='fnd'", 'Lore recarga el buscador'),
    (r"mode==='glos'\|\|mode==='fnd'", 'glosario recarga el buscador'), (r"mode==='ser'\|\|mode==='fnd'\) render", 'series recargan el buscador'),
    (r"mode==='rou'\|\|mode==='ser'\|\|mode==='fnd'", 'ruleta recarga el buscador'), (r'body\.glos,body\.ser,body\.fnd\{--accent', 'color de la pestaña'),
]:
    ok(re.search(pat, src), 'src.html: ' + why)
ok(re.search(r"else if\(d\.fdretry\)\{ ES_ERR=false; ESLOAD=false; ARCH\.err=false; ARCH\.asked=false; GL\.err=false; GL\.asked=false; LORE\.err=false; LORE\.asked=false; SER\.err=false; SER\.asked=false; ROU\.err=false; ROU\.asked=false;", src) is not None, 'reintentar reinicia los seis cargadores')
ok("FD.q=el.value; FD.more={}; FD.fz='';" in src, 'escribir reinicia Ver más y la pasada con errores')
ok("const fqKeep=document.activeElement&&document.activeElement.id==='fq'" in src and "if(fqKeep&&mode==='fnd')" in src, 'render conserva el foco y el cursor del buscador cuando un cargador redibuja')
ok("if(ES||ESLOAD||ES_ERR) return; ESLOAD=true;" in src and ".catch(()=>{ ESLOAD=false; ES_ERR=true;" in src, 'si fallan los nombres en español no se vuelven a pedir en cada tecla')
ok('"Buscar en todo"' in open('tools/i18n_static.json', encoding='utf-8').read(), 'i18n_static.json traduce la pestaña')
ok("'tests/check_search.py'" in open('tools/refresh.py', encoding='utf-8').read(), 'refresh.py corre este gate')
ok(re.search(r'<label class="sr" for="fq">', src) is not None, 'el cuadro de búsqueda tiene etiqueta accesible')

# 2 y 3. node
core = re.search(r'const ROUTE_MODES=.*?function routeBuild\(st\)\{.*?\n\}\n', page, re.S)
ok(bool(core), 'index.html: helpers de ruta')


def grab(pat):
    m = re.search(pat, page, re.S)
    return m.group(0) if m else ''


def arr(path):
    t = open(path, encoding='utf-8').read()
    return t[t.index('['):t.rindex(']') + 1]


def lit(path):
    t = open(path, encoding='utf-8').read()
    return t[t.index('{'):t.rindex('}') + 1]


pieces = [grab(r"const EN = [^\n]*\n"), grab(r"function __t\(a\)\{.*?\n\}\n"), grab(r"const esc = [^\n]*\n"), grab(r"const C = \{[^\n]*\n"),
          grab(r"const norm = .*?(?=function ensureES)"), grab(r"const ROU_MAX=[^\n]*\n"), grab(r"const ROU_SER=[^\n]*\n"), grab(r"function rouChars\(.*?\n\}\n"),
          grab(r"function archA\([^\n]*\n"), grab(r"const FMT_RETRO=[^\n]*\n"), grab(r"const GL=\{[^\n]*\n"), grab(r"const glHref=[^\n]*\n"), grab(r"const glLang=[^\n]*\n"),
          grab(r"const LORE=\{[^\n]*\n"), grab(r"const archHref=[^\n]*\n"), grab(r"const SER=\{.*?(?=function linkCards)"), core.group(0) if core else '']
ok(all(pieces), 'index.html: piezas del buscador encontradas %s' % [i for i, x in enumerate(pieces) if not x])
if all(pieces):
    js = r"""
const slug = x => x.toLowerCase().replace(/[^a-z0-9]+/g,'-');
let LANG='%(lang)s', mode='fnd', NAMES=[], CARDS={};
const how=(h,t)=>'<how>'+t+'</how>', pageHead=(t,l,h='')=>'<h2>'+t+'</h2><p class="lede">'+l+'</p>'+h;
let ESX={'Cadena Fantasma':'Ghost Chain','Dragon & "Co" <i>':'Drag\u00f3n & <b>'}; const esName=n=>ESX[n]||'', rouFace=()=>'<face>', loadData=()=>new Promise(()=>{}), render=()=>{}, archLoad=()=>{}, loreLoad=()=>{}, glLoad=()=>{}, rouLoad=()=>{}, ensureES=()=>{};
const ARCH={data:null,by:null}; const ROU={data:null,err:false};
%(pieces)s
const t = [];
let r = routeParse('?mode=search&q=Jaden%%20Yuki'); t.push(r.mode==='fnd' && r.name==='search' && r.q==='Jaden Yuki');
r = routeParse('?mode=search'); t.push(r.mode==='fnd' && r.q==='');
r = routeParse('?mode=search&q='+'a'.repeat(200)); t.push(r.q.length===60);
r = routeParse('?mode=search&q=a%%00b%%0Ac'); t.push(r.q==='a b c');
r = routeParse('?mode=cards&q=zzz'); t.push(r.q==='');
t.push(routeBuild({mode:'fnd',tcgf:'',view:'meta',deck:'',q:'Nibiru, the Primal'})==='?mode=search&q=Nibiru%%2C+the+Primal');
t.push(routeBuild({mode:'fnd',tcgf:'',view:'meta',deck:'',q:''})==='?mode=search');
t.push(routeBuild({mode:'tcg',tcgf:'',view:'meta',deck:'',q:'x'}).indexOf('q=')<0);
t.push(routeName('fnd','')==='search');
t.push(fdHref('Sangan')==='?mode=search&q=Sangan');
const out={routes:t};
// datos reales
const EXTRA=['Kuriboh','The Regulation of Tribe','There Be Dragons','Ash Blossom & Joyous Spring','Hraesvelg','Magatama','Bot Herder','Hero Mask','Pot of Greed','Mirror Force','E.T. Alien','Etude Test','Dark Magical Circle','Dark Magician',"Magician's Rod",'D.D. Warrior Lady','Mage Test','Dragon Xylophone Big','Red Dragon','Zed Match','Abe Match'].concat(Array.from({length:320},(_,i)=>'Cap Test '+i),['My Blue Eyes','Ghost Ogre','Kaibaman','TGX1-HL','Tuner Cat','Dragon & "Co" <i>']).concat(Array.from({length:14},(_,i)=>'Blue-Eyes Alternative Dragon '+String.fromCharCode(65+i)));
NAMES=['Elemental HERO Neos'].concat(EXTRA,['Cadena Fantasma','Elemental HERO Avian','Blue-Eyes White Dragon','Nibiru, the Primal Being','Sangan','Cyber Jar']);
for (const n of NAMES) CARDS[n]=[0,0,0,0,0,0,0,0,0,1];
CARDS['Cyber Jar']=[0,0,0,0,0,0,0,0,0,0];                       // sin passcode (Rush, etc.): se encuentra igual
ESN=NAMES.map(n=>mkEntry(ESX[n]||''));
const Q=function(q){ FD.q=q; FD.fz=q; return viewFind(); };
const QP=function(q){ FD.q=q; FD.fz=''; return viewFind(); };
out.short=Q('a'); out.empty=Q('');
out.nodata_wait=Q('jaden');                                   // nada cargado: "Buscando…"
out.pick_none=[fdPick('arch',0), fdPick('card',2)];           // sin arquetipos cargados -> null; card con r>=1 se acota
const J=%(arch)s; ARCH.data=J; ARCH.by={}; J.n.forEach((a,i)=>{ ARCH.by[archSlug(a)]=i; });
GL.data=%(glos)s; LORE.data=%(lore)s; ROU.data=%(rou)s; SER.data=%(ser)s;
out.hero=Q('elemental hero'); out.jaden=Q('jaden'); out.cadena=Q('cadena'); out.chain=Q('chain'); out.nope=Q('xqzvwk');
out.goat=Q('gx'); out.typo=Q('Nibirru'); out.cyberjar=Q('cyber jar'); out.pend=QP('nibirru'); out.html=Q('<zqx>'); out.ghost2=Q('ghost'); out.cadcard=Q('cadena');
out.be=Q('blue eyes'); FD.more={card:true}; out.beall=viewFind(); FD.more={};
out.amp=Q('dragon co'); out.sym1=Q('!!'); out.sym2=Q('\u{1F600}\u{1F600}'); out.ghost=Q('ghost chain');
out.kaiba=Q('kaiba'); out.kuri=Q("kuriboh's"); out.kaibas=Q("kaiba's"); out.heroes=Q('heroes'); out.there=Q('there'); out.ash=Q('ashblossom'); out.dmg=Q('dark mgician'); out.herp=Q('herp'); out.gred=Q('pot of gred'); out.eys=Q('blue eys'); out.mass=Q('mass'); out.joined=Q('blueeyes'); out.joined2=Q('mirrorforce'); out.et=Q('e.t.'); out.hroe=Q('hroe'); out.hreo=Q('hreo'); out.magican=Q('dark magican'); out.mrod=QP('magicians rod'); out.dd=QP('d.d.'); out.mago=Q('mago'); out.heros=QP('heros'); out.cap=Q('cap test'); FD.more={card:true}; out.capall=viewFind(); FD.more={}; out.dra=Q('dra'); out.match=Q('match'); ES_ERR=true; out.esfail=Q('nibiru'); ES_ERR=false; out.gx2=Q('gx'); out.tuner=Q('tuner'); out.dragon=Q('dragon'); out.an=Q('an');
const A0=ARCH.data, B0=ARCH.by; ARCH.data=null; ARCH.by=null; out.noarch=Q('elemental hero'); ARCH.data=A0; ARCH.by=B0;
const G0=GL.data; GL.data=null; GL.err=true; out.glfail=Q('elemental hero'); GL.data=G0; GL.err=false;
out.pick=[fdPick('card',0),fdPick('card',0.999999),fdPick('arch',0),fdPick('arch',0.999999)];
out.archall=J.n.every(n=>ARCH.by[archSlug(n)]!=null);
(async()=>{
  QP('nibirru'); FD.q='sangan'; await new Promise(r=>setTimeout(r,450)); out.stale=FD.fz;        // la pasada con errores de una consulta vieja no debe aplicarse a la nueva
  QP('nibirru'); await new Promise(r=>setTimeout(r,150)); out.early=FD.fz; await new Promise(r=>setTimeout(r,300)); out.fresh=FD.fz;                       // la de la consulta vigente sí
  console.log(JSON.stringify(out));
})();
"""
    for lang in ('es', 'en'):
        src_js = js % dict(lang=lang, pieces=chr(10).join(pieces), arch=lit('data/arch.js'), glos=lit('data/glossary.js'), lore=arr('data/lore.js'), rou=lit('data/roulette.js'), ser=lit('data/series.js'))
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
            tf.write(src_js)
        p = subprocess.run(['node', tf.name], capture_output=True, text=True, encoding='utf-8')
        os.unlink(tf.name)
        try:
            o = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            o = None
        ok(o is not None, 'render %s: el arnés corrió %s' % (lang, p.stderr.strip()[:300]))
        if not o:
            continue
        labels = ['URL con consulta', 'URL sin consulta', 'consulta de 60 como máximo', 'sin caracteres de control', 'q solo vale en Buscar', 'URL al escribir', 'sin consulta no hay q',
                  'otro modo no escribe q', 'routeName', 'fdHref']
        for g, l in zip(o['routes'], labels):
            ok(g, 'ruta: ' + l)
        ok(len(o['routes']) == len(labels), 'las %d pruebas de ruta corrieron' % len(labels))
        es = lang == 'es'
        ok(('Escribe al menos 2 letras' if es else 'Type at least 2 letters') in o['short'] and ('Escribe al menos 2 letras' if es else 'Type at least 2 letters') in o['empty'], 'render %s: con menos de 2 letras pide más' % lang)
        ok(('Buscando' if es else 'Searching') in o['nodata_wait'], 'render %s: sin datos cargados dice que busca, no que no hay nada' % lang)
        ok(o['pick_none'][0] is None and o['pick_none'][1] == 'Cyber Jar', 'fdPick: arquetipo sin datos es null y r fuera de rango se acota a la última carta')
        ok(all(o['pick']) and o['pick'][0] == 'Elemental HERO Neos' and o['pick'][1] == 'Cyber Jar' and o['archall'], 'fdPick: extremos 0 y 0.999999 dan cartas (también las de Rush y sin passcode) y arquetipos con hub')
        h = o['hero']
        ok('data-card="Elemental HERO Neos"' in h and 'data-card="Elemental HERO Avian"' in h and 'data-card="Blue-Eyes' not in h, 'render %s: "elemental hero" encuentra las dos cartas HERO y no otras' % lang)
        ok('data-arch="elemental-hero"' in h, 'render %s: "elemental hero" encuentra el hub de arquetipo' % lang)
        ok('data-serpick="gx" data-serchar="jaden-yuki"' in o['jaden'] or 'data-serchar="jaden-yuki"' in o['jaden'], 'render %s: "jaden" encuentra al duelista Jaden Yuki' % lang)
        ok('data-glterm=' in o['cadena'] if es else 'data-glterm=' in o['chain'], 'render %s: el glosario responde en el idioma (%s)' % (lang, 'cadena' if es else 'chain'))
        ok('data-serpick="gx"' in o['goat'] and 'data-serchar=""' in o['goat'], 'render %s: "gx" encuentra la serie GX' % lang)
        ok('data-card="Nibiru, the Primal Being"' in o['typo'], 'render %s: tolera un error de escritura (Nibirru)' % lang)
        ok('data-card=' not in o['jaden'], 'render %s: "jaden" no trae cartas por parecido ("cadena" no es Jaden): primero solo coincidencias exactas' % lang)
        ok('data-card="Cadena Fantasma"' in o['cadcard'], 'render %s: la coincidencia exacta de una carta sí sale' % lang)
        L12 = 'de 16' if es else 'of 16'
        ok(len(re.findall(r'data-card=', o['be'])) == 12 and ('12 ' + L12) in o['be'] and 'data-fdmore="card"' in o['be'], 'render %s: con más de 12 cartas muestra 12 y dice "12 %s" con botón Ver más' % (lang, L12))
        ok(o['be'].index('data-card="Blue-Eyes White Dragon"') < o['be'].index('data-card="Blue-Eyes Alternative Dragon A"'), 'render %s: "blue eyes" pone primero la carta de nombre más corto, no la alfabética' % lang)
        ok(len(re.findall(r'data-card=', o['beall'])) == 16 and 'data-fdmore' not in o['beall'], 'render %s: Ver más muestra las 16' % lang)
        ok('<i>' not in o['amp'] and '&lt;i&gt;' in o['amp'] and '&amp;' in o['amp'] and '&quot;Co&quot;' in o['amp'], 'render %s: los nombres de carta se escapan (&, comillas y <i>)' % lang)
        ok(all('data-card=' not in o[k] and ('Escribe al menos 2 letras' if es else 'Type at least 2 letters') in o[k] for k in ('sym1', 'sym2')), 'render %s: una consulta solo de símbolos o emoji no devuelve nada' % lang)
        ok(('data-card="Cadena Fantasma"' in o['ghost']) == es, 'render %s: el nombre en español solo cuenta con la página en español (%s)' % (lang, 'sí' if es else 'no'))
        ok(('<small>Ghost Chain</small>' in o['cadcard']) == es, 'render %s: en español la carta muestra también su nombre en inglés' % lang)
        k = o['kaiba']
        ok('data-serchar="seto-kaiba"' in k and 'data-card="Kaibaman"' in k and k.index('data-serchar="seto-kaiba"') < k.index('data-card="Kaibaman"'), 'render %s: "kaiba" pone al duelista Seto Kaiba antes que la carta Kaibaman' % lang)
        k = o['gx2']
        ok('data-serpick="gx"' in k and 'TGX1-HL' not in k, 'render %s: "gx" encuentra la serie GX y no la carta TGX1-HL (un pedazo en medio de una palabra no cuenta como exacto)' % lang)
        k = o['tuner']
        ok('data-glterm=' in k and k.index('data-glterm=') < k.index('data-card="Tuner Cat"'), 'render %s: "tuner" pone el término del glosario antes que la carta' % lang)
        ok(len(re.findall(r'data-arch=', o['dragon'])) == 12 and len(re.findall(r'data-arch=', o['dragon'])) < sum(1 for n in json.loads(lit('data/arch.js'))['n'] if 'dragon' in n.lower()), 'render %s: arquetipos: tope de 12 con muchos más disponibles' % lang)
        ok(len(re.findall(r'data-serchar="[a-z]', o['an'])) <= 12, 'render %s: duelistas: tope de 12' % lang)
        ok(('Cargando más resultados' if es else 'Loading more results') in o['noarch'] and 'data-card="Elemental HERO Neos"' in o['noarch'], 'render %s: si falta el índice de arquetipos avisa y muestra lo ya cargado' % lang)
        ok('data-fdretry="1"' in o['glfail'] and 'Cargando más' not in o['glfail'] and 'Loading more' not in o['glfail'], 'render %s: si un conjunto de datos falla ofrece reintentar y no queda cargando para siempre' % lang)
        ok('data-card="Ghost Ogre"' in o['ghost2'] and ('data-card="Cadena Fantasma"' in o['ghost2']) == es, 'render %s: "ghost" encuentra Ghost Ogre, y Cadena Fantasma solo en español' % lang)
        ok(o['beall'].index('data-card="Blue-Eyes White Dragon"') < o['beall'].index('data-card="My Blue Eyes"'), 'render %s: "blue eyes": el nombre que empieza con la consulta va antes que el que solo la contiene, aunque sea más largo' % lang)
        ok(('Buscando' if es else 'Searching') in o['pend'] and 'data-card=' not in o['pend'], 'render %s: sin coincidencias exactas la pasada con errores espera (no bloquea cada tecla) y mientras tanto dice que busca' % lang)
        ok(len(re.findall(r'data-card=', o['capall'])) == 300 and ('300 ' + ('de' if es else 'of') + ' 321') not in o['cap'] and ('300 ' + ('de' if es else 'of') + ' 320') in o['capall'] and ('Afina la búsqueda' if es else 'Narrow your search') in o['capall'], 'render %s: Ver más llega como mucho a 300 y avisa de afinar la búsqueda' % lang)
        ok('data-fdmore="card"' in o['cap'] and len(re.findall(r'data-card=', o['cap'])) == 12, 'render %s: con 320 coincidencias muestra solo 12 al principio' % lang)
        ok(o['dra'].index('data-card="Dragon Xylophone Big"') < o['dra'].index('data-card="Red Dragon"'), 'render %s: "dra": el nombre que empieza con el texto va antes que el que solo tiene una palabra que empieza, aunque sea más largo' % lang)
        ok(o['match'].index('data-card="Abe Match"') < o['match'].index('data-card="Zed Match"'), 'render %s: a igual calidad y largo, orden alfabético' % lang)
        ok('<b>' not in o['cadcard'] and ('&lt;b&gt;' in o['amp']) == es, 'render %s: el nombre en español también se escapa' % lang)
        ok('data-lorego=' in o['jaden'], 'render %s: el grupo Lore aparece (Jaden Yuki)' % lang)
        ok(es or ('Cadena' not in o['chain'] and 'data-glterm=' in o['chain']), 'render en: el glosario se busca y se muestra en inglés')
        ok('data-fdretry="1"' in o['esfail'], 'render %s: si fallan los nombres en español ofrece reintentar' % lang)
        ok('data-card="Elemental HERO Neos"' in o['hreo'] and 'data-card="Synchro' not in o['hroe'] and 'data-card="Synchro' not in o['hreo'], 'render %s: "hreo" (dos letras cambiadas de lugar) encuentra Elemental HERO, y "hroe" no trae cartas que lo contienen a través de dos palabras' % lang)
        ok(o['magican'].index('data-card="Dark Magician"') < o['magican'].index('data-card="Dark Magical Circle"'), 'render %s: "dark magican": el error más pequeño y el nombre más corto van primero' % lang)
        ok('data-card=' in o['mrod'] and 'Rod' in o['mrod'] and 'Buscando' not in o['mrod'] and 'Searching' not in o['mrod'], 'render %s: "magicians rod" (sin apóstrofo) es una coincidencia exacta, no espera a la pasada con errores' % lang)
        ok('D.D. Warrior Lady' in o['dd'] and 'Dark Magician' not in o['dd'] and 'Dragon' not in o['dd'], 'render %s: "d.d." busca las iniciales juntas, no cualquier palabra con D' % lang)
        ok('data-card=' not in o['mago'], 'render %s: una palabra de 4 letras no tolera una letra distinta ("mago" no es "mage")' % lang)
        ok('Elemental HERO' in o['heros'] and 'Buscando' not in o['heros'] and 'Searching' not in o['heros'], 'render %s: el plural "heros" cuenta como "hero" en la búsqueda exacta' % lang)
        ok(o['stale'] == '' and o['fresh'] == 'nibirru', 'render %s: la pasada con errores solo se aplica a la consulta vigente (stale=%r fresh=%r)' % (lang, o['stale'], o['fresh']))
        ok('data-card="Cyber Jar"' in o['cyberjar'], 'render %s: se encuentran todas las cartas, también las de Rush y sin passcode (identificador 0)' % lang)
        ok(all('data-card="%s"' % n not in o['hroe'] + o['hreo'] for n in ('Hraesvelg',)) and all('data-card="%s"' % n not in o['herp'] for n in ('Bot Herder',)) and 'data-card="Magatama"' not in o['mago'], 'render %s: con 4 letras solo vale un par cambiado de lugar (hroe, herp, mago no traen Hraesvelg, Bot Herder ni Magatama)' % lang)
        ok('data-card="Kuriboh"' in o['kuri'] and 'data-card="Sangan"' not in o['kuri'], 'render %s: un posesivo ("kuriboh\'s") se busca sin el \'s (no como una "s" suelta)' % lang)
        ok('data-serchar="seto-kaiba"' in o['kaibas'], 'render %s: "kaiba\'s" encuentra al duelista Seto Kaiba' % lang)
        ok('data-card="Elemental HERO Neos"' in o['heroes'], 'render %s: el plural "heroes" encuentra "hero"' % lang)
        ok('data-card="There Be Dragons"' in o['there'] and 'The Regulation of Tribe' not in o['there'], 'render %s: la grafía unida solo se usa si nada coincide por palabras ("there" no trae "The Regulation of Tribe")' % lang)
        ok('data-card="Ash Blossom &amp; Joyous Spring"' in o['ash'], 'render %s: "ashblossom" sí encuentra su carta cuando nada más coincide' % lang)
        ok('data-card="Dark Magician"' in o['dmg'], 'render %s: con varias palabras una de 7 letras tolera un error ("dark mgician")' % lang)
        ok('data-card="Pot of Greed"' in o['gred'] and 'data-card="Blue-Eyes White Dragon"' in o['eys'], 'render %s: con varias palabras tolera errores en las cortas ("pot of gred", "blue eys")' % lang)
        ok('data-card="Hero Mask"' not in o['mass'], 'render %s: el plural solo cuenta contra la palabra entera ("mass" no es "mask")' % lang)
        ok('data-card="Blue-Eyes White Dragon"' in o['joined'] and 'data-card="Mirror Force"' in o['joined2'], 'render %s: encuentra la grafía unida ("blueeyes", "mirrorforce")' % lang)
        ok('E.T. Alien' in o['et'] and 'Etude Test' not in o['et'], 'render %s: "e.t." busca las primeras palabras en orden, no cualquier nombre que empiece con ET' % lang)
        ok('16 de 16' not in o['beall'] and '16 of 16' not in o['beall'], 'render %s: tras Ver más el encabezado no dice "16 de 16"' % lang)
        ok(o['early'] == '' and o['fresh'] == 'nibirru', 'render %s: la pasada con errores espera su pausa (a los 150 ms todavía no corrió)' % lang)
        ok(('Nada coincide con' if es else 'Nothing matches') in o['nope'] and 'xqzvwk' in o['nope'], 'render %s: sin resultados lo dice y repite la consulta' % lang)
        ok('<zqx>' not in o['html'] and '&lt;zqx&gt;' in o['html'], 'render %s: la consulta se escapa (no entra HTML)' % lang)
        for k in ('hero', 'jaden', 'cadena', 'goat'):
            hrefs = re.findall(r'<a [^>]*href="([^"]*)"', o[k])
            ok(hrefs and all(x.startswith('?mode=') for x in hrefs), 'render %s: todo resultado de "%s" es un enlace real (%d)' % (lang, k, len(hrefs)))
        ok(es or not re.search(r'Al azar|Duelistas ·|Arquetipo al azar|Carta al azar|Escribe', o['hero'] + o['jaden'] + o['nope']), 'render en: sin textos en español en los resultados')
    lore = json.loads(arr('data/lore.js'))
    ok(len(lore) > 20, 'hay Lore real para buscar (%d entradas)' % len(lore))

if fails:
    print('\nFALLA check_search: %d' % len(fails))
    sys.exit(1)
print('\nok check_search')

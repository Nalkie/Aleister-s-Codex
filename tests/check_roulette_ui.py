"""Gate test of the deck roulette UI, variant A (a wheel).  No network.  Run from the project root:  python tests/check_roulette_ui.py

  * data/roulette.js has the shape the UI consumes (face, sig, flags, swapped, anime...).
  * The pure helpers of the wheel (seeded random, sampling to at most 24 slices, landing angle, face URL, monogram) run in node.
  * The page is wired: tool button, route (?mode=roulette&deck=..&seed=..&series=..), reduced-motion path, aria-live, legality, fidelity, markers, phone CSS.
  * Every Spanish string of the tool has an English translation (the full dictionary check is tests/check_i18n.py).
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


# ---- data shape ----
raw = open('data/roulette.js', encoding='utf-8').read()
m = re.match(r'__load\("roulette",(.*)\)\s*;?\s*$', raw, re.S)
check(bool(m), 'data/roulette.js calls __load("roulette", {...})')
decks = json.loads(m.group(1))['decks'] if m else []
check(len(decks) >= 1, 'the data has decks (%d)' % len(decks))
SER = {'dm', 'gx', '5d', 'zx'}
bad = []
for d in decks:
    ok = all(k in d for k in ('id', 'series', 'character', 'arc', 'name', 'blurb', 'wiki', 'main', 'extra', 'anime', 'swapped', 'missing', 'face', 'sig', 'kind', 'basis'))
    ok = ok and d['series'] in SER and 0 <= d['anime'] <= 100 and (d['face'] is None or d['face'].startswith('/')) and d['kind'] in ('anime', 'thematic') and isinstance(d['basis'], str) and (d['kind'] == 'anime' or d['basis'].strip())
    names = {c[0] for c in d['main'] + d['extra']}
    ok = ok and d['sig'] in names and all(len(c) == 3 and c[1] >= 1 and c[2] in (0, 1, 2) for c in d['main'] + d['extra'])
    ok = ok and all(len(x) == 2 for x in d['swapped']) and all(isinstance(x, str) for x in d['missing'])
    if not ok:
        bad.append(d.get('id'))
check(not bad, 'every deck has the consumed fields, a signature card inside the deck and flags 0/1/2' + (': %s' % bad[:3] if bad else ''))
check(len({d['id'] for d in decks}) == len(decks), 'deck ids are unique')
check({d['kind'] for d in decks} == {'anime', 'thematic'}, 'the sample mixes anime and thematic decks (thematic ones carry a basis text)')

src = open('src.html', encoding='utf-8').read()
page = open('index.html', encoding='utf-8').read()

# ---- pure helpers in node ----
pure = re.search(r'/\*ROU-PURE-START\*/(.*?)/\*ROU-PURE-END\*/', src, re.S)
check(bool(pure), 'the pure wheel helpers are delimited in src.html')
if pure:
    harness = pure.group(1) + r'''
const t=[];
const mk=(id,s,ch,face)=>({id,series:s,character:ch,face:face===undefined?'/img/a b/p.png':face,arc:'x'});
const D=[mk('a','dm','Yugi'),mk('b','dm','Yugi'),mk('c','dm','Kaiba',null),mk('d','gx','Jaden'),mk('e','5d','Yusei'),mk('f','zx','Yuma')];
let ch=rouChars(D,'all');
t.push(ch.length===5 && ch[0].series==='dm' && ch.find(c=>c.name==='Yugi').decks.length===2);
t.push(rouChars(D,'gx').length===1 && rouChars(D,'dm').length===2 && rouChars(D,'5d')[0].name==='Yusei');
const TH=[mk('t1','gx','Th',null),mk('t2','gx','Th2'),mk('t3','gx','Th2')]; TH[0].kind='thematic'; TH[1].kind='thematic'; TH[2].kind='anime'; const tc=rouChars(TH,'all'); t.push(tc.find(c=>c.name==='Th').thematic===true && tc.find(c=>c.name==='Th2').thematic===false && ch.every(c=>c.thematic===false||c.decks.every(d=>d.kind==='thematic')));
t.push(ch.find(c=>c.name==='Kaiba').face===null && ch.find(c=>c.name==='Yugi').face==='/img/a b/p.png');
// seeded random: same seed same stream, different seed different stream
const a1=rouRng(7), a2=rouRng(7), b1=rouRng(8); const sA=[a1(),a1(),a1()], sB=[a2(),a2(),a2()], sC=[b1(),b1(),b1()];
t.push(JSON.stringify(sA)===JSON.stringify(sB) && JSON.stringify(sA)!==JSON.stringify(sC) && sA.every(x=>x>=0&&x<1));
// deterministic pick with a seed, and every deck of the wheel is reachable over many seeds
const pickWith=seed=>{ const r=rouRng(seed); const sl=rouSample(ch,r); const p=rouPick(sl,r); return p.deck.id; };
t.push(pickWith(7)===pickWith(7));
const seen=new Set(); for(let s=1;s<=300;s++) seen.add(pickWith(s)); t.push(seen.size===D.length);
// sampling: at most 24, balanced across series, 'must' always in, canonical order kept, no sampling when it fits
const big=[]; for(let i=0;i<31;i++) big.push(mk('g'+i,'gx','G'+String(i).padStart(2,'0'))); for(let i=0;i<25;i++) big.push(mk('m'+i,'dm','M'+String(i).padStart(2,'0'))); for(let i=0;i<5;i++) big.push(mk('z'+i,'zx','Z'+i));
const bc=rouChars(big,'all'); const sm=rouSample(bc,rouRng(3));
t.push(bc.length===61 && sm.length===ROU_MAX && new Set(sm).size===ROU_MAX);
t.push(['dm','gx','zx'].every(s=>sm.some(c=>c.series===s)) && sm.filter(c=>c.series==='zx').length===5);
const must=bc.find(c=>c.name==='G30'); t.push(rouSample(bc,rouRng(5),must).includes(must) && rouSample(bc,rouRng(5),must).length===ROU_MAX);
const sorted=rouSample(bc,rouRng(9)).map(c=>bc.indexOf(c)); t.push(sorted.every((v,i)=>!i||sorted[i-1]<v));
t.push(rouSample(ch,rouRng(1)).length===5 && rouChars(big,'gx').length===31 && rouSample(rouChars(big,'gx'),rouRng(2)).length===ROU_MAX);
// landing angle: the pointer (top) ends on the slice that was picked, for 1..24 slices and any start rotation
let land=true; for(const n of [1,2,3,7,8,13,24]) for(const rot of [0,17.5,-40,1234.5]) for(let i=0;i<n;i++) for(const u of [-.38,0,.38]){ const to=rouTarget(rot,i,n,u,5); if(rouIndexAt(to,n)!==i||to<rot+5*360-1) land=false; }
t.push(land);
// faces: the Duel Links Meta URL is built with each segment encoded; no face -> '' and a monogram
t.push(rouFaceUrl('/img/characters/arkana/portrait.png')==='https://s3.duellinksmeta.com/img/characters/arkana/portrait.png');
t.push(rouFaceUrl('/img/a b/ñ.png')==='https://s3.duellinksmeta.com/img/a%20b/%C3%B1.png' && rouFaceUrl(null)==='' && rouFaceUrl('')==='');
t.push(rouMono('Yami Yugi')==='YY' && rouMono('Jaden Yuki')==='JY' && rouMono('Kaiba')==='K' && rouMono('Yuma-Tsukumo Z')==='YT');
t.push(rouShort('Yugi',10)==='Yugi' && rouShort('Reginald Kastle',11)==='Reginald K.' && rouShort('Maximillion Pegasus Crawford',8).length<=8 && rouShort('Abcdefghijklmnop',8)==='Abcdefg…');
t.push(rouArc({arc:'Decks'})==='' && rouArc({arc:' decks '})==='' && rouArc({arc:''})==='' && rouArc({})==='' && rouArc({arc:'Battle City'})==='Battle City');
// the spin: frame sequence driven by fake timestamps (no browser, no rAF)
{ const from=37, to=rouTarget(from,5,12,.2,6), t0=1000, dur=4800; let prev=-1, mono=true, first=null, last=null, n=0;
  for(let now=t0-50; now<=t0+dur+500; now+=16){ const f=rouFrame(from,to,t0,now,dur); if(f.rot<prev-1e-9) mono=false; prev=f.rot; if(first===null) first=f.rot; last=f; n++; }
  t.push(mono && first===from && last.rot===to && last.done===true && rouIndexAt(last.rot,12)===5 && n>300);
  const mid=rouFrame(from,to,t0,t0+dur/2,dur); t.push(mid.rot>from+(to-from)*.9 && mid.rot<to && mid.done===false);   // ease-out: most of the turn is done at half time
}
t.push(rouFlip(10,0)===false && rouFlip(200,0)===true && rouFlip(200,-100)===false && rouFlip(350,30)===false && rouFlip(10,-30)===true);
t.push(rouShort('Seto Kaiba',6)==='Seto' && rouShort('Seto Kaiba',9)==='Seto K.');
let upright=true; for(let m=0;m<360;m+=7.5) for(let rot=-720;rot<720;rot+=13.7){ let net=(((rouFlip(m,rot)?m+90:m-90)+rot)%360+360)%360; if(net>180) net-=360; if(Math.abs(net)>90.0001) upright=false; }
t.push(upright);
// geometry: points are on the circle, angle 0 is the top
const p0=rouPol(0,100), p1=rouPol(90,100); t.push(Math.abs(p0[0]-200)<1e-9 && Math.abs(p0[1]-100)<1e-9 && Math.abs(p1[0]-300)<1e-9 && Math.abs(p1[1]-200)<1e-9);
console.log(JSON.stringify(t));
'''
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8', errors='replace')
    try:
        res = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        res = []
    labels = ['one slice per duelist, decks grouped, series order', 'series filters', 'a duelist is thematic only when all their decks are', 'the face is kept (null stays null)', 'seeded RNG is reproducible',
              'a seed gives a deterministic pick', 'every deck can be picked (300 seeds)', 'a big pool is cut to ROU_MAX unique slices', 'the sample keeps every series, small ones whole',
              'the duelist coming from a shared URL is always on the wheel', 'the sample keeps the canonical order', 'a pool that fits is not sampled; one series of 31 is cut to ROU_MAX',
              'the landing angle puts the picked slice under the pointer (1..24 slices, any start)', 
              'face URL is built like charVic',
              'face URL encodes segments and handles no face', 'monogram initials', 'names are shortened to fit', 'the generic arc "Decks" is dropped', 'frame sequence: angle never goes back, starts at the start angle, ends exactly on the picked slice', 'ease-out: fast first, slow end', 'label flip follows the on-screen angle', 'a long name falls back to the first name', 'a label never reads further than 90 degrees from horizontal, at any wheel angle', 'wheel geometry']
    check(len(res) == len(labels), 'node ran the pure-helper harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:200]))
    for ok, lab in zip(res, labels):
        check(ok, 'pure: ' + lab)

# ---- rouTick with a fake clock ----
tick = re.search(r'/\*ROU-TICK-START\*/(.*?)/\*ROU-TICK-END\*/', src, re.S)
check(bool(tick) and bool(pure), 'the tick function is delimited in src.html')
if tick and pure:
    harness = pure.group(1) + r'''
const log=[]; let lands=0;
const mkT=m=>{ const at={}; return {dataset:{mid:String(m),xo:'300',xi:'100',fl:''},setAttribute:(k,v)=>{ at[k]=v; },at}; };
const labs=[5,95,185,275,340].map(mkT);
const document={getElementById:()=>null,querySelectorAll:q=>q.includes('rl-full')?labs:[]};
const ROU={anim:null,rot:0};
function rouLand(){ lands++; ROU.rot=ROU.anim.to; ROU.anim=null; }
''' + tick.group(1) + r'''
const n=10, i=3, from=12, to=rouTarget(from,i,n,.1,5);
ROU.anim={from,to,t0:500,dur:4800,n,last:from,idx:rouIndexAt(from,n),kick:0}; ROU.rot=from;
let prev=-1, mono=true, calls=0, up=true;
for(let now=480; ROU.anim && now<20000; now+=16.7){ const f=rouTick(now); calls++; if(ROU.rot<prev-1e-9) mono=false; prev=ROU.rot;
  for(const L of labs){ const fl=L.at['text-anchor']==='start'; let net=((((fl?+L.dataset.mid+90:+L.dataset.mid-90)+ROU.rot)%360)+360)%360; if(net>180) net-=360; if(Math.abs(net)>90.0001) up=false; } }
console.log(JSON.stringify([mono, lands===1, ROU.rot===to, rouIndexAt(ROU.rot,n)===i, calls>250&&calls<400, rouTick(99999)===null, up, labs.every(L=>L.at.transform&&L.at.x)]));
'''
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8', errors='replace')
    try:
        res = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        res = []
    labels = ['rouTick: the angle never goes back across the whole spin', 'rouTick: lands exactly once', 'rouTick: ends on the exact target angle',
              'rouTick: the pointer ends on the picked duelist', 'rouTick: about 4.8 s of frames at 60 fps', 'rouTick: does nothing when no spin is running', 'rouTick: on every frame no name is upside down, whatever slice it is on', 'rouTick: labels always carry x and transform']
    check(len(res) == len(labels), 'node ran the rouTick harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:200]))
    for ok, lab in zip(res, labels):
        check(ok, lab)

# ---- routes in node: the roulette URL round trip ----
core = re.search(r'const ROUTE_MODES=.*?function routeBuild\(st\)\{.*?\n\}\n', page, re.S)
if core:
    harness = r'''
const slug = s => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-');
%s
const t=[]; const P=(s)=>routeParse(s,'');
let r=P('?mode=roulette&deck=sample-yami-yugi&seed=7&series=gx');
t.push(r.mode==='rou' && r.deck==='sample-yami-yugi' && r.seed===7 && r.series==='gx');
r=P('?mode=roulette&seed=abc&series=nope&deck=%%3Cb%%3E'); t.push(r.mode==='rou' && r.seed===null && r.series==='' && /^[a-z0-9-]*$/.test(r.deck));
r=P('?mode=tcg&seed=7'); t.push(r.seed===null);
t.push(routeBuild({mode:'rou',tcgf:'',view:'meta',deck:'',seed:null,series:'all'})==='?mode=roulette');
t.push(routeBuild({mode:'rou',tcgf:'',view:'meta',deck:'sample-yami-yugi',seed:7,series:'gx'})==='?mode=roulette&deck=sample-yami-yugi&series=gx&seed=7');
t.push(routeName('rou','')==='roulette' && routeParse('','#rou').mode==='rou');
console.log(JSON.stringify(t));
''' % core.group(0)
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8', errors='replace')
    try:
        res = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        res = []
    labels = ['URL -> state keeps deck, seed and series', 'bad seed, series and deck are sanitised', 'seed only counts in the roulette', 'plain roulette URL',
              'state -> URL with deck, series and seed', 'route name and old #rou hash']
    check(len(res) == len(labels), 'node ran the roulette route harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:200]))
    for ok, lab in zip(res, labels):
        check(ok, 'route: ' + lab)
else:
    check(False, 'route helpers found in index.html')

# ---- wiring ----
check('id="tab-rou" data-mode="rou"' in src and src.index('id="tab-eng"') < src.index('id="tab-rou"') < src.index('id="tab-deck"'), 'the tool button sits between Engines and Constructor')
check("rou:['Ruleta de decks',viewRoulette]" in src and "roulette:['rou','']" in src, 'MODES and ROUTE_MODES know the roulette')
check("loadData('roulette')" in src, 'the roulette data is loaded with loadData')
check("if(mode==='rou') rouAfter();" in src and "'guide','rou'].includes(mode)) render()" in src, 'render() finishes the roulette and redraws when card limits arrive')
check('ROUTE.deck=ROU.deck' in src and "seed:mode==='rou'?ROU.seed:null" in src, 'the shared URL carries deck, seed and series')
check('const rouReduced=' in src and "if(rouReduced()){ ROU.rot=to; rouLand(); return; }" in src and 'prefers-reduced-motion:reduce){.rou-in' in src, 'reduced motion lands at once, no spin and no transition')
check('aria-live' in src[src.index('function rouAfter'):] and "id='rou-live'" in src and 'role="img" aria-label=' in src, 'the result is announced in an aria-live region and the wheel has a text label')
check('data-rspin' in src and 'data-rser' in src and 'aria-pressed="${ROU.series===s}"' in src and '<button class="rou-hub" data-rspin="1"' in src, 'spin and series chips are real buttons (keyboard) with aria-pressed')
check('copias</b> son cartas que salen en el anime' in src and 'Reemplazos · ${sw.length}' in src and 'rouLegal' not in src and 'rou-leg"' not in src, 'result shows fidelity and replacements; no legality block (the decks are meme decks)')
check('data-todeck' in src[src.index('function decklistNow'):src.index('function decklistNow') + 6000] and 'decklistNow(l,\'tcg\')' in src, 'the recipe reuses decklistNow (price, gallery/list, open in the constructor)')
check('rou-m f1' in src and 'rou-m f2' in src and 'Sin marca' in src, 'replacement and completion markers have a legend')
check("d.kind==='thematic'" in src and 'Temático' in src and 'Base del mazo' in src and 'rf-th' in src and 'Thematic' in page, 'thematic decks show a Temático badge (result, landing, wheel) and their basis instead of the fidelity bar')
check('rouFace(' in src and 'rouSig(' in src and 'rf-mono' in src and 'onerror="this.remove()"' in src, 'faces with monogram fallback and the signature card are drawn')
check('rouFaceUrl(c.face)' in src and "'https://s3.duellinksmeta.com'+String(p).split('/').map(encodeURIComponent).join('/')" in src, 'the face URL is built like charVic')
check('.seg.rou-ser{display:flex;flex-wrap:nowrap;overflow-x:auto' in open('tools/mobile.css', encoding='utf-8').read() and '.tools{grid-template-columns:repeat(3' in open('tools/mobile.css', encoding='utf-8').read() and '.rou-stage{grid-template-columns:minmax(0,1fr)' in open('tools/mobile.css', encoding='utf-8').read(), 'phone rules are in mobile.css (labels drop, wheel shrinks)')
check(open('tools/mobile.css', encoding='utf-8').read().strip() in src, 'mobile.css is injected in src.html')
check('rou-res' in page and 'Deck roulette' in page, 'index.html was rebuilt with the tool and its English strings')

# ---- the result layout ----
check(src.count('data-rspin') == 1 and 'class="rou-hub" data-rspin="1"' in src, 'there is exactly one spin button and it sits on the wheel hub')
check("d?'Girar de nuevo':'Girar'" in src and 'rou-spin' not in src, 'the hub says Girar first and Girar de nuevo after a result; no second spin button')
check('object-fit:cover;object-position:50% 12%;transform:scale(1.55)' in src, 'faces are zoomed in so the rectangular portrait frame is cropped by the circle')
check('rou-lgl' not in src and 'rouBest' not in src and 'ROU_FMTS' not in src, 'no per-format legality lines in the roulette')
check("ROU_MAX=16" in src and 'min(27,' in src, 'the wheel has at most 16 slices and big faces')
check("filter(([a,b])=>a!==b&&canon(a)!==canon(b))" in src and 'No existe en el TCG' in src and 'class="rou-nx"' in src, 'no-op replacements are hidden, each swap says why, and the missing-card count is visible')
check('copias</b> son cartas que salen en el anime' in src and "lang=\"es\"" in src, 'the fidelity says what the percentage counts and the Spanish data text is marked as such')
check('rouIdle' in src and 'rouFlip' in src and 'rouPop' in src, 'idle pulse on the hub and a reveal animation')
check('--rou-km' in src and '--rou-ink' in src and '.rou-w.done .sl:not(.win){opacity:.82}' in src, 'day mode: saturated slices with an ink colour per theme, non-winners are not washed out')
check(src.count('rou-hero') >= 3 and 'id="rou-h"' in src and src.count('id="rou-h"') == 1, 'one merged hero: face, signature card, deck, actions')
check('data-rcopy' in src and 'data-todeck="${ROU.recIdx}"' in src and 'Copiar enlace' in src, 'the hero has "Copiar enlace" and "Abrir en el constructor"')
check("rouArc(d)" in src and "ROU_SER[d.series]" in src, 'the series name is always shown under the duelist and the generic arc is dropped')
check('Muestra para probar' not in src and 'Muestra para probar' not in raw, 'no placeholder copy in the page or the data')
check(re.search(r'class="fc"', src) is not None and 'rouUpright' in src, 'faces are counter-rotated so they stay upright')
check("rouFlip(+t.dataset.mid,ROU.rot)" in src and 'data-xi=' in src and 'rouFlip(m,ROU.rot)' in src, 'names are re-oriented on every frame so none is ever upside down')
check("rou-swart" in src and 'cardImg(canon(b),false)' in src, 'replacements show the card image')

# ---- English ----
en = json.load(open('tools/i18n_en.json', encoding='utf-8'))
st = json.load(open('tools/i18n_static.json', encoding='utf-8'))
need = ['Girar', 'Girar de nuevo', 'Girando…', 'duelista', 'duelistas', 'Ruleta de decks', 'Mazo jugable con cartas reales']
check(all(en.get(k) for k in need) and st.get('Ruleta de decks') == 'Deck roulette', 'the tool strings and the tab label have English entries')
check(not [k for k, v in en.items() if 'rou-' in k and re.search(r'\b(Reemplaz|Fidelidad|Legalidad|Carta insignia|Cargando)', v)], 'no Spanish is left in the English roulette templates')
check(subprocess.run([sys.executable, 'tests/check_i18n.py'], capture_output=True, text=True, encoding='utf-8').returncode == 0, 'tests/check_i18n.py passes')

print('failed:', len(fails))
sys.exit(1 if fails else 0)

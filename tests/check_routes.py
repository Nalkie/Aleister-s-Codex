"""Gate test de los enlaces profundos (?mode=…&view=…&deck=…).  Sin red.  Run from the project root:  python tests/check_routes.py

  * routeParse / routeBuild / routeName (se ejecutan en node): URL -> estado -> URL, enlaces viejos (#tcg, mode=gen), valores raros.
  * La página: usa pushState al cambiar de pestaña o formato, replaceState al abrir un mazo, escucha popstate, lee la URL al cargar.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


page = open('index.html', encoding='utf-8').read()
core = re.search(r'const ROUTE_MODES=.*?function routeBuild\(st\)\{.*?\n\}\n', page, re.S)
check(bool(core), 'the route helpers are in index.html')
if core:
    harness = r'''
const slug = s => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-');
%s
const t = [];
const P = (s, h) => routeParse(s, h);
let r = P('?mode=edison&deck=Vayu Turbo');            t.push(r.mode==='tcg' && r.tcgf==='edison' && r.deck==='vayu-turbo' && r.view==='meta');
r = P('?mode=genesys&view=staples');                  t.push(r.mode==='gen' && r.view==='staples');
r = P('?mode=duellinks');                             t.push(r.mode==='dl');
r = P('?mode=tcg&view=nonsense');                     t.push(r.view==='meta');
r = P('?mode=nope');                                  t.push(r.mode==='');
r = P('', '#ex');                                     t.push(r.mode==='ex' && r.name==='cards');
r = P('?mode=gen');                                   t.push(r.mode==='gen' && r.name==='genesys');
r = P('?mode=cards&card=Dark%%20Magician');           t.push(r.mode==='ex' && r.card==='Dark Magician');
r = P('?mode=tcg&card=X');                            t.push(r.card==='');
r = P('?mode=tcg&deck=%%3Cscript%%3E');               t.push(/^[a-z0-9-]*$/.test(r.deck));
t.push(routeBuild({mode:'tcg',tcgf:'adv',view:'meta',deck:''})==='?mode=tcg');
t.push(routeBuild({mode:'tcg',tcgf:'edison',view:'staples',deck:'blackwing'})==='?mode=edison&view=staples&deck=blackwing');
t.push(routeBuild({mode:'gen',tcgf:'',view:'meta',deck:''})==='?mode=genesys');
t.push(routeBuild({mode:'dl',tcgf:'',view:'engines',deck:'x'})==='?mode=duellinks&view=engines&deck=x');
t.push(routeBuild({mode:'ex',tcgf:'',view:'meta',deck:'',card:'Dark Magician'})==='?mode=cards&card=Dark+Magician');
t.push(routeName('tcg','ocg')==='ocg' && routeName('tcg','')==='tcg' && routeName('eng','')==='engines');
// ida y vuelta: todo modo de la tabla sobrevive URL -> estado -> URL
let rt = true;
for (const k of Object.keys(ROUTE_MODES)) { const a = P('?mode='+k); const b = routeBuild({mode:a.mode, tcgf:a.tcgf, view:'meta', deck:''}); if (b !== '?mode='+k) rt = false; }
t.push(rt);
r = P('?mode=md&view=staples');                      t.push(r.mode==='md' && r.name==='md' && r.tcgf==='' && r.view==='staples');
t.push(routeBuild({mode:'md',tcgf:'',view:'meta',deck:''})==='?mode=md' && routeName('md','')==='md');
console.log(JSON.stringify(t));
''' % core.group(0)
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['mode=edison + deck (slug normalised)', 'mode=genesys + view=staples', 'mode=duellinks', 'unknown view falls back to meta', 'unknown mode gives no route',
              'old #ex hash still works', 'old mode=gen is renamed genesys', 'card= is kept in the card search', 'card= is ignored outside the card search',
              'deck slug is sanitised (no markup)', 'default TCG writes only ?mode=tcg', 'edison + staples + deck', 'genesys URL', 'duellinks + engines + deck',
              'card search URL carries the card', 'routeName for ocg / tcg / engines', 'every mode survives URL -> state -> URL', 'mode=md is its own mode (not a TCG format)', 'Master Duel URL and name']
    check(len(res) == len(labels), 'node ran the route harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:160]))
    for ok, lab in zip(res, labels):
        check(ok, 'route: ' + lab)

check('history.pushState(null' in page and 'history.replaceState(null' in page, 'the page uses pushState and replaceState')
check("addEventListener('popstate'" in page, 'Back / Forward re-read the URL (popstate)')
check('if(!routeFromUrl())' in page, 'the URL is read on load, the old #hash is the fallback')
check('data-slug="${deckSlug(' in page, 'every deck row carries its slug')
check("history.replaceState(null,'','#'+mode)" not in page, 'the old #hash writer is gone')

print('failed:', len(fails))
sys.exit(1 if fails else 0)

"""Gate test del simulador de mano inicial (Constructor de mazos).  Sin red.  Run from the project root:  python tests/check_hand.py

  * handDeck / handShuffle / handDeal / handDraw (en node): 5 cartas, nunca más copias de las que tiene el mazo, mulligan y robo coherentes, azar inyectable.
  * La página: el botón «Probar mano», «Mulligan / Nueva mano» y «Robar 1 carta extra» existen y cualquier cambio del mazo borra la mano.
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
core = re.search(r'const HAND_SIZE=5;.*?function handDraw\(H\)\{.*?\}\n', page, re.S)
check(bool(core), 'the hand functions are in index.html')
if core:
    harness = r'''
%s
const main = {A: 3, B: 2, C: 1, D: 3, E: 3, F: 1, G: 1, H: 2};      // 16 cartas
const total = 16, t = [];
let seed = 7; const rnd = () => (seed = (seed * 16807) %% 2147483647) / 2147483647;
t.push(handDeck(main).length === total);
let d = handDeal(main, rnd);
t.push(d.hand.length === 5 && d.rest.length === total - 5);
// el mazo completo (mano + resto) tiene exactamente las copias del Main
const multiset = x => JSON.stringify(Object.entries(x.reduce((m, c) => (m[c] = (m[c] || 0) + 1, m), {})).sort());
t.push(multiset(d.hand.concat(d.rest)) === multiset(handDeck(main)));
// 2000 manos: nunca más copias de las que hay, y todas las cartas salen alguna vez
let over = false; const seen = new Set();
for (let i = 0; i < 2000; i++) { const h = handDeal(main, rnd).hand; const c = {}; h.forEach(n => { c[n] = (c[n] || 0) + 1; seen.add(n); }); for (const n in c) if (c[n] > main[n]) over = true; }
t.push(!over && seen.size === Object.keys(main).length);
// robar: suma una carta de las que quedan; al vaciarse, false
const top = d.rest[0]; const before = d.rest.length;
t.push(handDraw(d) === true && d.hand.length === 6 && d.hand[5] === top && d.rest.length === before - 1);
let guard = 0; while (handDraw(d) && guard++ < 100) {}
t.push(d.hand.length === total && d.rest.length === 0 && handDraw(d) === false);
// mulligan: otra mano repartida desde el mazo completo
const m1 = handDeal(main, rnd), m2 = handDeal(main, rnd);
t.push(m2.hand.length === 5 && m2.rest.length === total - 5);
// mismo azar, misma mano; mazo de 5: mano completa y sin resto; mazo de 4: mano corta
seed = 99; const x1 = handDeal(main, rnd).hand.join(); seed = 99; const x2 = handDeal(main, rnd).hand.join(); t.push(x1 === x2);
const five = handDeal({Z: 5}, rnd); t.push(five.hand.length === 5 && five.rest.length === 0);
t.push(handDraw(null) === false);
// no modifica el mazo original
t.push(JSON.stringify(main) === JSON.stringify({A: 3, B: 2, C: 1, D: 3, E: 3, F: 1, G: 1, H: 2}));
console.log(JSON.stringify(t));
''' % core.group(0)
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['handDeck expands copies', 'a deal is 5 cards + the rest', 'hand + rest is exactly the Main Deck', '2000 hands never exceed the copies in the deck and every card shows up',
              'drawing adds the next card of the shuffled deck', 'drawing past the end stops', 'mulligan deals 5 again from the full deck', 'same random source, same hand',
              'a 5-card deck deals everything', 'drawing without a hand is a no-op', 'the deck is not modified']
    check(len(res) == len(labels), 'node ran the hand harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:160]))
    for ok, lab in zip(res, labels):
        check(ok, 'hand: ' + lab)

src = open('src.html', encoding='utf-8').read()
check('Probar mano' in src and 'Mulligan / Nueva mano' in src and 'Robar 1 carta extra' in src, 'the page has the three buttons (Probar mano, Mulligan / Nueva mano, Robar 1 carta extra)')
check(re.search(r'function dkDraft\(\)\{ DK\.hand=null;', src) is not None, 'any change to the deck clears the hand')
check("a==='hand-draw'" in src and "a==='hand'||a==='hand-new'" in src, 'dkAction handles hand, hand-new and hand-draw')
en = json.load(open('tools/i18n_en.json', encoding='utf-8'))
check(en.get('Mulligan / Nueva mano') == 'Mulligan / New hand' and en.get('Probar mano') == 'Test hand', 'English labels are translated')

print('failed:', len(fails))
sys.exit(1 if fails else 0)

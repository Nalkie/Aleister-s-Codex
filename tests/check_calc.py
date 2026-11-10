"""Gate test del botón «Calcular mejores jugadas» del Constructor.  Sin red.  Run from the project root:  python tests/check_calc.py

Outcome: el estimativo es correcto y reproducible: la similitud ordena bien los mazos, las probabilidades de mano coinciden con la hipergeométrica exacta,
la cobertura cuenta bien y la página nunca lo presenta como una tasa de victoria.
  * calcSimilarity / calcIdf, calcOpen, calcCover, calcRun (en node, con mazos y fichas sintéticos)
  * La página: botón, aviso de estimativo, el cálculo se borra al cambiar el mazo, se carga en diferido
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


src = open('src.html', encoding='utf-8').read()
core = re.search(r'const CALC_TRIALS=.*?\nconst CALC_PREFIX=', src, re.S)
hand = re.search(r'function handDeck\(main\)\{[^\n]*\n', src)
check(bool(core and hand), 'the calc functions are in src.html')
if core and hand:
    code = hand.group(0) + core.group(0)[:-len('const CALC_PREFIX=')]
    harness = r'''
%s
const t = [];
const L = (m, e) => ({main: Object.entries(m).map(([n, k]) => [n, k, 50]), extra: Object.entries(e || {}).map(([n, k]) => [n, k, 50]), side: []});
const mk = (n, m, e, share, out) => ({n, list: L(Object.assign({Fill: 27}, m), e), share: share || 10, out: !!out, tier: 'T1'});      // Fill: relleno común, como las cartas de uso general de un mazo real
const A = mk('Alpha', {Ash: 3, A1: 3, A2: 3, A3: 2, A4: 2}, {AX: 1});
const B = mk('Beta', {Ash: 3, B1: 3, B2: 3, B3: 2, B4: 2}, {BX: 1});
const C = mk('Gamma', {Ash: 3, C1: 3, C2: 3, C3: 2, C4: 2}, {CX: 1});
const decks = [A, B, C], idf = calcIdf(decks);
// similitud: la propia lista es 1; lista sin cartas en común es 0; la solo de staples pesa menos que la de un arquetipo
const own = {main: {Ash: 3, A1: 3, A2: 3, A3: 2, A4: 2, Fill: 27}, extra: {AX: 1}};
t.push(Math.abs(calcSimilarity(own, A, idf) - 1) < 1e-9);
t.push(calcSimilarity({main: {Z: 3}, extra: {}}, A, idf) === 0);
t.push(calcSimilarity(own, A, idf) > calcSimilarity(own, B, idf) && calcSimilarity(own, B, idf) > 0);
const staples = {main: {Ash: 3}, extra: {}};
t.push(calcSimilarity(staples, A, idf) < 0.2);
t.push(calcIdf(decks)('Ash') < calcIdf(decks)('A1'));
// una copia menos baja la similitud sin tirarla
const less = {main: {Ash: 3, A1: 3, A2: 3, A3: 1, A4: 2, Fill: 27}, extra: {AX: 1}};
t.push(calcSimilarity(less, A, idf) < 1 && calcSimilarity(less, A, idf) > 0.8);
// calcOpen vs la hipergeométrica exacta: 40 cartas, 3 de X y 2 de Y, mano de 5
const C2 = (n, k) => { let r = 1; for (let i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; };
const pNone = (copies, deck, hand) => C2(deck - copies, hand) / C2(deck, hand);
const main40 = {X: 3, Y: 2, Z: 35};
const o5 = calcOpen(main40, [['X'], ['X', 'Y']], 5, 60000, calcRng(1));
t.push(Math.abs(o5.routes[0] - (1 - pNone(3, 40, 5))) < 0.01);
const exactXY = 1 - pNone(3, 40, 5) - pNone(2, 40, 5) + C2(35, 5) / C2(40, 5);
t.push(Math.abs(o5.routes[1] - exactXY) < 0.01);
t.push(Math.abs(o5.any - o5.routes[0]) < 1e-9);      // «alguna ruta» = la unión: X solo ya incluye a X+Y
const o6 = calcOpen(main40, [['X']], 6, 60000, calcRng(2));
t.push(o6.routes[0] > o5.routes[0] && Math.abs(o6.routes[0] - (1 - pNone(3, 40, 6))) < 0.01);
t.push(calcOpen(main40, [['X', 'NoEsta']], 5, 5000, calcRng(3)).routes[0] === 0);
t.push(calcOpen({X: 3}, [['X']], 5, 100, calcRng(4)) === null);
t.push(calcOpen(main40, [], 5, 100, calcRng(4)) === null);
// reproducible: mismo mazo, mismas cifras; el orden de las claves no cambia la semilla
t.push(calcSeed({a: 1, b: 2}) === calcSeed({b: 2, a: 1}) && calcSeed({a: 1}) !== calcSeed({a: 2}));
const r1 = calcOpen(main40, [['X']], 5, 2000, calcRng(calcSeed(main40))), r2 = calcOpen(main40, [['X']], 5, 2000, calcRng(calcSeed(main40)));
t.push(r1.routes[0] === r2.routes[0]);
// cobertura: Main cuenta, Side cuenta aparte, la carta repetida se cuenta una vez, lo que falta se lista
const sheet = {chokepoints: [{card: 'Ash'}, {card: 'Veiler'}, {card: 'Nibiru'}, {card: 'Ash'}], starters: [{cards: ['A1'], route: {es: 'r', en: 'r'}}], win: {bullets: [{es: 'b', en: 'b'}]}};
const cv = calcCover({main: {Ash: 3}, extra: {}, side: {Veiler: 2, Ash: 1}}, sheet);
t.push(cv.total === 3 && cv.have === 2 && cv.side === 1 && JSON.stringify(cv.missing) === '["Nibiru"]');
// calcRun de punta a punta
const sheets = {'x/alpha': sheet, 'x/beta': sheet};
const slugOf = n => n.toLowerCase();
const u = {main: {Ash: 3, A1: 3, A2: 3, A3: 2, A4: 2, Fill: 27}, extra: {AX: 1}, side: {Veiler: 2}};
const res = calcRun(u, [A, B, C, mk('Delta', {D1: 3}, {}, 5, true)], sheets, 'x', slugOf);
t.push(res.matches.length >= 1 && res.matches[0].name === 'Alpha' && res.base && res.base.name === 'Alpha' && res.matches.every(m => m.sim >= CALC_SHOW));
t.push(!res.matches.some(m => m.name === 'Delta'));      // los ganadores fuera del meta no cuentan
t.push(res.routes.length === 1 && res.routes[0].p1 > 0 && res.routes[0].p2 > res.routes[0].p1 && res.routes[0].missing.length === 0);
t.push(res.win.length === 1 && res.any1 === res.routes[0].p1);
t.push(res.cover.length === 1 && res.cover[0].name === 'Beta' && res.noSheet === 1);      // contra el mazo base no hay cobertura; Beta tiene ficha, Gamma no
const noSheetRes = calcRun(u, [A, B, C], {}, 'x', slugOf);
t.push(noSheetRes.base && noSheetRes.routes.length === 0 && noSheetRes.cover.length === 0 && noSheetRes.noSheet === 2);
const far = calcRun({main: {Q: 40}, extra: {}, side: {}}, [A, B, C], sheets, 'x', slugOf);
t.push(far.base === null && far.routes.length === 0);
// parecido medio (entre CALC_MIN y CALC_APPLY): no se aplica la ficha, se avisa con near
const mid = {main: {Ash: 3, A1: 3, Fill: 34}, extra: {}, side: {}}, midSim = calcSimilarity(mid, A, idf);
const midRes = calcRun(mid, [A, B, C], sheets, 'x', slugOf);
t.push(midSim >= CALC_MIN && midSim < CALC_APPLY ? (midRes.base === null && midRes.near && midRes.near.name === 'Alpha' && midRes.routes.length === 0) : true);
// una ruta hecha de cartas del Extra Deck no se roba: cuenta como disponible y no como «falta»
const exSheet = {chokepoints: [{card: 'Ash'}], starters: [{cards: ['AX', 'A1'], route: {es: 'r', en: 'r'}}, {cards: ['AX'], route: {es: 'r', en: 'r'}}], win: {bullets: []}};
const exRes = calcRun(u, [A, B, C], {'x/alpha': exSheet}, 'x', slugOf);
t.push(exRes.routes.length === 2 && exRes.routes[0].p1 === 1 && exRes.routes[0].cards.length === 1 && exRes.routes.every(r => r.missing.length === 0) && exRes.routes.some(r => r.cards.includes('AX') && r.p1 > 0 && r.p1 < 1));
// una lista de solo staples nunca aplica una ficha
t.push(calcRun({main: {Ash: 3, Fill: 37}, extra: {}, side: {}}, [A, B, C], sheets, 'x', slugOf).base === null);
// sin cartas de la ruta: probabilidad 0 y «te falta»
const miss = calcRun({main: {Ash: 3, A2: 3, A3: 2, A4: 2, Fill: 30}, extra: {AX: 1}, side: {}}, [A, B, C], sheets, 'x', slugOf);
t.push(miss.routes.length === 1 && miss.routes[0].p1 === 0 && JSON.stringify(miss.routes[0].missing) === '["A1"]');
// velocidad: un mazo de 60 cartas contra 30 mazos
const many = []; for (let i = 0; i < 30; i++) many.push(mk('D' + i, {Ash: 3, ['K' + i]: 3, ['L' + i]: 3, ['M' + (i %% 7)]: 2}, {}, 30 - i));
const t0 = Date.now(); calcRun({main: {Ash: 3, K1: 3, L1: 3, Fill: 51}, extra: {}, side: {}}, many, {'x/d1': sheet}, 'x', slugOf); const ms = Date.now() - t0;
t.push(ms < 1500);
// no modifica lo que recibe
t.push(JSON.stringify(u.main) === JSON.stringify({Ash: 3, A1: 3, A2: 3, A3: 2, A4: 2, Fill: 27}));
console.log(JSON.stringify(t));
''' % code
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['a list identical to the deck scores 1', 'a list with no card in common scores 0', 'the own archetype scores higher than another',
              'a staples-only list scores under 0.2', 'a staple weighs less than an archetype card', 'one copy less lowers the score without sinking it',
              'P(card in 5) matches the exact hypergeometric', 'P(two cards in 5) matches the exact value', '"any route" is the union of the routes',
              'a 6-card hand (going second) matches the exact value and beats 5 cards', 'a route with a missing card has probability 0', 'a deck smaller than the hand returns null',
              'no routes returns null', 'the seed does not depend on key order', 'same deck, same numbers', 'coverage: Main, Side apart, duplicates once, missing listed',
              'calcRun picks the closest deck', 'decks outside the meta are not candidates', 'routes get probabilities, going second beats going first, nothing missing',
              'the plan bullets come from the sheet and any-route equals the single route', 'coverage skips the base deck, covers the decks with a sheet and counts those without',
              'no sheets: the match stays, routes and coverage are empty', 'a list nothing like the ranking has no base deck', 'a medium match shows "near" and applies no sheet', 'Extra Deck cards in a route are not drawn and not reported missing', 'a staples-only list never applies a sheet', 'a missing starter shows as probability 0 and "missing"',
              'a 60-card deck against 30 decks runs in under 1.5 s', 'the input is not modified']
    check(len(res) == len(labels), 'node ran the calc harness' + ('' if len(res) == len(labels) else ': ' + (r.stderr.strip().splitlines() or ['?'])[-1][:200]))
    for ok, lab in zip(res, labels):
        check(ok, 'calc: ' + lab)

check('data-dk="calc"' in src and 'Calcular mejores jugadas con esta configuración' in src, 'the Constructor has the "Calcular mejores jugadas con esta configuración" button')
check(re.search(r'function dkDraft\(\)\{ DK\.hand=null; DK\.calc=null;', src) is not None, 'any change to the deck clears the calculation')
check("a==='calc'" in src and '${handPanel()}${calcPanel()}' in src, 'dkAction handles calc and the panel is under the hand simulator')
check('no una tasa de victoria' in src and 'Estimativo' in src and 'no lo bastante como para aplicar su ficha' in src and 'Te faltan' in src and 'class="cmiss"' in src and 'calc-cov" open' in src, 'the panel says it is an estimate and not a win rate')
check(src.count('dkCalcGo(true)') == 2, 'the calculation resumes when the sheets and the format data arrive (playLoad and ymxLoad)')
go = src[src.index('function dkCalcGo'):src.index('function calcPanel')]
check('PLAY.data' in go and 'ymxLoad()' in go, 'it loads the tactical sheets and, for the other formats, the format data on demand')
en = json.load(open('tools/i18n_en.json', encoding='utf-8'))
check(en.get('Calcular mejores jugadas con esta configuración') == 'Calculate best plays with this setup', 'the button is translated')
print('failed:', len(fails))
sys.exit(1 if fails else 0)

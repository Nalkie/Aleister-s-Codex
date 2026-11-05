"""Can this deck be played?  Deterministic checks on a roulette deck (no network) that find the ways a list bricks: an Extra Deck monster whose summon the cards of the deck can never
pay for (a Fusion with no Polymerization, a Synchro whose levels no Tuner reaches, an Xyz without two monsters of its level...), a Ritual without its Spell, too few monsters to start.

  python tools/playable.py [thematic|all] [deck id]      the problems of every deck (exit 1 if a thematic deck has any)

The rules read the summon requirement of the first line of each card text (src/ygo_all.json): '"A" + "B"', '2 Level 4 Dragon-Type monsters', '1 Tuner + 1+ non-Tuner WIND monsters'.
Materials are the monsters of the Main Deck (one per copy); Extra Deck monsters are not counted as materials.  A summon that also has another way in (a card text with "can also")
is accepted.  This is a floor, not a guarantee that the deck is good: it finds decks that cannot do what their Extra Deck promises."""
import itertools, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_db = {}
RACES = ('Warrior', 'Spellcaster', 'Fairy', 'Fiend', 'Zombie', 'Machine', 'Aqua', 'Pyro', 'Rock', 'Winged Beast', 'Plant', 'Insect', 'Thunder', 'Dragon', 'Beast', 'Beast-Warrior',
         'Dinosaur', 'Fish', 'Sea Serpent', 'Reptile', 'Psychic', 'Divine-Beast', 'Wyrm', 'Cyberse')
ATTRS = ('LIGHT', 'DARK', 'EARTH', 'WATER', 'FIRE', 'WIND', 'DIVINE')
MIN_STARTERS = 10


def db():
    if not _db:
        for c in json.load(open(os.path.join(ROOT, 'src/ygo_all.json'), encoding='utf-8')):
            _db[c['name']] = c
    return _db


def kind(name):
    t = db()[name]['type']
    return ('fusion' if 'Fusion' in t else 'synchro' if 'Synchro' in t else 'xyz' if 'XYZ' in t else 'link' if 'Link' in t else 'ritual' if 'Ritual' in t and 'Monster' in t else
            'monster' if 'Monster' in t else 'spell' if 'Spell' in t else 'trap')


def first_line(name):
    return (db()[name].get('desc') or '').split('\n')[0]


def matches(name, want):
    """Does the monster `name` fit one material slot `want` ({'name', 'race', 'attr', 'level', 'tuner', 'nontuner', 'arch'})?"""
    c = db()[name]
    if kind(name) not in ('monster', 'ritual'):
        return False
    if want.get('name'):
        return name == want['name']
    t = c['type']
    if want.get('tuner') and 'Tuner' not in t:
        return False
    if want.get('nontuner') and 'Tuner' in t:
        return False
    if want.get('races') and (c.get('race') or '') not in want['races']:
        return False
    if want.get('attr') and (c.get('attr') or '').upper() != want['attr']:
        return False
    if want.get('arch') and want['arch'] not in name:
        return False
    lv = c.get('level') or 0
    if want.get('levels') and lv not in want['levels']:
        return False
    if want.get('level') and lv != want['level']:
        return False
    if want.get('max_level') and lv > want['max_level']:
        return False
    if want.get('min_level') and lv < want['min_level']:
        return False
    return True


def slot(text):
    """The material slot a phrase describes: ('1 LIGHT Warrior monster', '"Name"', '1 Level 4 or lower monster', '1 "Arch" Tuner', '2+ non-Tuner WIND monsters') -> (slot, minimum count)."""
    s = text.strip()
    m = re.match(r'^"([^"]+)"$', s)
    if m:
        return {'name': m.group(1)}, 1
    n = 1
    m = re.match(r'^(\d+)(\+| or more)?\s*', s)
    if m:
        n, s = int(m.group(1)), s[m.end():]
    w = {}
    m = re.search(r'"([^"]+)"', s)
    if m:
        w['arch'] = m.group(1)
    if 'non-Tuner' in s:
        w['nontuner'] = True
    elif 'Tuner' in s:
        w['tuner'] = True
    rest, races = s, []
    for r in sorted(RACES, key=len, reverse=True):          # longest first, and a matched name is cut out ('Beast-Warrior' must not also count as 'Beast')
        pat = r'(?<![\w-])%s(?:-Type)?(?![\w-])' % re.escape(r)
        if re.search(pat, rest):
            races.append(r)
            rest = re.sub(pat, ' ', rest)
    if races:
        w['races'] = races
    for a in ATTRS:
        if re.search(r'\b' + a + r'\b', s):
            w['attr'] = a
    m = re.search(r'Level (\d+) or (lower|higher|(\d+))', s)
    if m and m.group(2) == 'lower':
        w['max_level'] = int(m.group(1))
    elif m and m.group(2) == 'higher':
        w['min_level'] = int(m.group(1))
    elif m:
        w['levels'] = [int(m.group(1)), int(m.group(3))]
    else:
        m = re.search(r'Level (\d+)', s)
        if m:
            w['level'] = int(m.group(1))
    return w, n


def assign(slots, pool):
    """Can every slot take a different card of pool (a list of names, one per copy)?  Backtracking; slots are few."""
    if not slots:
        return True
    first, rest = slots[0], slots[1:]
    for i, n in enumerate(pool):
        if matches(n, first):
            if assign(rest, pool[:i] + pool[i + 1:]):
                return True
    return False


def split_materials(line):
    return [p for p in re.split(r'\s\+\s', line) if p.strip()]


def fusion_enablers(main):
    return [n for n in main if kind(n) in ('spell', 'trap') and ('Fusion Summon' in (db()[n].get('desc') or '')[:120]
            or re.search(r'Special Summon 1 Level \d or lower Fusion Monster', db()[n].get('desc') or ''))]


def can_enable(enabler, fusion):
    """Polymerization fits any Fusion Monster; a card that names an archetype of Fusion Monsters ('Fossil Fusion Monster') only that one."""
    d = db()[enabler].get('desc') or ''
    m = re.search(r'"([^"]+)" Fusion Monster', d)
    if m and m.group(1) not in fusion:
        return False
    m = re.search(r'Special Summon 1 Level (\d) or lower Fusion Monster from your Extra Deck', d)
    return not (m and (db()[fusion].get('level') or 9) > int(m.group(1))) or 'Fusion Substitute' in d


def reachable(extra_name, main_mons, main, extra_all=()):
    """(True, '') when the cards of the Main Deck can pay for the summon of this Extra Deck monster, else (False, why)."""
    k, line = kind(extra_name), first_line(extra_name)
    desc = db()[extra_name].get('desc') or ''
    if k == 'fusion':
        if not any(can_enable(e, extra_name) for e in fusion_enablers(main)):
            return False, 'no card of the deck Fusion Summons it'
        instant = [e for e in fusion_enablers(main) if re.search(r'Special Summon 1 Level \d or lower Fusion Monster', db()[e].get('desc') or '')]
        if instant and (db()[extra_name].get('level') or 9) <= 5 and all(not can_enable(e, extra_name) or e in instant for e in fusion_enablers(main)):
            return True, ''
        parts = [slot(p) for p in split_materials(line)]
        if any('GY' in p for p in split_materials(line)):
            return True, ''
        slots = [s for s, n in parts for _ in range(max(n, 1))]
        return (True, '') if assign(slots, list(main_mons)) else (False, 'materials %s not in the deck' % line[:70])
    if k == 'xyz':
        if extra_name.startswith('Number C'):
            # a Chaos Number is Xyz Summoned on top of its Number with a Rank-Up-Magic Spell
            base = re.search(r'Number (\d+)', desc)
            ok = any('Rank-Up-Magic' in n for n in main) and any(re.match(r'Number %s:' % re.escape(extra_name.split(':')[0][len('Number C'):].strip()), x) for x in extra_all)
            return (True, '') if ok else (False, 'a Chaos Number needs its Number in the Extra Deck and a Rank-Up-Magic Spell')
        if 'can also' in desc or 'by using' in desc[:300] and 'Xyz Summon this card' in desc:
            return True, ''
        s, n = slot(line.replace(' monsters', ' monster').replace('-Type', ''))
        have = sum(1 for m in main_mons if matches(m, s))
        return (True, '') if have >= max(n, 2) else (False, 'needs %s, the deck has %d' % (line[:60], have))
    if k == 'synchro':
        parts = split_materials(line)
        if len(parts) != 2 or 'Tuner' not in line:
            return True, ''
        ts, _ = slot(parts[0])
        ns, nmin = slot(parts[1])
        tuners = [m for m in set(main_mons) if matches(m, ts)]
        others = [m for m in main_mons if matches(m, ns) and 'Tuner' not in db()[m]['type']]
        target = db()[extra_name].get('level') or 0
        lv = lambda n: db()[n].get('level') or 0
        for t in tuners:
            for size in range(max(nmin, 1), 5):
                for combo in itertools.combinations(range(len(others)), size):
                    if lv(t) + sum(lv(others[i]) for i in combo) == target:
                        return True, ''
        return (False, 'no %s + %s reaches level %d' % (parts[0], parts[1], target))
    if k == 'link':
        return (True, '') if len(main_mons) >= 8 else (False, 'too few monsters')
    return True, ''


def problems(deck):
    """[(code, text)] of a roulette deck as in data/roulette.js: {'main': [[name, copies, flag]], 'extra': [...]}."""
    main = [n for n, c, *_ in deck['main'] for _ in range(c)]
    mons = [n for n in main if kind(n) in ('monster', 'ritual')]
    out = []
    for name in sorted({n for n, *_ in deck['extra']}):
        ok, why = reachable(name, mons, main, [n for n, *_ in deck['extra']])
        if not ok:
            out.append(('EXTRA-UNREACHABLE', '%s: %s' % (name, why)))
    rit = [n for n in main if kind(n) == 'ritual']
    spells = [n for n in main if kind(n) == 'spell' and 'Ritual Summon' in (db()[n].get('desc') or '')]
    if rit and not spells:
        out.append(('RITUAL-NO-SPELL', 'Ritual Monsters %s and no Ritual Spell' % sorted(set(rit))))
    if spells and not rit:
        out.append(('RITUAL-NO-MONSTER', 'Ritual Spells and no Ritual Monster'))
    starters = sum(1 for n in mons if (db()[n].get('level') or 9) <= 4 and 'Cannot be Normal Summoned' not in (db()[n].get('desc') or ''))
    if starters < MIN_STARTERS:
        out.append(('FEW-STARTERS', 'only %d monsters of level 4 or less that can be Normal Summoned (min %d)' % (starters, MIN_STARTERS)))
    return out


def load_decks():
    t = open(os.path.join(ROOT, 'data/roulette.js'), encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex(')')])['decks']


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'thematic'
    only = sys.argv[2] if len(sys.argv) > 2 else None
    bad = flagged = 0
    for d in load_decks():
        if (which == 'thematic' and d['kind'] != 'thematic') or (only and d['id'] != only):
            continue
        p = problems(d)
        if p:
            flagged += 1
            bad += d['kind'] == 'thematic'
            print('%-52s %s %s' % (d['id'], d['series'], d['kind']))
            for code, text in p:
                print('    %-18s %s' % (code, text[:170]))
    print(flagged, 'decks with problems')
    sys.exit(1 if bad else 0)

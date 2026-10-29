"""Deck roulette: anime decks of every character, playable with printed cards only.   Run from the project root:
  python tools/roulette.py build           src/roulette/*.json + src/anime_decks.json -> data/roulette.js   (no network, same input same output)
  python tools/roulette.py check           validates every sheet and prints the problems (exit 1 if any)
  python tools/roulette.py list <character>  the decklists the wiki has for a character (index, arc, title, cards kept / missing)
  python tools/roulette.py show <character> <title> [n]  every card of one wiki decklist: copies, Main or Extra, and whether the TCG has it
  python tools/roulette.py suggest <sheet id>  real decklists closest to a sheet, and the cards they play that the sheet does not (to pick replacements)

The data, in two layers:
  * src/anime_decks.json (tools/fetch_anime_decks.py): the decklists of the Yu-Gi-Oh! Wiki, as they are.  Every card that exists in the TCG database is kept as the wiki
    lists it; a card that is only in the anime (or the manga) is missing.
  * src/roulette/<series>.json: one sheet per roulette deck.  A person (or a builder agent) chooses which wiki decklist a deck comes from, and what replaces what the TCG
    does not have, always from a real decklist (a tournament or Master Duel deck, an Edison / Goat / HAT list) and never an invented one.
        {"id": {"character": "Jaden Yuki", "arc": "Seven Stars", "name": "Elemental HERO",
                "wiki": {"character": "Jaden Yuki", "title": "Elemental Hero Deck", "n": 0},         # n: which of the decklists with that title (0 = first)
                "blurb": "…",                                                                           # Spanish, one or two sentences
                "sig": "Elemental HERO Neos",                                                           # the signature card of the deck (shown next to the face of the duelist): a card of the deck
                "copies": {"Polymerization": 3},                                                        # the wiki lists most cards once: the copies the duel really showed or the deck needs
                "drop": [["Card", "why"]],                                                              # an anime card that exists but cannot be played as it appears (very rare)
                "add": [["Card", 2, "replace", "Missing Card", "ref: where a real list plays it"],     # replace: stands for a card the TCG does not have
                        ["Card", 3, "fill", "", "ref: …"]]}}                                           # fill: completes the 40 with what the same strategy really plays
Flags in data/roulette.js: 0 = the card of the anime deck, 1 = replaces a card the TCG does not have, 2 = fills the deck.  The page computes the legality against the
banlist of each format, nothing is removed for it."""
import collections, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERIES = ['dm', 'gx', '5d', 'zx']
MIN_MAIN, MAX_MAIN, MAX_EXTRA = 40, 60, 15
EXTRA_TYPES = ('Fusion', 'Synchro', 'XYZ', 'Link')
GENERIC_MAX = 6        # staples added only because they are generic (Pot of Greed, Mirror Force...) are capped: the deck must read as the character's
MIN_ANIME_SHARE = 0.5  # at least half of the copies of a deck are the anime ones

_db = {}

# The face of a duelist: the portrait Duel Links Meta (the same source as the Duel Links page) has for the character.  The names there are the game's, so some need a hand-made alias.
FACE_ALIAS = {'Bakura Ryou': 'Yami Bakura', 'Vellian Crowler': 'Dr. Vellian Crowler', 'Sartorius': 'Sartorius Kumar', 'Tetsu Trudge': 'Officer Tetsu Trudge',
              'Reginald Kastle': 'Reginald "Shark" Kastle', 'Rex Goodwin': 'Dark Signer Rex Goodwin', 'Yuma Tsukumo': 'Yuma and Astral', 'Astral': 'Yuma and Astral'}


def faces():
    """{character: portrait path of Duel Links Meta (/img/characters/...)} for the roulette characters that Duel Links Meta has."""
    norm = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    dl = {norm(c['n']): c['p'] for c in json.load(open(os.path.join(ROOT, 'src/dl_extra.json'), encoding='utf-8'))['chars'] if c.get('p')}
    return {ch: dl[norm(FACE_ALIAS.get(ch, ch))] for ch in anime_decks() if norm(FACE_ALIAS.get(ch, ch)) in dl}


def db():
    if not _db:
        for c in json.load(open(os.path.join(ROOT, 'src/ygo_all.json'), encoding='utf-8')):
            _db[c['name']] = c
    return _db


_norm = {}


def resolve(name):
    """The database spelling of a card name as the wiki writes it ("Elemental Hero Avian" -> "Elemental HERO Avian"), or None when the TCG does not have the card."""
    if not _norm:
        for n in db():
            _norm.setdefault(re.sub(r'[^a-z0-9]', '', n.lower()), n)
    return name if name in db() else _norm.get(re.sub(r'[^a-z0-9]', '', name.lower()))


def is_extra(name):
    t = db()[name]['type']
    return any(x in t for x in EXTRA_TYPES)


def anime_decks():
    return json.load(open(os.path.join(ROOT, 'src/anime_decks.json'), encoding='utf-8'))['characters']


def wiki_deck(ref):
    """The decklist of the wiki that a sheet points at: {'arc','title','sections'}."""
    ch = anime_decks().get(ref['character'])
    if not ch:
        return None
    same = [d for d in ch['decks'] if d['title'] == ref['title']]
    return same[ref.get('n', 0)] if len(same) > ref.get('n', 0) else None


def wiki_cards(deck):
    """-> ([(name, copies)] that the TCG has, [(name, copies)] that it does not), anime copies as the wiki lists them."""
    have, miss = collections.OrderedDict(), collections.OrderedDict()
    for cs in deck['sections'].values():
        for name, cp, _ in cs:
            real = resolve(name)
            tgt = have if real else miss
            tgt[real or name] = tgt.get(real or name, 0) + cp
    return list(have.items()), list(miss.items())


def load_sheets():
    out = collections.OrderedDict()
    for s in SERIES:
        p = os.path.join(ROOT, 'src/roulette', s + '.json')
        if os.path.exists(p):
            for k, v in json.load(open(p, encoding='utf-8')).items():
                out[k] = {**v, 'series': s}
    return out


def assemble(sheet):
    """-> (main [[name, copies, flag]], extra [[name, copies, flag]], problems)"""
    probs = []
    deck = wiki_deck(sheet['wiki'])
    if deck is None:
        return [], [], ['the wiki decklist %r does not exist' % (sheet['wiki'],)]
    have, miss = wiki_cards(deck)
    drop = {n for n, _ in sheet.get('drop', [])}
    cards = collections.OrderedDict()      # name -> [copies, flag]
    for n, cp in have:
        if n in drop:
            continue
        cards[n] = [min(3, sheet.get('copies', {}).get(n, cp)), 0]
    for n in sheet.get('copies', {}):
        if n not in cards and n not in drop:
            probs.append('copies: %s is not in the wiki decklist' % n)
    missing_left = {n for n, _ in miss}
    for a in sheet.get('add', []):
        if len(a) != 5:
            probs.append('add needs [card, copies, kind, for, ref]: %r' % (a,))
            continue
        n, cp, kind, for_, ref = a
        if n not in db():
            probs.append('add: %s is not a card of the database' % n)
            continue
        if kind not in ('replace', 'fill'):
            probs.append('add: %s has kind %r (replace or fill)' % (n, kind))
        if kind == 'replace':
            if for_ not in missing_left and for_ not in {x for x, _ in miss}:
                probs.append('add: %s replaces %r, which the wiki list does not miss' % (n, for_))
        if not str(ref).strip():
            probs.append('add: %s has no ref (the real list that plays it)' % n)
        if n in cards:
            cards[n][0] = min(3, cards[n][0] + cp)
        else:
            cards[n] = [min(3, cp), 1 if kind == 'replace' else 2]
    main, extra = [], []
    for n, (cp, fl) in cards.items():
        (extra if is_extra(n) else main).append([n, cp, fl])
    return main, extra, probs


def check_sheet(key, sheet):
    main, extra, probs = assemble(sheet)
    pr = lambda m: probs.append(m)
    for f in ('character', 'arc', 'name', 'blurb', 'wiki', 'sig'):
        if not sheet.get(f):
            pr('missing field ' + f)
    if sheet.get('sig') and sheet['sig'] not in {n for n, _, _ in main + extra}:
        pr('sig %s is not in the deck' % sheet['sig'])
    nm = sum(c for _, c, _ in main)
    ne = sum(c for _, c, _ in extra)
    if not (MIN_MAIN <= nm <= MAX_MAIN):
        pr('Main Deck has %d cards (%d-%d)' % (nm, MIN_MAIN, MAX_MAIN))
    if ne > MAX_EXTRA:
        pr('Extra Deck has %d cards (max %d)' % (ne, MAX_EXTRA))
    anime = sum(c for _, c, f in main + extra if f == 0)
    total = nm + ne
    if total and anime / total < MIN_ANIME_SHARE:
        pr('only %d%% of the copies are the anime ones (min %d%%)' % (anime * 100 // total, MIN_ANIME_SHARE * 100))
    fills = [(n, c) for n, c, f in main + extra if f == 2]
    if sum(c for _, c in fills) > max(GENERIC_MAX, total // 3):
        pr('too many filler copies (%d): the deck must read as the character\'s' % sum(c for _, c in fills))
    return probs


def build():
    FACES = faces()
    sheets = load_sheets()
    decks = []
    for key, sh in sheets.items():
        main, extra, _ = assemble(sh)
        deck = wiki_deck(sh['wiki'])
        have, miss = wiki_cards(deck)
        total = sum(c for _, c, _ in main + extra)
        anime = sum(c for _, c, f in main + extra if f == 0)
        decks.append({'id': key, 'series': sh['series'], 'character': sh['character'], 'arc': sh['arc'], 'name': sh['name'], 'blurb': sh['blurb'], 'sig': sh['sig'], 'face': FACES.get(sh['character']),
                      'wiki': {'page': anime_decks()[sh['wiki']['character']]['page'], 'title': sh['wiki']['title']},
                      'main': main, 'extra': extra,
                      'anime': round(anime * 100 / total) if total else 0,
                      'swapped': [[a[3], a[0]] for a in sh.get('add', []) if a[2] == 'replace' and a[3]],
                      'missing': [n for n, _ in miss]})
    order = {s: i for i, s in enumerate(SERIES)}
    decks.sort(key=lambda d: (order[d['series']], d['id']))
    js = '__load("roulette",' + json.dumps({'decks': decks}, ensure_ascii=False, separators=(',', ':')) + ');'
    open(os.path.join(ROOT, 'data/roulette.js'), 'w', encoding='utf-8').write(js)
    return decks


def real_decklists():
    """[(label, {card: copies})] of real decks we have: Master Duel top decks, TCG tournaments (YuGiOh Meta) and the Edison / Goat / HAT lists."""
    out = []
    md = json.load(open(os.path.join(ROOT, 'src/md.json'), encoding='utf-8'))
    for d in md['decks']:
        c = collections.Counter()
        for sec in ('main', 'extra', 'side'):
            for n, k in d[sec]:
                c[n.replace('Maliss P ', 'Maliss <P> ')] += k
        out.append(('md:%s · %s' % (d['type'], d['d']), c))
    for d in json.load(open(os.path.join(ROOT, 'src/ygm_topdecks.json'), encoding='utf-8')):
        c = collections.Counter()
        for sec in ('main', 'extra'):
            for e in d.get(sec) or []:
                if isinstance(e, dict) and (e.get('card') or {}).get('name'):
                    c[e['card']['name']] += e.get('amount', 1)
        if c:
            out.append(('tcg:%s · %s' % ((d.get('deckType') or {}).get('name', '?'), d.get('created', '')[:10]), c))
    return out


def suggest(key, top=6, cand=30):
    sh = load_sheets()[key]
    main, extra, _ = assemble(sh)
    mine = {n for n, _, _ in main + extra}
    generic = {n for n, c in collections.Counter(n for _, d in real_decklists() for n in d).items() if c > 0.25 * len(real_decklists())}
    scored = []
    for label, d in real_decklists():
        shared = [n for n in mine if n in d and n not in generic]
        if shared:
            scored.append((len(shared) / (len(mine) + len(d) - len(shared)), label, d))
    scored.sort(key=lambda x: -x[0])
    print('closest real decklists to', key)
    for s, label, d in scored[:top]:
        print('  %.2f  %s' % (s, label))
    freq = collections.Counter()
    for s, label, d in scored[:top]:
        for n, k in d.items():
            if n not in mine and n in db():
                freq[n] += k
    print('cards they play that the sheet does not:')
    for n, k in freq.most_common(cand):
        print('  %3d  %s  (%s)' % (k, n, db()[n]['type']))


def main():
    os.chdir(ROOT)
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'build':
        d = build()
        print('data/roulette.js', len(d), 'decks', collections.Counter(x['series'] for x in d))
    elif cmd == 'check':
        bad = 0
        for k, sh in load_sheets().items():
            for p in check_sheet(k, sh):
                print('ERROR', k + ':', p)
                bad += 1
        print('%d problems in %d sheets' % (bad, len(load_sheets())))
        sys.exit(1 if bad else 0)
    elif cmd == 'list':
        ch = anime_decks()[sys.argv[2]]
        seen = collections.Counter()
        for d in ch['decks']:
            have, miss = wiki_cards(d)
            print('n=%d  %-46s %-44s kept %3d  missing %3d' % (seen[d['title']], d['title'][:46], d['arc'][-44:], sum(c for _, c in have), sum(c for _, c in miss)))
            seen[d['title']] += 1
    elif cmd == 'show':
        d = wiki_deck({'character': sys.argv[2], 'title': sys.argv[3], 'n': int(sys.argv[4]) if len(sys.argv) > 4 else 0})
        print(d['arc'], '>', d['title'])
        for sec, cs in d['sections'].items():
            print('--', sec)
            for n, cp, an in cs:
                real = resolve(n)
                print('  %dx %-42s %s%s' % (cp, real or n, ('EXTRA ' if is_extra(real) else 'MAIN  ') if real else 'NOT IN THE TCG', ' (card differs in the anime)' if an and real else ''))
    elif cmd == 'suggest':
        suggest(sys.argv[2])
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()

"""Fill the card detail of the cards that only exist in Duel Links (every Rush Duel card and the Speed Duel cards with no TCG print):
effect text, type line and stats, from src/dl_text.json (tools/fetch_dltext.py). Edits data/c<N>.js in place; running it twice changes nothing.
Run from the project root after tools/build_db.py:  python tools/dltext.py"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROP_EFFECT = {'Fusion', 'Synchro', 'Xyz', 'Link', 'Ritual'}


def type_line(c):
    t, mt = c.get('type'), list(c.get('monsterType') or [])
    if t == 'Spell':
        return (c.get('race') or 'Normal') + ' Spell'
    if t == 'Trap':
        return (c.get('race') or 'Normal') + ' Trap'
    if DROP_EFFECT & set(mt):
        mt = [m for m in mt if m != 'Effect']
    return ' '.join(mt + ['Monster'])


def stats(c):
    if c.get('type') != 'Monster':
        return None
    link = 'Link' in (c.get('monsterType') or [])
    return [c.get('atk'), None if link else c.get('def'), None if link else c.get('level'), c.get('race'), c.get('attribute'), c.get('linkRating') if link else None, None]


def apply(det, dl_cards, texts):
    """det: {card name: detail}. Returns how many details were filled."""
    by = {}
    for c in dl_cards:
        by.setdefault((c['n'], bool(c.get('rush'))), c)
    n_filled = 0
    for name, d in det.items():
        if d.get('d') or not d.get('dl'):
            continue
        c = by.get((name, bool(d['dl'].get('rush'))))
        t = texts.get(c['id']) if c else None
        if not t or not (t.get('description') or '').strip():
            continue
        d['d'] = re.sub(r'\r\n?', '\n', t['description']).strip()
        d['ty'] = type_line(t)
        st = stats(t)
        if st:
            d['st'] = st
        n_filled += 1
    return n_filled


if __name__ == '__main__':
    os.chdir(ROOT)
    dl_cards = json.load(open('src/dl_cards.json', encoding='utf-8'))
    texts = json.load(open('src/dl_text.json', encoding='utf-8'))
    total = 0
    for f in sorted(x for x in os.listdir('data') if re.fullmatch(r'c\d+\.js', x)):
        t = open('data/' + f, encoding='utf-8').read()
        head = t[:t.index(',') + 1]
        det = json.loads(t[len(head):-2])
        n = apply(det, dl_cards, texts)
        if n:
            open('data/' + f, 'w', encoding='utf-8').write(head + json.dumps(det, ensure_ascii=False, separators=(',', ':')) + ');')
        total += n
    print('details filled from Duel Links Meta text:', total)

"""Archetype hubs data -> data/arch.js.  Run from the project root:  python tools/arch.py   (no network)

Outcome: every card page can say "Arquetipo: X" and "Aparece en el Lore: Y", and every archetype has a hub page, from one lazy file.
  n  archetype names (sorted)                       c  {card: index in n}   (src/archetypes.json filtered to cards in the database)
  l  {card: [lore slug, ...]}  cards shown in a Lore entry          la {lore slug: [index in n, ...]}  which archetype hubs each Lore entry belongs to
  ln {lore slug: entry name}
Lore entries about characters have no archetype; their cards still point back to them through l.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Archetype names that are only a fragment of a card name ("-Eyes Dragon", "Gem-"): not archetypes a player would look up
DENY = {'C', '-Eyes Dragon', 'Abyss-', 'Gem-', 'Fan-Made Cards', 'Greed', 'Anti', 'Change', 'Clear', 'Contact', 'Book of', 'Magician'}
# Cards YGOPRODeck files under a fragment archetype although the Lore (and the players) treat them as part of another one
MOVE = {'Snake-Eyes Doomed Dragon': 'Snake-Eye', 'Snake-Eyes Vengeance Dragon': 'Snake-Eye'}

# Lore entry -> the YGOPRODeck archetype names it tells the story of (checked by tests/check_arch.py)
LORE_ARCH = {
    'ancient-gear': ['Ancient Gear'],
    'blackwing': ['Blackwing'],
    'blue-eyes': ['Blue-Eyes'],
    'branded': ['Branded'],
    'dark-magician': ['Dark Magician'],
    'darklord': ['Darklord'],
    'dream-mirror': ['Dream Mirror'],
    'egyptian-gods': ['Egyptian God'],
    'eldlich': ['Eldlich'],
    'elemental-hero': ['Elemental HERO'],
    'exodia': ['Exodia'],
    'forbidden-maiden': ['Forbidden', 'Solemn'],
    'gusto': ['Gusto'],
    'invoked': ['Invoked'],
    'lightsworn': ['Lightsworn'],
    'live-evil-twin': ['Live☆Twin', 'Evil★Twin'],
    'machina': ['Machina'],
    'ritual-beast': ['Ritual Beast'],
    's-force': ['S-Force'],
    'sanctuary-in-the-sky': ['The Sanctuary in the Sky'],
    'shaddoll': ['Shaddoll'],
    'sky-striker': ['Sky Striker'],
    'snake-eye': ['Snake-Eye', 'Diabellstar', 'Diabell', 'Azamina', 'White Forest', 'Sinful Spoils'],
    'virtual-world': ['Virtual World'],
    'yubel': ['Yubel'],
    'world-chalice': ['World Chalice'],
    'cyber-dragon': ['Cyber Dragon'],
    'red-eyes': ['Red-Eyes'],
    'salamangreat': ['Salamangreat'],
    'dragon-ruler': ['Dragon Ruler'],
    'burning-abyss': ['Burning Abyss'],
    'tearlaments': ['Tearlaments'],
    'labrynth': ['Labrynth'],
    'swordsoul': ['Swordsoul'],
    'kashtira': ['Kashtira'],
    'dogmatika': ['Dogmatika'],
}


def slugify(a):      # the same slug the page makes (archSlug in src.html)
    return re.sub(r'^-+|-+$', '', re.sub(r'[^a-z0-9]+', '-', a.lower()))


def build(root=ROOT):
    cards = json.load(open(os.path.join(root, 'src/ygo_all.json'), encoding='utf-8'))
    names = {c['name'] for c in cards}
    tokens = {c['name'] for c in cards if c['type'] == 'Token'}
    arch = json.load(open(os.path.join(root, 'src/archetypes.json'), encoding='utf-8'))
    arch.update(MOVE)
    arch = {c: a for c, a in arch.items() if c in names and c not in tokens and a not in DENY}
    count = {}
    for a in arch.values():
        count[a] = count.get(a, 0) + 1
    # two spellings of one archetype ("D.D." and "D/D", "Roid" and "roid") share a URL slug: keep the bigger one and move the cards over
    canon = {}
    for a in sorted(count, key=lambda x: (-count[x], x)):
        canon.setdefault(slugify(a), a)
    arch = {c: canon[slugify(a)] for c, a in arch.items()}
    count = {}
    for a in arch.values():
        count[a] = count.get(a, 0) + 1
    wanted = {a for aa in LORE_ARCH.values() for a in aa}
    keep = sorted((a for a, n in count.items() if n >= 2 or a in wanted), key=lambda s: s.lower())
    idx = {a: i for i, a in enumerate(keep)}
    c = {card: idx[a] for card, a in sorted(arch.items()) if a in idx}
    l, entries = {}, {}
    for f in sorted(os.listdir(os.path.join(root, 'src/lore'))):
        if not f.endswith('.json'):
            continue
        e = json.load(open(os.path.join(root, 'src/lore', f), encoding='utf-8'))
        entries[e['slug']] = e
        for b in e['blocks']:
            for card in b['cards']:
                if e['slug'] not in l.setdefault(card, []):
                    l[card].append(e['slug'])
    la = {s: [idx[a] for a in LORE_ARCH[s] if a in idx] for s in sorted(LORE_ARCH) if s in entries}
    ln = {s: e['name'] for s, e in sorted(entries.items())}
    return {'n': keep, 'c': c, 'l': dict(sorted(l.items())), 'la': la, 'ln': ln}


def main():
    os.chdir(ROOT)
    d = build()
    os.makedirs('data', exist_ok=True)
    open('data/arch.js', 'w', encoding='utf-8').write('__load("arch",' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ');')
    print('data/arch.js: %d arquetipos, %d cartas con arquetipo, %d cartas en el Lore, %d entradas de Lore enlazadas' % (len(d['n']), len(d['c']), len(d['l']), len(d['la'])))


if __name__ == '__main__':
    main()

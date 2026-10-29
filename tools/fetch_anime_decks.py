"""Anime decklists -> src/anime_decks.json.   Run from the project root:  python tools/fetch_anime_decks.py
Source: the character pages "<Name>'s Decks" of the Yu-Gi-Oh! Wiki (yugioh.fandom.com, text under CC BY-SA). Each page lists the Deck a character plays in every arc as a
{{Decklist|<title> |normal monsters= ... |spells= ...}} block under an arc heading, one card per line with its copies ("x2").  Nothing is judged here: the raw lists
are copied as they are (the wiki link of a card ends in "(anime)" when the card shown on screen differs from the printed one).
tools/roulette.py turns them into playable decks; src/roulette/*.json holds the human-reviewed decisions."""
import json, os, re, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'AleistersCodex/1.0'}
OUT = 'src/anime_decks.json'

# (series, character) in the order the roulette lists them.  Wave 1: Duel Monsters, GX, 5D's, ZEXAL.
ROSTER = [
    ('dm', 'Yami Yugi'), ('dm', 'Yugi Muto'), ('dm', 'Joey Wheeler'), ('dm', 'Seto Kaiba'), ('dm', 'Mai Valentine'), ('dm', 'Weevil Underwood'),
    ('dm', 'Rex Raptor'), ('dm', 'Bakura Ryou'), ('dm', 'Yami Bakura'), ('dm', 'Marik Ishtar'), ('dm', 'Ishizu Ishtar'), ('dm', 'Maximillion Pegasus'),
    ('dm', 'Mako Tsunami'), ('dm', 'Espa Roba'), ('dm', 'Duke Devlin'), ('dm', 'Mokuba Kaiba'), ('dm', 'Noah Kaiba'), ('dm', 'Rafael'), ('dm', 'Valon'),
    ('dm', 'Alister'), ('dm', 'Dartz'), ('dm', 'Odion'), ('dm', 'Tristan Taylor'),
    ('gx', 'Jaden Yuki'), ('gx', 'Syrus Truesdale'), ('gx', 'Chazz Princeton'), ('gx', 'Alexis Rhodes'), ('gx', 'Zane Truesdale'), ('gx', 'Bastion Misawa'),
    ('gx', 'Aster Phoenix'), ('gx', 'Jesse Anderson'), ('gx', 'Tyranno Hassleberry'), ('gx', 'Atticus Rhodes'), ('gx', 'Vellian Crowler'), ('gx', 'Sartorius'),
    ('gx', 'Camula'), ('gx', 'Titan'), ('gx', 'Yubel'), ('gx', 'Axel Brodie'), ('gx', 'Adrian Gecko'), ('gx', 'Blair Flannigan'), ('gx', 'Jim Crocodile Cook'),
    ('gx', 'Tania'), ('gx', 'Nightshroud'),
    ('5d', 'Yusei Fudo'), ('5d', 'Jack Atlas'), ('5d', 'Crow Hogan'), ('5d', 'Akiza Izinski'), ('5d', 'Leo'), ('5d', 'Luna'), ('5d', 'Kalin Kessler'),
    ('5d', 'Carly Carmine'), ('5d', 'Bruno'), ('5d', 'Lazar'), ('5d', 'Aporia'), ('5d', 'Sherry LeBlanc'), ('5d', 'Rex Goodwin'),
    ('5d', 'Roman Goodwin'), ('5d', 'Misty Tredwell'), ('5d', 'Devack'), ('5d', 'Tetsu Trudge'), ('5d', 'Ghost'),
    ('zx', 'Yuma Tsukumo'), ('zx', 'Kite Tenjo'), ('zx', 'Reginald Kastle'), ('zx', 'Tori Meadows'), ('zx', 'Rio Kastle'), ('zx', 'Vector'),
    ('zx', 'Quinton'), ('zx', 'Dr. Faker'), ('zx', 'Girag'), ('zx', 'Alito'), ('zx', 'Vetrix'),
    ('zx', 'Bronk Stone'), ('zx', 'Cathy Katherine'), ('zx', 'Mizar'), ('zx', 'Astral'),
]


def api(**kw):
    u = 'https://yugioh.fandom.com/api.php?' + urllib.parse.urlencode({**kw, 'format': 'json'})
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=90))


def page(title):
    try:
        r = api(action='parse', page=title, prop='wikitext', redirects=1)
        return r['parse']['title'], r['parse']['wikitext']['*']
    except Exception:
        return None, None


def clean(name):
    return re.sub(r'\s*\((anime|later anime|manga|card)\)$', '', name.strip())


def parse_decklists(wt):
    """[{'arc': 'Season > Arc', 'title': 'Elemental Hero Deck', 'sections': {'effect monsters': [[name, copies, anime_version?]]}}] in page order."""
    out = []
    heads = [(m.start(), len(m.group(1)), m.group(2).strip()) for m in re.finditer(r'^(=+)\s*(.+?)\s*=+\s*$', wt, re.M)]
    for m in re.finditer(r'\{\{Decklist\s*\|', wt):
        i = m.end()
        depth, j = 2, i
        while j < len(wt) and depth > 0:
            if wt.startswith('{{', j):
                depth += 2
                j += 2
            elif wt.startswith('}}', j):
                depth -= 2
                j += 2
            else:
                j += 1
        body = wt[i:j - 2]
        first = body.split('\n', 1)[0].split('|')[0].strip()
        if re.match(r'^[a-z ]+\s*=\s*$', first):      # no title: the first line is already a section header ("{{Decklist|normal monsters=")
            title, lines = '', ('|' + body).split('\n')
        else:
            title, lines = first, body.split('\n')[1:]
        sections, cur = {}, None
        for line in lines:
            h = re.match(r'^\|\s*([a-z ]+?)\s*=\s*$', line.strip())
            if h:
                cur = h.group(1)
                sections[cur] = []
                continue
            c = re.match(r'^\*\s*\[\[([^\]|]+)(?:\|[^\]]*)?\]\](.*)$', line.strip())
            if c and cur:
                rest = re.sub(r'<ref.*?(/>|</ref>)', '', c.group(2))
                n = re.search(r'x\s*(\d+)', rest)
                sections[cur].append([clean(c.group(1)), int(n.group(1)) if n else 1, bool(re.search(r'\((anime|later anime)\)', c.group(1)))])
        arcs = [h for h in heads if h[0] < m.start()]
        trail = []
        for h in arcs:       # the heading path above the block: a heading closes the deeper ones before it
            trail = [t for t in trail if t[1] < h[1]] + [h]
        out.append({'arc': ' > '.join(t[2] for t in trail), 'title': title, 'sections': sections})
    return out


def main():
    os.chdir(ROOT)
    res, missing = {}, []
    for series, ch in ROSTER:
        got = None
        for t in (ch + "'s Decks", ch + "' Decks", ch + "'s Deck", ch + "' Deck", ch):      # a page that redirects to another character is not this one
            title, wt = page(t)
            if wt and '{{Decklist' in wt and title.lower().startswith(ch.lower()):
                got = (title, wt)
                break
        if not got:
            missing.append(ch)
            continue
        res[ch] = {'series': series, 'page': got[0], 'decks': parse_decklists(got[1])}
        print(ch, '->', got[0], len(res[ch]['decks']), 'decklists')
    json.dump({'source': 'https://yugioh.fandom.com/wiki/', 'characters': res}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('no decklist page for:', missing)


if __name__ == '__main__':
    main()

"""Archetype of every TCG card -> src/archetypes.json {card name: archetype} (YGOPRODeck).   Run from the project root:  python tools/fetch_archetypes.py
tools/engines.py uses it to keep, in an engine's package, only the cards of the engine's own archetype (Bystial, Horus, Sky Striker...)."""
import json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if __name__ == '__main__':
    os.chdir(ROOT)
    d = json.load(urllib.request.urlopen(urllib.request.Request('https://db.ygoprodeck.com/api/v7/cardinfo.php', headers={'User-Agent': 'Mozilla/5.0'}), timeout=300))['data']
    out = {c['name']: c['archetype'] for c in d if c.get('archetype')}
    json.dump(out, open('src/archetypes.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('cards with an archetype', len(out), 'archetypes', len(set(out.values())))

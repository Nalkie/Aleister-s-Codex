"""patch 77 (2026-11-03): the Duel Links tiers are calculated by this page from the power ranking of Duel Links Meta; they are not the editorial tiers of the site (Centur-Ion is
tier 1 there and tier 3 here, Horus and Snake-Eye the other way round).  The text says so, in src.html and in the English dictionaries.
Run once from the project root:  python tools/patch_src77.py   (backup: src.before_patch77.html)"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAIRS_ES = [
    ('<p>El tier sale del ranking de poder de Duel Links Meta: cada tipo', '<p>El tier lo calcula esta página con el ranking de poder de Duel Links Meta (no es el tier editorial que publica el sitio): cada tipo'),
    ('agrupados por tier según el ranking de poder de Duel Links Meta.', 'agrupados en tiers calculados con el ranking de poder de Duel Links Meta (no son los tiers editoriales del sitio).'),
]
PAIRS_EN = [
    ('<p>The tier comes from the Duel Links Meta power ranking: each deck type', '<p>The tier is calculated by this page from the Duel Links Meta power ranking (not the editorial tier the site publishes): each deck type'),
    ('decks grouped by tier according to the Duel Links Meta power ranking.', 'decks grouped into tiers calculated from the Duel Links Meta power ranking (not the editorial tiers of the site).'),
]


def swap(path, es_pairs, en_pairs, backup=None):
    p = os.path.join(ROOT, path)
    t = open(p, encoding='utf-8').read()
    if backup and not os.path.exists(os.path.join(ROOT, backup)):
        shutil.copy2(p, os.path.join(ROOT, backup))
    n = 0
    for a, b in es_pairs + en_pairs:
        n += t.count(a)
        t = t.replace(a, b)
    open(p, 'w', encoding='utf-8').write(t)
    return n


# src.html and the dictionaries hold the Spanish text as a key and the English as a value: the raw replacement is valid JSON too (no quotes or escapes in the snippets)
print('src.html', swap('src.html', PAIRS_ES, [], 'src.before_patch77.html'))
for f in ('tools/i18n_en.json', 'tools/i18n_parts/out_104.json'):
    print(f, swap(f, PAIRS_ES, PAIRS_EN))
for f in ('tools/i18n_en.json', 'tools/i18n_parts/out_104.json'):
    json.load(open(os.path.join(ROOT, f), encoding='utf-8'))

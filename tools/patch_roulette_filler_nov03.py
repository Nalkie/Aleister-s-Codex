"""2026-11-03, roulette audit: the replacements and filler that are modern generic staples (Ash Blossom, Impermanence, Called by the Grave...) in a deck of an older period are
swapped for printed staples of that period (same kind, same copies).  Run once from the project root:  python tools/patch_roulette_filler_nov03.py"""
import json, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roulette as R

R.os.chdir(R.ROOT)
NOTE = 'era:printed staple of the period of the series (2002-2011 sets) instead of a modern generic card'
n_rows = 0
for series in R.SERIES:
    for name in (series + '.json', series + '_thematic.json'):
        p = os.path.join(R.ROOT, 'src/roulette', name)
        if not os.path.exists(p):
            continue
        data = json.load(open(p, encoding='utf-8'))
        changed = 0
        for key, sh in data.items():
            main, extra, _ = R.assemble(sh)
            used = {n for n, _, _ in main + extra}
            for row in sh.get('add', []):
                if not R.anachronistic(row[0], series):
                    continue
                new = R.era_staple(series, R.card_group(row[0]), used)
                if not new:
                    print('NO STAND-IN', key, row[0])
                    continue
                print('%-42s %-30s -> %s' % (key, row[0], new))
                used.add(new)
                row[0], row[4] = new, NOTE
                changed += 1
        if changed:
            n_rows += changed
            json.dump(data, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(n_rows, 'rows')

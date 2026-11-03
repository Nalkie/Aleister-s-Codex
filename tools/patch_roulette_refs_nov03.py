"""2026-11-03: repoints the `add` refs whose dated list ("md:Volcanic · 2026-09-20") rotated out of src/md.json / src/ygm_topdecks.json, or never had the card, to the live list
that plays the card and shares the most cards with the sheet; a card no recent list plays gets an era note instead of a dead link.  Run from the project root."""
import json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roulette as R

R.os.chdir(R.ROOT)
NOTE = 'era:printed card of the same archetype; no recent list plays it'
LD = R.real_decklists()
LIVE = dict(LD)
for series in R.SERIES:
    for name in (series + '.json', series + '_thematic.json'):
        p = os.path.join(R.ROOT, 'src/roulette', name)
        if not os.path.exists(p):
            continue
        data = json.load(open(p, encoding='utf-8'))
        changed = 0
        for key, sh in data.items():
            main, extra, _ = R.assemble(sh)
            mine = {n for n, _, _ in main + extra}
            for row in sh.get('add', []):
                bad = False
                for m in re.finditer(r'(md|tcg):([^/;]*?)\(?(\d{4}-\d{2}-\d{2})', row[4]):
                    lab = '%s:%s · %s' % (m.group(1), m.group(2).replace('·', '').strip(), m.group(3))
                    if lab not in LIVE or row[0] not in LIVE[lab]:
                        bad = True
                if not bad:
                    continue
                cands = [(len(mine & set(d)), l) for l, d in LD if row[0] in d]
                row[4] = max(cands)[1] if cands else NOTE
                changed += 1
                print('%-42s %-34s -> %s' % (key, row[0], row[4]))
        if changed:
            shutil.copy2(p, p + '.before_refs_nov03')
            open(p, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1))

"""Gate test of the self-hosted pictures (python tools/build_db.py --selfhost).  Sin red.  Run from the project root:
  python tests/check_selfhost.py              only checks the page is consistent (a normal build hot-links, FC is empty and nothing is required)
  python tests/check_selfhost.py --selfhost   full-card sprites (cards/f*.jpg) and TCG box art (box/b*.jpg) exist and the page points at them
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SELF = '--selfhost' in sys.argv
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


page = open('index.html', encoding='utf-8').read()
m = re.search(r'const FC = (\{.*?\});', page)
check(bool(m), 'the page declares the full-card sprite map (const FC)')
fc = json.loads(m.group(1)) if m else {}
src = open('src.html', encoding='utf-8').read()
check('function fcSprite' in src and 'function boxSprite' in src and '.fcs{' in src, 'src.html has the sprite helpers and CSS')
sets_tcg = open('data/sets-tcg.js', encoding='utf-8').read()
bs = [int(x) for x in re.findall(r'"b":(-?\d+)', sets_tcg)]
if SELF:
    check(len(fc) > 1500, 'full-card sprite map covers more than 1500 cards (%d)' % len(fc))
    check(all(os.path.exists('cards/f%d.jpg' % s) for s in {k // 144 for k in fc.values()}), 'every full-card sprite sheet exists on disk')
    check(os.path.exists('cards/f0.jpg') and os.path.getsize('cards/f0.jpg') > 100000, 'full-card sheet f0.jpg is not empty')
    check(len(bs) > 500 and sum(1 for b in bs if b >= 0) / len(bs) > 0.85, 'most TCG sets have box art (%d of %d)' % (sum(1 for b in bs if b >= 0), len(bs)))
    check(all(os.path.exists('box/b%d.jpg' % (b // 64)) for b in bs if b >= 0), 'every box sprite sheet exists')
    refresh = open('tools/refresh.py', encoding='utf-8').read()      # files.json is written after the gate: check the wiring instead
    check("'--selfhost'" in refresh and "('cards', 'box') if selfhost" in refresh and "['cards', 'box'] if selfhost" in refresh, 'refresh.py --selfhost passes the flag on and lists cards/ and box/ in files.json and in the backup')
else:
    check(not fc, 'a normal build leaves the sprite map empty (images are hot-linked)')
print('failed:', len(fails))
sys.exit(1 if fails else 0)

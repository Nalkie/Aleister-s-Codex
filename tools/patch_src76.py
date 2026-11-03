"""patch 76 (2026-11-03): Speed Duel and Rush Duel share card names with other rarity and boxes, so the page reads the Rush card (DLD.rcards) when the format is Rush.
Run once from the project root:  python tools/patch_src76.py   (backup: src.before_patch76.html)"""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'src.html')
t = open(P, encoding='utf-8').read()
if not os.path.exists(os.path.join(ROOT, 'src.before_patch76.html')):
    shutil.copy2(P, os.path.join(ROOT, 'src.before_patch76.html'))
PAIRS = [
    ("function dlBadge(n){\n  const i=DLD.cards[n]; if(!i) return '';",
     "function dlc(n,rush){   // the Duel Links card of the format: Speed Duel and Rush Duel share names with another rarity and boxes\n  return (rush===undefined?dlFormat==='rush':rush) ? DLD.rcards[n] : DLD.cards[n];\n}\nfunction dlBadge(n,rush){\n  const i=dlc(n,rush); if(!i) return '';"),
    ("function dlBadgeTitle(n){\n  const i=DLD.cards[n]; if(!i) return '';", "function dlBadgeTitle(n,rush){\n  const i=dlc(n,rush); if(!i) return '';"),
    ("function dlHow(n){   // cómo conseguir una carta, en una línea\n  const i=DLD.cards[n]; if(!i) return '';\n  const b=dlBadge(n);",
     "function dlHow(n,rush){   // cómo conseguir una carta, en una línea\n  const i=dlc(n,rush); if(!i) return '';\n  const b=dlBadge(n,rush);"),
    ("if(kind==='dl'){ const i=DLD.cards[n]; return `<span class=\"ex\">", "if(kind==='dl'){ const i=dlc(n); return `<span class=\"ex\">"),
    ("const i=kind==='dl'?DLD.cards[n]:null;", "const i=kind==='dl'?dlc(n):null;"),
    ("filter(e=>DLD.cards[e.n]).map(e=>", "filter(e=>dlc(e.n)).map(e=>"),
    ("${esc(DLD.cards[n]?dlBadge(n):'')}", "${esc(dlc(n,!!dl.rush)?dlBadge(n,!!dl.rush):'')}"),
]
for old, new in PAIRS:
    assert t.count(old) == 1, old[:60]
    t = t.replace(old, new)
open(P, 'w', encoding='utf-8').write(t)
print('ok', len(PAIRS), 'edits')

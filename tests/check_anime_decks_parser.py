"""Gate test of tools/fetch_anime_decks.parse_decklists (no network).  python tests/check_anime_decks_parser.py
Regression: a Decklist without a title ("{{Decklist|normal monsters=") lost its first card section."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'tools')
import fetch_anime_decks as f

titled = "== Arc ==\n{{Decklist|Blue Deck\n|normal monsters=\n*[[Alpha]] x2\n|spells=\n*[[Beta]]\n}}"
untitled = "== Arc ==\n{{Decklist|normal monsters=\n*[[Alpha]] x3\n*[[Gamma (anime)]]\n|spells=\n*[[Beta]]\n}}"
a, b = f.parse_decklists(titled)[0], f.parse_decklists(untitled)[0]
bad = []
if not (a['title'] == 'Blue Deck' and a['sections'] == {'normal monsters': [['Alpha', 2, False]], 'spells': [['Beta', 1, False]]}):
    bad.append('titled list changed: %r' % a)
if not (b['title'] == '' and b['sections'].get('normal monsters') == [['Alpha', 3, False], ['Gamma', 1, True]] and b['sections'].get('spells') == [['Beta', 1, False]]):
    bad.append('untitled list lost its first section: %r' % b)
print('\n'.join('FAIL ' + m for m in bad) or 'ok   titled and untitled Decklists keep every section')
sys.exit(1 if bad else 0)

"""One command to bring the whole page up to date.

  python tools/refresh.py             download everything again, rebuild, test, and print what is new
  python tools/refresh.py --offline   rebuild from the sources already on disk (no downloads)
  python tools/refresh.py --quick     like the full run but without the TCGplayer picture lists (the slowest download)
  python tools/refresh.py --unattended  (or an empty file named .unattended) for the scheduled daily run: a tactical sheet that no longer matches today's lists is
                                      left out and named in the log instead of stopping the whole refresh. Without it the refresh is strict, to find the sheets to fix by hand.
  python tools/refresh.py --selfhost  (or an empty file named .selfhost in this folder) also host the card and box pictures inside the page (cards/, box/): for a page published where hot-linked images do not load
                                      (the claude.ai artifact). Combine with the other flags. files.json then lists cards/ and box/ too.

What it refreshes (all from public sources, no model involved):
  * cards, TCG sets, rarities and prices (YGOPRODeck), the official TCG banlist (Konami), Genesys points (YuGiOh Meta)
  * Spanish names and alternate artworks (YGOResources, YGOPRODeck)
  * TCGplayer picture of every printing: recent and upcoming sets are downloaded again, so cards of boxes that were not printed yet appear
    as soon as TCGplayer lists them
  * Duel Links: cards, boxes, characters (portraits, skills, rewards), in-game events, top decks, tiers (Duel Links Meta)
  * TCG and Genesys: tournament events with results, top decks, tiers, recipes (YuGiOh Meta)
If a download fails halfway, the previous files are restored and the page is left as it was.

After it finishes, publish index.html together with the files listed in files.json (art/, sheets/, data/).
Hand-written parts are NOT refreshed: the Guía texts (tools/guide_extra.js, src.html), the engines tables and the ticket icons.
Run from build/.
"""
import datetime, json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refreshlib

PY = sys.executable
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
DOWNLOADED = ['src/ygo_all.json', 'src/cardsets.json', 'src/dl_cards.json', 'src/dl_sets.json', 'src/dl_bans.json', 'src/ygm_topdecks.json',
              'dl/topdecks.json', 'dl/power.json', 'src/konami_current.json', 'src/ygm_genesys.json', 'src/extra.json', 'src/dl_extra.json', 'src/ygm_events.json', 'src/tcgplayer.json', 'src/prices.json', 'src/fx_ars.json', 'src/tcgprices.json', 'src/formats.json', 'src/dl_text.json', 'src/fandom_anniversary.json', 'src/yuyutei_rush.json', 'src/rush_names.json', 'src/fx.json', 'src/engines_ygm.json', 'src/archetypes.json', 'src/engines_dlm.json', 'src/formats_meta.json', 'src/ygm_ocg.json', 'src/md.json']
BAK = 'src/.refresh_bak'
unattended = '--unattended' in sys.argv or os.path.exists('.unattended')      # the scheduled daily run: stale tactical sheets are skipped, not fatal
offline, quick, selfhost = '--offline' in sys.argv, '--quick' in sys.argv, '--selfhost' in sys.argv or os.path.exists('.selfhost')      # a file named .selfhost in the project folder turns it on for every run (the scheduled task that publishes the artifact)


def run(*args):
    print('>>', ' '.join(args), flush=True)
    return subprocess.run([PY, *args], env=ENV).returncode == 0


def backup():
    os.makedirs(BAK, exist_ok=True)
    for f in DOWNLOADED:
        if os.path.exists(f):
            os.makedirs(os.path.join(BAK, os.path.dirname(f)), exist_ok=True)
            shutil.copy2(f, os.path.join(BAK, f))


BUILT = ['data', 'sheets', 'art', *(['cards', 'box'] if selfhost else [])]          # build_db.py wipes these first: keep a copy until the new build passes its test


def backup_built():
    for d in BUILT:
        if os.path.exists(d):
            shutil.copytree(d, os.path.join(BAK, 'built', d), dirs_exist_ok=True)
    shutil.copy2('index.html', os.path.join(BAK, 'built', 'index.html'))


def restore_built():
    for d in BUILT:
        b = os.path.join(BAK, 'built', d)
        if os.path.exists(b):
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(b, d)
    shutil.copy2(os.path.join(BAK, 'built', 'index.html'), 'index.html')


def restore():
    for f in DOWNLOADED:
        b = os.path.join(BAK, f)
        if os.path.exists(b):
            shutil.copy2(b, f)
    print('the previous sources were restored; the page was not changed', flush=True)


before = refreshlib.snapshot()
if not offline:
    backup()
    steps = [('tools/fetch_sources.py', '--refresh'), ('tools/extra.py', '--refresh'), ('tools/dlx.py', '--refresh'), ('tools/fetch_prices.py',), ('tools/ygm_events.py',), ('tools/fetch_formats.py',), ('tools/fetch_formats_meta.py',), ('tools/fetch_md.py',), ('tools/fetch_dltext.py',), ('tools/fetch_rush_prices.py',), ('tools/fetch_engines.py',), ('tools/fetch_archetypes.py',), ('tools/fandom_anniv.py', '--fetch')]
    if not quick:
        steps.append(('tools/tcgp.py', '--refresh'))
        steps.append(('tools/fetch_tcg_prices.py',))      # unos 70 minutos: un pedido por página de cada expansión
    for st in steps:
        if not run(*st):
            restore()
            sys.exit(f'step failed: {" ".join(st)}')
os.makedirs(BAK, exist_ok=True)
backup_built()
for st in (('tools/dl.py',), ('tools/ygm.py'), ('tools/build_db.py', *(('--selfhost',) if selfhost else ())), ('tools/dltext.py',), ('tools/tickets.py',), ('tools/fandom_anniv.py',), ('tools/prices.py',), ('tools/rushprice.py',), ('tools/formats.py',), ('tools/formats_meta.py',), ('tools/engines.py',), ('tools/playcards.py', *(('--lenient',) if unattended else ()))):
    st = (st,) if isinstance(st, str) else st
    if not run(*st):
        if not offline:
            restore()
        restore_built()
        sys.exit(f'step failed: {" ".join(st)}')
if not (run('tests/check_build.py') and run('tests/check_tickets.py') and run('tests/check_formats.py') and run('tests/check_dltext.py') and run('tests/check_anniversary.py') and run('tests/check_rushprice.py') and run('tests/check_engines.py') and run('tests/check_prices.py') and run('tests/check_i18n.py') and run('tests/check_routes.py') and run('tests/check_hand.py') and run('tests/check_dl_legal.py') and run('tests/check_playcards.py', *(('--lenient',) if unattended else ())) and run('tests/check_md.py') and run('tests/check_selfhost.py', *(('--selfhost',) if selfhost else ()))):
    restore_built()
    sys.exit('the gate test failed: the previous page was restored, nothing to publish')

files = [{'path': f'{d}/{f}'} for d in ('art', 'sheets', 'data', *(('cards', 'box') if selfhost else ())) for f in sorted(os.listdir(d))]
json.dump(files, open('files.json', 'w'), separators=(',', ':'))
shutil.rmtree(BAK, ignore_errors=True)

new = refreshlib.diff(before, refreshlib.snapshot())
print(f'\n=== what is new ({datetime.date.today()}) ===')
for k in ('cards', 'tcg sets', 'duel links boxes', 'duel links characters', 'duel links events', 'tcg/genesys events'):
    items = new.get(k, [])
    print(f'{k}: {len(items)}' + (' · ' + ', '.join(items[:8]) + (' …' if len(items) > 8 else '') if items else ''))
print(f'\nok: {len(files)} files listed in files.json; publish index.html with them.')

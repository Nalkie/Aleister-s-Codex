"""2026-11-03, roulette audit: Shark decks get printed cards of their own era instead of 2022-2026 Master Duel cards (and the dead Seventh Tachyon goes);
Celina / Shay get the signature card the wiki names; the refs of the Master Duel / tournament lists that rotated out are repointed to a live list or to an era note.
Run once from the project root:  python tools/patch_roulette_nov03.py"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ERA = 'era:ZEXAL-era printed card (TCG 2012-2014 sets, Xyz decks of the period)'


def load(name):
    return json.load(open(os.path.join(ROOT, 'src/roulette', name), encoding='utf-8'))


def save(name, data):
    p = os.path.join(ROOT, 'src/roulette', name)
    if not os.path.exists(p + '.before_nov03'):
        shutil.copy2(p, p + '.before_nov03')
    open(p, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')


zx = load('zx.json')
barian = zx['shark-barian-invasion-shark-fortress']
SWAP_BARIAN = {'Seventh Ascension': 'Xyz Reflect', 'Seventh Tachyon': 'Xyz Encore', 'Aqua Jet Surface': 'Fish Depth Charge', 'Triple Tactics Talent': 'Xyz Gift',
               'Reincarnation Unveiling Mail': 'Rank-Up-Magic Numeron Force', 'Unbreakable Xyz Barrier': 'Xyz Block', 'Forbidden Crown': "Rank-Up-Magic Barian's Force",
               'Infinite Impermanence': 'Solemn Warning', 'Dominus Impulse': 'Dimensional Prison', 'Dominus Spiral': 'Xyz Reborn'}
SWAP_PRE = {'Aqua Jet Surface': 'Fish Depth Charge', 'Infinite Impermanence': 'Solemn Warning', 'Dominus Impulse': 'Bottomless Trap Hole', 'Triple Tactics Talent': 'Xyz Reflect',
            'Unbreakable Xyz Barrier': 'Dimensional Prison'}
for sheet, swap in ((barian, SWAP_BARIAN), (zx['shark-pre-wdc-aero-shark'], SWAP_PRE)):
    for row in sheet['add']:
        if row[0] in swap:
            row[0], row[4] = swap[row[0]], ERA
    sheet['blurb'] = sheet['blurb'].replace('apoyo que juegan listas Shark reales', 'apoyo Xyz y trampas impresos de la misma época')
save('zx.json', zx)

av = load('av.json')
for k, sig in (('celina-fusion-dimension-lunalight', 'Lunalight Cat Dancer'), ('shay-xyz-dimension-raidraptor', 'Raidraptor - Rise Falcon')):
    print(k, '|', av[k]['sig'], '->', sig, '|', av[k]['blurb'])
    av[k]['sig'] = sig
save('av.json', av)
print('ok')

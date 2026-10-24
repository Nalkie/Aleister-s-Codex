"""Helpers of tools/refresh.py (pure functions, covered by tests/check_refresh.py)."""
import json, os


def load_data(name, root='data'):
    txt = open(f'{root}/{name}.js', encoding='utf-8').read()
    return json.loads(txt[txt.index(',') + 1:-2])


def snapshot(root='data'):
    """What the page shows right now, as sets of names, so two snapshots can be diffed."""
    out = {k: set() for k in ('cards', 'tcg sets', 'duel links boxes', 'duel links characters', 'duel links events', 'tcg/genesys events')}
    if not os.path.exists(f'{root}/index.js'):
        return out
    out['cards'] = {r[0] for r in load_data('index', root)['cards']}
    out['tcg sets'] = {s['n'] for s in load_data('sets-tcg', root)}
    out['duel links boxes'] = {s['n'] for s in load_data('sets-dl', root) if s['kind'] == 'set'}
    if os.path.exists(f'{root}/dlinfo.js'):
        info = load_data('dlinfo', root)
        out['duel links characters'] = set(info['chars'])
        out['duel links events'] = {e['t'] for e in info['events']}
    if os.path.exists(f'{root}/events.js'):
        out['tcg/genesys events'] = {f"{e['n']} ({e['d']})" for e in load_data('events', root)}
    return out


def diff(before, after):
    return {k: sorted(after[k] - before.get(k, set())) for k in after if after[k] - before.get(k, set())}


def stale_sets(done, dates, cutoff):
    """Sets whose TCGplayer product list must be downloaded again: recent or upcoming sets (cards get listed over time)
    and any set that came back empty while it is still recent. Old sets never change."""
    return [name for name in done if dates.get(name, '9999') >= cutoff]

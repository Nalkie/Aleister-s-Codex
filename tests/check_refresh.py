"""Gate test for tools/refreshlib.py (no network).  Run from build/:  python tests/check_refresh.py"""
import json, os, sys, tempfile
sys.path.insert(0, 'tools')
import refreshlib

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


def dump(root, name, obj):
    open(f'{root}/{name}.js', 'w', encoding='utf-8').write('__load(' + json.dumps(name) + ',' + json.dumps(obj) + ');')


def fixture(cards, sets, chars, events):
    root = tempfile.mkdtemp()
    dump(root, 'index', {'cards': [[c] for c in cards]})
    dump(root, 'sets-tcg', [{'n': s} for s in sets])
    dump(root, 'sets-dl', [{'n': 'Box A', 'kind': 'set'}, {'n': 'Gate', 'kind': 'other'}])
    dump(root, 'dlinfo', {'chars': {c: {} for c in chars}, 'events': [{'t': e} for e in events]})
    dump(root, 'events', [{'n': 'YCS X', 'd': '2026-10-18'}])
    return root


a = refreshlib.snapshot(fixture(['A', 'B'], ['S1'], ['Yugi'], ['Ev1']))
b = refreshlib.snapshot(fixture(['A', 'B', 'C'], ['S1', 'S2'], ['Yugi', 'Zane'], ['Ev1', 'Ev2']))
d = refreshlib.diff(a, b)
check(d == {'cards': ['C'], 'tcg sets': ['S2'], 'duel links characters': ['Zane'], 'duel links events': ['Ev2']}, f'diff lists only what is new: {d}')
check(refreshlib.diff(a, a) == {}, 'no changes -> empty diff')
check(refreshlib.snapshot(tempfile.mkdtemp())['cards'] == set(), 'snapshot of an empty folder does not fail')
done = {'Old': [1], 'Recent': [1], 'Upcoming': [], 'Unknown': [1]}
dates = {'Old': '2020-01-01', 'Recent': '2026-09-01', 'Upcoming': '2026-11-12'}
check(sorted(refreshlib.stale_sets(done, dates, '2026-05-01')) == ['Recent', 'Unknown', 'Upcoming'], 'recent, upcoming and undated sets are downloaded again; old sets are kept')
print('failed:', len(fails))
sys.exit(1 if fails else 0)

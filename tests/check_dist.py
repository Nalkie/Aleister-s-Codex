"""Gate test: dist/ is index.html plus exactly the files in files.json, byte for byte, and index.html only references published files.
Run from the project root after tools/dist.py:  python tests/check_dist.py   (deterministic, no network)"""
import filecmp, json, os, re, sys

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


files = [f['path'] for f in json.load(open('files.json', encoding='utf-8'))]
have = sorted(os.path.relpath(os.path.join(r, f), 'dist').replace(os.sep, '/') for r, _, fs in os.walk('dist') for f in fs)
check(have == sorted(files + ['index.html']), f'dist/ holds index.html + the {len(files)} files of files.json and nothing else')
check(all(filecmp.cmp(p, os.path.join('dist', p), shallow=False) for p in files + ['index.html']), 'every dist/ file is identical to its source (index.html is current)')
page = open('dist/index.html', encoding='utf-8').read()
refs = set(re.findall(r'''["'`(]((?:sheets|data)/[A-Za-z0-9_.-]+\.(?:jpg|js))''', page))
check(all(os.path.isfile('dist/' + r) for r in refs if '${' not in r), f'{len(refs)} sheets/data paths named in index.html exist in dist/')
print('failed:', len(fails))
sys.exit(1 if fails else 0)

"""Build dist/ for publishing: index.html plus exactly the files listed in files.json (art/, sheets/, data/), nothing else.
Run from the project root after tools/refresh.py:  python tools/dist.py
Then:  npx wrangler pages deploy dist --project-name aleisters-codex
Fails (and leaves the old dist/ untouched) if a listed file is missing."""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
files = [f['path'] for f in json.load(open('files.json', encoding='utf-8'))]
missing = [p for p in ['index.html'] + files if not os.path.isfile(p)]
if missing:
    sys.exit(f'{len(missing)} files listed but missing, dist/ not touched: {missing[:5]}')
tmp = 'dist.tmp'
shutil.rmtree(tmp, ignore_errors=True)
for p in ['index.html'] + files:
    os.makedirs(os.path.dirname(os.path.join(tmp, p)) or tmp, exist_ok=True)
    shutil.copy2(p, os.path.join(tmp, p))
shutil.rmtree('dist', ignore_errors=True)
os.rename(tmp, 'dist')
print(f'dist/: index.html + {len(files)} files, {sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk("dist") for f in fs) / 1e6:.1f} MB')

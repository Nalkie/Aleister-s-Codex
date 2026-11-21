"""Gate: los scripts de la página (src.html y la index.html generada) no tienen errores de sintaxis ni declaraciones repetidas.  python tests/check_syntax.py

Nació de un error real: dos `const glPend` en el mismo script dejaban la página en blanco y ningún otro gate lo notó (leen texto, no ejecutan JS)."""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []
node = shutil.which('node')


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


if not node:
    print('skip node no está instalado; no se pudo revisar la sintaxis')
    sys.exit(0)
for name in ('src.html', 'index.html'):
    html = open(name, encoding='utf-8').read()
    scripts = re.findall(r'<script(?![^>]*\bsrc=)(?![^>]*type="(?:application/ld\+json|text/template)")[^>]*>(.*?)</script>', html, re.S)
    ok(len(scripts) >= 1, '%s: %d scripts en línea' % (name, len(scripts)))
    for i, js in enumerate(scripts):
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(js)
        p = subprocess.run([node, '--check', f.name], capture_output=True, text=True, encoding='utf-8', errors='replace')
        os.unlink(f.name)
        ok(p.returncode == 0, '%s script %d: sintaxis válida%s' % (name, i + 1, '' if p.returncode == 0 else ' · ' + (p.stderr.strip().splitlines() or ['?'])[-1][:160]))
print('\nfailed: %d' % len(fails))
sys.exit(1 if fails else 0)

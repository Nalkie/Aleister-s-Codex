"""Gate test de tools/pr.py (sin red): un origin falso (repositorio bare en una carpeta temporal), un clon y una carpeta de trabajo de juguete.  Desde la raíz:  python tests/check_pr.py"""
import os, subprocess, sys, tempfile
sys.path.insert(0, 'tools')
import pr

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


def sh(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, encoding='utf-8', check=True).stdout


def put(root, rel, text='x'):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(text)


tmp = tempfile.mkdtemp()
origin, clone, work = (os.path.join(tmp, n) for n in ('origin.git', 'clone', 'work'))
sh('git', 'init', '-q', '--bare', '-b', 'main', origin)
sh('git', 'clone', '-q', origin, clone)
for k, v in (('user.name', 't'), ('user.email', 't@t')):
    sh('git', 'config', k, v, cwd=clone)
put(clone, 'src/a.txt', 'viejo')
put(clone, 'src/gone.txt', 'sobra')
put(clone, 'dist/index.html', 'v1')
put(clone, 'index.html', 'v1')
sh('git', 'add', '-A', cwd=clone)
sh('git', 'commit', '-q', '-m', 'base', cwd=clone)
sh('git', 'push', '-q', '-u', 'origin', 'HEAD:main', cwd=clone)
sh('git', 'branch', '-M', 'main', cwd=clone)

# la carpeta de trabajo: un cambio, un archivo nuevo, uno borrado y basura que no debe subir
put(work, 'src/a.txt', 'nuevo')
put(work, 'src/b.txt', 'b')
put(work, 'src/__pycache__/m.pyc', 'junk')
put(work, 'src/.refresh_bak/old.json', 'junk')
put(work, 'src/before_patch9.html', 'junk')
put(work, 'tools/run.log', 'junk')
put(work, 'dist/index.html', 'v2')
put(work, 'index.html', 'v2')
put(work, 'raw/huge.bin', 'no va')

check(pr.skip('src/__pycache__/m.pyc') and pr.skip('src/.refresh_bak/x.json') and pr.skip('tools/a.log') and pr.skip('x/before_patch3.html') and not pr.skip('src/a.txt'), 'skip(): cachés, respaldos del refresco, registros y respaldos de parche quedan fuera')
check(pr.clone_path('/nada', {'AC_PR_CLONE': 'Z:/c'}) == 'Z:/c' and pr.clone_path('/nada', {}) == pr.DEFAULT_CLONE, 'el clon sale de AC_PR_CLONE o del valor por defecto')

# gh falso: sin sesión -> solo el enlace
class R:
    def __init__(s, rc=0, out='', err=''):
        s.returncode, s.stdout, s.stderr = rc, out, err


calls = []


def runner_nologin(cmd, **kw):
    calls.append(cmd)
    return R(1, '', 'not logged in')


code, text = pr.open_pr('2026-11-02', '2026-11-02', ['SKIPPED 1 stale sheets (a/b)'], src=work, clone=clone, gh='gh', runner=runner_nologin)
check(code == 0 and 'compare/main...auto%2Fpublish-2026-11-02' in text, 'sin sesión de gh sube la rama y da el enlace para abrir el PR: ' + text[:120])
check(not any('create' in c for c in calls), 'sin sesión no intenta crear el PR')
check('auto/publish-2026-11-02' in sh('git', 'branch', '-r', cwd=origin.replace('origin.git', 'clone')) and sh('git', 'rev-parse', '--abbrev-ref', 'HEAD', cwd=clone).strip() == 'main', 'la rama quedó en origin y el clon volvió a main')
files = sh('git', 'ls-tree', '-r', '--name-only', 'origin/auto/publish-2026-11-02', cwd=clone).split()
check(sorted(files) == ['dist/index.html', 'index.html', 'src/a.txt', 'src/b.txt'], 'la rama trae lo nuevo y cambiado, borra lo que ya no está y deja afuera la basura: %s' % files)
check(sh('git', 'show', 'origin/auto/publish-2026-11-02:src/a.txt', cwd=clone) == 'nuevo', 'el contenido es el de la carpeta de trabajo')
check(sh('git', 'rev-parse', 'origin/main', cwd=clone).strip() == sh('git', 'rev-parse', 'main', cwd=clone).strip(), 'main no se tocó')

# con sesión: crea el PR con título y cuerpo
calls.clear()


def runner_ok(cmd, **kw):
    calls.append(cmd)
    if cmd[1:3] == ['auth', 'status']:
        return R(0)
    if cmd[1:3] == ['pr', 'list']:
        return R(0, '')
    return R(0, 'https://github.com/x/y/pull/99\n')


put(work, 'src/c.txt', 'c')
code, text = pr.open_pr('2026-11-03', '2026-11-03', [], src=work, clone=clone, gh='gh', runner=runner_ok)
create = [c for c in calls if c[1:3] == ['pr', 'create']]
check(code == 0 and text.endswith('/pull/99') and len(create) == 1, 'con sesión crea el PR y devuelve su dirección')
check('--base' in create[0] and create[0][create[0].index('--base') + 1] == 'main' and create[0][create[0].index('--head') + 1] == 'auto/publish-2026-11-03' and 'Publicación 2026-11-03' in create[0], 'PR contra main desde la rama del día y con el título del día')
check('Generated with [Claude Code]' in create[0][create[0].index('--body') + 1], 'el cuerpo del PR lleva la marca de generación')

# mismo día otra vez: la rama se actualiza y no se abre un segundo PR
calls.clear()


def runner_exists(cmd, **kw):
    calls.append(cmd)
    if cmd[1:3] == ['pr', 'list']:
        return R(0, 'https://github.com/x/y/pull/99\n')
    return R(0)


put(work, 'src/d.txt', 'd')
code, text = pr.open_pr('2026-11-03', '2026-11-03', [], src=work, clone=clone, gh='gh', runner=runner_exists)
check(code == 0 and 'ya existe' in text and not any(c[1:3] == ['pr', 'create'] for c in calls), 'una segunda publicación del día actualiza la rama y no abre otro PR')

# nada nuevo
same = os.path.join(tmp, 'same')
import shutil
shutil.copytree(clone, same, ignore=shutil.ignore_patterns('.git'))
code, text = pr.open_pr('2026-11-04', '2026-11-04', [], src=same, clone=clone, gh='gh', runner=runner_exists)
check(code == 0 and 'nada nuevo' in text and 'auto/publish-2026-11-04' not in sh('git', 'branch', '-r', cwd=clone), 'si la carpeta de trabajo ya es igual a origin/main no se sube ni se abre nada')

# clon sucio: se niega
put(clone, 'src/sucio.txt', 'sin guardar')
code, text = pr.open_pr('2026-11-05', '2026-11-05', [], src=work, clone=clone, gh='gh', runner=runner_ok)
check(code == 1 and 'sin guardar' in text, 'un clon con cambios sin guardar se rechaza sin tocarlo')
os.remove(os.path.join(clone, 'src/sucio.txt'))
# no es un clon
code, text = pr.open_pr('2026-11-05', '2026-11-05', [], src=work, clone=os.path.join(tmp, 'nada'), gh='gh', runner=runner_ok)
check(code == 1 and 'no es un clon' in text, 'una ruta que no es un clon de git se rechaza')

print('failed:', len(fails))
sys.exit(1 if fails else 0)

"""Abre un pull request con lo que se acaba de publicar (lo usa `python tools/publish.py --pr`).

La carpeta de trabajo no es un repositorio git: el repositorio (Nalkie/Aleister-s-Codex) vive en un clon aparte.  Este módulo copia ahí lo que el repositorio guarda (dist/, las fuentes, los datos
y las herramientas), crea la rama auto/publish-AAAA-MM-DD desde origin/main, hace commit, la sube y abre el PR con `gh`.  Nunca toca main y nunca fusiona: una persona revisa y fusiona.

Clon: la variable AC_PR_CLONE, o el archivo .pr_clone (una línea con la ruta) en la raíz del proyecto, o F:/pepo/aleisters-pr/repo.
Sin `gh` instalado o sin sesión (`gh auth login`) igual sube la rama e imprime el enlace para abrir el PR con un clic.
Salida de open_pr: (0, texto) hecho · (1, texto) falló un paso, el texto dice cuál (la publicación ya estaba hecha)."""
import filecmp, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CLONE = 'F:/pepo/aleisters-pr/repo'
REPO = 'Nalkie/Aleister-s-Codex'
DIRS = ['art', 'contracts', 'data', 'dist', 'dl', 'gen', 'images', 'og', 'p', 'r', 'sheets', 'src', 'tests', 'tools']
FILES = ['LICENSE', 'index.html', 'src.html', 'files.json', 'sitemap.xml', 'robots.txt', 'actualizar.bat', 'actualizar-rapido.bat']


def skip(rel):
    """Lo que no va al repositorio: cachés, copias de seguridad de un refresco, registros y los respaldos src.before_patchNN."""
    return '__pycache__' in rel or '/.refresh_bak' in rel or rel.endswith('.log') or '/before_patch' in rel or rel.endswith('.pyc')


def clone_path(root=ROOT, env=None):
    env = os.environ if env is None else env
    if env.get('AC_PR_CLONE'):
        return env['AC_PR_CLONE']
    f = os.path.join(root, '.pr_clone')
    if os.path.exists(f):
        return open(f, encoding='utf-8').read().strip()
    return DEFAULT_CLONE


def git(clone, *args, check=True):
    p = subprocess.run(['git', '-C', clone, *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if check and p.returncode != 0:
        raise RuntimeError('git %s: %s' % (' '.join(args), (p.stderr or p.stdout).strip()[:300]))
    return p


def sync(src, dst, dirs=DIRS, files=FILES):
    """Deja en dst los mismos archivos que src para esas carpetas y archivos (copia lo nuevo y lo cambiado, borra lo que ya no está).  Devuelve (copiados, borrados)."""
    copied = removed = 0
    for d in dirs:
        seen = set()
        for r, _, fs in os.walk(os.path.join(src, d)):
            for f in fs:
                full = os.path.join(r, f)
                rel = os.path.relpath(full, src).replace(os.sep, '/')
                if skip(rel):
                    continue
                seen.add(rel)
                to = os.path.join(dst, rel)
                if not os.path.exists(to) or not filecmp.cmp(full, to, shallow=False):
                    os.makedirs(os.path.dirname(to), exist_ok=True)
                    shutil.copy2(full, to)
                    copied += 1
        for r, _, fs in os.walk(os.path.join(dst, d)):
            for f in fs:
                rel = os.path.relpath(os.path.join(r, f), dst).replace(os.sep, '/')
                if rel not in seen and not skip(rel):
                    os.remove(os.path.join(dst, rel))
                    removed += 1
    for f in files:
        if os.path.exists(os.path.join(src, f)):
            to = os.path.join(dst, f)
            if not os.path.exists(to) or not filecmp.cmp(os.path.join(src, f), to, shallow=False):
                shutil.copy2(os.path.join(src, f), to)
                copied += 1
    return copied, removed


def find_gh(which=shutil.which):
    return which('gh') or next((p for p in ('C:/Program Files/GitHub CLI/gh.exe',) if os.path.exists(p)), None)


def pr_body(day, built, copied, removed, stat, skipped):
    lines = ['Publicación automática del %s (`python tools/publish.py --pr`).' % day, '',
             '- La página publicada trae "Página generada el %s".' % built,
             '- Archivos copiados o cambiados: %d · borrados: %d.' % (copied, removed)]
    if skipped:
        lines.append('- Fichas tácticas que quedaron fuera por no coincidir con las listas del día: ' + '; '.join(s.replace('SKIPPED ', '') for s in skipped))
    lines += ['', 'Pruebas que corrió la publicación: el refresco con sus pruebas de compuerta y `tests/check_dist.py`.', '', '```', stat.strip()[-1500:], '```', '',
              '🤖 Generated with [Claude Code](https://claude.com/claude-code)']
    return '\n'.join(lines)


def open_pr(day, built, skipped=(), src=ROOT, clone=None, gh=None, runner=subprocess.run, log=print):
    """Rama + commit + push + PR.  Devuelve (código, texto)."""
    clone = clone or clone_path(src)
    branch = 'auto/publish-' + day
    try:
        if not os.path.isdir(os.path.join(clone, '.git')):
            return 1, 'PR: %s no es un clon de git (AC_PR_CLONE o .pr_clone dicen dónde está).' % clone
        if git(clone, 'status', '--porcelain').stdout.strip():
            return 1, 'PR: el clon %s tiene cambios sin guardar; no lo toco.' % clone
        git(clone, 'fetch', '-q', 'origin')
        git(clone, 'switch', '-q', '-C', branch, 'origin/main')
        copied, removed = sync(src, clone)
        git(clone, 'add', '-A', '--', *[d for d in DIRS if os.path.isdir(os.path.join(clone, d))], *[f for f in FILES if os.path.exists(os.path.join(clone, f))])
        if not git(clone, 'diff', '--cached', '--name-only').stdout.strip():
            git(clone, 'switch', '-q', 'main', check=False)
            return 0, 'PR: no hay nada nuevo respecto de origin/main; no se abre ninguno.'
        stat = git(clone, 'diff', '--cached', '--stat').stdout
        git(clone, 'commit', '-q', '-m', 'Publicación %s' % day, '-m', 'Datos y página generados el %s: %d archivos copiados o cambiados, %d borrados.' % (built, copied, removed))
        git(clone, 'push', '-q', '-u', 'origin', branch, '--force-with-lease', '--force-if-includes')
        url = 'https://github.com/%s/compare/main...%s?expand=1' % (REPO, branch.replace('/', '%2F'))
        exe = gh or find_gh()
        if exe and runner([exe, 'auth', 'status'], capture_output=True).returncode == 0:
            have = runner([exe, 'pr', 'list', '--repo', REPO, '--head', branch, '--state', 'open', '--json', 'url', '--jq', '.[0].url'], capture_output=True, text=True, encoding='utf-8')
            if have.stdout.strip():
                return 0, 'PR: la rama se actualizó, el PR ya existe: ' + have.stdout.strip()
            p = runner([exe, 'pr', 'create', '--repo', REPO, '--base', 'main', '--head', branch, '--title', 'Publicación %s' % day,
                        '--body', pr_body(day, built, copied, removed, stat, skipped)], capture_output=True, text=True, encoding='utf-8')
            if p.returncode == 0:
                return 0, 'PR: ' + p.stdout.strip().splitlines()[-1]
            return 1, 'PR: la rama está subida pero `gh pr create` falló (%s). Abrilo a mano: %s' % ((p.stderr or '').strip()[:200], url)
        return 0, 'PR: rama %s subida. gh no está instalado o sin sesión (gh auth login); abrí el PR con este enlace: %s' % (branch, url)
    except (RuntimeError, OSError) as e:
        return 1, 'PR: %s' % e
    finally:
        if os.path.isdir(os.path.join(clone, '.git')):
            git(clone, 'switch', '-q', 'main', check=False)


if __name__ == '__main__':
    _day = sys.argv[1] if len(sys.argv) > 1 else __import__('datetime').date.today().isoformat()
    code, text = open_pr(_day, _day)
    print(text)
    sys.exit(code)

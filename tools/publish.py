"""Actualiza los datos de la página y los publica en Cloudflare con un solo comando (lo que antes eran tres a mano).   Desde la carpeta del proyecto:

  python tools/publish.py             refresco completo, arma dist/ y publica
  python tools/publish.py --quick     igual, sin las listas de imágenes de TCGplayer (la descarga más lenta)
  python tools/publish.py --no-deploy hace todo menos subir: sirve para probar
  python tools/publish.py --pr        además, tras publicar, sube la rama auto/publish-AAAA-MM-DD al repositorio y abre el PR (tools/pr.py; necesita gh con sesión)

Doble clic: actualizar.bat (completo) o actualizar-rapido.bat.

Por qué existe: `refresh.py` a secas es estricto y, si una ficha táctica ya no coincide con las listas del día, restaura todo y deja la página como estaba; si después se
corre dist.py y el deploy, se sube la página vieja y parece que "no cambia nada".  Acá el refresco siempre va con --unattended (las fichas que ya no coinciden quedan fuera
y se nombran) y el script NO sube nada si la fecha de la página no es la de hoy.

Pasos, y se corta en el primero que falle sin publicar:  refresh.py --unattended  ->  la página trae la fecha de hoy  ->  dist.py  ->  tests/check_dist.py  ->  wrangler pages deploy
(a producción, rama main)  ->  se abre la página publicada y se comprueba que trae la fecha de hoy.
Salida: 0 publicado y verificado · 1 falló un paso, no se publicó nada nuevo · 2 publicado pero la página en línea todavía muestra otra fecha (puede ser la caché: recargá) ·
3 publicado y verificado pero el PR de --pr falló (la página en línea está bien; el mensaje dice cómo abrirlo a mano).

Vercel no lo toca: Vercel sirve la carpeta dist/ del repositorio de GitHub y solo cambia con un commit.
"""
import datetime, os, re, shutil, subprocess, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pr as prmod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://aleisters-codex.pages.dev/'
PROJECT = 'aleisters-codex'
PY = sys.executable


def built_date(html):
    """La fecha 'Página generada el ...' que lleva index.html (const BUILT = 'AAAA-MM-DD'), o None."""
    m = re.search(r"const BUILT = '(\d{4}-\d{2}-\d{2})'", html)
    return m.group(1) if m else None


def refresh_cmd(quick):
    return [PY, '-B', 'tools/refresh.py', '--unattended'] + (['--quick'] if quick else [])


def deploy_cmd():
    npx = shutil.which('npx') or 'npx'
    return [npx, 'wrangler', 'pages', 'deploy', 'dist', '--project-name', PROJECT, '--branch', 'main', '--commit-dirty=true']


def run_stream(argv):
    """Corre un comando mostrando su salida en vivo; devuelve (código, líneas)."""
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    p = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    lines = []
    for ln in p.stdout:
        print(ln, end='', flush=True)
        lines.append(ln.rstrip('\n'))
    return p.wait(), lines


def fetch_live(stamp):
    req = urllib.request.Request(SITE + '?v=%d' % stamp, headers={'User-Agent': 'AleistersCodex-publish/1.0', 'Cache-Control': 'no-cache'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')


def main(argv, run=run_stream, today=datetime.date.today, read=None, fetch=fetch_live, sleep=time.sleep, open_pr=prmod.open_pr):
    quick, no_deploy, want_pr = '--quick' in argv, '--no-deploy' in argv, '--pr' in argv
    read = read or (lambda: open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read())
    day = today().isoformat()

    def step(title, cmd):
        print('\n=== %s ===' % title, flush=True)
        rc, lines = run(cmd)
        if rc != 0:
            print('\nFALLÓ: %s (código %s). No se publicó nada nuevo; la página en línea sigue como estaba.' % (title, rc))
        return rc, lines

    rc, lines = step('1/5 Refrescar los datos', refresh_cmd(quick))
    if rc != 0:
        return 1
    skipped = [ln for ln in lines if ln.startswith('SKIPPED')]
    built = built_date(read())
    if built != day:
        print('\nFALLÓ: la página generada dice %s y hoy es %s: el refresco no cambió la página. No publico para no subir lo viejo.' % (built, day))
        return 1
    rc, _ = step('2/5 Armar dist/', [PY, '-B', 'tools/dist.py'])
    if rc != 0:
        return 1
    rc, _ = step('3/5 Comprobar dist/', [PY, '-B', 'tests/check_dist.py'])
    if rc != 0:
        return 1

    def pull_request():
        print('\n=== 6/6 Pull request ===', flush=True)
        code, text = open_pr(day, built, skipped)
        print(text)
        return code

    if no_deploy:
        print('\nListo (--no-deploy): dist/ quedó armado con la fecha %s y no se subió nada.' % built)
        for s in skipped:
            print(s)
        return 3 if want_pr and pull_request() else 0
    rc, _ = step('4/5 Publicar en Cloudflare', deploy_cmd())
    if rc != 0:
        return 1
    print('\n=== 5/5 Verificar la página publicada ===', flush=True)
    live = None
    for i in range(6):
        try:
            live = built_date(fetch(int(time.time())))
        except Exception as e:
            live = None
            print('  no se pudo abrir %s: %s' % (SITE, e))
        if live == day:
            break
        sleep(5)
    for s in skipped:
        print(s)
    if live != day:
        print('\nPublicado, pero %s todavía muestra la fecha %s (hoy es %s). Si es la caché, recargá sin caché en un minuto.' % (SITE, live, day))
        return 2
    print('\nPublicado y verificado: %s muestra "Página generada el %s".' % (SITE, live))
    return 3 if want_pr and pull_request() else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

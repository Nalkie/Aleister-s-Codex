"""Gate test for tools/publish.py (sin red, sin correr nada de verdad).  Desde la carpeta del proyecto:  python tests/check_publish.py"""
import datetime, sys
sys.path.insert(0, 'tools')
import publish

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


DAY = datetime.date(2026, 11, 2)
page = lambda d: "<script>const BUILT = '%s';</script>" % d


def harness(argv, fail_at=None, built='2026-11-02', live=('2026-11-02',), skipped=True, pr=(0, 'PR: ok')):
    calls, fetched = [], []
    prs = []
    seq = list(live)

    def run(cmd):
        calls.append(cmd)
        name = ' '.join(map(str, cmd))
        if fail_at and fail_at in name:
            return 3, ['boom']
        return 0, (['SKIPPED 2 stale sheets (a, b)'] if skipped and 'refresh.py' in name else ['ok'])

    def fetch(stamp):
        fetched.append(stamp)
        v = seq.pop(0) if len(seq) > 1 else seq[0]
        if v is None:
            raise OSError('sin red')
        return page(v)

    rc = publish.main(argv, run=run, today=lambda: DAY, read=lambda: page(built), fetch=fetch, sleep=lambda s: None, open_pr=lambda day, b, sk: prs.append((day, b, list(sk))) or pr)
    names = [' '.join(map(str, c)) for c in calls]
    harness.prs = prs
    return rc, names, fetched


def has(names, word):
    return any(word in n for n in names)


# built_date
check(publish.built_date(page('2026-10-29')) == '2026-10-29', 'built_date lee la fecha')
check(publish.built_date('<html></html>') is None, 'built_date sin fecha -> None')

# camino feliz: 4 comandos en orden, deploy a producción, verificado
rc, n, f = harness([])
check(rc == 0, 'camino feliz sale 0')
check(len(n) == 4, 'cuatro pasos')
check('refresh.py' in n[0] and '--unattended' in n[0] and '--quick' not in n[0], 'refresca con --unattended (completo)')
check('tools/dist.py' in n[1] and 'tests/check_dist.py' in n[2] and 'wrangler' in n[3], 'orden: dist, check_dist, deploy')
check('--branch main' in n[3] and '--project-name aleisters-codex' in n[3], 'deploy a producción del proyecto correcto')
check(len(f) == 1, 'verifica la página publicada')

# --quick
rc, n, f = harness(['--quick'])
check('--quick' in n[0], '--quick llega a refresh.py')

# --no-deploy: no sube ni verifica
rc, n, f = harness(['--no-deploy'])
check(rc == 0 and not has(n, 'wrangler') and not f, '--no-deploy no sube ni consulta la web')

# falla en cada paso: se corta, no sube
for step, word in (('refresh', 'refresh.py'), ('dist', 'tools/dist.py'), ('check', 'check_dist.py')):
    rc, n, f = harness([], fail_at=word)
    check(rc == 1 and not has(n, 'wrangler'), 'si falla %s sale 1 y no publica' % step)
rc, n, f = harness([], fail_at='wrangler')
check(rc == 1 and not f, 'si falla el deploy sale 1 y no verifica')

# la causa raíz: refresh "ok" pero la página quedó con la fecha vieja -> no se publica
rc, n, f = harness([], built='2026-10-29')
check(rc == 1 and not has(n, 'wrangler') and not has(n, 'dist.py'), 'fecha vieja en index.html: sale 1 y no arma ni sube')
rc, n, f = harness([], built=None)
check(rc == 1 and not has(n, 'wrangler'), 'index.html sin fecha: no publica')

# página en línea con otra fecha -> 2; reintenta; si llega la fecha correcta -> 0; error de red tolerado
rc, n, f = harness([], live=('2026-10-29',))
check(rc == 2 and len(f) == 6, 'en línea con fecha vieja: sale 2 tras 6 intentos')
rc, n, f = harness([], live=('2026-10-29', '2026-10-29', '2026-11-02'))
check(rc == 0 and len(f) == 3, 'la caché se actualiza al tercer intento: sale 0')
rc, n, f = harness([], live=(None, '2026-11-02'))
check(rc == 0, 'un error de red en la verificación se reintenta')

# --pr: el PR se abre solo con el flag, solo si todo lo anterior salió bien, y su falla no desmiente la publicación
rc, n, f = harness([])
check(harness.prs == [], 'sin --pr no se abre ningún PR')
rc, n, f = harness(['--pr'])
check(rc == 0 and harness.prs == [('2026-11-02', '2026-11-02', ['SKIPPED 2 stale sheets (a, b)'])], 'con --pr se abre el PR después de publicar, con la fecha y las fichas excluidas')
rc, n, f = harness(['--pr'], pr=(1, 'PR: boom'))
check(rc == 3 and len(f) == 1, 'si el PR falla la salida es 3 (la página ya quedó publicada y verificada)')
rc, n, f = harness(['--pr'], fail_at='wrangler')
check(rc == 1 and harness.prs == [], 'si el deploy falla no se abre PR')
rc, n, f = harness(['--pr'], live=('2026-10-29',))
check(rc == 2 and harness.prs == [], 'si la página en línea no muestra la fecha de hoy no se abre PR')
rc, n, f = harness(['--pr'], built='2026-10-29')
check(rc == 1 and harness.prs == [], 'si el refresco no cambió la página no se abre PR')
rc, n, f = harness(['--pr', '--no-deploy'])
check(rc == 0 and len(harness.prs) == 1 and not has(n, 'wrangler'), '--pr con --no-deploy arma el PR sin subir a Cloudflare')

# deploy_cmd usa un ejecutable resoluble
check(publish.deploy_cmd()[1:4] == ['wrangler', 'pages', 'deploy'], 'deploy_cmd arma wrangler pages deploy')

print('\n%d fallas' % len(fails))
sys.exit(1 if fails else 0)

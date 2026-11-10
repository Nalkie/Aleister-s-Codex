"""Chequeo EN VIVO (usa la red; no es un gate): el formulario de contacto de «Fuentes y licencia» sigue abierto al público.  python tests/check_form_live.py
Un formulario de Google restringido a una cuenta responde 401 y redirige a accounts.google.com: el botón «Formulario de contacto» llevaría a un login.
Sale 0 si abre (200 y página de formulario), 1 si no; sale 2 si no hay red (no se puede decir nada)."""
import os, re, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'src.html'), encoding='utf-8').read()
m = re.search(r"const CONTACT_FORM='(https://[^']*)';", src)
if not m:
    print('FAIL CONTACT_FORM vacío o ausente en src.html')
    sys.exit(1)
try:
    r = urllib.request.urlopen(urllib.request.Request(m.group(1), headers={'User-Agent': 'Mozilla/5.0'}), timeout=20)
    final, body = r.geturl(), r.read(200000).decode('utf-8', 'replace')
except urllib.error.HTTPError as e:
    print('FAIL el formulario responde %s: probablemente restringido a una cuenta (%s)' % (e.code, m.group(1)))
    sys.exit(1)
except (urllib.error.URLError, OSError) as e:
    print('SIN RED: no se pudo comprobar (%s)' % e)
    sys.exit(2)
ok = 'accounts.google.com' not in final and 'docs.google.com/forms' in final and '<title>' in body
print(('ok   el formulario abre sin sesión: ' if ok else 'FAIL el formulario pide iniciar sesión: ') + final[:90])
sys.exit(0 if ok else 1)

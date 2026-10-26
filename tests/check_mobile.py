"""Gate test for the mobile layout: tools/mobile.css must live entirely inside a max-width media query (the desktop layout does not change), it must be
injected into the built page, and the navigation must not be a sideways-scrolling strip on phones. Run from the project root:  python tests/check_mobile.py
Exit code 0 = every check passed. Deterministic, no network."""
import re, sys

fails = []


def check(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg)
    if not cond:
        fails.append(msg)


def strip_media(css):
    """Return (css with every top-level @media block removed, list of media conditions)."""
    out, conds, i = [], [], 0
    while i < len(css):
        m = re.compile(r'@media\s*([^{]*)\{').search(css, i)
        if not m:
            out.append(css[i:]); break
        out.append(css[i:m.start()])
        conds.append(m.group(1).strip())
        depth, j = 1, m.end()
        while depth and j < len(css):
            depth += {'{': 1, '}': -1}.get(css[j], 0)
            j += 1
        i = j
    return ''.join(out), conds


css = open('tools/mobile.css', encoding='utf-8').read()
bare, conds = strip_media(re.sub(r'/\*.*?\*/', '', css, flags=re.S))
check(bare.strip() == '', 'mobile.css has no rule outside an @media block (desktop untouched)')
check(conds and all(re.fullmatch(r'\(max-width:\s*\d+px\)', c) for c in conds), f'every media query is a plain max-width one: {conds}')

page = open('index.html', encoding='utf-8').read()
src = open('src.html', encoding='utf-8').read()
check(css.strip() in page and css.strip() in src, 'mobile.css is injected into src.html and index.html')
check('c.dataset.l=h[i]' in src, 'render() labels table cells for the stacked mobile tables')

# the nav (modes + tools) is a grid on phones, not a scroll strip
m = re.search(r'\.modes\{display:grid;[^}]*overflow:visible', css)
check(bool(m), '.modes is a visible grid on phones')
m = re.search(r'\.tools\{display:grid;[^}]*overflow:visible', css)
check(bool(m), '.tools is a visible grid on phones')
check('.tbl table:not(.ptab) thead{display:none}' in css and 'attr(data-l)' in css, 'wide tables stack into labelled cards on phones')

check("mobTo('#app .detail')" in src and "mobTo('#app .sethero,#app .chcard')" in src, 'picking a card or set scrolls to its detail on narrow screens')
check('data-mback' in src and 'Volver a la lista' in src, 'the detail has a back-to-list button on narrow screens')
check("innerWidth<=900?'más abajo'" in src, 'texts say "más abajo" instead of "a la derecha" on narrow screens')

sys.exit(1 if fails else 0)

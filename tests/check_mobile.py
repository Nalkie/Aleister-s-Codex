"""Gate: the mobile polish of src.html (rules that must not disappear).  No network, <2 s.  python tests/check_mobile.py
Outcome: on a phone the side character stays visible (one, behind the content), taps have 44px targets, inputs do not trigger the iOS zoom, the ranking keeps its card,
and there is a way back to the top (the mode bar is not sticky on mobile)."""
import re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'src.html'), encoding='utf-8').read()
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


def block(media):
    """The text of every @media(...) block whose query contains `media` (brace matched)."""
    out = []
    for m in re.finditer(r'@media\s*\(?\s*max-width:\s*%s' % re.escape(media), src):
        i = src.index('{', m.start()); d = 0
        for j in range(i, len(src)):
            d += src[j] == '{'; d -= src[j] == '}'
            if d == 0:
                out.append(src[i:j + 1]); break
    return '\n'.join(out)


m1000, m760 = block('1000px'), block('760px')
check('.sideart.l{display:none}' in m1000 and '.sideart.day.l{display:none!important}' in m1000, 'under 1000px only the LEFT side character is hidden')
check(re.search(r'\.sideart\.r\{[^}]*opacity:\.1[0-9]', m1000) is not None and '.sideart.day.r{' in m1000, 'under 1000px the right character stays (night and day versions) at a low opacity behind the content')
check('.sideart{display:none}' not in src and '.sideart.day{display:none!important}' not in src, 'no rule hides every side character on narrow screens any more')
check('input,select,textarea{font-size:16px}' in m760, 'inputs are 16px on mobile (no iOS zoom on focus)')
check('.seg.mini button{min-height:44px' in m760, 'format switches have 44px tap targets on mobile')
check('#app li > a{display:inline-block;padding:7px 0}' in m760, 'links inside lists have a taller tap area on mobile')
check('.deck .card-fg{display:block;' in m760 and '.deck .card-fg{display:none}' not in src, 'the ranking keeps its small card on mobile')
check("className='totop'" in src and '.totop.on{' in m760 and '.totop:hover{border-color:var(--accent)}' in src, 'the back-to-top button exists on mobile and desktop')
check('.hero{padding-block:var(--s5) 64px}' in m760, 'the mobile header is shorter')
check('.mode .mstat{' in src and 'text-overflow:ellipsis' not in re.search(r'\.mode \.mstat\{[^}]*\}', src).group(0), 'mode-card stats wrap instead of being cut with an ellipsis (desktop)')
check('.dock.compact .tools{flex-wrap:nowrap' in src, 'the sticky desktop dock keeps its tools on one row')
check('.ptile .mini,.pv .mini,.recgal .mini{font-size:.7rem}' in src, 'desktop floor for the smallest labels (>=11px)')
check('#app p{max-width:78ch}' in src, 'desktop prose is capped to a readable line length')
check('html{scroll-padding-top:84px}' in src, 'desktop anchor jumps clear the sticky dock')
print('failed:', len(fails))
sys.exit(1 if fails else 0)

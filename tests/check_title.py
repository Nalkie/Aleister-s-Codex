"""Gate: el título de la pestaña del navegador es corto y legible (antes salía «TCGYu-Gi-Oh! Advanced492 decks · Elfnote 17,7% · Aleister's Codex»: juntaba el texto de todo el botón de la pestaña).  python tests/check_title.py

  1. el título sale de MODES[mode][0] (el nombre de la sección), no del textContent de un botón con varios elementos adentro
  2. cada sección tiene un nombre corto, sin números ni separadores, y no se repite: es lo que se lee en la pestaña
  3. el título final queda «Sección · Aleister's Codex» (la función real, en node), también para «Fuentes y licencia», que no tiene pestaña
"""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


src = open('src.html', encoding='utf-8').read().replace('\r\n', '\n')
ok("const b=MODES[mode]?MODES[mode][0]:''; return b&&mode==='tcg'&&RETRO_ES[TCGF]?b+' '+RETRO_ES[TCGF].n:b&&mode==='dl'&&DL_FMT[dlFormat]?b+' '+DL_FMT[dlFormat]:b;" in src and "tb.textContent.trim()" not in src, 'el título sale de MODES[mode][0] más el formato (TCG Advanced, Duel Links Speed Duel), no del texto del botón de la pestaña')
m = re.search(r"const MODES = \{(.*?)\};\n", src, re.S)
ok(bool(m), 'src.html trae MODES')
if m:
    names = re.findall(r"(\w+):\['([^']+)',", m.group(1))
    ok(len(names) >= 18, 'MODES trae %d secciones' % len(names))
    ok(all(0 < len(n) <= 30 and not re.search(r'\d|·', n) for k, n in names), 'cada nombre es corto y sin números ni separadores %s' % [n for k, n in names if re.search(r'\d|·', n) or len(n) > 30])
    ok(len({n for k, n in names}) == len(names), 'ningún nombre de sección se repite')
    ok(('abt', 'Fuentes y licencia') in names, '«Fuentes y licencia» (sin pestaña) también tiene nombre')
    mt = re.search(r"document\.title=nm\?nm\+\" · Aleister's Codex\":\"Aleister's Codex\";", src)
    ok(bool(mt), 'el título final es «Nombre · Aleister\'s Codex»')
print('failed:', len(fails))
sys.exit(1 if fails else 0)

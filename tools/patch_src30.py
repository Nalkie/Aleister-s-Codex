"""Eventos y torneos: se saca "Personajes y habilidades" (los personajes, sus cartas y habilidades viven en la pestaña Obtención, donde al tocar una carta
se abre la vista previa a la derecha en vez de ir al buscador). Backup: src.before_patch30.html."""
import re, shutil
shutil.copy('src.html', 'src.before_patch30.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("""
    ${EV.fmt==='dl'?`<div class="seg" role="group" aria-label="Sección"><button data-evtab="events" aria-pressed="${EV.tab==='events'}">Eventos del juego</button><button data-evtab="chars" aria-pressed="${EV.tab==='chars'}">Personajes y habilidades</button></div>`:''}`;""", "`;")
rep("(EV.fmt==='dl'?(EV.tab==='chars'?evChars():evDL()):evComp(EV.fmt))", "(EV.fmt==='dl'?evDL():evComp(EV.fmt))")
rep("'Duel Links: eventos activos del juego y lo que da cada personaje. TCG y Genesys: torneos con sus resultados.'", "'Duel Links: eventos activos del juego. TCG, OCG y Genesys: torneos con sus resultados. Los personajes y sus cartas están en Obtención.'")
a = s.index("function evChars(){")
m = re.search(r"\n(?=function |/\* -{5,})", s[a + 10:])
b = a + 10 + m.start() + 1
s = s[:a] + s[b:]
lines = s.split('\n')
keep = [l for l in lines if not (l.lstrip().startswith('else if(d.evtab)') or l.lstrip().startswith('else if(d.evchar)') or l.lstrip().startswith("else if(id==='evcq')"))]
assert len(lines) - len(keep) == 3, len(lines) - len(keep)
s = '\n'.join(keep)
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 30 ok')

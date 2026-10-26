"""La pestaña "Obtención" pasa a llamarse "Obtención en Duel Links" para que se entienda que es solo de ese juego; "Motores" pasa a llamarse "Engines", el término del juego. Backup: src.before_patch38.html."""
import shutil
shutil.copy('src.html', 'src.before_patch38.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("</svg>Obtención</button>", "</svg>Obtención en Duel Links</button>")
rep("obt:['Obtención',viewSets],", "obt:['Obtención en Duel Links',viewSets],")
rep("están en la pestaña Obtención.", "están en la pestaña Obtención en Duel Links.")
rep("Los personajes y sus cartas están en Obtención.", "Los personajes y sus cartas de Duel Links están en la pestaña Obtención en Duel Links.")
rep("</svg>Motores</button>", "</svg>Engines</button>")
rep("eng:['Motores',viewEngines],", "eng:['Engines',viewEngines],")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 38 ok')

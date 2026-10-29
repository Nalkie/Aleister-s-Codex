"""Ruleta de decks: las fotos de los duelistas dejan de verse cuadradas.  Los retratos de Duel Links Meta (124x146) traen un marco rectangular (borde blanco, fondo rayado,
sombra con muesca); recortados con un círculo del ancho completo, el marco asoma en los costados y el círculo parece una foto cuadrada.  Ahora el círculo recorta por dentro del
marco (ROU_FACE: centro y radio en píxeles del retrato), tanto en la rueda (SVG) como en el duelista que sale (CSS).  Backup: src.before_patch66.html."""
import shutil

shutil.copy('src.html', 'src.before_patch66.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


# la rueda: la imagen se escala y se corre para que el círculo caiga dentro del marco
rep("function rouFaceUrl(p){",
    "const ROU_FACE={w:124,h:146,cx:62,cy:64,r:54};   // retrato de Duel Links Meta: el círculo (centro cx,cy y radio r, en píxeles del retrato) queda dentro del marco rectangular\nfunction rouFaceUrl(p){")
rep("""<image href="${esc(u)}" x="${(-fr).toFixed(1)}" y="${(-fr).toFixed(1)}" width="${(fr*2).toFixed(1)}" height="${(fr*2).toFixed(1)}" preserveAspectRatio="xMidYMin slice" clip-path="url(#rcl)" """,
    """<image href="${esc(u)}" x="${(-ROU_FACE.cx*fr/ROU_FACE.r).toFixed(1)}" y="${(-ROU_FACE.cy*fr/ROU_FACE.r).toFixed(1)}" width="${(ROU_FACE.w*fr/ROU_FACE.r).toFixed(1)}" height="${(ROU_FACE.h*fr/ROU_FACE.r).toFixed(1)}" preserveAspectRatio="xMinYMin slice" clip-path="url(#rcl)" """)

# el duelista que sale (y las miniaturas): mismo recorte con porcentajes del lado del círculo (k = lado / (2r))
rep(".rou-face img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:top;background:var(--surface2)}",
    ".rou-face img{position:absolute;left:-7.4%;top:-9.3%;width:114.8%;height:auto;max-width:none;background:var(--surface2)}   /* recorte por dentro del marco del retrato: ver ROU_FACE */")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 66 ok')

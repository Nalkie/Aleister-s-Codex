"""Ruleta de decks: retratos propios.  Los personajes que Duel Links Meta no tiene (Adrian, Atticus, Camula, Nightshroud, Tania, Titan, Bruno, Devack, Ghost, Lazar, Misty, Roman, Vetrix)
traen un retrato en data/face-<slug>.webp (tools/roulette_faces.py), ya recortado a cuadrado con la cabeza centrada: el círculo lo muestra entero, sin el recorte por dentro del marco
(ROU_FACE) que necesitan los retratos de Duel Links Meta.  Backup: src.before_patch69.html."""
import shutil

shutil.copy('src.html', 'src.before_patch69.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep("function rouFaceUrl(p){ return p?'https://s3.duellinksmeta.com'+String(p).split('/').map(encodeURIComponent).join('/'):''; }",
    "function rouOwn(p){ return /^data\//.test(p||''); }   // retrato propio (data/face-*.webp, ya recortado al círculo) y no uno de Duel Links Meta\n"
    "function rouFaceUrl(p){ return !p?'':rouOwn(p)?p:'https://s3.duellinksmeta.com'+String(p).split('/').map(encodeURIComponent).join('/'); }")
rep("""${u?`<img src="${esc(u)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.remove()">`:''}</span>`;""",
    """${u?`<img${rouOwn(c.face)?' class="own"':''} src="${esc(u)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.remove()">`:''}</span>`;""")
rep("""${u?`<image href="${esc(u)}" x="${(-ROU_FACE.cx*fr/ROU_FACE.r).toFixed(1)}" y="${(-ROU_FACE.cy*fr/ROU_FACE.r).toFixed(1)}" width="${(ROU_FACE.w*fr/ROU_FACE.r).toFixed(1)}" height="${(ROU_FACE.h*fr/ROU_FACE.r).toFixed(1)}" preserveAspectRatio="xMinYMin slice" clip-path="url(#rcl)" """,
    """${u?`<image href="${esc(u)}" ${rouFit(c.face,fr)} clip-path="url(#rcl)" """)
FIT = (
    "function rouFit(p,fr){      // posición de la imagen dentro del círculo de la rueda (radio fr): el retrato propio llena el cuadrado; el de Duel Links Meta se corre para caer dentro de su marco\n"
    "  const f=x=>x.toFixed(1), k=fr/ROU_FACE.r, a=rouOwn(p)?[-fr,-fr,fr*2,fr*2,'xMidYMid']:[-ROU_FACE.cx*k,-ROU_FACE.cy*k,ROU_FACE.w*k,ROU_FACE.h*k,'xMinYMin'];\n"
    "  return 'x=\"'+f(a[0])+'\" y=\"'+f(a[1])+'\" width=\"'+f(a[2])+'\" height=\"'+f(a[3])+'\" preserveAspectRatio=\"'+a[4]+' slice\"';\n}\n")
rep("function rouFaceUrl(p){", FIT + "function rouFaceUrl(p){")
rep("/* recorte por dentro del marco del retrato: ver ROU_FACE */",
    "/* recorte por dentro del marco del retrato: ver ROU_FACE */\n.rou-face img.own{left:0;top:0;width:100%;height:100%;object-fit:cover}   /* retrato propio: ya viene recortado */")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 69 ok')

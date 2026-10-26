"""Cartas recomendadas de Duel Links: con la imagen real de la carta (galería de cartas) en vez del recorte pequeño. Backup: src.before_patch35.html."""
import shutil
shutil.copy('src.html', 'src.before_patch35.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("""  const cards=rs=>`<div class="cgrid">${rs.map(r=>`<button class="cc" data-card="${esc(r.n)}">${thumb(r.n)}<span class="n">${esc(r.n)}<b>${fmt(r.cov)} de los mazos${r.k>1?' · '+r.k+' arquetipos':''}</b><small class="rhow">${esc(r.how)}</small></span></button>`).join('')}</div>`;""",
    """  const cards=rs=>`<div class="gal recgal">${rs.map(r=>`<button class="tile ptile" data-card="${esc(r.n)}" title="${esc(r.n)} · ${fmt(r.cov)} de los mazos${r.k>1?' · '+r.k+' arquetipos':''}"><span class="art">${cardImg(r.n,false)}</span><span class="tn">${esc(r.n)}</span><span class="tm"><b class="${rchip(dlRar(r.n),'dl')}">${esc(dlRar(r.n))}</b><b class="vv">${fmt(r.cov)}</b></span><span class="mini">${esc(r.how)}</span></button>`).join('')}</div>`;""")
rep(".fmtbar{margin:var(--s4) 0 0}", ".fmtbar{margin:var(--s4) 0 0}\n.recgal{grid-template-columns:repeat(auto-fill,minmax(118px,1fr))}\n.recgal .mini{font-size:.62rem;line-height:1.25;white-space:normal;text-align:center;min-height:2.5em}")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 35 ok')

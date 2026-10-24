"""Deck builder shows full card images (YGOPRODeck) with the cropped art as fallback."""
import shutil
shutil.copy('src.html','src.before_patch8.html')
s=open('src.html',encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a[:70]
    s=s.replace(a,b)
rep("function cardChips(cards)", """function cardImg(n){
  const c=CARDS[canon(n)], id=c&&c[C.ID];
  return `<span class="cf">${thumb(n)}${id?`<img src="https://images.ygoprodeck.com/images/cards_small/${id}.jpg" alt="${esc(n)}" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.remove()">`:''}</span>`;
}
function cardChips(cards)""")
rep("""<span class="art">${thumb(n)}<b class="cnt">×${k}</b>${(()=>{""","""<span class="art">${cardImg(n)}<b class="cnt">×${k}</b>${(()=>{""")
rep('<span class="art">${thumb(n)}<b class="plus">+</b>','<span class="art">${cardImg(n)}<b class="plus">+</b>')
rep("</style>", """
/* constructor: cartas completas */
.cf{position:relative;display:grid;place-items:center;width:100%;aspect-ratio:59/86;border-radius:9px;overflow:hidden;background:var(--surface2);border:1px solid var(--line2)}
.cf .th{width:100%!important;height:auto!important;aspect-ratio:1;border:0!important;border-radius:0!important}
.cf img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background:var(--surface2)}
.dkdeck .gal,.dkpick .gal{grid-template-columns:repeat(auto-fill,minmax(88px,1fr))}
.dkdeck .tile .art .cf,.dkpick .tile .art .cf{box-shadow:none}
</style>""")
open('src.html','w',encoding='utf-8').write(s)

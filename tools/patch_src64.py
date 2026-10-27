"""Ficha táctica de cada mazo: 4 bloques plegables (Objetivo y ritmo, Iniciadores clave, Puntos de interrupción, Plan de Side Deck).
Los datos viven en data/play.js (tools/playcards.py los valida contra las cartas y la lista del mazo); contrato en contracts/playcard.ts.
Un mazo sin ficha no muestra nada.  Backup: src.before_patch64.html."""
import shutil

shutil.copy('src.html', 'src.before_patch64.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("function deckRow(d,i,pctVal,barVal,metaTxt,body){", r"""/* ---------- ficha táctica del mazo ---------- */
const PLAY={data:null,asked:false};
function playLoad(){ if(PLAY.asked) return; PLAY.asked=true; loadData('play').then(j=>{ PLAY.data=j; if(['tcg','gen','dl'].includes(mode)){
  const open=[...document.querySelectorAll('details.deck[open]')].map(x=>x.dataset.slug), y=window.scrollY; render();
  document.querySelectorAll('details.deck').forEach(x=>{ if(open.includes(x.dataset.slug)) x.open=true; }); window.scrollTo(0,y); } }).catch(()=>{}); }
const PLAY_PLAN={control:'Control',otk:'OTK',grind:'Grind',tempo:'Tempo',combo:'Combo',burn:'Burn',stun:'Stun'};
const PLAY_PACE={fast:'Ritmo rápido',medium:'Ritmo medio',slow:'Ritmo lento'};
function playCard(fmtKey,d){
  playLoad(); if(!PLAY.data) return '';
  const c=PLAY.data[fmtKey+'/'+deckSlug(d.n)]; if(!c) return '';
  const L=o=>esc(o[LANG==='en'?'en':'es']), cn=n=>`<b class="pc-c">${esc(n)}</b>`;
  const sec=(i,title,body,open)=>`<details class="pc-sec"${open?' open':''}><summary><span class="pc-n">${i}</span>${title}</summary>${body}</details>`;
  const moves=(arr,sign)=>arr.map(m=>`<li><span class="pc-mv ${sign==='+'?'in':'out'}">${sign}${m.qty}</span> ${cn(m.card)} <span class="pc-why">${L(m.why)}</span></li>`).join('');
  const swap=(title,sw)=>`<div class="pc-swap"><h5>${title}</h5><ul>${moves(sw.in,'+')}${moves(sw.out,'−')}</ul></div>`;
  return `<div class="pcard"><div class="pc-head"><h3>Ficha táctica</h3><span class="pc-tags"><i>${PLAY_PLAN[c.win.plan]}</i><i>${PLAY_PACE[c.win.pace]}</i></span></div>
    ${sec(1,'Objetivo y ritmo',`<ul>${c.win.bullets.map(b=>`<li>${L(b)}</li>`).join('')}</ul>`,true)}
    ${sec(2,'Iniciadores clave',`<ul>${c.starters.map(x=>`<li><span class="pc-cards">${x.cards.map(cn).join('<span class="pc-plus">+</span>')}</span> ${L(x.route)}</li>`).join('')}</ul>`)}
    ${sec(3,'Puntos de interrupción',`<ul>${c.chokepoints.map(k=>`<li>${cn(k.card)} <span class="pc-step">${L(k.stepText)}</span> ${L(k.loss)}</li>`).join('')}</ul>`)}
    ${sec(4,'Plan de Side Deck',`<div class="pc-sides">${swap('Yendo primero',c.side.first)}${swap('Yendo segundo',c.side.second)}</div>${c.side.basis==='editorial'?'<p class="rnote">Criterio editorial de la redacción, no una estadística de torneos.</p>':''}`)}
    <p class="rnote">Revisada el ${dmy(c.updated)}.</p></div>`;
}
function deckRow(d,i,pctVal,barVal,metaTxt,body){""")

# la ficha va debajo de la lista de cada mazo
rep("`${decklist(d.list,k)}<p>${esc(d.res)}</p>${d.cards.length?", "`${decklist(d.list,k)}${playCard(k,d)}<p>${esc(d.res)}</p>${d.cards.length?")
rep("`${decklist(d.list,'tcg')}<p>${esc(d.res)}</p>${d.cards.length?", "`${decklist(d.list,'tcg')}${playCard('adv',d)}<p>${esc(d.res)}</p>${d.cards.length?")
rep("`${decklist(d.list,'gen')}<p>${esc(d.res)}</p>`", "`${decklist(d.list,'gen')}${playCard('gen',d)}<p>${esc(d.res)}</p>`")
rep("`${decklist(d.list,'dl')}<p>${esc(d.res)}</p>`);\n  const sorted", "`${decklist(d.list,'dl')}${playCard('dl',d)}<p>${esc(d.res)}</p>`);\n  const sorted")

css = '''/* ficha táctica */
.pcard{margin:var(--s3) 0;border:1px solid var(--line2);border-radius:var(--r2);background:color-mix(in srgb,var(--panel,var(--bg)) 70%,transparent);overflow:hidden}
.pc-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:var(--s2);padding:var(--s2) var(--s3);border-bottom:1px solid var(--line2)}
.pc-head h3{margin:0}
.pc-tags{display:flex;gap:6px;flex-wrap:wrap}
.pc-tags i{font:500 .72rem var(--f-data);font-style:normal;letter-spacing:.06em;text-transform:uppercase;padding:2px 10px;border-radius:99px;border:1px solid var(--line2);color:var(--muted)}
.pc-sec{border-bottom:1px solid var(--line2)}
.pc-sec:last-of-type{border-bottom:0}
.pc-sec>summary{display:flex;align-items:center;gap:var(--s2);padding:12px var(--s3);cursor:pointer;font:600 .9rem var(--f-body);min-height:44px;list-style:none}
.pc-sec>summary::-webkit-details-marker{display:none}
.pc-sec>summary::after{content:"+";margin-left:auto;color:var(--muted);font-size:1.1rem}
.pc-sec[open]>summary::after{content:"−"}
.pc-n{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:var(--accent);color:var(--bg);font:700 .75rem var(--f-data)}
.pc-sec ul{margin:0;padding:0 var(--s3) var(--s3) calc(var(--s3) + 22px + var(--s2));display:grid;gap:10px;list-style:disc;font-size:.88rem;line-height:1.45}
.pc-sec li::marker{color:var(--accent)}
.pc-c{font-weight:600}
.pc-plus{margin:0 4px;color:var(--muted)}
.pc-step{display:block;font-size:.8rem;color:var(--muted)}
.pc-sides{display:grid;grid-template-columns:1fr 1fr;gap:var(--s3);padding:0 var(--s3)}
.pc-sides ul{padding:0;list-style:none}
.pc-swap h5{font:600 .78rem var(--f-data);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 var(--s2)}
.pc-mv{display:inline-block;min-width:26px;text-align:center;font:700 .74rem var(--f-data);border-radius:6px;padding:1px 4px}
.pc-mv.in{background:color-mix(in srgb,var(--ac-dl,#3a3) 25%,transparent)}
.pc-mv.out{background:color-mix(in srgb,var(--red,#c33) 22%,transparent)}
.pc-why{display:block;font-size:.8rem;color:var(--muted)}
.pcard>.rnote{padding:0 var(--s3) var(--s2);margin:0}
.pc-sec .rnote{padding:var(--s2) var(--s3) var(--s3);margin:0}
@media(max-width:600px){.pc-sides{grid-template-columns:1fr}.pc-sec ul{padding-left:calc(var(--s3) + 18px)}}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 64 ok')

"""Constructor de mazos: simulador de mano inicial («Probar mano»): 5 cartas al azar del Main Deck respetando las copias, en fila con su imagen,
con «Mulligan / Nueva mano» (baraja todo y reparte 5 de nuevo) y «Robar 1 carta extra» (la siguiente del mazo ya barajado).  Backup: src.before_patch63.html."""
import shutil

shutil.copy('src.html', 'src.before_patch63.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


# estado
rep("modal:null,msg:'',png:'',imp:'',bk:'',tab:'ydk',saved:[]};", "modal:null,msg:'',png:'',imp:'',bk:'',tab:'ydk',saved:[],hand:null};")
# cualquier cambio del mazo invalida la mano
rep("function dkDraft(){ try{", "function dkDraft(){ DK.hand=null; try{")

# funciones puras + panel
rep("function dkTile(n,k,sec){", r"""/* ---------- simulador de mano inicial ---------- */
const HAND_SIZE=5;
function handShuffle(list,rnd){            // Fisher-Yates; rnd es inyectable para poder probarlo
  const a=list.slice(), r=rnd||Math.random;
  for(let i=a.length-1;i>0;i--){ const j=Math.floor(r()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; }
  return a;
}
function handDeck(main){ const out=[]; for(const [n,k] of Object.entries(main)) for(let i=0;i<k;i++) out.push(n); return out; }
function handDeal(main,rnd){ const d=handShuffle(handDeck(main),rnd); return {hand:d.slice(0,HAND_SIZE),rest:d.slice(HAND_SIZE)}; }
function handDraw(H){ if(!H||!H.rest.length) return false; H.hand.push(H.rest.shift()); return true; }
function handPanel(){
  const n=dkCount('main'), H=DK.hand;
  const cards=H?H.hand.map(c=>`<span class="hc" title="${esc(c)}"><span class="art">${cardImg(c)}</span><span class="tn">${esc(c)}</span></span>`).join(''):'';
  return `<div class="dsec hand"><h4>Probar mano</h4>
    <div class="handbar"><button class="abtn pri" data-dk="${H?'hand-new':'hand'}"${n<HAND_SIZE?' disabled':''}>${H?'Mulligan / Nueva mano':'Probar mano'}</button>${H?`<button class="abtn" data-dk="hand-draw"${H.rest.length?'':' disabled'}>Robar 1 carta extra</button>`:''}
    <small class="mini">${n<HAND_SIZE?`Hacen falta al menos ${HAND_SIZE} cartas en el Main Deck.`:H?`En mano: ${H.hand.length} · quedan ${H.rest.length} en el mazo`:`Reparte ${HAND_SIZE} cartas al azar de tu Main Deck.`}</small></div>
    ${H?`<div class="handrow" aria-live="polite">${cards}</div>`:''}</div>`;
}
function dkTile(n,k,sec){""")
rep("${sec('main')}${sec('extra')}${sec('side')}\n        <div class=\"dsec notes\">", "${handPanel()}${sec('main')}${sec('extra')}${sec('side')}\n        <div class=\"dsec notes\">")

# acciones
rep("  else if(a==='clear-target'){ DK.target=d.val; }", "  else if(a==='hand'||a==='hand-new'){ if(dkCount('main')>=HAND_SIZE) DK.hand=handDeal(DK.main); }\n  else if(a==='hand-draw'){ handDraw(DK.hand); }\n  else if(a==='clear-target'){ DK.target=d.val; }")

css = '''/* simulador de mano */
.dsec.hand h4::before{background:var(--ac-dl,var(--accent))}
.handbar{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s2);margin-bottom:var(--s3)}
.handbar .abtn[disabled]{opacity:.45;cursor:not-allowed}
.handrow{display:flex;flex-wrap:wrap;gap:var(--s3)}
.hc{display:flex;flex-direction:column;gap:4px;width:104px}
.hc .art{display:block;aspect-ratio:59/86;border-radius:6px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.35)}
.hc .art img{width:100%;height:100%;object-fit:cover;display:block}
.hc .tn{font-size:.7rem;line-height:1.2;text-align:center}
@media(max-width:600px){.hc{width:calc(33.3% - var(--s3))}}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 63 ok')

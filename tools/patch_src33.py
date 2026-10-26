"""1) La cabecera de los tickets no tapa el título: las cartas van en su propia columna. 2) En Duel Links las cajas indican con color y etiqueta si son de
Speed Duel (azul) o de Rush Duel (naranja) y se pueden filtrar. 3) Sin selector de rareza cuando la lista es de una sola rareza. Backup: src.before_patch33.html."""
import shutil
shutil.copy('src.html', 'src.before_patch33.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- 1) cabecera de tickets: las cartas en su columna ----------
rep("    ${top.map((n,i)=>`<img class=\"chfg f${i+1}\" src=\"${imgUrl(cardId(n),true)}\" alt=\"${esc(n)}\" loading=\"lazy\" referrerpolicy=\"no-referrer\" onerror=\"this.remove()\">`).join('')}\n  </div>`;",
    "    ${top.length?`<div class=\"othcards\">${top.map((n,i)=>`<img class=\"chfg f${i+1}\" src=\"${imgUrl(cardId(n),true)}\" alt=\"${esc(n)}\" loading=\"lazy\" referrerpolicy=\"no-referrer\" onerror=\"this.remove()\">`).join('')}</div>`:''}\n  </div>`;")
rep(".chcard.oth .chtxt{max-width:34%}", ".chcard.oth .chtxt{max-width:none;flex:1;min-width:0}\n.othcards{position:relative;flex:none;width:204px;align-self:stretch;min-height:176px}\n.othcards .chfg{height:100%;top:50%}")
rep(".chfg.f1{right:17%;rotate:-6deg;z-index:1}\n.chfg.f2{right:3%;rotate:8deg;z-index:2}", ".othcards .chfg.f1{right:62px;rotate:-6deg;z-index:1}\n.othcards .chfg.f2{right:0;rotate:8deg;z-index:2}")
rep("@container (max-width:600px){.chcard.oth .othticket{width:170px}.chcard.oth .chtxt{max-width:calc(100% - 290px)}.chfg.f1{display:none}.chfg.f2{right:2.5%}}\n@container (max-width:470px){.chcard.oth .othticket{width:120px}.chcard.oth .chtxt{max-width:none}.chfg.f2{display:none}}",
    "@container (max-width:640px){.chcard.oth .othticket{width:170px}.othcards{width:128px}.othcards .chfg.f1{display:none}}\n@container (max-width:480px){.chcard.oth .othticket{width:118px}.othcards{display:none}}")

# ---------- 2) Rush / Speed en las cajas ----------
rep("let list=data.filter(s=>(fmt==='tcg'||s.kind===SETS.kind)&&(fmt==='tcg'||SETS.kind!=='other'||!!s.rush===SETS.rush)&&(!q||matchText(q,s.n)));",
    "let list=data.filter(s=>(fmt==='tcg'||s.kind===SETS.kind)&&(fmt==='tcg'||SETS.kind!=='other'||!!s.rush===SETS.rush)&&(fmt==='tcg'||s.kind!=='set'||!SETS.rushf||SETS.rushf==='all'||(SETS.rushf==='rush')===!!s.rush)&&(!q||matchText(q,s.n)));")
rep("<button data-sfmt=\"dl\" aria-pressed=\"${fmt==='dl'}\">Duel Links</button></div>`;",
    "<button data-sfmt=\"dl\" aria-pressed=\"${fmt==='dl'}\">Duel Links</button></div>\n    ${fmt==='dl'?`<div class=\"seg\" role=\"group\" aria-label=\"Modo\"><button data-srf=\"all\" aria-pressed=\"${!SETS.rushf||SETS.rushf==='all'}\">Todas</button><button class=\"sk\" data-srf=\"speed\" aria-pressed=\"${SETS.rushf==='speed'}\">Speed Duel</button><button class=\"rk\" data-srf=\"rush\" aria-pressed=\"${SETS.rushf==='rush'}\">Rush Duel</button></div>`:''}`;")
rep("  else if(d.sfmt){", "  else if(d.srf){ SETS.rushf=d.srf; SETS.sel=null; SETS.limit=80; SETS.card=null; render(); }\n  else if(d.sfmt){")
rep("<button class=\"setb\" data-setsel=\"${esc(s.n)}\"", "<button class=\"setb${fmt==='dl'&&s.kind==='set'?(s.rush?' isrush':' isspeed'):''}\" data-setsel=\"${esc(s.n)}\"")
rep("<span class=\"schips\"><i>${fmt==='tcg'?esc(", "<span class=\"schips\">${fmt==='dl'&&s.kind==='set'?`<i class=\"mk ${s.rush?'rk':'sk'}\">${s.rush?'Rush':'Speed'}</i>`:''}<i>${fmt==='tcg'?esc(")
rep("<small>${fmt==='tcg'?'Expansión del TCG':esc(KIND_ES[sel.kind]||'')}</small><h3>${esc(sel.n)}</h3></div></div>`}",
    "<small>${fmt==='tcg'?'Expansión del TCG':esc(KIND_ES[sel.kind]||'')+(fmt==='dl'&&sel.kind==='set'?(sel.rush?' · Rush Duel':' · Speed Duel'):'')}</small><h3>${esc(sel.n)}</h3></div></div>`}")
rep(".fmtbar{margin:var(--s4) 0 0}", """.fmtbar{margin:var(--s4) 0 0}
/* Speed Duel (azul) y Rush Duel (naranja) */
.setb.isspeed{--sc:#4aa8ff}.setb.isrush{--sc:#ff9d2e}
.setb.isspeed,.setb.isrush{border-left:3px solid var(--sc)}
.mk{font-weight:700;letter-spacing:.04em;text-transform:uppercase;font-size:.62rem!important}
.mk.sk{color:#4aa8ff!important;border-color:color-mix(in srgb,#4aa8ff 55%,transparent)!important;background:color-mix(in srgb,#4aa8ff 12%,transparent)}
.mk.rk{color:#ff9d2e!important;border-color:color-mix(in srgb,#ff9d2e 55%,transparent)!important;background:color-mix(in srgb,#ff9d2e 12%,transparent)}
.seg button.sk[aria-pressed="true"]{background:#4aa8ff;color:#06122a}
.seg button.rk[aria-pressed="true"]{background:#ff9d2e;color:#2a1400}""")

# ---------- 3) sin selector de rareza si hay una sola ----------
a = s.index("<label class=\"sr\" for=\"srf\">Rareza</label>")
b = s.index("</select>", a) + len("</select>")
old = s[a:b]
s = s[:a] + "${rarList.length>1?`" + old + "`:''}" + s[b:]
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 33 ok')

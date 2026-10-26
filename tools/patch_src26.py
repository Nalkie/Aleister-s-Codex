"""Tickets: se saca la pestaña Tickets (ya existía "Cajas y sets > Duel Links > Otras vías") y los Dream UR / SR, los tickets farmeables y los demás
quedan ahí. El ícono del Dream Ticket lleva la cabeza del dragón blanco como en el juego (letras claras en Speed, naranjas en Rush).
Backup: src.before_patch26.html."""
import re, shutil
shutil.copy('src.html', 'src.before_patch26.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- quitar la pestaña Tickets ----------
a = s.index('\n    <button class="tool" role="tab" id="tab-tk"')
b = s.index('</button>', a) + len('</button>')
s = s[:a] + s[b:]
rep(",tk:['Tickets',viewTickets]};", "};")
rep("'ev','tk'].includes(mode)", "'ev'].includes(mode)")
a = s.index("  else if(d.tkk){")
b = s.index("  else if(d.evfmt){")
s = s[:a] + s[b:]
rep("  else if(id==='tkq'){ TK.q=e.target.value; TK.limit=80; render('tkq'); }\n", "")
a = s.index("/* ---------- TICKETS ---------- */")
b = s.index("/* ---------- BANLIST ---------- */")
s = s[:a] + s[b:]
a = s.index(".tkhead{display:flex")
b = s.index(".tkgal{grid-template-columns")
b = s.index("\n", b) + 1
s = s[:a] + s[b:]

# ---------- ícono: cabeza de dragón en los Dream Tickets ----------
a = s.index("function tkSvg(kind,label,stars){")
b = s.index("const TICKET = [")
new_svg = r'''const DRAGON={ok:false};   // si existe art/ticket-dragon.png (PNG sin fondo de la cabeza del dragón) los Dream Tickets lo usan; si no, el dibujo propio
(()=>{ try{ const i=new Image(); i.onload=()=>{ DRAGON.ok=true; if(typeof render==='function'&&typeof mode!=='undefined'&&mode==='sets') render(); }; i.src='art/ticket-dragon.png'; }catch(e){} })();
function tkSvg(kind,label,stars,o={}){   // o.dragon: cabeza del dragón blanco (Dream Tickets) · o.ink: color de las letras
  const g=TKKIND[kind]||TKKIND.gen, uid=(tkSvg.n=(tkSvg.n||0)+1), id='tk'+uid, gid='tkg'+uid, big=label.length<=2, st=[[104,16],[104,31]].slice(0,stars||0), ink=o.ink||'#fff';
  const star=(x,y)=>`<polygon points="${x},${y-8} ${x+2.4},${y-2.6} ${x+8},${y-2.2} ${x+3.7},${y+1.6} ${x+5},${y+7.4} ${x},${y+4.2} ${x-5},${y+7.4} ${x-3.7},${y+1.6} ${x-8},${y-2.2} ${x-2.4},${y-2.6}" fill="#ffd54a" stroke="#a8620a" stroke-width="1.3" stroke-linejoin="round"/>`;
  const tx=o.dragon?89:stars?54:60, ty=o.dragon?44:big?40:38, cid='tkc'+uid, did='tkd'+uid;
  const dragonImg=`<g clip-path="url(#${cid})"><image href="art/ticket-dragon.png" x="9" y="12" width="68" height="38" preserveAspectRatio="xMidYMid meet" style="filter:drop-shadow(0 0 1.2px rgba(255,255,255,.9))"/></g>`;
  const dragon=`<g clip-path="url(#${cid})"><g transform="translate(5 12) scale(1.02)"><path d="M0 15C8 10 14 6 24 4C32 2 40 -1 54 -2L46 5L58 4L48 10L60 12L46 16C50 24 56 32 62 42L34 42C34 36 30 31 26 29C20 29 12 28 5 27L2 24C9 22 15 20 22 19C14 18 8 17 0 15Z" fill="url(#${did})" stroke="#14295a" stroke-width="1.5" stroke-linejoin="round"/><path d="M5 27C12 28 20 29 26 29C30 31 34 36 34 42L62 42C56 32 50 24 46 16C40 24 30 24 22 19C15 20 9 22 2 24Z" fill="#4f82d8" opacity=".4"/><path d="M30 6C38 3 46 1 52 -1M32 9C40 7 48 6 56 5M24 4C28 9 34 12 42 14" fill="none" stroke="#14295a" stroke-width="1" opacity=".7"/><ellipse cx="21" cy="10" rx="3" ry="1.7" transform="rotate(-18 21 10)" fill="#d8f1ff" stroke="#0a1e5a" stroke-width=".8"/><circle cx="21.5" cy="10" r=".9" fill="#0a1e5a"/><path d="M3 15.5L5 19.5L7 16.2M8 16.4L10 20.5L12 17M13 17.2L15 21L17 17.6M4 23.6L6 20.6L8 22.8M10 22L12 19L14 21.4M16 21L18 18.6L20 20.2" fill="#fff" stroke="#14295a" stroke-width=".8" stroke-linejoin="round"/></g></g>`;
  return `<svg viewBox="0 0 120 64" role="img" aria-label="Ticket ${esc(label)}"><defs>
    <linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${g[0]}"/><stop offset=".55" stop-color="${g[1]}"/><stop offset="1" stop-color="${g[2]}"/></linearGradient>
    <clipPath id="${cid}"><rect x="10" y="14" width="100" height="34" rx="5"/></clipPath><linearGradient id="${did}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#e3eaf8"/><stop offset="1" stop-color="#b9c7e6"/></linearGradient><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe28a"/><stop offset=".5" stop-color="#d8932a"/><stop offset="1" stop-color="#9a5a10"/></linearGradient></defs>
    <g transform="translate(60 33) rotate(-4) skewX(-5) translate(-60 -33)">
      <rect x="6" y="12" width="108" height="42" rx="8" fill="rgba(0,0,0,.35)" transform="translate(2 4)"/>
      <rect x="6" y="10" width="108" height="42" rx="8" fill="url(#${gid})"/>
      <rect x="10" y="14" width="100" height="34" rx="5" fill="url(#${id})"/>
      <g fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="1"><path d="M84 14l8 4v8l-8 4-8-4v-8zM100 28l8 4v8l-8 4-8-4v-8z"/><path d="M10 44l30-30"/></g>
      <path d="M10 14h100v7L10 40z" fill="#fff" opacity=".13"/>
      ${o.dragon?(DRAGON.ok?dragonImg:dragon):''}
      <text x="${tx}" y="${ty}" text-anchor="middle" font-family="Unbounded,Arial Black,sans-serif" font-weight="800" font-size="${o.dragon?27:big?25:label.length>3?13:17}" fill="${ink}" stroke="rgba(60,30,0,.55)" stroke-width="2.4" paint-order="stroke" stroke-linejoin="round">${esc(label)}</text>
      ${st.map(([x,y])=>star(x,y)).join('')}
    </g></svg>`;
}
'''
s = s[:a] + new_svg + s[b:]
rep("const TICKET = [   // [expresión del nombre de la fuente, tipo, texto, estrellas]\n  [/UR Tickets/,'UR','UR',0],",
    "const TICKET = [   // [expresión del nombre de la fuente, tipo, texto, estrellas, es Dream]\n  [/^Dream UR/,'URD','UR',1,1],[/^Dream SR/,'SRD','SR',0,1],[/^UR Ticket/,'UR','UR',0],[/^SR Ticket/,'SR','SR',0],[/^R Ticket/,'R','R',0],\n  [/UR Tickets/,'UR','UR',0],")
rep("function ticketIcon(name){\n  const t=TICKET.find(x=>x[0].test(name))||[0,'gen','✦',0];\n  return tkSvg(t[1],t[2],t[3]);\n}",
    "function ticketIcon(name,rush){\n  const t=TICKET.find(x=>x[0].test(name))||[0,'gen','✦',0];\n  return tkSvg(t[1],t[2],t[3],t[4]?{dragon:true,ink:rush?'#ff9d2e':'#fff3b0'}:{});\n}")
rep("${ticketIcon(s.n)}<img class=\"tkimg\"", "${ticketIcon(s.n,s.rush)}<img class=\"tkimg\"")
rep("  UR:['#46e6ff','#8b63ff','#ff6fd8'],", "  UR:['#46e6ff','#8b63ff','#ff6fd8'], URD:['#2fe3cf','#6a6fe0','#9a4fd8'], SRD:['#fff3a8','#ffc83a','#f19a1e'],")
rep("const TKSLUG=[[/UR Tickets/,'ur'],", "const TKSLUG=[[/^Dream UR/,'dream-ur'],[/^Dream SR/,'dream-sr'],[/^UR Ticket/,'ur'],[/^SR Ticket/,'sr'],[/^R Ticket/,'r'],[/UR Tickets/,'ur'],")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 26 ok')

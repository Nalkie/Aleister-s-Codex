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
new_svg = r'''function tkSvg(kind,label,stars,o={}){   // o.dragon: cabeza del dragón blanco (Dream Tickets) · o.ink: color de las letras
  const g=TKKIND[kind]||TKKIND.gen, uid=(tkSvg.n=(tkSvg.n||0)+1), id='tk'+uid, gid='tkg'+uid, big=label.length<=2, st=[[104,16],[104,31]].slice(0,stars||0), ink=o.ink||'#fff';
  const star=(x,y)=>`<polygon points="${x},${y-8} ${x+2.4},${y-2.6} ${x+8},${y-2.2} ${x+3.7},${y+1.6} ${x+5},${y+7.4} ${x},${y+4.2} ${x-5},${y+7.4} ${x-3.7},${y+1.6} ${x-8},${y-2.2} ${x-2.4},${y-2.6}" fill="#ffd54a" stroke="#a8620a" stroke-width="1.3" stroke-linejoin="round"/>`;
  const dragon=`<g transform="translate(13 15) scale(.92)"><path d="M1 19 L9 11 L19 8 L25 3 L35 0 L31 8 L38 6 L32 15 L35 23 L26 24 L21 31 L12 27 L5 25 L2 22 L9 20 Z" fill="#f4f7ff" stroke="#44506e" stroke-width="1.4" stroke-linejoin="round"/><path d="M9 20 L14 16 L21 17 M12 27 L14 23 M6 24 L7 21" fill="none" stroke="#44506e" stroke-width="1.1" stroke-linecap="round"/><circle cx="18" cy="13" r="2" fill="#2a77ff"/><path d="M4 21 L6 25 L8 21 Z M10 21 L12 26 L14 21 Z" fill="#fff" stroke="#44506e" stroke-width=".8"/></g>`;
  const tx=o.dragon?72:stars?54:60;
  return `<svg viewBox="0 0 120 64" role="img" aria-label="Ticket ${esc(label)}"><defs>
    <linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${g[0]}"/><stop offset=".55" stop-color="${g[1]}"/><stop offset="1" stop-color="${g[2]}"/></linearGradient>
    <linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe28a"/><stop offset=".5" stop-color="#d8932a"/><stop offset="1" stop-color="#9a5a10"/></linearGradient></defs>
    <g transform="translate(60 33) rotate(-4) skewX(-5) translate(-60 -33)">
      <rect x="6" y="12" width="108" height="42" rx="8" fill="rgba(0,0,0,.35)" transform="translate(2 4)"/>
      <rect x="6" y="10" width="108" height="42" rx="8" fill="url(#${gid})"/>
      <rect x="10" y="14" width="100" height="34" rx="5" fill="url(#${id})"/>
      <g fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="1"><path d="M84 14l8 4v8l-8 4-8-4v-8zM100 28l8 4v8l-8 4-8-4v-8z"/><path d="M10 44l30-30"/></g>
      <path d="M10 14h100v7L10 40z" fill="#fff" opacity=".13"/>
      ${o.dragon?dragon:''}
      <text x="${tx}" y="${big?40:38}" text-anchor="middle" font-family="Unbounded,Arial Black,sans-serif" font-weight="800" font-size="${big?25:label.length>3?13:17}" fill="${ink}" stroke="rgba(60,30,0,.55)" stroke-width="2.4" paint-order="stroke" stroke-linejoin="round">${esc(label)}</text>
      ${st.map(([x,y])=>star(x,y)).join('')}
    </g></svg>`;
}
'''
s = s[:a] + new_svg + s[b:]
rep("const TICKET = [   // [expresión del nombre de la fuente, tipo, texto, estrellas]\n  [/UR Tickets/,'UR','UR',0],",
    "const TICKET = [   // [expresión del nombre de la fuente, tipo, texto, estrellas, es Dream]\n  [/^Dream UR/,'UR','UR',1,1],[/^Dream SR/,'SR','SR',1,1],[/^UR Ticket/,'UR','UR',0],[/^SR Ticket/,'SR','SR',0],[/^R Ticket/,'R','R',0],\n  [/UR Tickets/,'UR','UR',0],")
rep("function ticketIcon(name){\n  const t=TICKET.find(x=>x[0].test(name))||[0,'gen','✦',0];\n  return tkSvg(t[1],t[2],t[3]);\n}",
    "function ticketIcon(name,rush){\n  const t=TICKET.find(x=>x[0].test(name))||[0,'gen','✦',0];\n  return tkSvg(t[1],t[2],t[3],t[4]?{dragon:true,ink:rush?'#ff9d2e':'#fff3b0'}:{});\n}")
rep("${ticketIcon(s.n)}<img class=\"tkimg\"", "${ticketIcon(s.n,s.rush)}<img class=\"tkimg\"")
rep("const TKSLUG=[[/UR Tickets/,'ur'],", "const TKSLUG=[[/^Dream UR/,'dream-ur'],[/^Dream SR/,'dream-sr'],[/^UR Ticket/,'ur'],[/^SR Ticket/,'sr'],[/^R Ticket/,'r'],[/UR Tickets/,'ur'],")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 26 ok')

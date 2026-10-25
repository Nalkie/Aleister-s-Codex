"""Tickets: ícono parecido al del juego (marco dorado, degradé por rareza, letras grandes, estrellas), también usable para los Dream Tickets.
tkSvg(kind, label, stars) dibuja uno; ticketIcon(nombre) elige el tipo según el nombre de la fuente. Backup: src.before_patch23.html."""
import re, shutil
shutil.copy('src.html', 'src.before_patch23.html')
s = open('src.html', encoding='utf-8').read()
a = s.index("const TICKET = [")
b = s.index("const TKSLUG=")
new = r'''/* tickets: ícono propio con el aspecto del juego (marco dorado, degradé por rareza, letras con contorno, estrellas) */
const TKKIND = {   // degradé del interior por rareza o categoría
  UR:['#46e6ff','#8b63ff','#ff6fd8'], SR:['#fff0a0','#f7b32a','#ffd75a'], R:['#8cc0ff','#3a6ee0','#6aa5ff'], N:['#ffffff','#c3cbe0','#eef1fa'],
  gift:['#a6f7c8','#35bd78','#7be9a8'], trader:['#8ff5e6','#25a9a2','#6fe0d3'], mission:['#ffd0a0','#e8803c','#ffb877'], special:['#ffb3df','#c75bd3','#f08ad8'], event:['#b6d0ff','#5b82e6','#8fb0ff'], gen:['#dfe4f6','#8a93b6','#c0c8e4']
};
function tkSvg(kind,label,stars){
  const g=TKKIND[kind]||TKKIND.gen, id='tk'+kind, big=label.length<=2, st=[[104,16],[104,31]].slice(0,stars||0);
  const star=(x,y)=>`<polygon points="${x},${y-8} ${x+2.4},${y-2.6} ${x+8},${y-2.2} ${x+3.7},${y+1.6} ${x+5},${y+7.4} ${x},${y+4.2} ${x-5},${y+7.4} ${x-3.7},${y+1.6} ${x-8},${y-2.2} ${x-2.4},${y-2.6}" fill="#ffd54a" stroke="#a8620a" stroke-width="1.3" stroke-linejoin="round"/>`;
  return `<svg viewBox="0 0 120 64" role="img" aria-label="Ticket ${esc(label)}"><defs>
    <linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${g[0]}"/><stop offset=".55" stop-color="${g[1]}"/><stop offset="1" stop-color="${g[2]}"/></linearGradient>
    <linearGradient id="tkgold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe28a"/><stop offset=".5" stop-color="#d8932a"/><stop offset="1" stop-color="#9a5a10"/></linearGradient></defs>
    <g transform="translate(60 33) rotate(-4) skewX(-5) translate(-60 -33)">
      <rect x="6" y="12" width="108" height="42" rx="8" fill="rgba(0,0,0,.35)" transform="translate(2 4)"/>
      <rect x="6" y="10" width="108" height="42" rx="8" fill="url(#tkgold)"/>
      <rect x="10" y="14" width="100" height="34" rx="5" fill="url(#${id})"/>
      <g fill="none" stroke="#fff" stroke-opacity=".22" stroke-width="1"><path d="M84 14l8 4v8l-8 4-8-4v-8zM100 28l8 4v8l-8 4-8-4v-8z"/><path d="M10 44l30-30"/></g>
      <path d="M10 14h100v7L10 40z" fill="#fff" opacity=".13"/>
      <text x="${stars?54:60}" y="${big?40:38}" text-anchor="middle" font-family="Unbounded,Arial Black,sans-serif" font-weight="800" font-size="${big?25:label.length>3?13:17}" fill="#fff" stroke="rgba(60,30,0,.55)" stroke-width="2.4" paint-order="stroke" stroke-linejoin="round">${esc(label)}</text>
      ${st.map(([x,y])=>star(x,y)).join('')}
    </g></svg>`;
}
const TICKET = [   // [expresión del nombre de la fuente, tipo, texto, estrellas]
  [/UR Tickets/,'UR','UR',0],[/SR Tickets/,'SR','SR',0],[/Acquirable with Tickets/,'N','N·R',0],
  [/Ranked/,'R','R',0],[/Anniversary/,'SR','1º',1],[/Gift|Campaign/,'gift','🎁',0],
  [/Card Trader/,'trader','⇄',0],[/Mission|Bingo|Lifetime/,'mission','✔',0],[/Special Set/,'special','★',1],[/Event|Tournament|Grand Prix|Scramble|Quest|Chronicles|Carnival|Circuit/,'event','⚑',0]
];
function ticketIcon(name){
  const t=TICKET.find(x=>x[0].test(name))||[0,'gen','✦',0];
  return tkSvg(t[1],t[2],t[3]);
}
'''
s = s[:a] + new + s[b:]
# css: tickets are wider than before
assert s.count(".spack.tk{width:96px;max-width:40%}") == 1
s = s.replace(".spack.tk{width:96px;max-width:40%}",
              ".spack.tk{width:112px;max-width:44%}\n.sgrid .setb:has(.spack.tk) .stxt{max-width:calc(100% - 124px)}\n.setb .spack.tk{right:6px}")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 23 ok')

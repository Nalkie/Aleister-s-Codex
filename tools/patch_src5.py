"""Identity pass: new style system (tools/style.css), mode portals + tool pills instead of tabs, live stats in the portals.
Run once from build/ (backs src.html up first)."""
import re, shutil

shutil.copy('src.html', 'src.before_patch5.html')
s = open('src.html', encoding='utf-8').read()
css = open('tools/style.css', encoding='utf-8').read()
css = css.replace('.hero .in > *{max-width:min(100%,58ch)}', '.hero .in > :not(.circle){max-width:min(100%,58ch)}').replace('.hero .in > *{max-width:100%}', '.hero .in > :not(.circle){max-width:100%}')


def sub1(pattern, repl, flags=re.S):
    global s
    s, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    assert n == 1, pattern[:70]


sub1(r'<style>.*?</style>', '<style>\n' + css + '</style>')
sub1(r'<link rel="stylesheet" href="https://fonts.googleapis.com/css2\?[^"]*">',
     '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700;800&family=Figtree:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">')
sub1(r'<p class="sub">.*?</p>', '<p class="sub">Qué se juega hoy en el TCG, en Genesys y en Duel Links: mazos reales, cartas, banlist y cómo conseguir cada una. Todo sale de datos de torneos y se actualiza solo.</p>')

NAV = '''<div class="dock" id="dock">
  <nav class="modes" role="tablist" aria-label="Modo de juego">
    <button class="mode" role="tab" id="tab-tcg" data-mode="tcg" style="--mc:var(--ac-tcg)">
      <svg class="glyph" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="20"/><path d="M24 8 L37.9 32 L10.1 16 L24 40 L37.9 16 L10.1 32 Z"/></svg>
      <span class="mtxt"><b>TCG</b><small>Yu-Gi-Oh! Advanced</small></span><span class="mstat" id="st-tcg"></span></button>
    <button class="mode" role="tab" id="tab-gen" data-mode="gen" style="--mc:var(--ac-gen)">
      <svg class="glyph" viewBox="0 0 48 48" aria-hidden="true"><path d="M24 4 L41 14 V34 L24 44 L7 34 V14 Z"/><path d="M24 24 V4 M24 24 L41 34 M24 24 L7 34"/><circle cx="24" cy="24" r="3.5" fill="currentColor"/></svg>
      <span class="mtxt"><b>Genesys</b><small>Formato por puntos</small></span><span class="mstat" id="st-gen"></span></button>
    <button class="mode" role="tab" id="tab-dl" data-mode="dl" style="--mc:var(--ac-dl)">
      <svg class="glyph" viewBox="0 0 48 48" aria-hidden="true"><rect x="13" y="5" width="22" height="38" rx="6"/><path d="M26 15 L19 26 H25 L22 35"/><path d="M21 40 H27"/></svg>
      <span class="mtxt"><b>Duel Links</b><small>Speed y Rush Duel</small></span><span class="mstat" id="st-dl"></span></button>
  </nav>
  <nav class="tools" role="tablist" aria-label="Herramientas">
    <button class="tool" role="tab" id="tab-ex" data-mode="ex"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20 L16 16"/></svg>Buscador de cartas</button>
    <button class="tool" role="tab" id="tab-sets" data-mode="sets"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 L20 7.5 V16.5 L12 21 L4 16.5 V7.5 Z"/><path d="M12 12 L20 7.5 M12 12 V21 M12 12 L4 7.5"/></svg>Cajas y sets</button>
    <button class="tool" role="tab" id="tab-ban" data-mode="ban"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M5.6 5.6 L18.4 18.4"/></svg>Banlist</button>
  </nav>
</div>'''
sub1(r'<nav role="tablist" aria-label="Sección">.*?</nav>', NAV)

# live stats and compact dock, before the first render
sub1(r"const h=location\.hash\.slice\(1\); if\(MODES\[h\]\) mode=h;",
     r'''(()=>{
  const top=a=>a.filter(d=>!d.out).sort((x,y)=>y.share-x.share)[0];
  const put=(id,d,total)=>{ const el=$('#'+id); if(el&&d) el.textContent=`${total} decks · ${d.n} ${fmt(d.share)}`; };
  put('st-tcg',top(TCG_DECKS),YGM.tcg.total); put('st-gen',top(GEN_DECKS),YGM.gen.total); put('st-dl',top(DL_SPEED),DLD.speed.total);
  const dock=$('#dock'); const onScroll=()=>dock.classList.toggle('compact',window.scrollY>240);
  window.addEventListener('scroll',onScroll,{passive:true}); onScroll();
})();
const h=location.hash.slice(1); if(MODES[h]) mode=h;''')
open('src.html', 'w', encoding='utf-8').write(s)
print('patched', len(s))

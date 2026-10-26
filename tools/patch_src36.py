"""Vista previa al compartir el link (Discord, WhatsApp, Telegram, X): etiquetas Open Graph y Twitter con la imagen art/og.jpg (tools/og_image.py).
La URL de la imagen es absoluta porque los buscadores de previews no resuelven rutas relativas; SITE se cambia aquí si el dominio cambia. Backup: src.before_patch36.html."""
import shutil
shutil.copy('src.html', 'src.before_patch36.html')
s = open('src.html', encoding='utf-8').read()
SITE = 'https://aleisters-codex.pages.dev'
TITLE = "Aleister's Codex · El meta de Yu-Gi-Oh!"
DESC = 'Mazos reales, cartas, banlist y precios del TCG, OCG, Genesys y Duel Links. Cómo conseguir cada carta, tickets y cartas recomendadas para empezar.'
tags = f'''<meta name="description" content="{DESC}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Aleister's Codex">
<meta property="og:locale" content="es_AR">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:image" content="{SITE}/art/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Aleister's Codex: el meta de Yu-Gi-Oh! al día con TCG, OCG, Genesys y Duel Links">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{SITE}/art/og.jpg">
'''
a = '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
assert s.count(a) == 1
s = s.replace(a, a + tags)
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 36 ok')

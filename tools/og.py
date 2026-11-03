"""Vista previa (Open Graph) de cada mazo de la ruleta: al pegar el enlace de un mazo en Discord, WhatsApp, Telegram o X sale una tarjeta con la cara del duelista, el nombre del mazo y la serie.
Desde la raíz del proyecto:  python tools/og.py        (sin red salvo para bajar los retratos de Duel Links Meta una vez; se guardan en raw/og_faces/)

Los rastreadores de enlaces no ejecutan JavaScript, así que `?mode=roulette&deck=...` siempre mostraría la tarjeta general del sitio.  Por eso cada mazo tiene una página propia,
r/<id>.html, que solo trae las etiquetas og:/twitter: de ese mazo y lleva a la persona a la página real (<meta refresh> + JS); la imagen de la tarjeta es og/<id>.jpg (1200x630).
La página de la ruleta comparte ese enlace (rouShareUrl).  Mismo insumo, mismo resultado.  Salida: r/ y og/ (los lista files.json y los sube dist.py)."""
import html, json, os, re, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://aleisters-codex.pages.dev'
W, H = 1200, 630
SER = {'dm': ('Duel Monsters', (212, 98, 31)), 'gx': ('GX', (16, 147, 94)), '5d': ("5D's", (10, 143, 184)), 'zx': ('ZEXAL', (122, 73, 214)),
       'av': ('ARC-V', (214, 62, 120)), 'vr': ('VRAINS', (224, 176, 32))}
BG = (7, 10, 28)
FACE_ROW = (124, 146, 62, 64, 54)       # el retrato de Duel Links Meta: ancho, alto, centro y radio del círculo (igual que ROU_FACE de la página)
CACHE = os.path.join('raw', 'og_faces')


def load_decks():
    t = open(os.path.join(ROOT, 'data/roulette.js'), encoding='utf-8').read()
    return json.loads(t[t.index('{'):t.rindex(')')])['decks']


def font(size, bold=True):
    for f in ('segoeuib.ttf' if bold else 'segoeui.ttf', 'arialbd.ttf' if bold else 'arial.ttf', 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def face_image(d):
    """RGBA cuadrado con la cara del duelista (recortada al círculo seguro) o None si no hay retrato."""
    p = d.get('face')
    if not p:
        return None
    try:
        if p.startswith('data/'):
            return Image.open(os.path.join(ROOT, p)).convert('RGBA')
        os.makedirs(os.path.join(ROOT, CACHE), exist_ok=True)
        f = os.path.join(ROOT, CACHE, re.sub(r'[^a-z0-9]+', '-', p.lower()).strip('-') + '.img')
        if not os.path.exists(f):
            u = 'https://s3.duellinksmeta.com' + '/'.join(urllib.parse.quote(x) for x in p.split('/'))
            open(f, 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'AleistersCodex/1.0'}), timeout=30).read())
        im = Image.open(f).convert('RGBA')
        w, h, cx, cy, r = FACE_ROW
        k = im.size[0] / w
        return im.crop((round((cx - r) * k), round((cy - r) * k), round((cx + r) * k), round((cy + r) * k)))
    except Exception:
        return None


def fit(draw, text, size, max_w, bold=True, min_size=30):
    while size > min_size and draw.textlength(text, font=font(size, bold)) > max_w:
        size -= 2
    return font(size, bold)


def wrap(draw, text, f, max_w, lines):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=f) <= max_w:
            cur = t
        else:
            out.append(cur)
            cur = w
    out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1].rstrip('., ') + '…'
    return out


def card_image(d):
    """RGB 1200x630 de la tarjeta de un mazo."""
    name, col = SER.get(d['series'], ('', (80, 90, 140)))
    glow = Image.new('RGB', (W, H), BG)
    ImageDraw.Draw(glow).ellipse((-200, -200, 760, 760), fill=tuple(int(c * .55) for c in col))
    img = Image.blend(Image.new('RGB', (W, H), BG), glow.filter(ImageFilter.GaussianBlur(160)), .85)
    dr = ImageDraw.Draw(img)
    dr.rectangle((0, 0, 14, H), fill=col)
    cx, cy, R = 300, 315, 205
    dr.ellipse((cx - R - 12, cy - R - 12, cx + R + 12, cy + R + 12), fill=col)
    dr.ellipse((cx - R - 4, cy - R - 4, cx + R + 4, cy + R + 4), fill=BG)
    fa = face_image(d)
    disc = Image.new('RGBA', (R * 2, R * 2), tuple(int(c * .45) for c in col) + (255,))
    if fa:
        disc.alpha_composite(fa.resize((R * 2, R * 2), Image.LANCZOS))
    else:
        mono = ''.join(w[0] for w in d['character'].split()[:2]).upper()
        ImageDraw.Draw(disc).text((R, R), mono, font=font(150), fill=(255, 255, 255, 235), anchor='mm')
    mask = Image.new('L', (R * 2, R * 2), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, R * 2 - 1, R * 2 - 1), fill=255)
    img.paste(disc.convert('RGB'), (cx - R, cy - R), mask)
    x = 560
    dr = ImageDraw.Draw(img)
    accent = col if sum(col) > 250 else (150, 170, 255)
    dr.text((x, 92), ('RULETA DE DECKS · ' + name).upper(), font=font(26), fill=accent)
    dr.text((x, 150), d['character'], font=fit(dr, d['character'], 92, W - x - 60), fill=(238, 241, 255))
    f2, y = font(46), 270
    for ln in wrap(dr, d['name'], f2, W - x - 60, 2):
        dr.text((x, y), ln, font=f2, fill=(255, 255, 255))
        y += 58
    arc = d.get('arc') or ''
    if arc and not re.fullmatch(r'(?i)decks?', arc.strip()):
        dr.text((x, y + 6), arc, font=font(32, False), fill=(154, 164, 214))
    tag = 'Mazo temático' if d.get('kind') == 'thematic' else '%d%% del mazo del anime' % d.get('anime', 0)
    n = sum(c for _, c, _ in d['main'])
    line = '%s · %d cartas del TCG' % (tag.replace(' del mazo del anime', ' del anime'), n)
    dr.text((x, 470), line, font=fit(dr, line, 30, W - x - 50, False, 20), fill=(200, 208, 240))
    dr.text((x, 548), "Aleister's Codex", font=font(34), fill=accent)
    return img


def page(d):
    url = '%s/r/%s.html' % (SITE, d['id'])
    title = '%s · %s · Ruleta de decks' % (d['character'], d['name'])
    ser = SER.get(d['series'], ('', None))[0]
    desc = (d.get('blurb') or '').strip() or 'Mazo de %s en la ruleta de decks.' % d['character']
    desc = ('%s (%s). %s' % (d['character'], ser, desc) if ser else desc)[:300]
    img = '%s/og/%s.jpg' % (SITE, d['id'])
    go = '../?mode=roulette&deck=' + urllib.parse.quote(d['id'])
    e = html.escape
    return f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Aleister's Codex"><meta property="og:locale" content="es_AR">
<meta property="og:url" content="{e(url)}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(img)}"><meta property="og:image:width" content="{W}"><meta property="og:image:height" content="{H}"><meta property="og:image:alt" content="{e(d['character'])}: {e(d['name'])}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{e(img)}">
<meta http-equiv="refresh" content="0;url={e(go)}">
<style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#070a1c;color:#eef1ff;font:16px system-ui,sans-serif}}a{{color:#4ee1ff}}</style>
</head><body><p>Abriendo <a href="{e(go)}">{e(d['character'])} · {e(d['name'])}</a>…</p><script>location.replace({json.dumps(go)}+location.hash)</script></body></html>
'''


def build(decks=None, root=None):
    root = root or ROOT
    decks = decks if decks is not None else load_decks()
    os.makedirs(os.path.join(root, 'r'), exist_ok=True)
    os.makedirs(os.path.join(root, 'og'), exist_ok=True)
    keep_r, keep_o = set(), set()
    for d in decks:
        open(os.path.join(root, 'r', d['id'] + '.html'), 'w', encoding='utf-8').write(page(d))
        card_image(d).save(os.path.join(root, 'og', d['id'] + '.jpg'), 'JPEG', quality=84, optimize=True)
        keep_r.add(d['id'] + '.html')
        keep_o.add(d['id'] + '.jpg')
    for sub, keep in (('r', keep_r), ('og', keep_o)):       # un mazo que ya no existe no deja página ni imagen
        for f in os.listdir(os.path.join(root, sub)):
            if f not in keep:
                os.remove(os.path.join(root, sub, f))
    return len(decks)


if __name__ == '__main__':
    os.chdir(ROOT)
    print('r/ y og/: %d mazos' % build())

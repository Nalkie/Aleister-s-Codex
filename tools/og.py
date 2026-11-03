"""Vista previa (Open Graph) de cada mazo de la ruleta: al pegar el enlace de un mazo en Discord, WhatsApp, Telegram o X sale una tarjeta con la cara del duelista, el nombre del mazo y la serie.
Desde la raíz del proyecto:  python tools/og.py        (sin red salvo para bajar los retratos de Duel Links Meta una vez; se guardan en raw/og_faces/)

La tarjeta muestra el mazo: la cara del duelista en chico, su nombre y el nombre del mazo, y debajo el Main Deck completo, una carta por cada copia (40 a 60), en el orden de la lista (monstruos, magias, trampas), y el Extra Deck en filas aparte con un borde de color.  Las imágenes
de las cartas se bajan una vez de YGOPRODeck y se guardan en raw/og_cards/; sin red se dibuja el dorso para que la tarjeta siga saliendo.

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
CARD_CACHE = os.path.join('raw', 'og_cards')
ASPECT, GAP, SEP, LAB, AREA = 0.686, 5, 12, 20, (30, 190, 1170, 622)      # las cartas de abajo: proporción de la carta, separación y la franja (x0, y0, x1, y1) donde se reparten
_ids = {}


def card_id(name):
    """El id de YGOPRODeck de una carta por su nombre (src/ygo_all.json), o None."""
    if not _ids:
        for c in json.load(open(os.path.join(ROOT, 'src/ygo_all.json'), encoding='utf-8')):
            _ids[c['name']] = c['id']
    return _ids.get(name)


def pick_cards(d):
    """Los nombres de las cartas del Main que se dibujan: todas, una por copia, en el orden de la lista (monstruos, magias, trampas)."""
    return [n for n, c, *_ in d['main'] for _ in range(c)]


def pick_extra(d):
    """Los nombres del Extra Deck, una carta por copia, en el orden de la lista."""
    return [n for n, c, *_ in d.get('extra', []) for _ in range(c)]


def balance(n, cols):
    """Tamaños de fila para repartir n cartas en filas de a lo sumo `cols`, lo más parejas posible (la última fila no queda a medias): [14, 13, 13] para 40 en 14 columnas."""
    rows = -(-n // cols)
    return [n // rows + (1 if k < n % rows else 0) for k in range(rows)] if n else []


def layout(n, ne=0, area=AREA, gap=GAP, sep=SEP, lab=LAB):
    """(columnas, ancho, alto) de la grilla que da la carta más grande para n cartas del Main y ne del Extra dentro de area.  Cada sección lleva su rótulo (lab de alto) y el Extra va
    separado del Main por sep."""
    w_all, h_all = area[2] - area[0], area[3] - area[1]
    best = None
    for cols in range(1, n + ne + 1):
        rows = len(balance(n, cols)) + len(balance(ne, cols))
        w = min((w_all - (cols - 1) * gap) / cols, (h_all - (rows - 1) * gap - lab - ((sep + lab) if ne else 0)) / rows * ASPECT)
        if best is None or w > best[1]:
            best = (cols, w)
    cols, w = best
    return cols, int(w), int(w / ASPECT)


def row_xs(m, cols, cw, x0, x1, justify=True):
    """Las x de las m cartas de una fila: repartidas de borde a borde (justificada) o, si no, en las columnas de una fila llena, desde la izquierda."""
    if m == 1 or not justify:
        pitch = (x1 - x0 - cw) / (cols - 1) if cols > 1 else 0
        return [round(x0 + k * pitch) for k in range(m)]
    return [round(x0 + k * (x1 - x0 - cw) / (m - 1)) for k in range(m)]


def card_image_file(name):
    """Imagen RGBA de la carta (cache en raw/og_cards/) o None si no hay red o no existe."""
    cid = card_id(name)
    if not cid:
        return None
    try:
        os.makedirs(os.path.join(ROOT, CARD_CACHE), exist_ok=True)
        f = os.path.join(ROOT, CARD_CACHE, '%s.jpg' % cid)
        if not os.path.exists(f):
            u = 'https://images.ygoprodeck.com/images/cards_small/%s.jpg' % cid
            open(f, 'wb').write(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'AleistersCodex/1.0'}), timeout=30).read())
        return Image.open(f).convert('RGB')
    except Exception:
        return None


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


def card_image(d, fetch=None):
    """RGB 1200x630 de la tarjeta de un mazo: cabecera con el duelista y el mazo, y debajo las cartas del Main Deck."""
    fetch = fetch or card_image_file
    name, col = SER.get(d['series'], ('', (80, 90, 140)))
    glow = Image.new('RGB', (W, H), BG)
    ImageDraw.Draw(glow).ellipse((-260, -260, 620, 560), fill=tuple(int(c * .55) for c in col))
    img = Image.blend(Image.new('RGB', (W, H), BG), glow.filter(ImageFilter.GaussianBlur(150)), .85)
    dr = ImageDraw.Draw(img)
    dr.rectangle((0, 0, 14, H), fill=col)
    cx, cy, R = 108, 108, 66
    dr.ellipse((cx - R - 7, cy - R - 7, cx + R + 7, cy + R + 7), fill=col)
    dr.ellipse((cx - R - 3, cy - R - 3, cx + R + 3, cy + R + 3), fill=BG)
    fa = face_image(d)
    disc = Image.new('RGBA', (R * 2, R * 2), tuple(int(c * .45) for c in col) + (255,))
    if fa:
        disc.alpha_composite(fa.resize((R * 2, R * 2), Image.LANCZOS))
    else:
        mono = ''.join(w[0] for w in d['character'].split()[:2]).upper()
        ImageDraw.Draw(disc).text((R, R), mono, font=font(54), fill=(255, 255, 255, 235), anchor='mm')
    mask = Image.new('L', (R * 2, R * 2), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, R * 2 - 1, R * 2 - 1), fill=255)
    img.paste(disc.convert('RGB'), (cx - R, cy - R), mask)
    x = 210
    dr = ImageDraw.Draw(img)
    accent = col if sum(col) > 250 else (150, 170, 255)
    dr.text((x, 28), ('RULETA DE DECKS · ' + name).upper(), font=font(20), fill=accent)
    dr.text((W - 40, 28), "Aleister's Codex", font=font(22), fill=accent, anchor='ra')
    dr.text((x, 56), d['character'], font=fit(dr, d['character'], 56, W - x - 40), fill=(238, 241, 255))
    f2, y = font(32), 124
    for ln in wrap(dr, d['name'], f2, W - x - 40, 1):
        dr.text((x, y), ln, font=f2, fill=(255, 255, 255))
        y += 40
    arc = d.get('arc') or ''
    tag = 'Mazo temático' if d.get('kind') == 'thematic' else '%d%% del mazo del anime' % d.get('anime', 0)
    n, ne = len(pick_cards(d)), len(pick_extra(d))
    line = ' · '.join([x for x in (arc if arc and not re.fullmatch(r'(?i)decks?', arc.strip()) else '', tag.replace(' del mazo del anime', ' del anime'), '%d Main + %d Extra' % (n, ne) if ne else '%d cartas' % n) if x])
    dr.text((x, y + 2), line, font=fit(dr, line, 22, W - x - 40, False, 16), fill=(176, 186, 230))
    main, extra = pick_cards(d), pick_extra(d)
    cols, cw, chh = layout(len(main), len(extra))
    ax0, ay0, ax1, ay1 = AREA
    sections = [('MAIN DECK', main, False)] + ([('EXTRA DECK', extra, True)] if extra else [])
    rows_n = sum(len(balance(len(c), cols)) for _, c, _ in sections)
    total = rows_n * chh + (rows_n - 1) * GAP + LAB + ((SEP + LAB) if extra else 0)
    y = ay0 + ((ay1 - ay0) - total) // 2
    lab_f, got = font(15), {}
    for si, (title, cards, is_extra) in enumerate(sections):
        if si:
            y += SEP - GAP
        text = '%s · %d' % (title, len(cards))
        dr.text((ax0, y + LAB // 2 + 1), text, font=lab_f, fill=accent, anchor='lm')
        lx = ax0 + int(dr.textlength(text, font=lab_f)) + 12
        dr.line((lx, y + LAB // 2 + 1, ax1, y + LAB // 2 + 1), fill=tuple(int(c * .55) for c in accent), width=1)
        y += LAB + GAP
        k = 0
        for m in balance(len(cards), cols):
            for px, nm in zip(row_xs(m, cols, cw, ax0, ax1, justify=not is_extra or m == cols), cards[k:k + m]):
                if nm not in got:
                    got[nm] = fetch(nm)
                ci = got[nm]
                if ci:
                    img.paste(ci.resize((cw, chh), Image.LANCZOS), (px, y))
                else:
                    dr.rounded_rectangle((px, y, px + cw, y + chh), 4, fill=tuple(int(c * .35) for c in col), outline=col, width=2)
                if is_extra:
                    dr.rectangle((px - 1, y - 1, px + cw, y + chh), outline=accent, width=2)
            k += m
            y += chh + GAP
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


def build(decks=None, root=None, fetch=None):
    root = root or ROOT
    decks = decks if decks is not None else load_decks()
    os.makedirs(os.path.join(root, 'r'), exist_ok=True)
    os.makedirs(os.path.join(root, 'og'), exist_ok=True)
    keep_r, keep_o = set(), set()
    for d in decks:
        open(os.path.join(root, 'r', d['id'] + '.html'), 'w', encoding='utf-8').write(page(d))
        card_image(d, fetch).save(os.path.join(root, 'og', d['id'] + '.jpg'), 'JPEG', quality=84, optimize=True)
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

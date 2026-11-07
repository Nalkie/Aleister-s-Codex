"""Two vivid colours of each deck's art, for the gradient behind the card in the deck rows (--k1, --k2).
The browser cannot read the pixels of the YGOPRODeck pictures (no CORS), so the colours are computed here and shipped inside the page as ARTCOL {art name: [c1, c2]}.
Read from art/<id>.jpg when the file is there, otherwise the cropped art is downloaded once; the results are cached in src/artcol.json (a name is computed once).
  python tools/artcolors.py          colours of every deck art named in the data (prints how many)
Used by tools/page_only.py and tools/build_db.py."""
import colorsys, io, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'src/artcol.json')
UA = {'User-Agent': 'Mozilla/5.0 (Aleister Codex art colours)'}
B = 12            # hue buckets


def colors_of(im):
    """[c1, c2] as '#rrggbb' from the most vivid hues of a PIL image (saturation x brightness^2 per hue bucket); None when the picture has no colour."""
    im = im.convert('RGB').resize((32, 32))
    w = [0.0] * B
    acc = [[0.0, 0.0, 0.0, 0.0] for _ in range(B)]
    for r, g, b in im.getdata():
        r, g, b = r / 255, g / 255, b / 255
        mx, mn = max(r, g, b), min(r, g, b)
        d = mx - mn
        if mx < .25 or d < .18:
            continue
        h = colorsys.rgb_to_hsv(r, g, b)[0] * 6
        k = int(h * B / 6) % B
        wt = (d / mx) * mx * mx
        w[k] += wt
        a = acc[k]
        a[0] += r * wt; a[1] += g * wt; a[2] += b * wt; a[3] += wt
    order = sorted(range(B), key=lambda k: -w[k])
    if not order or w[order[0]] <= 0:
        return None
    k1 = order[0]
    k2 = next((k for k in order if w[k] > w[k1] * .18 and min((k - k1) % B, (k1 - k) % B) >= 2), order[1])

    def col(k):
        a = acc[k]
        if not a[3]:
            return None
        m = max(a[0], a[1], a[2]) / a[3]
        f = .92 / max(m, .01)
        return '#%02x%02x%02x' % tuple(min(255, round(a[i] / a[3] * f * 255)) for i in range(3))
    c1 = col(k1)
    return [c1, col(k2) or c1]


def _ids():
    return {c['name']: c['id'] for c in json.load(open(os.path.join(ROOT, 'src/ygo_all.json'), encoding='utf-8'))}


def names_in_data():
    """Every deck art name the page can show: the art:'...' of the page and every \"art\": \"...\" of the data files (meta decks of each format, Duel Links, Master Duel)."""
    import glob
    out = set(m.group(1) for m in re.finditer(r"art:'([^']*)'", open(os.path.join(ROOT, 'src.html'), encoding='utf-8').read()))
    for pat in ('data/*.js', 'dl/*.json', 'src/*.json'):
        for f in glob.glob(os.path.join(ROOT, pat)):
            if os.path.basename(f) == 'artcol.json':
                continue
            out |= set(m.group(1) for m in re.finditer(r'"art":\s*"([^"]+)"', open(f, encoding='utf-8', errors='ignore').read()))
    return out


def cached_names():
    """Names already coloured. build_db empties data/ (the roulette is rebuilt afterwards), so names_in_data() alone misses the roulette arts at that moment; the cache does not."""
    return set(json.load(open(CACHE, encoding="utf-8"))) if os.path.exists(CACHE) else set()


def ensure(names, download=True):
    """{name: [c1, c2]} for the names that have a picture; computes (and caches) the missing ones."""
    from PIL import Image
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    ids, changed = None, False
    for n in sorted(names):
        if n in cache:
            continue
        ids = ids or _ids()
        pid = ids.get(n)
        if not pid:
            continue
        pid = str(pid)
        p = os.path.join(ROOT, 'art', pid + '.jpg')
        try:
            if os.path.exists(p):
                im = Image.open(p)
            elif download:
                with urllib.request.urlopen(urllib.request.Request('https://images.ygoprodeck.com/images/cards_cropped/%s.jpg' % pid, headers=UA), timeout=60) as r:
                    im = Image.open(io.BytesIO(r.read()))
            else:
                continue
            c = colors_of(im)
        except Exception as e:
            print('art colours: skipped', n, e)
            continue
        if c:
            cache[n] = c
            changed = True
    if changed:
        json.dump(cache, open(CACHE, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=0, sort_keys=True)
    return {n: cache[n] for n in names if n in cache}


if __name__ == '__main__':
    names = names_in_data()
    got = ensure(names)
    print('art colours: %d of %d deck arts' % (len(got), len(names)))

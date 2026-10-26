"""Preview image for links shared on Discord, WhatsApp, Telegram, X... -> art/og.jpg (1200 x 630).  Run from the project root:  python tools/og_image.py
Deterministic: a dark gradient, the title, the four formats and a fan of five deck artworks already in art/. The page points to it from its <meta property="og:image">."""
import os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630


def font(names, size):
    for n in names:
        for d in ('C:/Windows/Fonts/', '/usr/share/fonts/truetype/dejavu/', ''):
            try:
                return ImageFont.truetype(d + n, size)
            except OSError:
                pass
    return ImageFont.load_default()


def build():
    os.chdir(ROOT)
    img = Image.new('RGB', (W, H), '#080b22')
    px = img.load()
    for y in range(H):
        for x in range(W):
            t = (x / W * 0.55 + y / H * 0.45)
            px[x, y] = (int(8 + 14 * t), int(11 + 20 * t), int(34 + 58 * t))
    glow = Image.new('RGB', (W, H), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((640, -120, 1300, 540), fill=(40, 120, 200))
    g.ellipse((760, 200, 1320, 760), fill=(110, 70, 210))
    img = Image.blend(img, Image.composite(glow, img, glow.convert('L').filter(ImageFilter.GaussianBlur(140))), 0.55)
    arts = sorted(f for f in os.listdir('art') if f.endswith('.jpg') and f[:-4].isdigit())
    rnd = random.Random(7)
    pick = [arts[i] for i in sorted(rnd.sample(range(len(arts)), 5))]
    for k, f in enumerate(pick):
        a = Image.open('art/' + f).convert('RGB')
        s = 250
        a = a.resize((s, int(a.height * s / a.width)))
        mask = Image.new('L', a.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, a.width - 1, a.height - 1), 18, fill=255)
        card = Image.new('RGBA', (a.width + 12, a.height + 12), (0, 0, 0, 0))
        ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 22, fill=(255, 255, 255, 235))
        card.paste(a, (6, 6), mask)
        card = card.rotate(-14 + k * 7, expand=True, resample=Image.BICUBIC)
        shadow = Image.new('RGBA', card.size, (0, 0, 0, 0))
        shadow.paste((0, 0, 0, 160), mask=card.split()[3])
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))
        x, y = 560 + k * 118, 70 + (k % 2) * 150 + k * 18
        img.paste(shadow, (x + 8, y + 14), shadow)
        img.paste(card, (x, y), card)
    d = ImageDraw.Draw(img)
    big, mid, sm = font(['seguibl.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf'], 86), font(['segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf'], 34), font(['segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf'], 28)
    d.text((70, 150), "Aleister's", font=big, fill='#ffffff')
    d.text((70, 240), 'Codex', font=big, fill='#8fb6ff')
    d.text((72, 372), 'El meta de Yu-Gi-Oh! al día', font=mid, fill='#dfe6ff')
    d.text((72, 418), 'mazos reales · cartas · banlist · precios', font=sm, fill='#9fb0e8')
    x = 72
    for label, col in (('TCG', '#4ee1ff'), ('OCG', '#4ee1ff'), ('Genesys', '#b78bff'), ('Duel Links', '#3ddc97')):
        w = d.textlength(label, font=sm) + 40
        d.rounded_rectangle((x, 500, x + w, 552), 26, outline=col, width=3, fill=(10, 16, 48))
        d.text((x + 20, 507), label, font=sm, fill=col)
        x += w + 14
    img.save('art/og.jpg', quality=86, optimize=True)
    return img.size


if __name__ == '__main__':
    print('art/og.jpg', build(), os.path.getsize('art/og.jpg') // 1024, 'KB')

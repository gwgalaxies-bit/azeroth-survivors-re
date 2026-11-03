"""Painted battle backdrops at 960x640 (a 240x160 design grid scaled 4x): eight outdoor zones,
town, arena and nine instance halls. Smooth gradients, lit terrain, soft clouds, fog and light."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from px import Paint, brush, kuwahara, rgb, shade_col, value_noise, veins

S = 4
W, H = 240 * S, 160 * S
GY = 124  # ground line in design units
YY, XX = np.mgrid[0:H, 0:W].astype(float) / S


def C(c):
    return np.array(rgb(c), float)


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def noise(scale, seed, oct=4):
    return value_noise(W, H, scale * S, seed, oct, wrap=False)


def noise1(scale, seed, oct=4):
    return value_noise(W, 1, scale * S, seed, oct, wrap=False)[0]


def blend(arr, col, a):
    a = np.clip(a, 0, 1)[..., None]
    return arr + (C(col) - arr) * a


def sky(top, mid, horizon, y1=GY):
    t = np.clip(YY / y1, 0, 1)
    a = C(top)[None, None] * (1 - sstep(0, 0.65, t))[..., None] + C(mid)[None, None] * (sstep(0, 0.65, t) * (1 - sstep(0.55, 1, t)))[..., None] \
        + C(horizon)[None, None] * sstep(0.55, 1, t)[..., None]
    n = noise(60, 7, 3)
    return a * (0.97 + 0.06 * n[..., None])


def sun(arr, cx, cy, r, col, glow, gr, amt=0.6):
    d = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    g = np.exp(-np.maximum(0, d - r) / gr) * amt
    arr = blend(arr, glow, g)
    return blend(arr, col, sstep(r + 0.6, r - 0.6, d))


def stars(arr, n, seed, ymax=GY - 20):
    rng = np.random.default_rng(seed)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(n):
        x, y = rng.random() * W, rng.random() * ymax * S
        r = rng.choice([0.6, 0.9, 1.3, 2.0], p=[0.5, 0.3, 0.15, 0.05])
        a = int(120 + rng.random() * 135)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 235, a))
        if r >= 1.3:
            d.ellipse([x - r * 3, y - r * 3, x + r * 3, y + r * 3], fill=(200, 210, 255, 25))
    return np.array(img).astype(float)


def clouds(arr, seed, col, y0, y1, dens=0.5, shadow='#8890a8'):
    n = value_noise(W, H * 3, 46 * S, seed, 5, wrap=False)[::3, :]
    mid, half = (y0 + y1) / 2, (y1 - y0) / 2
    band = np.clip(1 - np.abs(YY - mid) / half, 0, 1) ** 0.7
    v = n * band
    a = sstep(dens, dens + 0.14, v)
    below = np.roll(a, -6 * S // 2, 0)
    lit = np.clip(a - below * 0.6, 0, 1)
    arr = blend(arr, shadow, a * 0.55)
    arr = blend(arr, col, a * (0.55 + 0.45 * (1 - below)))
    return blend(arr, '#ffffff', lit * 0.25)


def ridge(seed, base, amp, scale, sharp=False, oct=5):
    n = noise1(scale, seed, oct)
    if sharp:
        n = 1 - np.abs(n * 2 - 1)
    return base - n * amp


def mesa(seed, base, amp):
    n = noise1(55, seed, 2)
    steps = sstep(0.45, 0.5, n) * amp * 0.45 + sstep(0.56, 0.6, n) * amp * 0.55 + amp * 0.12
    return base - steps - noise1(5, seed + 5, 3) * 2.5


def terrain(arr, hts, col, seed, snow=None, fog=None, fog_amt=0.0, light=0.5, tex=0.12, dark_base=0.25):
    hts2 = hts[None, :]
    mask = YY >= hts2
    edge = sstep(-0.6, 0.6, YY - hts2)
    k = np.exp(-np.linspace(-3, 3, 6 * 3 * S + 1) ** 2 / 2)
    hs = np.convolve(np.pad(hts, len(k) // 2, mode='edge'), k / k.sum(), mode='valid')
    slope = np.gradient(hs) * S
    lit = np.clip(0.5 - slope[None, :] * 1.6 * light, 0.15, 1.1)
    depth = np.clip((YY - hts2) / 40, 0, 1)
    n = noise(6, seed, 4)
    base = C(col)
    n2 = noise(18, seed + 4, 3)
    shade = (0.78 + 0.4 * lit) * (1 - dark_base * depth) * (1 + (n - 0.5) * tex * 2 + (n2 - 0.5) * 0.12)
    layer = base[None, None] * shade[..., None]
    if snow:
        sn = sstep(6 + n * 6, 2 + n * 4, YY - hts2) * sstep(np.percentile(hts, 70), np.percentile(hts, 35), hts2)
        layer = layer + (C(snow) * (0.75 + 0.35 * lit[..., None]) - layer) * sn[..., None]
    if fog:
        layer = layer + (C(fog) - layer) * fog_amt
    a = (edge * mask)[..., None]
    return arr * (1 - a) + layer * a


def ground(arr, col, col2, seed, top=GY, path=None, grass=None):
    n = noise(5, seed, 4)
    n2 = noise(30, seed + 1, 3)
    t = np.clip((n - 0.5) * 2.2 + 0.5 + (n2 - 0.5), 0, 1)
    depth = np.clip((YY - top) / (160 - top), 0, 1)
    layer = C(col)[None, None] * (1 - t[..., None]) + C(col2)[None, None] * t[..., None]
    layer = layer * (0.78 + 0.32 * depth[..., None])
    if path:
        center = 120 + np.sin(XX / 30) * 8
        wdt = 6 + (YY - top) * 0.95
        pm = sstep(1.5, -1.5, np.abs(XX - center) - wdt + (n - 0.5) * 6) * sstep(top + 1, top + 6, YY)
        pc = C(path)[None, None] * (0.85 + 0.25 * n[..., None]) * (0.85 + 0.25 * depth[..., None])
        layer = layer + (pc - layer) * pm[..., None]
    m = sstep(top - 0.4, top + 0.4, YY)[..., None]
    arr = arr * (1 - m) + layer * m
    if grass:
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img, 'RGBA')
        rng = np.random.default_rng(seed + 9)
        g = C(grass)
        for _ in range(int(W * 3.2)):
            x = rng.random() * W
            y = top * S + rng.random() * (H - top * S) ** 0.9 * rng.random()
            hgt = (3 + rng.random() * 6) * (0.6 + (y / H))
            k = 0.7 + rng.random() * 0.6
            cc = tuple(int(v) for v in np.clip(g * k, 0, 255)) + (200,)
            d.line([(x, y), (x + rng.random() * 3 - 1.5, y - hgt)], fill=cc, width=1)
        arr = np.array(img).astype(float)
    return arr


def fog_band(arr, col, y0, y1, amt=0.45):
    mid, half = (y0 + y1) / 2, (y1 - y0) / 2
    t = np.clip(1 - np.abs(YY - mid) / half, 0, 1) ** 1.2 * amt
    t = t * (0.8 + 0.4 * noise(30, 3, 3))
    return blend(arr, col, t)


def glow(arr, x, y, r, col, amt=0.55):
    d = np.sqrt((XX - x) ** 2 + (YY - y) ** 2)
    g = np.exp(-(d / r) ** 2 * 2.2) * amt
    return arr + (C(col) - arr * 0.3) * g[..., None] * 0.9


def torch(arr, x, y, col='#ffb040', r=18):
    arr = glow(arr, x, y, r, col, 0.6)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, 'RGBA')
    X, Y = x * S, y * S
    d.rectangle([X - 2, Y + 2, X + 2, Y + 14], fill=(70, 44, 24, 255))
    d.polygon([(X - 5, Y + 3), (X + 5, Y + 3), (X, Y - 14)], fill=rgb(col) + (230,))
    d.polygon([(X - 2.5, Y + 2), (X + 2.5, Y + 2), (X, Y - 7)], fill=(255, 250, 200, 255))
    return np.array(img).astype(float)


def vignette(arr, amt=0.35):
    d = np.sqrt(((XX - 120) / 120) ** 2 + ((YY - 80) / 80) ** 2)
    f = 1 - sstep(0.6, 1.45, d) * amt
    return arr * f[..., None]


def grade(arr, warm=0.06, contrast=1.06):
    lum = arr.mean(axis=2, keepdims=True) / 255
    arr = (arr - 128) * contrast + 128
    arr = arr + np.concatenate([lum * 22 * warm * 10, lum * 10 * warm * 10, -lum * 6 * warm * 10], axis=2) * 0.1
    arr = arr + np.concatenate([-(1 - lum) * 4, -(1 - lum) * 2, (1 - lum) * 6], axis=2)
    return arr


def bloom(arr, thresh=200, amt=0.35):
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    lum = np.array(img.convert('L')).astype(float)
    m = np.clip((lum - thresh) / (255 - thresh), 0, 1)
    br = np.array(img).astype(float) * m[..., None]
    b = np.array(Image.fromarray(br.astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))).astype(float)
    return arr + b * amt


def composite(arr, img):
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    base.alpha_composite(img)
    return np.array(base)[:, :, :3].astype(float)


def props(fn, seed=0, fog=None, fog_amt=0.0, outline=None, blur=0):
    c = Paint(W, H, design=240, seed=seed, ss=1)
    fn(c)
    img = c.render(outline=outline, inner=True, rim_a=0.15, ao=0.3, out_w=0.6)
    if fog:
        a = np.array(img).astype(float)
        m = a[:, :, 3] > 0
        a[m, :3] = a[m, :3] + (C(fog) - a[m, :3]) * fog_amt
        img = Image.fromarray(a.astype(np.uint8), 'RGBA')
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    return img


# --------------------------------------------------------------------------------------------- prop kit
def pine(c, x, y, h, col, snow=None, trunk='#4a3020'):
    c.cap(x, y, x, y - h * 0.3, 1.2, 1.0, c.M(trunk))
    m = c.M(col)
    for i in range(4):
        yy = y - h * 0.2 - i * h * 0.19
        w = h * (0.36 - i * 0.07)
        c.poly([(x - w, yy), (x - w * 0.3, yy - h * 0.08), (x + w * 0.3, yy - h * 0.06), (x + w, yy), (x, yy - h * 0.36)], m, shade=0.55, grad=0.55, gdir=(1, 0.4), tex=0.25)
        if snow:
            c.poly([(x - w * 0.55, yy - h * 0.16), (x + w * 0.15, yy - h * 0.2), (x, yy - h * 0.36)], c.M(snow), shade=0.85, edge=False)


def oak(c, x, y, h, col, trunk='#5a3c24'):
    c.cap(x, y, x + 1, y - h * 0.55, 2.2, 1.4, c.M(trunk), tex=0.3)
    c.cap(x + 0.5, y - h * 0.45, x - h * 0.15, y - h * 0.62, 0.9, 0.5, c.M(trunk))
    c.cap(x + 0.5, y - h * 0.48, x + h * 0.18, y - h * 0.64, 0.9, 0.5, c.M(trunk))
    m = c.M(col)
    m2 = c.M(shade_col(col, 0.75))
    for (dx, dy, r) in [(-0.3, -0.58, 0.26), (0.3, -0.6, 0.26), (0.02, -0.66, 0.3), (-0.12, -0.8, 0.24), (0.18, -0.82, 0.22)]:
        c.ell(x + dx * h, y + dy * h + 2, r * h, r * h * 0.82, m2, tex=0.5)
    for (dx, dy, r) in [(-0.28, -0.62, 0.22), (0.28, -0.64, 0.2), (0.0, -0.74, 0.26), (-0.1, -0.86, 0.18), (0.16, -0.88, 0.16)]:
        c.ell(x + dx * h - 1, y + dy * h, r * h, r * h * 0.8, m, tex=0.55)


def dead_tree(c, x, y, h, col='#2a2228'):
    m = c.M(col)
    c.cap(x, y, x, y - h * 0.6, 2.2, 1.0, m, tex=0.3)
    rng = c.rng
    for i in range(5):
        sy = y - h * (0.3 + i * 0.1)
        d = -1 if i % 2 else 1
        c.chain([(x, sy), (x + d * h * 0.18, sy - h * 0.12), (x + d * h * 0.32, sy - h * 0.1 - rng.random() * 4)], 1.1, 0.35, m)


def palm(c, x, y, h):
    c.chain([(x, y), (x + 2, y - h * 0.5), (x + 5, y - h * 0.9)], 1.8, 1.1, c.M('#8a6a40'), tex=0.4)
    m = c.M('#4a8a30')
    tx, ty = x + 5, y - h * 0.9
    for a in (-2.7, -2.1, -1.4, -0.8, -0.2, 0.3):
        c.chain([(tx, ty), (tx + math.cos(a) * h * 0.3, ty + math.sin(a) * h * 0.18 - 2), (tx + math.cos(a) * h * 0.5, ty + h * 0.12)], 1.9, 0.4, m, tex=0.2)


def rock(c, x, y, r, col):
    c.ell(x, y - r * 0.4, r, r * 0.7, c.M(col), tex=0.35, clip=lambda X, Y: Y <= y)
    c.ell(x - r * 0.35, y - r * 0.55, r * 0.5, r * 0.4, c.M(shade_col(col, 1.1)), tex=0.3, edge=False)


def bush(c, x, y, r, col):
    m = c.M(col)
    m2 = c.M(shade_col(col, 0.75))
    for dx in (-0.6, 0, 0.6):
        c.ell(x + dx * r, y - r * 0.45, r * 0.62, r * 0.55, m2, tex=0.45)
    for dx in (-0.5, 0.1, 0.55):
        c.ell(x + dx * r - 0.5, y - r * 0.62, r * 0.48, r * 0.42, m, tex=0.5)


def flowers(c, x0, x1, y0, y1, cols, n):
    rng = c.rng
    for _ in range(n):
        x, y = x0 + rng.random() * (x1 - x0), y0 + rng.random() * (y1 - y0)
        c.dot(x, y, 0.55, cols[int(rng.random() * len(cols))])


def tomb(c, x, y, s=1.0):
    m = c.M('#6a6a78')
    c.rect(x - 4 * s, y - 9 * s, 8 * s, 9 * s, m, shade=0.6, tex=0.3)
    c.ell(x, y - 9 * s, 4 * s, 3 * s, m, clip=lambda X, Y: Y < y - 9 * s)
    c.line(x - 1.5 * s, y - 7 * s, x + 1.5 * s, y - 7 * s, '#3a3a44', 2)
    c.line(x, y - 9 * s, x, y - 4 * s, '#3a3a44', 2)


def crystal(c, x, y, h, col):
    m = c.M(col, contrast=0.9, gloss=0.9)
    for (dx, hh, w) in [(0, 1, 3), (-4, 0.6, 2.4), (4, 0.7, 2.2)]:
        c.poly([(x + dx - w, y), (x + dx + w, y), (x + dx + w * 0.5, y - h * hh), (x + dx - w * 0.2, y - h * hh - 2)], m, shade=0.7, grad=0.5, gdir=(1, 0))


def tower(c, x, y, w, h, col, roof, banner=None):
    m = c.M(col)
    c.rect(x - w / 2, y - h, w, h, m, shade=0.62, grad=0.3, gdir=(1, 0), tex=0.25)
    for i in range(-1, 2):
        c.rect(x + i * w / 3 - 1.5, y - h - 3, 3, 3, m, shade=0.7)
    c.poly([(x - w / 2 - 1, y - h - 3), (x + w / 2 + 1, y - h - 3), (x, y - h - w * 1.1)], c.M(roof, gloss=0.3), shade=0.6, gdir=(1, 0))
    c.rect(x - 1, y - h * 0.6, 2, 4, c.M('#2a1a10'), shade=0.1)
    if banner:
        c.rect(x - 2, y - h * 0.35, 4, 7, c.M(banner), shade=0.7)


def treeline(seed, y, n, col, kinds=('pine', 'oak'), hmin=24, hmax=34, snow=None):
    def f(c):
        rng = c.rng
        for i in range(n):
            x = i * (250 / n) + rng.random() * 8 - 4
            k = kinds[i % len(kinds)]
            hh = hmin + rng.random() * (hmax - hmin)
            if k == 'pine':
                pine(c, x, y + rng.random() * 4, hh, col, snow=snow)
            elif k == 'oak':
                oak(c, x, y + rng.random() * 4, hh, col)
            elif k == 'dead':
                dead_tree(c, x, y + rng.random() * 4, hh, col)
    return f


# --------------------------------------------------------------------------------------------- zones
def finish(a, vig=0.35, bl=0.3, seed=1):
    a = kuwahara(a, 5)
    a = brush(a, seed, -0.5, 10, 0.06)
    a = bloom(a, 205, bl)
    a = grade(a)
    return vignette(a, vig)


def zone_goldhain():
    a = sky('#3f86d8', '#7fb8ea', '#e8eedc')
    a = sun(a, 196, 26, 7, '#fffbe8', '#fff1c0', 28, 0.7)
    a = clouds(a, 3, '#ffffff', 2, 52, 0.47)
    a = terrain(a, ridge(1, 90, 36, 60, sharp=True), '#7f93b8', 1, snow='#f2f6ff', fog='#c6dcea', fog_amt=0.35)
    a = terrain(a, ridge(2, 106, 16, 40), '#4f8e46', 2, fog='#a8c8c0', fog_amt=0.25)
    a = composite(a, props(treeline(2, 114, 15, '#3c7c3a'), 2, fog='#9cbcb0', fog_amt=0.32))
    a = ground(a, '#5e9e3c', '#4a8a30', 4, path='#bfa070', grass='#78b848')

    def near(c):
        oak(c, 14, 152, 66, '#3a8a30')
        pine(c, 230, 158, 74, '#2a6a30')
        bush(c, 52, 160, 11, '#3a7a2a')
        bush(c, 194, 160, 13, '#3a7a2a')
        rock(c, 172, 158, 7, '#8a8a90')
        flowers(c, 30, 210, 132, 158, ['#f0e040', '#f05050', '#ffffff', '#e070e0'], 40)
    a = composite(a, props(near, 3, outline=(20, 16, 10, 120)))
    return finish(a, 0.3)


def zone_nebelmoor():
    a = sky('#2e4a46', '#5f7a68', '#b4c4a0')
    a = sun(a, 60, 34, 10, '#eef4dc', '#c8d8b0', 24, 0.6)
    a = terrain(a, ridge(11, 98, 18, 50), '#4a6058', 11, fog='#90a890', fog_amt=0.5)
    a = composite(a, props(treeline(12, 118, 11, '#33503a', ('oak', 'dead')), 12, fog='#8aa088', fog_amt=0.45))
    a = ground(a, '#4a5a34', '#3c4c2a', 13, grass='#5f7f3a')
    for (cx, cy, rx, ry) in [(60, 142, 40, 7), (190, 136, 34, 5), (128, 154, 30, 4)]:
        d = ((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2
        m = sstep(1.05, 0.9, d)
        water = C('#24443f') * (0.85 + 0.3 * np.sin(YY * 6 + XX * 0.3)[..., None] * 0.15)
        water = water + C('#c8d8b0') * 0.25 * sstep(0.6, 0, d)[..., None] * 0.4
        a = a * (1 - m[..., None]) + water * m[..., None]
    a = fog_band(a, '#bccaa8', 100, 134, 0.55)

    def near(c):
        dead_tree(c, 18, 160, 72, '#24302a')
        for x in (90, 98, 104, 170, 176, 226):
            c.chain([(x, 160), (x + 1, 140), (x + 2, 132)], 0.8, 0.4, c.M('#6a7a3a'))
            c.ell(x + 2, 134, 1.1, 3, c.M('#6a4a2a'))
    a = composite(a, props(near, 13))
    return finish(a, 0.45)


def zone_rotfels():
    a = sky('#3a6fc8', '#8fb4e0', '#f4c08c')
    a = sun(a, 40, 40, 9, '#fff6dc', '#ffd0a0', 30, 0.6)
    a = clouds(a, 21, '#ffeede', 4, 40, 0.5)
    a = terrain(a, mesa(21, 104, 48), '#b55c3a', 21, fog='#e8a888', fog_amt=0.35, light=1.2)
    a = terrain(a, mesa(22, 116, 26), '#a64a2c', 22, fog='#d09070', fog_amt=0.15, light=1.2)
    a = ground(a, '#b8784a', '#a0663e', 23, path='#d4a676')

    def near(c):
        rock(c, 20, 158, 16, '#8a4a30')
        rock(c, 214, 152, 12, '#9a5434')
        for x in (70, 150, 186):
            bush(c, x, 136, 5, '#7a7a30')
    a = composite(a, props(near, 24, outline=(30, 14, 8, 110)))
    return finish(a, 0.3)


def zone_sonnenglut():
    a = sky('#2c7ee0', '#76b2ec', '#fbe6b0')
    a = sun(a, 180, 30, 12, '#fffde8', '#fff2c0', 40, 0.8)

    def pyr(c):
        m = c.M('#d8b070')
        c.poly([(40, 110), (78, 62), (116, 110)], m, shade=0.6, grad=0.7, gdir=(1, 0))
        c.poly([(150, 112), (170, 86), (190, 112)], m, shade=0.6, grad=0.7, gdir=(1, 0))
    a = composite(a, props(pyr, 30, fog='#f0d8a8', fog_amt=0.45))
    x = np.arange(W) / S
    a = terrain(a, 104 - (np.sin(x / 22) * 6 + np.sin(x / 9 + 1) * 3), '#e2ba72', 31, tex=0.05, light=2.0)
    a = terrain(a, 116 - np.sin(x / 30 + 2) * 6, '#ebc47c', 32, tex=0.05, light=2.0)
    a = ground(a, '#ecc884', '#dcb474', 33)
    rip = np.sin((XX + YY * 3 + np.sin(YY / 3.0) * 4) * 1.4) * sstep(GY + 2, GY + 10, YY)
    a = a * (1 - 0.05 * rip[..., None])

    def near(c):
        palm(c, 16, 158, 72)
        palm(c, 222, 154, 62)
        rock(c, 186, 158, 8, '#b08a5a')
    a = composite(a, props(near, 34, outline=(30, 20, 8, 110)))
    return finish(a, 0.25, 0.4)


def zone_frostgipfel():
    a = sky('#6f98cc', '#a8c4e4', '#eef4fa')
    a = clouds(a, 41, '#ffffff', 2, 30, 0.5)
    a = terrain(a, ridge(41, 96, 56, 40, sharp=True), '#b0c2dc', 41, snow='#ffffff', fog='#dce8f4', fog_amt=0.35, light=1.4)
    a = terrain(a, ridge(42, 110, 22, 30, sharp=True), '#d8e4f2', 42, fog='#e8f0f8', fog_amt=0.1, light=1.4)
    a = composite(a, props(treeline(42, 120, 13, '#3a5a5a', ('pine',), snow='#f0f8ff'), 42, fog='#c0d0e0', fog_amt=0.35))
    a = ground(a, '#eaf2fc', '#d2deee', 43, path='#c4d0e4')

    def near(c):
        pine(c, 12, 160, 78, '#2a4a4a', snow='#ffffff')
        crystal(c, 210, 156, 22, '#a0d8ff')
        rock(c, 184, 158, 8, '#8a9ab0')
    a = composite(a, props(near, 44, outline=(16, 20, 30, 110)))
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, 'RGBA')
    rng = np.random.default_rng(45)
    for _ in range(260):
        x, y, r = rng.random() * W, rng.random() * H, rng.random() * 1.8 + 0.6
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(150 + rng.random() * 100)))
    return finish(np.array(img).astype(float), 0.25)


def zone_schattenhain():
    a = sky('#0c0820', '#2a2048', '#5a4878')
    a = stars(a, 260, 51)
    a = sun(a, 186, 34, 13, '#eceefa', '#8e7ec4', 34, 0.7)
    a = terrain(a, ridge(51, 104, 24, 40), '#2a2440', 51, fog='#4a3a64', fog_amt=0.45)
    a = composite(a, props(treeline(52, 120, 11, '#1a1626', ('dead',), 28, 42), 52))
    a = ground(a, '#3a3a40', '#2e2e36', 53, path='#4a4650', grass='#3a4a3a')

    def near(c):
        dead_tree(c, 14, 160, 86, '#141018')
        for (x, y, s_) in [(56, 140, 1.0), (82, 146, 1.2), (176, 142, 1.1), (206, 150, 1.4), (120, 136, 0.8)]:
            tomb(c, x, y, s_)
    a = composite(a, props(near, 54, outline=(8, 6, 12, 140)))
    a = fog_band(a, '#8a70b0', 110, 142, 0.4)
    return finish(a, 0.5, 0.45)


def zone_glutschlund():
    # stormy red sky with swirling, painterly clouds
    a = sky('#1e0404', '#6a140c', '#c4441a')
    n1 = noise(34, 61, 5)
    warp = noise(60, 62, 3)
    n2 = value_noise(W, H, 22 * S, 63, 4, wrap=False)
    sw = np.roll(n1, int(S * 8), 1) * 0.5 + n1 * 0.5 + (warp - 0.5) * 0.5
    band = sstep(GY - 10, 20, YY)
    dark = sstep(0.42, 0.7, sw) * band
    a = blend(a, '#2a0606', dark * 0.75)
    lit = sstep(0.55, 0.85, n2 * 0.6 + sw * 0.4) * band
    a = blend(a, '#e0582a', lit * 0.45)
    a = glow(a, 92, 70, 70, '#ff6a20', 0.45)
    # distant ranges with lava rim light
    a = terrain(a, ridge(64, 104, 30, 50, sharp=True), '#3a1a1e', 64, fog='#7a2418', fog_amt=0.45, light=1.4)

    xs = np.arange(W) / S
    cone = 54 + np.maximum(0, np.abs(xs - 90) - 6) * 1.05 + noise1(6, 65, 4) * 5 - 2.5
    cone = np.where(np.abs(xs - 90) < 6, 54 + noise1(3, 66, 2) * 3, cone)
    a = terrain(a, cone, '#2e1e20', 65, light=1.6, tex=0.3, dark_base=0.1)
    # lava rivers down the cone
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, 'RGBA')
    rng = np.random.default_rng(66)
    for k in range(6):
        side = -1 if k % 2 else 1
        x, y = (90 + side * rng.random() * 4) * S, 55 * S
        pts = [(x, y)]
        while y < 112 * S:
            y += S * (2 + rng.random() * 2.5)
            x += S * side * (0.6 + rng.random() * 0.9) * (0.4 + k * 0.18)
            pts.append((x + rng.random() * 3 - 1.5, y))
        for wdt, col in ((12, (255, 70, 15, 60)), (6, (255, 110, 25, 210)), (2, (255, 225, 140, 255))):
            d.line(pts, fill=col, width=wdt, joint='curve')
    a = np.array(img).astype(float)
    a = glow(a, 90, 50, 22, '#ffb040', 0.9)
    a = glow(a, 90, 40, 46, '#ff6a20', 0.5)
    # eruption plume
    plume = sstep(1.0, 0.0, np.abs(XX - 90 - (54 - YY) * 0.15) / (6 + (54 - YY) * 0.35)) * sstep(56, 50, YY) * sstep(-10, 30, YY)
    a = blend(a, '#ffb050', plume * 0.55 * (0.6 + 0.4 * noise(8, 70, 3)))
    a = terrain(a, ridge(67, 117, 8, 30), '#24161a', 67, fog='#5a1a12', fog_amt=0.3, light=0.8)
    # basalt ground with glowing cracks
    a = ground(a, '#2a2022', '#1e1618', 63)
    v = veins(H, W, 68, 420, 0.11) * sstep(GY + 1, GY + 6, YY)
    vg = np.array(Image.fromarray((v * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(5))).astype(float) / 255
    a = blend(a, '#ff5a18', np.clip(vg * 1.4, 0, 1))
    a = blend(a, '#ffd080', v * 0.9)

    def near(c):
        for (x, y, w_, h_) in [(-4, 162, 46, 40), (196, 162, 52, 34), (150, 166, 30, 16), (60, 166, 26, 12)]:
            m = c.M('#221a1c')
            c.poly([(x, y), (x + w_ * 0.15, y - h_ * 0.7), (x + w_ * 0.35, y - h_), (x + w_ * 0.55, y - h_ * 0.6), (x + w_ * 0.75, y - h_ * 0.85), (x + w_, y)], m, shade=0.45, grad=0.6, gdir=(1, 0.2), tex=0.4)
    rocks = props(near, 65, outline=(6, 2, 2, 180))
    ra = np.array(rocks).astype(float)
    mask = ra[:, :, 3] > 0
    vv = veins(H, W, 69, 160, 0.06) * mask
    ra[..., :3] = ra[..., :3] * (1 - vv[..., None]) + np.array([255, 120, 40]) * vv[..., None]
    rim = np.roll(mask, -3, 1) & ~np.roll(mask, 4, 1) & mask
    ra[rim, :3] = ra[rim, :3] * 0.4 + np.array([255, 110, 40]) * 0.6
    a = composite(a, Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8), 'RGBA'))
    a = finish(a, 0.5, 0.55, 61)
    # ash rain and embers, painted after the oil filter so they stay crisp
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(240):
        x, y = rng.random() * W, rng.random() * H
        ln = 10 + rng.random() * 16
        d.line([(x, y), (x - ln * 0.22, y + ln)], fill=(18, 6, 6, int(110 + rng.random() * 100)), width=2)
    for _ in range(180):
        x, y, r = rng.random() * W, rng.random() * H, rng.random() * 1.8 + 0.6
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, int(150 + rng.random() * 80), 80, int(140 + rng.random() * 115)))
    return np.array(img).astype(float)


def zone_leerenriss():
    a = sky('#04030c', '#140a28', '#2c1650')
    a = stars(a, 380, 71, ymax=GY)
    n = noise(50, 72, 5)
    a = blend(a, '#7a2aa8', sstep(0.45, 0.8, n) * 0.55)
    n2 = noise(34, 73, 4)
    a = blend(a, '#20a0a0', sstep(0.58, 0.85, n2) * 0.35)
    a = sun(a, 60, 40, 17, '#120618', '#c060ff', 14, 0.9)

    def isl(c):
        for (x, y, r) in [(170, 50, 14), (30, 76, 9), (110, 30, 6), (210, 92, 8)]:
            m = c.M('#3a2a50')
            c.poly([(x - r, y), (x + r, y), (x + r * 0.3, y + r * 1.4), (x - r * 0.2, y + r * 1.1)], m, shade=0.45, grad=0.5, tex=0.2)
            c.ell(x, y, r, r * 0.3, c.M('#5a4a7a'))
            crystal(c, x, y, r * 0.8, '#c080ff')
    a = composite(a, props(isl, 74))
    a = terrain(a, ridge(75, 114, 12, 25, sharp=True), '#24183a', 75)
    a = ground(a, '#2a2040', '#221a36', 76)

    def near(c):
        crystal(c, 20, 158, 30, '#a060ff')
        crystal(c, 220, 156, 24, '#40e0d0')
        rock(c, 186, 158, 7, '#3a2a50')
    a = composite(a, props(near, 77, outline=(10, 6, 18, 140)))
    return finish(a, 0.45, 0.6)


def town():
    a = sky('#3f86d8', '#82b8ea', '#eef0dc')
    a = clouds(a, 81, '#ffffff', 2, 44, 0.47)
    a = terrain(a, ridge(81, 100, 20, 60), '#6a8aa8', 81, fog='#b8d0e0', fog_amt=0.35)

    def walls(c):
        c.rect(0, 92, 240, 26, c.M('#a8a094'), shade=0.62, tex=0.3)
        for x in range(0, 240, 8):
            c.rect(x, 88, 5, 5, c.M('#a8a094'), shade=0.7)
        for (x, w, h, roof, ban) in [(30, 18, 50, '#3a5aa8', '#c02020'), (90, 24, 70, '#3a5aa8', '#2a4ab0'), (150, 22, 60, '#3a5aa8', '#c02020'), (214, 18, 46, '#3a5aa8', '#2a4ab0')]:
            tower(c, x, 118, w, h, '#b8b0a4', roof, ban)
        c.ell(120, 118, 10, 14, c.M('#2a1a10'), flat=0.15, clip=lambda X, Y: Y < 118)
    a = composite(a, props(walls, 82))
    a = ground(a, '#5e9e3c', '#4a8a30', 83, path='#b0a888', grass='#78b848')

    def near(c):
        oak(c, 12, 160, 62, '#3a8a30')
        c.rect(196, 132, 34, 24, c.M('#8a5a34'), shade=0.6, tex=0.3)
        c.poly([(192, 133), (234, 133), (213, 118)], c.M('#a03020'), shade=0.6)
        c.rect(206, 142, 8, 14, c.M('#3a2414'), shade=0.2)
    a = composite(a, props(near, 84, outline=(20, 14, 8, 110)))
    return finish(a, 0.3)


def arena():
    a = sky('#3a6fc8', '#8ab4e4', '#f2dcb0')
    wall_top = 70 + ((XX - 120) / 120) ** 2 * 12
    m = sstep(-0.5, 0.5, YY - wall_top) * sstep(118.5, 117.5, YY)
    n = noise(4, 91, 3)
    wall = C('#a08060')[None, None] * (0.8 + 0.35 * n[..., None])
    a = a * (1 - m[..., None]) + wall * m[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, 'RGBA')
    rng = np.random.default_rng(92)
    for _ in range(2600):
        xx = rng.random() * W
        yy = (70 + ((xx / S - 120) / 120) ** 2 * 12 + 4 + rng.random() * 30) * S
        if yy < 116 * S:
            col = rgb(['#c04040', '#4060c0', '#e0c040', '#e0e0e0', '#40a040', '#c08060'][int(rng.random() * 6)])
            d.ellipse([xx - 2, yy - 2, xx + 2, yy + 2], fill=col + (255,))
            d.ellipse([xx - 1.4, yy - 5, xx + 1.4, yy - 2], fill=(220, 180, 140, 255))
    for xx in range(0, 240, 30):
        d.rectangle([(xx - 2) * S, 70 * S, (xx + 2) * S, 118 * S], fill=(110, 82, 60, 255))
    d.rectangle([0, 112 * S, W, 118 * S], fill=(90, 64, 48, 255))
    a = np.array(img).astype(float)
    a = ground(a, '#dcbc84', '#c8a870', 93)
    return finish(a, 0.3)


# --------------------------------------------------------------------------------------------- interiors
def hall(wall, mortar, floor, floor2, light, pillar, seed, arch='#0c0810', extra=None, banner=None, lights=True):
    n = noise(5, seed, 4)
    row = np.floor(YY / 7)
    off = (row % 2) * 6
    bx = (XX + off) % 12
    by = YY % 7
    # per-brick colour variation
    bid = (np.floor((XX + off) / 12) * 7.13 + row * 3.71) % 1
    wc = C(wall)[None, None] * (0.8 + 0.32 * bid[..., None] + 0.12 * (n[..., None] - 0.5))
    bev = np.clip(1 - sstep(0.3, 1.2, bx) * 0 + sstep(10.5, 11.8, bx) * -0.25 + sstep(5.8, 6.8, by) * -0.25 + sstep(1.2, 0.2, by) * 0.15 + sstep(1.2, 0.2, bx) * 0.12, 0.5, 1.3)
    a = wc * bev[..., None]
    mortar_m = (sstep(0.5, 0.0, bx) + sstep(0.5, 0.0, by)).clip(0, 1)
    a = a * (1 - mortar_m[..., None]) + C(mortar)[None, None] * mortar_m[..., None]
    for cx in (60, 180):
        d = ((XX - cx) / 22) ** 2 + ((YY - 52) / 30) ** 2
        inside = np.maximum(sstep(1.02, 0.98, d) * (YY < 52), sstep(22.3, 21.7, np.abs(XX - cx)) * (YY >= 52)) * (YY < GY)
        depth = C(arch)[None, None] * (0.7 + 0.6 * sstep(GY, 40, YY)[..., None])
        a = a * (1 - inside[..., None]) + depth * inside[..., None]
        rd = ((XX - cx) / 25.5) ** 2 + ((YY - 52) / 33.5) ** 2
        rim = sstep(1.04, 0.98, rd) * (1 - inside) * (YY < 60)
        a = a * (1 - rim[..., None]) + C(pillar)[None, None] * 1.05 * rim[..., None]
    if extra:
        a = extra(a)
    for cx in (10, 120, 230):
        dx = (XX - cx) / 9
        m = sstep(1.05, 0.95, np.abs(dx)) * (YY < GY)
        cyl = np.sqrt(np.clip(1 - dx ** 2, 0, 1))
        shade = 0.45 + 0.75 * cyl * (0.75 - dx * 0.35) + 0.25 * np.clip(1 - np.abs(dx + 0.35) * 5, 0, 1)
        pc = C(pillar)[None, None] * shade[..., None] * (0.92 + 0.12 * n[..., None])
        a = a * (1 - m[..., None]) + pc * m[..., None]
        ring = sstep(1.25, 1.1, np.abs(dx)) * ((YY % 36) < 3) * (YY < GY)
        a = a * (1 - ring[..., None] * 0.6) + C(pillar)[None, None] * 1.2 * ring[..., None] * 0.6
    if banner:
        for cx in (60, 180):
            dx = (XX - cx) / 7
            m = sstep(1.05, 0.95, np.abs(dx)) * (YY >= 14) * (YY < 40 + 4 * (1 - np.abs(dx)))
            fold = 0.8 + 0.25 * np.cos(dx * 6)
            a = a * (1 - m[..., None]) + C(banner)[None, None] * fold[..., None] * m[..., None]
            em = sstep(2.6, 2.0, np.sqrt(dx ** 2 * 49 + (YY - 26) ** 2))
            a = a * (1 - em[..., None]) + C('#f0c040')[None, None] * em[..., None]
    # floor
    fy = np.clip(YY - GY, 0, None)
    persp = XX + fy * ((XX - 120) / 60)
    t = ((np.floor(persp / 16) + np.floor(fy / 9)) % 2)
    f1, f2 = C(floor), C(floor2)
    fl = (f1[None, None] * (1 - t[..., None]) + f2[None, None] * t[..., None]) * (0.85 + 0.25 * n[..., None])
    gl = sstep(0.8, 0, np.minimum(persp % 16, 16 - persp % 16)) + sstep(0.8, 0, np.minimum(fy % 9, 9 - fy % 9))
    fl = fl * (1 - 0.35 * np.clip(gl, 0, 1)[..., None])
    fl = fl * (0.7 + 0.45 * (fy / (160 - GY)))[..., None]
    m = sstep(GY - 0.3, GY + 0.3, YY)[..., None]
    a = a * (1 - m) + fl * m
    a = a * (1 - 0.4 * sstep(GY + 3, GY, YY) * sstep(GY - 3, GY, YY))[..., None]
    if lights:
        for (lx, ly) in ((34, 60), (86, 60), (154, 60), (206, 60)):
            a = torch(a, lx, ly, light, 26)
    return finish(a, 0.55, 0.45)


def inst_mine():
    def extra(a):
        for cx in (34, 86, 154, 206):
            m = sstep(2.2, 1.8, np.abs(XX - cx)) * (YY > 20) * (YY < GY)
            a = a * (1 - m[..., None]) + C('#6a4a2a')[None, None] * (0.8 + 0.3 * (XX < cx))[..., None] * m[..., None]
        m = ((YY >= 18) & (YY < 23)).astype(float)
        a = a * (1 - m[..., None]) + C('#6a4a2a')[None, None] * m[..., None]
        rng = np.random.default_rng(5)
        for _ in range(40):
            a = glow(a, rng.random() * 240, rng.random() * GY, 1.5, '#60c0ff', 0.9)
        return a
    return hall('#5a4a40', '#2a2420', '#4a4038', '#40362e', '#ffc060', '#6a5444', 101, extra=extra)


def inst_cave():
    def extra(a):
        for cx in range(8, 240, 22):
            ln = 10 + (cx * 7) % 18
            m = sstep(0.5, -0.5, np.abs(XX - cx) - (ln - YY) / 5) * (YY < ln)
            a = a * (1 - m[..., None]) + C('#3a3248')[None, None] * m[..., None]
        for (cx, cy) in [(40, 110), (200, 106), (130, 114)]:
            a = glow(a, cx, cy, 18, '#c060ff', 0.7)
        return a
    return hall('#3a3a4a', '#1e1e28', '#344034', '#2c362c', '#80ff80', '#4a4a5a', 102, extra=extra, lights=False)


def inst_temple():
    def extra(a):
        m = (YY >= 8) & (YY < 14)
        k = (np.floor(XX / 3) + np.floor(YY)) % 4
        a[m & (k == 0)] = C('#3a6ab0')
        a[m & (k == 1)] = C('#c09030')
        return a
    return hall('#c8a070', '#8a6a44', '#d0b080', '#c0a070', '#ffd060', '#d8b880', 103, extra=extra, banner='#3a6ab0')


def inst_ice():
    def extra(a):
        for cx in range(4, 240, 10):
            ln = 6 + (cx * 13) % 12
            m = sstep(0.4, -0.4, np.abs(XX - cx) - (ln - YY) / 4) * (YY < ln)
            a = a * (1 - m[..., None]) + C('#e8f6ff')[None, None] * m[..., None]
        return a
    return hall('#8ab0d8', '#5a80b0', '#c8dcf0', '#b0c8e4', '#60d0ff', '#a8c8e8', 104, extra=extra, banner='#2a4a8a')


def inst_cathedral():
    def extra(a):
        cols = np.array([rgb('#c02030'), rgb('#6030a0'), rgb('#e0a020'), rgb('#2050c0')], float)
        for cx in (60, 180):
            d = ((XX - cx) / 10) ** 2 + ((YY - 40) / 18) ** 2
            m = sstep(1.05, 0.95, d)
            idx = ((np.floor(XX / 4) + np.floor(YY / 5)) % 4).astype(int)
            lead = (np.minimum(XX % 4, 4 - XX % 4) < 0.35) | (np.minimum(YY % 5, 5 - YY % 5) < 0.35)
            glass = cols[idx] * np.where(lead, 0.25, 1.0)[..., None]
            a = a * (1 - m[..., None]) + glass * m[..., None]
            a = glow(a, cx, 40, 22, '#ff8040', 0.25)
        return a
    return hall('#4a3a40', '#221a1e', '#3a3034', '#30282c', '#ff9040', '#5a4a50', 105, arch='#140a10', extra=extra, banner='#7a1818')


def inst_abyss():
    a = sky('#03020a', '#120824', '#28104a', y1=160)
    a = stars(a, 300, 106, ymax=GY)
    a = sun(a, 120, 50, 28, '#0a0410', '#9040ff', 18, 0.9)
    d = ((XX - 120) / 16) ** 2 + ((YY - 50) / 8) ** 2
    a = blend(a, '#40ffe0', sstep(1.05, 0.9, d))
    a = blend(a, '#e0fff8', sstep(0.35, 0.0, d) * 0.6)
    d2 = ((XX - 120) / 4) ** 2 + ((YY - 50) / 7) ** 2
    a = blend(a, '#0a0410', sstep(1.05, 0.9, d2))
    n = noise(6, 107, 3)
    plat = sstep(GY - 0.3, GY + 0.3, YY)
    pc = C('#2a2040')[None, None] * (0.75 + 0.45 * n[..., None]) * (0.7 + 0.5 * ((YY - GY) / 36))[..., None]
    a = a * (1 - plat[..., None]) + pc * plat[..., None]
    a = blend(a, '#7050c0', sstep(1.5, 0, np.abs(YY - GY - 0.5)) * 0.8)
    for (cx, cy) in ((20, 100), (220, 100)):
        a = glow(a, cx, cy, 22, '#a060ff', 0.6)
    return finish(a, 0.55, 0.6)


def raid_glut():
    def extra(a):
        lava = (YY >= 100) & (YY < GY)
        n = noise(8, 5, 3)
        lc = C('#ff6020')[None, None] * (0.8 + 0.5 * n[..., None]) + C('#ffd040')[None, None] * sstep(0.6, 0.8, n)[..., None] * 0.6
        a = np.where(lava[..., None], lc, a)
        for cx in (60, 180):
            a = glow(a, cx, 108, 40, '#ff8020', 0.5)
        return a
    return hall('#2a1a1a', '#120808', '#3a2a28', '#2e2020', '#ff7020', '#3a2626', 111, arch='#ff5010', extra=extra, banner='#a02010')


def raid_nebel():
    def extra(a):
        m = sstep(12.5, 11.5, np.abs(XX - 120)) * (YY > 50) * (YY < GY)
        a = a * (1 - m[..., None]) + C('#a0c8f0')[None, None] * (0.8 + 0.3 * (XX < 120))[..., None] * m[..., None]
        m2 = sstep(16.5, 15.5, np.abs(XX - 120)) * (YY > 44) * (YY < 52)
        a = a * (1 - m2[..., None]) + C('#d0e8ff')[None, None] * m2[..., None]
        return glow(a, 120, 70, 30, '#80c0ff', 0.4)
    return hall('#5a6a88', '#2a3a58', '#8a9ab8', '#7a8aa8', '#80c0ff', '#7a8aa8', 112, arch='#0a1428', extra=extra, banner='#1a3060')


def raid_thron():
    a = inst_abyss()
    rng = np.random.default_rng(113)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, 'RGBA')
    for _ in range(7):
        cx = rng.random() * 240
        pts = [((cx + math.sin(yy / 6 + cx) * 4) * S, yy * S) for yy in range(GY - 62, GY + 1)]
        for wdt, col in ((18, (26, 10, 42, 255)), (12, (58, 26, 90, 255)), (4, (110, 60, 160, 200))):
            d.line(pts, fill=col, width=wdt)
    return np.array(img).astype(float)


def catalogue():
    B = dict(
        bg_goldhain=zone_goldhain, bg_nebelmoor=zone_nebelmoor, bg_rotfels=zone_rotfels,
        bg_sonnenglut=zone_sonnenglut, bg_frostgipfel=zone_frostgipfel, bg_schattenhain=zone_schattenhain,
        bg_glutschlund=zone_glutschlund, bg_leerenriss=zone_leerenriss, bg_town=town, bg_arena=arena,
        bg_mine=inst_mine, bg_cave=inst_cave, bg_temple=inst_temple, bg_ice=inst_ice,
        bg_cathedral=inst_cathedral, bg_abyss=inst_abyss, bg_raid_glut=raid_glut, bg_raid_nebel=raid_nebel,
        bg_raid_thron=raid_thron,
    )
    return {k: Image.fromarray(np.clip(f(), 0, 255).astype(np.uint8)).convert('RGB') for k, f in B.items()}

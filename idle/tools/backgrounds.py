"""240x160 pixel-art battle backdrops: eight outdoor zones, town, arena and nine instance halls."""
import math

import numpy as np
from PIL import Image

from px import BAYER4, Canvas, mix, rgb, shade_col, value_noise, noise1d

W, H = 240, 160
GROUND = 124


def bayer(h, w):
    return BAYER4[np.arange(h)[:, None] % 4, np.arange(w)[None, :] % 4]


def sky(top, bottom, horizon=GROUND, bands=10, extra=None):
    arr = np.zeros((H, W, 3))
    t = np.clip(np.arange(H) / horizon, 0, 1)[:, None] + (bayer(H, W) - 0.5) / bands
    t = np.clip(np.floor(t * bands) / bands, 0, 1)
    a, b = np.array(rgb(top), float), np.array(rgb(bottom), float)
    arr[:] = a[None, None, :] + (b - a)[None, None, :] * t[:, :, None]
    if extra:
        c = np.array(rgb(extra), float)
        tt = np.clip((np.arange(H) / horizon - 0.55) / 0.45, 0, 1)[:, None] ** 2
        tt = np.floor((tt + (bayer(H, W) - 0.5) / 6) * 6) / 6
        arr = arr + (c - arr) * np.clip(tt, 0, 1)[:, :, None] * 0.6
    return arr


def to_img(arr):
    out = np.zeros((H, W, 4), np.uint8)
    out[:, :, :3] = np.clip(arr, 0, 255)
    out[:, :, 3] = 255
    return Image.fromarray(out, 'RGBA')


def disc(arr, cx, cy, r, col, glow=None, glow_r=None):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    if glow:
        gr = glow_r or r * 3
        g = np.clip(1 - (d - r) / gr, 0, 1) ** 2
        g = np.floor((g + (bayer(H, W) - 0.5) / 4) * 4) / 4
        arr += (np.array(rgb(glow), float) - arr) * np.clip(g, 0, 1)[:, :, None] * 0.55
    m = d <= r
    arr[m] = rgb(col)
    return arr


def stars(arr, n, seed, ymax=GROUND - 20, cols=('#ffffff', '#c0d0ff', '#ffe0c0')):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y = int(rng.random() * W), int(rng.random() * ymax)
        arr[y, x] = rgb(cols[int(rng.random() * len(cols))])
        if rng.random() < 0.08 and 0 < x < W - 1 and 0 < y < H - 1:
            c = np.array(rgb(cols[0]), float)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                arr[y + dy, x + dx] = arr[y + dy, x + dx] * 0.4 + c * 0.6
    return arr


def clouds(arr, seed, col, y0=8, y1=60, thresh=0.58, scale=40):
    n = value_noise(W, H * 3, scale, seed, 4)[::3, :]
    band = np.zeros(H)
    mid, half = (y0 + y1) / 2, (y1 - y0) / 2
    band = np.clip(1 - np.abs(np.arange(H) - mid) / half, 0, 1) ** 0.6
    v = n * band[:, None]
    mask = v > thresh
    under = mask & ~np.roll(mask, -2, 0)
    c = np.array(rgb(col), float)
    arr[mask] = arr[mask] * 0.2 + c * 0.8
    arr[under] = arr[under] * 0.82 + np.array(rgb('#8090b0'), float) * 0.0
    return arr


def ridge(seed, base, amp, scale, octaves=4, sharp=False):
    n = noise1d(W, scale, seed, octaves)
    if sharp:
        n = 1 - np.abs(n * 2 - 1)
    return base - n * amp


def mesa(seed, base, amp):
    n = noise1d(W, 50, seed, 2)
    steps = np.where(n > 0.55, amp, np.where(n > 0.42, amp * 0.55, amp * 0.15))
    return base - steps - noise1d(W, 6, seed + 5, 2) * 3


def fill(arr, hts, col, seed=0, tex=0.12, col2=None, snow=None, light_top=True, fog=None, fog_amt=0.0):
    y = np.arange(H)[:, None]
    mask = y >= hts[None, :]
    nz = value_noise(W, H, 8, seed, 3)
    c1 = np.array(rgb(col), float)
    c2 = np.array(rgb(col2 or shade_col(col, 0.78)), float)
    t = np.clip((nz - 0.5) * tex * 6 + (bayer(H, W) - 0.5) * 0.5 + 0.5, 0, 1)
    t = np.round(t)
    layer = c1[None, None, :] * (1 - t[:, :, None]) + c2[None, None, :] * t[:, :, None]
    if light_top:
        top = (y - hts[None, :] < 2) & mask
        layer[top] = np.minimum(255, layer[top] * 1.22)
    if snow:
        s = (y - hts[None, :] < 4 + (nz * 6)) & mask & (hts[None, :] < np.percentile(hts, 55))
        layer[s] = rgb(snow)
    if fog:
        layer = layer + (np.array(rgb(fog), float) - layer) * fog_amt
    arr[mask] = layer[mask]
    return arr


def ground(arr, col, col2, seed, top=GROUND, path=None, grass=None):
    y = np.arange(H)[:, None]
    nz = value_noise(W, H, 6, seed, 3)
    mask = np.broadcast_to(y >= top, (H, W))
    t = np.clip((nz - 0.5) * 2.2 + (bayer(H, W) - 0.5) * 0.6 + 0.5, 0, 1)
    depth = np.clip((y - top) / (H - top), 0, 1)
    c1, c2 = np.array(rgb(col), float), np.array(rgb(col2), float)
    layer = c1 * (1 - np.round(t)[:, :, None]) + c2 * np.round(t)[:, :, None]
    layer = layer * (0.82 + 0.3 * depth[:, :, None] ** 0.8)
    if path:
        pc = np.array(rgb(path), float)
        center = 120 + np.sin(np.arange(W) / 30) * 8
        wdt = 10 + (y - top) * 0.9
        pm = (np.abs(np.arange(W)[None, :] - center[None, :]) < wdt) & mask & (nz > 0.3)
        pm &= np.broadcast_to(y >= top + 4, (H, W))
        layer[pm] = pc * (0.85 + 0.2 * np.round(t[pm]))[:, None]
    arr[mask] = layer[mask]
    if grass:
        rng = np.random.default_rng(seed + 1)
        g = np.array(rgb(grass), float)
        for x in range(W):
            hgt = int(rng.integers(1, 4))
            for k in range(hgt):
                yy = top - k
                if 0 <= yy < H:
                    arr[yy, x] = g * (1.0 + 0.1 * k)
    return arr


def fog_band(arr, col, y0, y1, amt=0.45):
    c = np.array(rgb(col), float)
    for y in range(max(0, y0), min(H, y1)):
        t = 1 - abs((y - (y0 + y1) / 2) / ((y1 - y0) / 2))
        t = max(0, t) * amt
        dith = (bayer(1, W)[0] - 0.5) * 0.15
        arr[y] = arr[y] + (c - arr[y]) * np.clip(t + dith, 0, 1)[:, None]
    return arr


def vignette(arr, amt=0.35):
    y, x = np.mgrid[0:H, 0:W]
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    f = 1 - np.clip(d - 0.75, 0, 1) * amt * 2
    f = np.floor((f + (bayer(H, W) - 0.5) / 8) * 8) / 8
    return arr * f[:, :, None]


def composite(arr, img):
    base = to_img(arr)
    base.alpha_composite(img)
    return np.array(base)[:, :, :3].astype(float)


def props(fn, seed=0, outline=(14, 10, 14, 255), fog=None, fog_amt=0.0):
    c = Canvas(W, H, seed=seed)
    fn(c)
    img = c.render(outline=outline, inner=False)
    if fog:
        a = np.array(img).astype(float)
        f = np.array(rgb(fog), float)
        m = a[:, :, 3] > 0
        a[m, :3] = a[m, :3] + (f - a[m, :3]) * fog_amt
        img = Image.fromarray(a.astype(np.uint8), 'RGBA')
    return img


# --------------------------------------------------------------------------------------------- prop kit
def pine(c, x, y, h, col, snow=None, trunk='#4a3020'):
    c.cap(x, y, x, y - h * 0.3, 1.2, 1.0, c.M(trunk))
    m = c.M(col)
    for i in range(3):
        yy = y - h * 0.25 - i * h * 0.24
        w = h * (0.34 - i * 0.08)
        c.poly([(x - w, yy), (x + w, yy), (x, yy - h * 0.42)], m, shade=0.55, grad=0.5, gdir=(1, 0.4), tex=0.15)
        if snow:
            c.poly([(x - w * 0.5, yy - h * 0.2), (x + w * 0.2, yy - h * 0.24), (x, yy - h * 0.42)], c.M(snow), shade=0.85, edge=False)


def oak(c, x, y, h, col, trunk='#5a3c24'):
    c.cap(x, y, x + 1, y - h * 0.55, 2.2, 1.6, c.M(trunk), tex=0.2)
    m = c.M(col)
    for (dx, dy, r) in [(-0.3, -0.62, 0.3), (0.28, -0.6, 0.3), (0, -0.82, 0.32), (-0.05, -0.55, 0.28)]:
        c.ell(x + dx * h, y + dy * h, r * h, r * h * 0.85, m, tex=0.35, dith=0.8)


def dead_tree(c, x, y, h, col='#2a2228'):
    m = c.M(col)
    c.cap(x, y, x, y - h * 0.6, 2.0, 1.2, m, tex=0.2)
    rng = c.rng
    for i in range(4):
        sy = y - h * (0.35 + i * 0.12)
        d = -1 if i % 2 else 1
        c.chain([(x, sy), (x + d * h * 0.18, sy - h * 0.12), (x + d * h * 0.3, sy - h * 0.1 - rng.random() * 4)], 1.1, 0.5, m)


def palm(c, x, y, h):
    c.chain([(x, y), (x + 2, y - h * 0.5), (x + 5, y - h * 0.9)], 1.8, 1.2, c.M('#8a6a40'), tex=0.3)
    m = c.M('#4a8a30')
    tx, ty = x + 5, y - h * 0.9
    for a in (-2.6, -2.0, -1.2, -0.5, 0.2):
        c.chain([(tx, ty), (tx + math.cos(a) * h * 0.3, ty + math.sin(a) * h * 0.18 - 2), (tx + math.cos(a) * h * 0.5, ty + h * 0.12)], 1.8, 0.6, m)


def rock(c, x, y, r, col):
    c.ell(x, y - r * 0.4, r, r * 0.7, c.M(col), tex=0.25, clip=lambda X, Y: Y <= y)


def bush(c, x, y, r, col):
    m = c.M(col)
    for dx in (-0.6, 0, 0.6):
        c.ell(x + dx * r, y - r * 0.5 - (0.3 if dx == 0 else 0) * r, r * 0.6, r * 0.55, m, tex=0.3, dith=0.8)


def tomb(c, x, y, s=1.0):
    m = c.M('#6a6a78')
    c.rect(x - 4 * s, y - 9 * s, 8 * s, 9 * s, m, shade=0.6, tex=0.2)
    c.ell(x, y - 9 * s, 4 * s, 3 * s, m, clip=lambda X, Y: Y < y - 9 * s)
    c.line(x - 1.5 * s, y - 7 * s, x + 1.5 * s, y - 7 * s, '#3a3a44')
    c.line(x, y - 9 * s, x, y - 4 * s, '#3a3a44')


def crystal(c, x, y, h, col):
    m = c.M(col, contrast=0.9)
    for (dx, hh, w) in [(0, 1, 3), (-4, 0.6, 2.4), (4, 0.7, 2.2)]:
        c.poly([(x + dx - w, y), (x + dx + w, y), (x + dx + w * 0.5, y - h * hh), (x + dx - w * 0.2, y - h * hh - 2)], m, shade=0.7, grad=0.5, gdir=(1, 0))


def tower(c, x, y, w, h, col, roof, banner=None):
    m = c.M(col)
    c.rect(x - w / 2, y - h, w, h, m, shade=0.6, tex=0.15)
    for i in range(-1, 2):
        c.rect(x + i * w / 3 - 1.5, y - h - 3, 3, 3, m, shade=0.7)
    c.poly([(x - w / 2 - 1, y - h - 3), (x + w / 2 + 1, y - h - 3), (x, y - h - w * 1.1)], c.M(roof), shade=0.6, gdir=(1, 0))
    c.rect(x - 1, y - h * 0.6, 2, 4, c.M('#2a1a10'), shade=0.1)
    if banner:
        c.rect(x - 2, y - h * 0.35, 4, 7, c.M(banner), shade=0.7)


def torch(arr, x, y, col='#ffb040', r=18):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
    g = np.clip(1 - d / r, 0, 1) ** 1.5
    g = np.floor((g + (bayer(H, W) - 0.5) / 5) * 5) / 5
    c = np.array(rgb(col), float)
    arr += (c - arr) * np.clip(g, 0, 1)[:, :, None] * 0.5
    for (dx, dy, cc) in [(0, 0, '#ffffff'), (0, -1, '#fff0a0'), (-1, 0, col), (1, 0, col), (0, -2, col), (0, 1, '#6a4020'), (0, 2, '#6a4020'), (0, 3, '#4a2a18')]:
        if 0 <= y + dy < H and 0 <= x + dx < W:
            arr[int(y + dy), int(x + dx)] = rgb(cc)
    return arr


# --------------------------------------------------------------------------------------------- outdoor zones
def zone_goldhain():
    a = sky('#5aa0e0', '#d8eef0', extra='#f0e0b0')
    a = disc(a, 196, 26, 9, '#fff6d0', glow='#fff0b0', glow_r=30)
    a = clouds(a, 3, '#ffffff', 4, 50, 0.48)
    a = fill(a, ridge(1, 92, 34, 60, sharp=True), '#7a90b8', 1, snow='#e8f0ff', fog='#c0d8e8', fog_amt=0.3)
    a = fill(a, ridge(2, 108, 16, 40), '#4a8a48', 2, fog='#a8c8c0', fog_amt=0.2)

    def mid(c):
        rng = c.rng
        for i in range(14):
            x = i * 18 + rng.random() * 8
            (pine if i % 3 else oak)(c, x, 114 + rng.random() * 4, 26 + rng.random() * 10, '#3a7a3a')
    a = composite(a, props(mid, 2, outline=None, fog='#90b8b0', fog_amt=0.25))
    a = ground(a, '#5a9a3a', '#4a8a34', 4, path='#b89a68', grass='#6ab040')

    def near(c):
        oak(c, 14, 150, 64, '#3a8a30')
        pine(c, 230, 156, 70, '#2a6a30')
        bush(c, 50, 160, 10, '#3a7a2a')
        bush(c, 196, 160, 12, '#3a7a2a')
        rock(c, 172, 158, 7, '#8a8a90')
        for (x, y, col) in [(70, 150, '#f0e040'), (84, 154, '#f05050'), (160, 148, '#f0f0f0'), (40, 140, '#e070e0')]:
            c.px(x, y, col)
            c.px(x + 1, y + 1, col)
    a = composite(a, props(near, 3))
    return vignette(a, 0.25)


def zone_nebelmoor():
    a = sky('#3a5650', '#a8b890', extra='#c8d0a0')
    a = disc(a, 60, 34, 12, '#e8f0d0', glow='#c8d8b0', glow_r=26)
    a = fill(a, ridge(11, 98, 18, 50), '#4a6058', 11, fog='#90a890', fog_amt=0.45)

    def mid(c):
        rng = c.rng
        for i in range(10):
            x = i * 26 + rng.random() * 10
            if i % 2:
                dead_tree(c, x, 118, 30 + rng.random() * 10, '#2e3a30')
            else:
                oak(c, x, 118, 30, '#3a5a3a', '#3a3024')
    a = composite(a, props(mid, 12, outline=None, fog='#8aa088', fog_amt=0.4))
    a = ground(a, '#4a5a34', '#3e4e2c', 13, grass='#5a7a3a')
    # pools
    y, x = np.mgrid[0:H, 0:W]
    for (cx, cy, rx, ry) in [(60, 142, 40, 7), (190, 136, 34, 5), (128, 154, 30, 4)]:
        m = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1
        a[m] = np.array(rgb('#2a4a48')) * (0.9 + 0.25 * ((x[m] + y[m] * 3) % 7 == 0))[:, None]
    a = fog_band(a, '#b8c8a8', 100, 130, 0.5)

    def near(c):
        dead_tree(c, 18, 158, 70, '#24302a')
        for x in (90, 98, 104, 170, 176, 226):
            c.chain([(x, 160), (x + 1, 140), (x + 2, 132)], 0.9, 0.5, c.M('#6a7a3a'))
            c.ell(x + 2, 134, 1.2, 3, c.M('#6a4a2a'))
    a = composite(a, props(near, 13))
    return vignette(a, 0.4)


def zone_rotfels():
    a = sky('#4a7ad0', '#f8c890', extra='#f8a070')
    a = disc(a, 40, 40, 10, '#fff4d0', glow='#ffd0a0', glow_r=30)
    a = clouds(a, 21, '#ffe8d8', 8, 40, 0.5)
    a = fill(a, mesa(21, 104, 48), '#b05a3a', 21, col2='#9a4a30', fog='#e0a080', fog_amt=0.35)
    a = fill(a, mesa(22, 116, 26), '#a04a2a', 22, col2='#8a3c24', fog='#d09070', fog_amt=0.15)
    a = ground(a, '#b8784a', '#a0663e', 23, path='#d0a070')

    def near(c):
        rng = c.rng
        rock(c, 20, 156, 16, '#8a4a30')
        rock(c, 214, 152, 12, '#9a5434')
        for x in (70, 150, 186):
            bush(c, x, 132 + rng.random() * 6, 5, '#7a7a30')
        for (x, y) in [(110, 150), (40, 136)]:
            c.pxs([(x, y), (x + 2, y), (x + 1, y - 1)], '#e8e0d0')
    a = composite(a, props(near, 24))
    return vignette(a, 0.3)


def zone_sonnenglut():
    a = sky('#3a8ae8', '#f8e8b0', extra='#f8d890')
    a = disc(a, 180, 30, 14, '#fffbe0', glow='#fff0b0', glow_r=40)
    # pyramid
    def pyr(c):
        m = c.M('#d8b070')
        c.poly([(40, 110), (78, 62), (116, 110)], m, shade=0.62, grad=0.6, gdir=(1, 0))
        c.poly([(150, 112), (170, 86), (190, 112)], m, shade=0.62, grad=0.6, gdir=(1, 0))
    a = composite(a, props(pyr, 30, outline=None, fog='#f0d8a8', fog_amt=0.4))
    a = fill(a, 104 - (np.sin(np.arange(W) / 22) * 6 + np.sin(np.arange(W) / 9 + 1) * 3), '#e0b870', 31, col2='#d0a860', tex=0.04)
    a = fill(a, 116 - (np.sin(np.arange(W) / 30 + 2) * 6), '#e8c078', 32, col2='#d8b068', tex=0.04)
    a = ground(a, '#e8c480', '#d8b070', 33)
    y = np.arange(H)[:, None]
    rip = ((np.arange(W)[None, :] + y * 3 + (np.sin(y / 3.0) * 4)).astype(int) % 11 == 0) & (y > GROUND + 4)
    a[rip] = a[rip] * 0.86

    def near(c):
        palm(c, 16, 156, 70)
        palm(c, 222, 152, 60)
        rock(c, 186, 158, 8, '#b08a5a')
        for x in (60, 140):
            c.chain([(x, 140), (x - 3, 136), (x - 1, 133)], 0.8, 0.4, c.M('#e8e0c8'))
    a = composite(a, props(near, 34))
    return vignette(a, 0.25)


def zone_frostgipfel():
    a = sky('#7aa0d0', '#eaf2fa')
    a = clouds(a, 41, '#ffffff', 2, 30, 0.5)
    a = fill(a, ridge(41, 96, 56, 40, sharp=True), '#b8c8e0', 41, col2='#a8b8d4', snow='#ffffff', fog='#dce8f4', fog_amt=0.35)
    a = fill(a, ridge(42, 110, 22, 30, sharp=True), '#e0eaf6', 42, col2='#c8d8ec', fog='#e8f0f8', fog_amt=0.1)

    def mid(c):
        rng = c.rng
        for i in range(13):
            pine(c, i * 19 + rng.random() * 8, 120, 24 + rng.random() * 10, '#3a5a5a', snow='#f0f8ff')
    a = composite(a, props(mid, 42, outline=None, fog='#c0d0e0', fog_amt=0.3))
    a = ground(a, '#e8f0fa', '#d0dcee', 43, path='#c0cce0')

    def near(c):
        pine(c, 12, 158, 76, '#2a4a4a', snow='#ffffff')
        crystal(c, 210, 156, 22, '#a0d8ff')
        rock(c, 184, 158, 8, '#8a9ab0')
    a = composite(a, props(near, 44))
    rng = np.random.default_rng(45)
    for _ in range(140):
        x, y = int(rng.random() * W), int(rng.random() * H)
        a[y, x] = (255, 255, 255)
    return vignette(a, 0.25)


def zone_schattenhain():
    a = sky('#120c24', '#4a3a64', extra='#6a4a7a')
    a = stars(a, 90, 51)
    a = disc(a, 186, 34, 15, '#e8e8f8', glow='#9080c0', glow_r=36)
    a = fill(a, ridge(51, 104, 24, 40), '#2a2440', 51, fog='#4a3a64', fog_amt=0.4)

    def mid(c):
        rng = c.rng
        for i in range(11):
            dead_tree(c, i * 23 + rng.random() * 10, 120, 28 + rng.random() * 14, '#1a1626')
    a = composite(a, props(mid, 52, outline=None))
    a = ground(a, '#3a3a40', '#2e2e36', 53, path='#4a4650', grass='#3a4438')

    def near(c):
        dead_tree(c, 14, 158, 84, '#141018')
        for (x, y, s) in [(56, 140, 1.0), (82, 146, 1.2), (176, 142, 1.1), (206, 150, 1.4), (120, 136, 0.8)]:
            tomb(c, x, y, s)
    a = composite(a, props(near, 54))
    a = fog_band(a, '#8a70b0', 112, 140, 0.35)
    return vignette(a, 0.45)


def zone_glutschlund():
    a = sky('#1a0606', '#a03a14', extra='#ff6a20')

    def volc(c):
        m = c.M('#3a2222')
        c.poly([(70, 112), (118, 44), (132, 44), (190, 112)], m, shade=0.5, grad=0.5, gdir=(1, 0), tex=0.1)
        c.poly([(118, 44), (132, 44), (127, 54), (123, 50)], c.M('#ff8030'), shade=0.9, edge=False)
        c.chain([(125, 48), (122, 66), (118, 84), (112, 104)], 1.6, 2.6, c.M('#ff6020'), flat=0.9, edge=False)
    a = composite(a, props(volc, 61, outline=None))
    a = torch(a, 125, 42, '#ffa040', 46)
    a = fill(a, ridge(61, 112, 14, 30, sharp=True), '#2a1818', 61, fog='#6a2a1a', fog_amt=0.25)
    a = ground(a, '#2e2424', '#241c1e', 63)
    rng = np.random.default_rng(64)
    for _ in range(9):
        x, y = rng.random() * W, GROUND + 4 + rng.random() * 30
        for s in range(14):
            xi, yi = int(x), int(y)
            if 0 <= xi < W and 0 <= yi < H:
                a[yi, xi] = rgb('#ff7020') if s % 3 else rgb('#ffd040')
            x += rng.random() * 2.4 - 0.7
            y += rng.random() * 1.4 - 0.7
    for _ in range(70):
        x, y = int(rng.random() * W), int(rng.random() * GROUND)
        a[y, x] = rgb('#ffb060') if rng.random() < 0.5 else rgb('#5a4a48')

    def near(c):
        rock(c, 18, 158, 18, '#2a1e1e')
        rock(c, 220, 158, 14, '#2a1e1e')
        crystal(c, 196, 152, 14, '#ff6a30')
    a = composite(a, props(near, 65))
    return vignette(a, 0.4)


def zone_leerenriss():
    a = sky('#06040e', '#2a1448')
    a = stars(a, 160, 71, ymax=GROUND)
    n = value_noise(W, H, 50, 72, 4)
    neb = np.clip((n - 0.5) * 3, 0, 1)
    neb = np.floor((neb + (bayer(H, W) - 0.5) / 4) * 4) / 4
    a = a + (np.array(rgb('#7a2aa8'), float) - a) * neb[:, :, None] * 0.5
    n2 = value_noise(W, H, 34, 73, 3)
    neb2 = np.floor((np.clip((n2 - 0.6) * 4, 0, 1) + (bayer(H, W) - 0.5) / 4) * 4) / 4
    a = a + (np.array(rgb('#20a0a0'), float) - a) * neb2[:, :, None] * 0.35
    a = disc(a, 60, 40, 18, '#1a0a24', glow='#c060ff', glow_r=20)

    def isl(c):
        for (x, y, r) in [(170, 50, 14), (30, 76, 9), (110, 30, 6), (210, 92, 8)]:
            m = c.M('#3a2a50')
            c.poly([(x - r, y), (x + r, y), (x + r * 0.3, y + r * 1.4), (x - r * 0.2, y + r * 1.1)], m, shade=0.45, grad=0.4)
            c.ell(x, y, r, r * 0.3, c.M('#5a4a7a'))
            crystal(c, x, y, r * 0.8, '#c080ff')
    a = composite(a, props(isl, 74))
    a = fill(a, ridge(75, 114, 12, 25, sharp=True), '#24183a', 75)
    a = ground(a, '#2a2040', '#221a36', 76)

    def near(c):
        crystal(c, 20, 158, 30, '#a060ff')
        crystal(c, 220, 156, 24, '#40e0d0')
        rock(c, 186, 158, 7, '#3a2a50')
    a = composite(a, props(near, 77))
    return vignette(a, 0.4)


def town():
    a = sky('#5a9ae0', '#e0eef4', extra='#f0e8c8')
    a = clouds(a, 81, '#ffffff', 4, 46, 0.48)
    a = fill(a, ridge(81, 100, 20, 60), '#6a8aa8', 81, fog='#b8d0e0', fog_amt=0.3)

    def walls(c):
        c.rect(0, 92, 240, 26, c.M('#a8a094'), shade=0.6, tex=0.15)
        for x in range(0, 240, 8):
            c.rect(x, 88, 5, 5, c.M('#a8a094'), shade=0.7)
        for (x, w, h, roof, ban) in [(30, 18, 50, '#3a5aa8', '#c02020'), (90, 24, 70, '#3a5aa8', '#2a4ab0'), (150, 22, 60, '#3a5aa8', '#c02020'), (214, 18, 46, '#3a5aa8', '#2a4ab0')]:
            tower(c, x, 118, w, h, '#b8b0a4', roof, ban)
        c.ell(120, 118, 10, 14, c.M('#2a1a10'), flat=0.15, clip=lambda X, Y: Y < 118)
    a = composite(a, props(walls, 82))
    a = ground(a, '#5a9a3a', '#4a8a34', 83, path='#b0a888', grass='#6ab040')

    def near(c):
        oak(c, 12, 158, 60, '#3a8a30')
        c.rect(196, 132, 34, 24, c.M('#8a5a34'), shade=0.6, tex=0.2)
        c.poly([(192, 133), (234, 133), (213, 118)], c.M('#a03020'), shade=0.6)
        c.rect(206, 142, 8, 14, c.M('#3a2414'), shade=0.2)
    a = composite(a, props(near, 84))
    return vignette(a, 0.25)


def arena():
    a = sky('#4a7ad0', '#f0d8a8')
    y, x = np.mgrid[0:H, 0:W]
    wall_top = 70 + ((x - 120) / 120) ** 2 * 12
    m = (y >= wall_top) & (y < 118)
    nz = value_noise(W, H, 6, 91, 3)
    a[m] = np.array(rgb('#a08060'))[None, :] * (0.85 + 0.3 * (nz[m] > 0.5))[:, None]
    rng = np.random.default_rng(92)
    for _ in range(900):
        xx = int(rng.random() * W)
        yy = int(wall_top[0, xx] + 4 + rng.random() * 30)
        if yy < 116:
            a[yy, xx] = rgb(['#c04040', '#4060c0', '#e0c040', '#e0e0e0', '#40a040'][int(rng.random() * 5)])
    for xx in range(0, W, 30):
        a[(y >= wall_top) & (y < 118) & (np.abs(x - xx) < 2)] = rgb('#7a5a40')
    a[(y >= 112) & (y < 118)] = rgb('#5a4030')
    a = ground(a, '#d8b880', '#c8a870', 93)
    return vignette(a, 0.3)


# --------------------------------------------------------------------------------------------- interiors
def hall(wall, mortar, floor, floor2, light, pillar, seed, arch='#0c0810', extra=None, banner=None, lights=True):
    a = np.zeros((H, W, 3))
    y, x = np.mgrid[0:H, 0:W]
    nz = value_noise(W, H, 5, seed, 3)
    wc = np.array(rgb(wall), float)
    row = y // 7
    off = (row % 2) * 6
    brick = (((x + off) % 12) == 0) | ((y % 7) == 0)
    a[:] = wc * (0.82 + 0.35 * nz[:, :, None])
    a[brick] = rgb(mortar)
    # arches
    for cx in (60, 180):
        m = (((x - cx) / 22) ** 2 + ((y - 52) / 30) ** 2 <= 1) | ((np.abs(x - cx) <= 22) & (y >= 52) & (y < GROUND))
        a[m] = rgb(arch)
        rim = (((x - cx) / 25) ** 2 + ((y - 52) / 33) ** 2 <= 1) & ~m & (y < 60)
        a[rim] = np.array(rgb(pillar), float) * 1.1
    if extra:
        a = extra(a)
    # pillars
    pc = np.array(rgb(pillar), float)
    for cx in (10, 120, 230):
        m = (np.abs(x - cx) <= 9) & (y < GROUND)
        shade = 0.7 + 0.5 * (1 - np.abs(x - cx) / 9) - (x - cx) / 40
        a[m] = pc * np.clip(shade[m], 0.4, 1.3)[:, None]
        a[(np.abs(x - cx) <= 11) & ((y // 2) % 18 == 0) & (y < GROUND)] = pc * 1.25
    if banner:
        for cx in (60, 180):
            m = (np.abs(x - cx) <= 7) & (y >= 14) & (y < 40 + (np.abs(x - cx) < 3) * 4)
            a[m] = np.array(rgb(banner), float) * (0.85 + 0.3 * ((x[m] - cx) < 0))[:, None]
            a[(np.abs(x - cx) <= 2) & (y >= 22) & (y < 28)] = rgb('#f0c040')
    # floor
    fm = y >= GROUND
    t = (((x + (y - GROUND) * ((x - 120) / 60)) // 16 + (y - GROUND) // 9) % 2).astype(bool)
    f1, f2 = np.array(rgb(floor), float), np.array(rgb(floor2), float)
    fl = np.where(t[:, :, None], f1, f2) * (0.85 + 0.25 * nz[:, :, None])
    fl = fl * (0.75 + 0.4 * ((y - GROUND) / (H - GROUND)))[:, :, None]
    a[fm] = fl[fm]
    a[(y == GROUND)] = np.array(rgb(pillar), float) * 0.6
    if lights:
        for (lx, ly) in ((34, 60), (86, 60), (154, 60), (206, 60)):
            a = torch(a, lx, ly, light, 30)
    return vignette(a, 0.45)


def inst_mine():
    def extra(a):
        y, x = np.mgrid[0:H, 0:W]
        for cx in (34, 86, 154, 206):
            a[(np.abs(x - cx) <= 2) & (y > 20) & (y < GROUND)] = rgb('#6a4a2a')
        a[(y >= 18) & (y < 23)] = rgb('#6a4a2a')
        rng = np.random.default_rng(5)
        for _ in range(40):
            xx, yy = int(rng.random() * W), int(rng.random() * GROUND)
            a[yy, xx] = rgb('#60c0ff')
        return a
    return hall('#5a4a40', '#3a2e28', '#4a4038', '#40362e', '#ffc060', '#6a5444', 101, extra=extra)


def inst_cave():
    def extra(a):
        y, x = np.mgrid[0:H, 0:W]
        for cx in range(8, W, 22):
            ln = 10 + (cx * 7) % 18
            a[(np.abs(x - cx) <= (ln - y) / 5) & (y < ln)] = rgb('#3a3248')
        for (cx, cy) in [(40, 110), (200, 106), (130, 114)]:
            a = torch(a, cx, cy, '#c060ff', 20)
        return a
    return hall('#3a3a4a', '#2a2a38', '#344034', '#2c362c', '#80ff80', '#4a4a5a', 102, extra=extra, lights=False)


def inst_temple():
    def extra(a):
        y, x = np.mgrid[0:H, 0:W]
        m = (y >= 8) & (y < 14)
        a[m & ((x // 3 + y) % 4 == 0)] = rgb('#3a6ab0')
        a[m & ((x // 3 + y) % 4 == 1)] = rgb('#c09030')
        return a
    return hall('#c8a070', '#a07a50', '#d0b080', '#c0a070', '#ffd060', '#d8b880', 103, extra=extra, banner='#3a6ab0')


def inst_ice():
    def extra(a):
        y, x = np.mgrid[0:H, 0:W]
        for cx in range(4, W, 10):
            ln = 6 + (cx * 13) % 12
            a[(np.abs(x - cx) <= (ln - y) / 4) & (y < ln)] = rgb('#e0f4ff')
        return a
    return hall('#8ab0d8', '#6a90c0', '#c8dcf0', '#b0c8e4', '#60d0ff', '#a8c8e8', 104, extra=extra, banner='#2a4a8a')


def inst_cathedral():
    def extra(a):
        y, x = np.mgrid[0:H, 0:W]
        for cx in (60, 180):
            m = (((x - cx) / 10) ** 2 + ((y - 40) / 18) ** 2 <= 1)
            cols = np.array([rgb('#c02030'), rgb('#6030a0'), rgb('#e0a020'), rgb('#2050c0')])
            idx = ((x // 4 + y // 5) % 4)
            a[m] = cols[idx[m]]
        return a
    return hall('#4a3a40', '#2e2428', '#3a3034', '#30282c', '#ff9040', '#5a4a50', 105, arch='#140a10', extra=extra, banner='#7a1818')


def inst_abyss():
    a = sky('#05030a', '#24103a', horizon=H)
    a = stars(a, 120, 106, ymax=GROUND)
    a = disc(a, 120, 50, 30, '#0a0410', glow='#9040ff', glow_r=26)
    y, x = np.mgrid[0:H, 0:W]
    eye = ((x - 120) / 16) ** 2 + ((y - 50) / 8) ** 2 <= 1
    a[eye] = rgb('#40ffe0')
    a[((x - 120) / 4) ** 2 + ((y - 50) / 7) ** 2 <= 1] = rgb('#0a0410')
    plat = (y >= GROUND) & (np.abs(x - 120) < 150 - (y - GROUND) * 0)
    nz = value_noise(W, H, 6, 107, 3)
    a[plat] = np.array(rgb('#2a2040'))[None, :] * (0.8 + 0.4 * (nz[plat] > 0.5))[:, None]
    a[(y >= GROUND) & (y < GROUND + 2)] = rgb('#6040a0')
    for (cx, cy) in ((20, 100), (220, 100)):
        a = torch(a, cx, cy, '#a060ff', 24)
    return vignette(a, 0.45)


def raid_glut():
    def extra(a):
        y, x = np.mgrid[0:H, 0:W]
        lava = (y >= 100) & (y < GROUND)
        a[lava] = np.where(((x[lava] + y[lava] * 2) // 5 % 3 == 0)[:, None], rgb('#ffd040'), rgb('#ff6020'))
        for cx in (60, 180):
            a = torch(a, cx, 110, '#ff8020', 40)
        return a
    return hall('#2a1a1a', '#160c0c', '#3a2a28', '#2e2020', '#ff7020', '#3a2626', 111, arch='#ff5010', extra=extra, banner='#a02010')


def raid_nebel():
    def extra(a):
        y, x = np.mgrid[0:H, 0:W]
        throne = (np.abs(x - 120) < 12) & (y > 50) & (y < GROUND)
        a[throne] = rgb('#a0c8f0')
        a[(np.abs(x - 120) < 16) & (y > 44) & (y < 52)] = rgb('#d0e8ff')
        return a
    return hall('#5a6a88', '#3a4a68', '#8a9ab8', '#7a8aa8', '#80c0ff', '#7a8aa8', 112, arch='#0a1428', extra=extra, banner='#1a3060')


def raid_thron():
    a = inst_abyss()
    y, x = np.mgrid[0:H, 0:W]
    rng = np.random.default_rng(113)
    for _ in range(6):
        cx = rng.random() * W
        for yy in range(GROUND - 60, GROUND):
            xx = int(cx + math.sin(yy / 6 + cx) * 4)
            for d in range(-2, 3):
                if 0 <= xx + d < W:
                    a[yy, xx + d] = rgb('#3a1a5a') if abs(d) < 2 else rgb('#1a0a2a')
    return a


def catalogue():
    B = dict(
        bg_goldhain=zone_goldhain(), bg_nebelmoor=zone_nebelmoor(), bg_rotfels=zone_rotfels(),
        bg_sonnenglut=zone_sonnenglut(), bg_frostgipfel=zone_frostgipfel(), bg_schattenhain=zone_schattenhain(),
        bg_glutschlund=zone_glutschlund(), bg_leerenriss=zone_leerenriss(), bg_town=town(), bg_arena=arena(),
        bg_mine=inst_mine(), bg_cave=inst_cave(), bg_temple=inst_temple(), bg_ice=inst_ice(),
        bg_cathedral=inst_cathedral(), bg_abyss=inst_abyss(), bg_raid_glut=raid_glut(), bg_raid_nebel=raid_nebel(),
        bg_raid_thron=raid_thron(),
    )
    return {k: to_img(v).convert('RGB') for k, v in B.items()}

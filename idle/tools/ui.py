"""UI textures: stone and parchment tiles, gilded 9-slice frames, buttons, bar fills, quest markers.
Frames and buttons are drawn at 1x and doubled so border-image needs no scaling on a 2x screen."""
import numpy as np
from PIL import Image

from px import BAYER4, Canvas, rgb, shade_col, value_noise


def dbl(img, f=2):
    return img.resize((img.width * f, img.height * f), Image.NEAREST)


def tile(w, h, c1, c2, seed, scale=10, cracks=False, contrast=1.0):
    n = value_noise(w, h, scale, seed, 4)
    n2 = value_noise(w, h, scale / 3, seed + 9, 2)
    bay = BAYER4[np.arange(h)[:, None] % 4, np.arange(w)[None, :] % 4]
    t = np.clip((n - 0.5) * 2.5 * contrast + 0.5 + (bay - 0.5) * 0.35, 0, 1)
    t = np.round(t * 4) / 4
    a, b = np.array(rgb(c1), float), np.array(rgb(c2), float)
    arr = a + (b - a) * t[:, :, None]
    arr *= (0.92 + 0.16 * (n2 > 0.55))[:, :, None]
    if cracks:
        e = np.abs(n2 - 0.5) < 0.018
        arr[e] *= 0.6
    out = np.zeros((h, w, 4), np.uint8)
    out[:, :, :3] = np.clip(arr, 0, 255)
    out[:, :, 3] = 255
    return Image.fromarray(out, 'RGBA')


def frame9(size, slc, metal, inner_col=None, gem=None, seed=0, fill=None):
    """A square 9-slice frame: bevelled metal border `slc` px wide, rivets in the corners."""
    c = Canvas(size, size, seed=seed)
    m = c.M(metal, contrast=1.2)
    s = slc
    w = size
    # outer and inner bevel rects drawn as polys so shading runs top-left light
    c.poly([(0, 0), (w, 0), (w, w), (0, w)], m, shade=0.62, grad=0.5, gdir=(1, 1), tex=0.15)
    img = c.render(outline=None)
    arr = np.array(img).astype(int)
    # hollow the middle
    inner = slice(s, w - s)
    if fill is None:
        arr[inner, inner, 3] = 0
    else:
        arr[inner, inner, :3] = rgb(fill)
        arr[inner, inner, 3] = 255
    # dark lines: outermost and innermost
    for (y0, y1, x0, x1) in [(0, 1, 0, w), (w - 1, w, 0, w), (0, w, 0, 1), (0, w, w - 1, w)]:
        arr[y0:y1, x0:x1, :3] = (16, 10, 6)
        arr[y0:y1, x0:x1, 3] = 255
    for (y0, y1, x0, x1) in [(s - 1, s, s - 1, w - s + 1), (w - s, w - s + 1, s - 1, w - s + 1), (s - 1, w - s + 1, s - 1, s), (s - 1, w - s + 1, w - s, w - s + 1)]:
        arr[y0:y1, x0:x1, :3] = (16, 10, 6)
        arr[y0:y1, x0:x1, 3] = 255
    # highlights
    hi = np.array(rgb(metal)) * 1.35
    arr[1, 1:w - 1, :3] = np.clip(hi, 0, 255)
    arr[1:w - 1, 1, :3] = np.clip(hi, 0, 255)
    lo = np.array(rgb(metal)) * 0.5
    arr[w - 2, 1:w - 1, :3] = lo
    arr[1:w - 1, w - 2, :3] = lo
    # inner groove
    if inner_col:
        g = s // 2
        arr[g, g:w - g, :3] = rgb(inner_col)
        arr[g:w - g, g, :3] = rgb(inner_col)
        arr[w - g - 1, g:w - g, :3] = rgb(inner_col)
        arr[g:w - g, w - g - 1, :3] = rgb(inner_col)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    if gem:
        g = Canvas(size, size, seed=seed + 1)
        gm = g.M(gem)
        r = s * 0.3
        for (x, y) in [(s / 2, s / 2), (w - s / 2, s / 2), (s / 2, w - s / 2), (w - s / 2, w - s / 2)]:
            g.ell(x, y, r, r, gm, amb=0.4)
        out.alpha_composite(g.render(outline=(16, 10, 6, 255)))
    return out


def button(w, h, base, rim, seed=0, pressed=False):
    c = Canvas(w, h, seed=seed)
    r = c.M(rim, contrast=1.2)
    b = c.M(base, contrast=1.1)
    c.poly([(0, 0), (w, 0), (w, h), (0, h)], r, shade=0.65, grad=0.5, gdir=(0, 1))
    c.poly([(2, 2), (w - 2, 2), (w - 2, h - 2), (2, h - 2)], b, shade=0.5 if pressed else 0.62, grad=-0.5 if pressed else 0.55, gdir=(0, 1), tex=0.08)
    img = c.render(outline=None)
    arr = np.array(img)
    arr[0, :, :3] = (12, 8, 6)
    arr[-1, :, :3] = (12, 8, 6)
    arr[:, 0, :3] = (12, 8, 6)
    arr[:, -1, :3] = (12, 8, 6)
    if not pressed:
        arr[2, 3:-3, :3] = np.clip(np.array(rgb(base)) * 1.6, 0, 255)
    return Image.fromarray(arr, 'RGBA')


def bar(col, w=4, h=12):
    base = np.array(rgb(col), float)
    arr = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        t = y / (h - 1)
        f = 1.35 - t * 0.75
        if y == 1:
            f = 1.7
        if y == h - 2:
            f = 0.55
        arr[y, :, :3] = np.clip(base * f, 0, 255)
        arr[y, :, 3] = 255
    arr[:, w - 1, :3] = (arr[:, w - 1, :3] * 0.85).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def marker(char, col):
    c = Canvas(10, 16)
    m = c.M(col, contrast=1.1)
    if char == '!':
        c.poly([(2.5, 1), (7.5, 1), (6.2, 10), (3.8, 10)], m, shade=0.75, grad=0.5)
        c.ell(5, 13.2, 2.2, 2.2, m)
    else:
        c.cap(2.5, 4, 5, 1.6, 1.4, 1.4, m)
        c.cap(5, 1.6, 7.5, 4, 1.4, 1.4, m)
        c.cap(7.5, 4, 5, 7.5, 1.4, 1.4, m)
        c.cap(5, 7.5, 5, 9.5, 1.4, 1.4, m)
        c.ell(5, 13.2, 1.9, 1.9, m)
    return c.render(outline=(20, 12, 4, 255))


def ring(size, metal):
    c = Canvas(size, size)
    m = c.M(metal, contrast=1.2)
    r = size / 2
    c.ell(r, r, r - 1, r - 1, m, tex=0.12)
    img = c.render(outline=(16, 10, 6, 255))
    arr = np.array(img)
    y, x = np.mgrid[0:size, 0:size] + 0.5
    d = np.sqrt((x - r) ** 2 + (y - r) ** 2)
    arr[d < r - 4.2, 3] = 0
    arr[(d >= r - 4.2) & (d < r - 3.4), :3] = (16, 10, 6)
    return Image.fromarray(arr, 'RGBA')


def catalogue():
    U = {}
    U['ui_stone'] = tile(64, 64, '#2a2a30', '#3a3a44', 1, 9, cracks=True)
    U['ui_stone_dark'] = tile(64, 64, '#16151a', '#222128', 2, 9, cracks=True)
    U['ui_parch'] = tile(96, 96, '#d8c398', '#e2cfa8', 3, 24, contrast=0.22)
    U['ui_wood'] = tile(64, 32, '#3a2416', '#4e3220', 4, 12)
    w = np.array(U['ui_wood'])
    for y in (0, 15, 16, 31):
        w[y, :, :3] = (w[y, :, :3] * 0.55).astype(np.uint8)
    U['ui_wood'] = Image.fromarray(w, 'RGBA')
    U['ui_frame_gold'] = dbl(frame9(24, 7, '#c8a050', inner_col='#6a4a1a', gem='#8a1a1a', seed=5))
    U['ui_frame_iron'] = dbl(frame9(16, 4, '#6a6a74', seed=6))
    U['ui_frame_item'] = dbl(frame9(16, 3, '#4a4a52', seed=7))
    U['ui_btn'] = dbl(button(24, 14, '#9a1a14', '#c8a050', 8))
    U['ui_btn_down'] = dbl(button(24, 14, '#6a1010', '#a88040', 8, pressed=True))
    U['ui_btn_off'] = dbl(button(24, 14, '#4a4646', '#7a7470', 8))
    U['ui_btn_gold'] = dbl(button(24, 14, '#b8861a', '#f0d070', 9))
    U['ui_btn_blue'] = dbl(button(24, 14, '#1e3c7a', '#a8b8d8', 10))
    U['ui_btn_green'] = dbl(button(24, 14, '#1e6a24', '#c8a050', 11))
    for n, col in [('green', '#28b030'), ('red', '#c82020'), ('blue', '#2050d8'), ('orange', '#e07818'), ('purple', '#8a3ac8'),
                   ('rested', '#3a7ad8'), ('yellow', '#e0b820'), ('grey', '#4a4a50'), ('teal', '#18a0a0')]:
        U['bar_' + n] = bar(col)
    U['bar_bg'] = bar('#141216')
    U['q_bang'] = dbl(marker('!', '#ffd200'))
    U['q_turnin'] = dbl(marker('?', '#ffd200'))
    U['q_daily'] = dbl(marker('!', '#40a0ff'))
    U['q_grey'] = dbl(marker('!', '#8a8a8a'))
    U['ui_ring'] = dbl(ring(26, '#c8a050'))
    U['ui_ring_elite'] = dbl(ring(26, '#e8c060'))
    U['ui_ring_silver'] = dbl(ring(26, '#a0a8b8'))
    return U

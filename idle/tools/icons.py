"""32x32 painted pixel icons in square bevelled frames, like an MMO's action-bar icons."""
import math

import numpy as np
from PIL import Image

import sprites
from px import Canvas, Paint, mix, rgb, shade_col, value_noise

TIERS = [
    dict(metal='#b08a58', leather='#8a5a34', cloth='#7a6a50', gem='#70d050', accent='#6a8a3a', bg='#3a2a1a'),
    dict(metal='#a8b0b8', leather='#6a5040', cloth='#4a6a8a', gem='#4a90ff', accent='#3a5a8a', bg='#1e2a3a'),
    dict(metal='#d0dcf0', leather='#4a4060', cloth='#3a60b0', gem='#40d0ff', accent='#2a58c0', bg='#16244a'),
    dict(metal='#f0c850', leather='#7a2a20', cloth='#a02828', gem='#ff4060', accent='#c03030', bg='#4a1414'),
    dict(metal='#b890f8', leather='#3a2460', cloth='#5a2a9a', gem='#60fff0', accent='#7040e0', bg='#24123e'),
    dict(metal='#ffa040', leather='#5a2410', cloth='#c05010', gem='#fff070', accent='#ff7020', bg='#4a1a06'),
]


ICON = 96


def bg(theme, seed=0):
    n = ICON
    col = np.array(rgb(theme), float)
    y, x = np.mgrid[0:n, 0:n] + 0.5
    d = np.sqrt((x - n * 0.42) ** 2 + (y - n * 0.38) ** 2) / (n * 0.7)
    nz = value_noise(n, n, 14, seed, 4)
    nz2 = value_noise(n, n, 4, seed + 3, 2)
    f = np.clip(1.55 - d * 1.15 + (nz - 0.5) * 0.45 + (nz2 - 0.5) * 0.12, 0.25, 1.9)
    arr = np.zeros((n, n, 4), np.uint8)
    arr[:, :, :3] = np.clip(col[None, None, :] * f[:, :, None], 0, 255)
    arr[:, :, 3] = 255
    return Image.fromarray(arr, 'RGBA')


def frame(img):
    arr = np.array(img).astype(float)
    n = arr.shape[0]
    y, x = np.mgrid[0:n, 0:n]
    edge = np.minimum(np.minimum(x, y), np.minimum(n - 1 - x, n - 1 - y))
    # inner bevel: darken toward the border, light top-left lip
    shade = np.clip(edge / 6.0, 0, 1) * 0.35 + 0.65
    arr[:, :, :3] *= shade[:, :, None]
    lip = (edge == 2) & ((x < n / 2) | (y < n / 2)) & (x + y < n)
    arr[lip, :3] = np.clip(arr[lip, :3] * 1.6 + 30, 0, 255)
    arr[edge <= 1, :3] = (8, 6, 6)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


def icon(theme, draw, seed=0, glow=None, outline=(14, 8, 10, 230)):
    c = Paint(ICON, ICON, design=32, seed=seed, ss=3)
    draw(c)
    fg = c.render(outline=outline, glow=glow, glow_r=1.4, glow_a=0.7, out_w=0.7)
    b = bg(theme, seed)
    b.alpha_composite(fg)
    return frame(b)


def diag_blade(c, x1, y1, x2, y2, w1, w2, m, **kw):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    c.poly([(x1 + nx * w1, y1 + ny * w1), (x2 + nx * w2, y2 + ny * w2), (x2 + dx / L * 2.5, y2 + dy / L * 2.5),
            (x2 - nx * w2, y2 - ny * w2), (x1 - nx * w1, y1 - ny * w1)], m, shade=0.7, grad=0.5, gdir=(nx, ny), **kw)


def bez(p0, p1, p2, n=8):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]


# --------------------------------------------------------------------------------------------- items
def i_sword(T):
    def d(c):
        diag_blade(c, 12, 20, 27, 5, 2.4, 1.6, c.M(T['metal'], contrast=1.25, gloss=0.8))
        c.line(13, 19, 26, 6, shade_col(T['metal'], 1.25))
        c.cap(6, 18, 14, 26, 1.4, 1.4, c.M(T['metal']))
        c.cap(4, 28, 10, 22, 1.4, 1.4, c.M(T['leather']))
        c.ell(4, 28.5, 2, 2, c.M(T['gem']), amb=0.5)
    return d


def i_staff(T):
    def d(c):
        c.cap(4, 30, 21, 11, 1.4, 1.4, c.M(T['leather'] if T is not TIERS[0] else '#7a5434'), tex=0.2)
        g = c.M(T['metal'])
        c.chain([(18, 14), (17, 7), (21, 4)], 1.1, 0.6, g)
        c.chain([(18, 14), (25, 15), (28, 11)], 1.1, 0.6, g)
        c.ell(22.5, 9.5, 4.4, 4.4, c.M(T['gem']), amb=0.55)
        c.px(21, 8, '#ffffff')
    return d


def i_bow(T):
    def d(c):
        pts = bez((5, 27), (26, 26), (27, 5), 9)
        c.chain(pts, 1.8, 1.8, c.M(T['leather'] if T is not TIERS[0] else '#8a5a2c'))
        c.cap(17, 23, 22, 19, 2.2, 2.2, c.M(T['metal']))
        c.line(5, 27, 27, 5, '#f0e8d0')
        c.ell(5, 27, 1.8, 1.8, c.M(T['gem']))
        c.ell(27, 5, 1.8, 1.8, c.M(T['gem']))
    return d


def i_mace(T):
    def d(c):
        c.cap(5, 28, 17, 15, 1.5, 1.5, c.M(T['leather']), tex=0.2)
        c.ell(20, 12, 6.5, 6.5, c.M(T['metal'], contrast=1.2))
        for a in range(8):
            t = a / 8 * math.tau
            c.cap(20 + math.cos(t) * 5, 12 + math.sin(t) * 5, 20 + math.cos(t) * 8, 12 + math.sin(t) * 8, 1.4, 0.5, c.M(T['metal']))
        c.ell(20, 12, 2, 2, c.M(T['gem']), amb=0.5)
        c.ell(4.5, 29, 1.8, 1.8, c.M(T['metal']))
    return d


def i_helm(T):
    def d(c):
        m = c.M(T['metal'], contrast=1.2, gloss=0.75)
        c.ell(16, 16, 10, 10, m, clip=lambda x, y: y < 22)
        c.rect(6, 17, 20, 8, m, shade=0.55)
        c.rect(15, 6, 2.4, 16, c.M(shade_col(T['metal'], 1.15)), shade=0.85, edge=False)
        c.line(8, 19, 24, 19, '#100808')
        c.line(9, 20, 23, 20, '#2a1a1a')
        c.rect(7, 24, 18, 2, c.M(T['accent']), shade=0.7)
        if T is TIERS[3] or T is TIERS[4] or T is TIERS[5]:
            h = c.M('#f0e8d0')
            c.chain([(7, 12), (3, 7), (4, 2)], 2, 0.6, h)
            c.chain([(25, 12), (29, 7), (28, 2)], 2, 0.6, h)
        if T is TIERS[2]:
            c.chain([(16, 5), (20, 1), (26, 2)], 1.8, 1.0, c.M(T['accent']))
    return d


def i_shoulder(T):
    def d(c):
        m = c.M(T['metal'], contrast=1.2, gloss=0.75)
        if T is TIERS[3] or T is TIERS[4] or T is TIERS[5]:
            for x in (10, 16, 22):
                c.poly([(x - 2.5, 12), (x, 1), (x + 2.5, 12)], c.M('#e8e0d0'), shade=0.8)
        c.ell(16, 18, 13, 9, m, clip=lambda x, y: y < 22)
        c.ell(16, 14, 9, 4.5, c.M(shade_col(T['metal'], 1.12)), edge=False)
        c.rect(3, 20, 26, 4, c.M(T['accent']), shade=0.65)
        c.rect(6, 24, 20, 3, c.M(T['leather']), shade=0.5)
        c.ell(16, 21.6, 1.6, 1.6, c.M(T['gem']))
    return d


def i_chest(T):
    def d(c):
        m = c.M(T['cloth'] if T is TIERS[0] else T['metal'], contrast=1.1)
        c.poly([(5, 7), (12, 5), (16, 9), (20, 5), (27, 7), (25, 27), (7, 27)], m, shade=0.6, grad=0.4)
        c.ell(6, 9, 4.4, 3.6, c.M(T['metal']))
        c.ell(26, 9, 4.4, 3.6, c.M(T['metal']))
        c.rect(7, 20, 18, 3, c.M(T['leather']), shade=0.5)
        c.rect(14.5, 19.5, 3, 4, c.M(T['metal']), shade=0.9)
        c.poly([(13, 11), (19, 11), (16, 17)], c.M(T['accent']), shade=0.7)
        c.px(16, 13, rgb(T['gem']))
    return d


def i_hands(T):
    def d(c):
        m = c.M(T['metal'], contrast=1.1)
        l = c.M(T['leather'])
        c.rect(8, 21, 13, 8, c.M(T['accent']), shade=0.6)
        c.ell(15, 16, 7, 7, m)
        for i, x in enumerate((10, 13.5, 17, 20.5)):
            c.cap(x, 13, x - 0.5 + i * 0.3, 4 + abs(i - 1.5), 1.7, 1.4, m)
        c.cap(22, 18, 26, 12, 2, 1.6, m)
        c.line(9, 17, 21, 17, shade_col(T['metal'], 0.5))
        c.ell(15, 25, 1.5, 1.5, c.M(T['gem']))
        _ = l
    return d


def i_legs(T):
    def d(c):
        m = c.M(T['cloth'] if T in (TIERS[0], TIERS[4]) else T['metal'], contrast=1.1)
        c.rect(7, 4, 18, 5, c.M(T['leather']), shade=0.55)
        c.cap(11, 8, 9, 28, 4.2, 3.4, m)
        c.cap(21, 8, 23, 28, 4.2, 3.4, m)
        c.ell(10, 17, 2.6, 2.2, c.M(T['metal']))
        c.ell(22, 17, 2.6, 2.2, c.M(T['metal']))
        c.rect(14.5, 4.5, 3, 4, c.M(T['gem']), shade=0.9)
    return d


def i_feet(T):
    def d(c):
        m = c.M(T['leather'] if T is TIERS[0] else T['metal'], contrast=1.1)
        c.cap(13, 5, 13, 20, 5.5, 5, m)
        c.ell(17, 23.5, 10, 4.6, m)
        c.rect(7, 26, 21, 2.5, c.M('#2a1a14'), shade=0.4)
        c.rect(7, 7, 12, 3, c.M(T['accent']), shade=0.7)
        c.ell(13, 15, 1.6, 1.6, c.M(T['gem']))
    return d


def i_trinket(T):
    def d(c):
        c.line(6, 2, 16, 12, rgb(T['metal']))
        c.line(26, 2, 16, 12, rgb(T['metal']))
        c.line(7, 2, 16, 11, shade_col(T['metal'], 0.6))
        c.ell(16, 19, 8.5, 9, c.M(T['metal'], contrast=1.2, gloss=0.8))
        c.ell(16, 19, 5.4, 6, c.M(T['gem'], contrast=0.9, gloss=1.0), amb=0.45)
        c.px(14, 16, '#ffffff')
        c.px(15, 16, '#ffffff')
        for a in range(6):
            t = a / 6 * math.tau
            c.px(16 + math.cos(t) * 7.2, 19 + math.sin(t) * 7.6, shade_col(T['metal'], 1.3))
    return d


WEAPON = dict(krieger=i_sword, magier=i_staff, jaeger=i_bow, priester=i_mace)
ARMOR = dict(head=i_helm, shoulder=i_shoulder, chest=i_chest, hands=i_hands, legs=i_legs, feet=i_feet, trinket=i_trinket)


# --------------------------------------------------------------------------------------------- misc
def coins(c):
    g = c.M('#f0c040', contrast=1.1, gloss=0.9)
    for (x, y) in [(10, 24), (21, 25), (15, 19), (12, 14), (22, 17), (17, 10)]:
        c.ell(x, y, 6.4, 4.4, g)
        c.ell(x, y - 0.6, 4.2, 2.6, c.M('#ffe070'), edge=False)
    c.pxs([(17, 8), (16, 9), (18, 9), (17, 10)], '#ffffff')


def star(c, col='#c080ff', core='#ffffff'):
    pts = []
    for i in range(10):
        r = 13 if i % 2 == 0 else 5.4
        t = -math.pi / 2 + i * math.pi / 5
        pts.append((16 + math.cos(t) * r, 17 + math.sin(t) * r))
    c.poly(pts, c.M(col), shade=0.7, grad=0.5)
    c.ell(16, 17, 3.4, 3.4, c.M(core), flat=1.0, edge=False)


def emblem_shield(col, rim, sym):
    def d(c):
        c.poly([(5, 4), (27, 4), (27, 17), (16, 29), (5, 17)], c.M(rim), shade=0.75)
        c.poly([(8, 7), (24, 7), (24, 16), (16, 25), (8, 16)], c.M(col), shade=0.6, grad=0.4)
        sym(c)
    return d


def sym_sword(c):
    c.cap(16, 9, 16, 21, 1.2, 0.8, c.M('#e8ecf4'))
    c.cap(12, 18, 20, 18, 0.9, 0.9, c.M('#f0c040'))


def sym_dragon(c):
    c.ell(16, 15, 4.4, 3.6, c.M('#f0c040'))
    c.chain([(13, 12), (10, 7), (12, 6)], 1.1, 0.5, c.M('#f0c040'))
    c.chain([(19, 12), (22, 7), (20, 6)], 1.1, 0.5, c.M('#f0c040'))
    c.px(14.5, 15, '#ff3020')
    c.px(17.5, 15, '#ff3020')


def sym_swords(c):
    c.cap(10, 9, 22, 21, 1.1, 0.8, c.M('#e8ecf4'))
    c.cap(22, 9, 10, 21, 1.1, 0.8, c.M('#e8ecf4'))


def key(c):
    g = c.M('#f0c040', contrast=1.2)
    c.ell(9, 10, 6, 6, g)
    c.ell(9, 10, 2.6, 2.6, c.M('#1a1210'), flat=0.1)
    c.cap(13, 14, 26, 27, 1.8, 1.8, g)
    c.cap(21, 26, 24, 23, 1.4, 1.4, g)
    c.cap(18, 23, 21, 20, 1.4, 1.4, g)


def chest(col, band, lock='#f0c040'):
    def d(c):
        w = c.M(col)
        b = c.M(band, contrast=1.2)
        c.rect(4, 15, 24, 13, w, shade=0.5, tex=0.15)
        c.ell(16, 15, 12, 7, w, clip=lambda x, y: y < 15.5, tex=0.15)
        c.rect(3.5, 14, 25, 2.5, b, shade=0.7)
        c.rect(8, 8, 3, 20, b, shade=0.65, edge=False)
        c.rect(21, 8, 3, 20, b, shade=0.65, edge=False)
        c.rect(13.5, 14, 5, 6, c.M(lock), shade=0.85)
        c.px(16, 17, '#1a1010')
    return d


def flask(liquid, shape='round'):
    def d(c):
        glass = c.M('#c8dce8', contrast=0.6, gloss=1.0)
        liq = c.M(liquid, contrast=1.0, gloss=0.8)
        if shape == 'round':
            c.ell(16, 20, 9.5, 9.5, glass)
            c.ell(16, 21.5, 8.3, 7.6, liq, clip=lambda x, y: y > 17, amb=0.45)
            c.cap(16, 4, 16, 11, 3.2, 3.2, glass)
        else:
            c.poly([(11, 10), (21, 10), (24, 28), (8, 28)], glass, shade=0.75)
            c.poly([(10, 16), (22, 16), (23.6, 27), (8.4, 27)], liq, shade=0.7, grad=0.5)
            c.cap(16, 4, 16, 10, 3, 3, glass)
        c.rect(12.6, 1.5, 6.8, 4, c.M('#9a6a3a'), shade=0.6)
        c.ell(12, 16, 1.6, 2.6, c.M('#ffffff'), flat=1.0, edge=False)
    return d


def ore(col):
    def d(c):
        r = c.M('#7a7570', contrast=1.1)
        c.poly([(4, 22), (8, 10), (16, 6), (26, 10), (29, 22), (22, 28), (9, 28)], r, shade=0.62, grad=0.4, tex=0.25)
        g = c.M(col, contrast=1.3)
        for (x, y, rr) in [(12, 14, 2.6), (19, 12, 2.0), (22, 20, 2.8), (13, 22, 2.0), (17, 17, 1.6)]:
            c.ell(x, y, rr, rr * 0.8, g, amb=0.45)
        c.pxs([(11, 13), (21, 19)], '#ffffff')
    return d


def herb(leaf, flower):
    def d(c):
        st = c.M(shade_col(leaf, 0.7))
        lf = c.M(leaf)
        for (x2, y2) in [(9, 8), (16, 4), (23, 9)]:
            c.cap(16, 29, x2, y2, 1.0, 0.7, st)
        for (x, y, r) in [(10, 20, 0.6), (22, 19, -0.6), (12, 13, 0.9), (20, 12, -0.9)]:
            c.ell(x, y, 5, 2.2, lf, rot=r)
        fl = c.M(flower)
        for (x, y) in [(9, 8), (16, 4), (23, 9)]:
            c.ell(x, y, 3.2, 3.2, fl, amb=0.4)
            c.px(x, y, '#fff8c0')
    return d


def fish(body, belly, fin):
    def d(c):
        f = c.M(fin)
        c.poly([(5, 16), (0.5, 9), (2, 16), (0.5, 23)], f, shade=0.6)
        c.poly([(14, 9), (20, 4), (22, 10)], f, shade=0.6)
        c.ell(16, 16, 12, 7, c.M(body), tex=0.12)
        c.ell(17, 19, 9, 3, c.M(belly), edge=False)
        c.poly([(14, 19), (17, 25), (19, 19)], f, shade=0.55)
        c.ell(24, 14.5, 1.8, 1.8, c.M('#f0f0f0'), flat=0.9)
        c.px(24.5, 14.5, '#101010')
        c.line(21, 12, 21, 20, shade_col(body, 0.6))
    return d


def food(kind):
    def d(c):
        c.ell(16, 22, 13, 6, c.M('#d8d4cc', contrast=0.6))
        c.ell(16, 21, 10, 4, c.M('#f0ece4', contrast=0.4), edge=False)
        if kind == 'fish':
            c.ell(16, 17, 9, 4.5, c.M('#c0782c'), tex=0.2)
            c.poly([(6, 17), (2, 13), (2, 21)], c.M('#a0601e'), shade=0.6)
            c.line(11, 15, 13, 19, '#6a3a10')
            c.line(15, 14, 17, 19, '#6a3a10')
            c.line(19, 14, 21, 19, '#6a3a10')
        elif kind == 'stew':
            c.ell(16, 16, 10, 7, c.M('#6a4a3a'), clip=lambda x, y: y > 15)
            c.ell(16, 15, 9, 3, c.M('#c06a2a'), flat=0.7)
            c.pxs([(13, 14), (18, 15), (15, 16)], '#f0d080')
            c.line(20, 7, 24, 14, '#e0e0e0')
        else:
            c.ell(15, 16, 8, 5.5, c.M('#a04a2a'), tex=0.25)
            c.cap(21, 13, 27, 8, 1.4, 2, c.M('#f0e8d8'))
    return d


def skull(c, col='#e8e2d0'):
    m = c.M(col)
    c.ell(16, 13, 10, 9.5, m)
    c.rect(10, 18, 12, 7, m, shade=0.6)
    d = c.M('#1a1014')
    c.ell(12, 13, 3, 3.2, d, flat=0.1)
    c.ell(20, 13, 3, 3.2, d, flat=0.1)
    c.poly([(16, 16), (14.5, 20), (17.5, 20)], d, shade=0.1)
    for x in (12, 15, 18, 21):
        c.line(x, 22, x, 25, '#4a3a3a')


def heart(c):
    m = c.M('#e02838', contrast=1.1)
    c.ell(11, 12, 6.6, 6.6, m)
    c.ell(21, 12, 6.6, 6.6, m)
    c.poly([(4.6, 14), (27.4, 14), (16, 28)], m, shade=0.55)
    c.ell(9.5, 10, 2, 1.6, c.M('#ffd0d0'), flat=1, edge=False)


def bolt(c, col='#ffe040'):
    c.poly([(19, 2), (7, 18), (15, 18), (11, 30), (25, 12), (17, 12), (22, 2)], c.M(col), shade=0.8, grad=0.4)


def hourglass(c):
    g = c.M('#c89a50')
    c.rect(7, 3, 18, 3, g, shade=0.7)
    c.rect(7, 26, 18, 3, g, shade=0.7)
    gl = c.M('#c8e0f0', contrast=0.5)
    c.poly([(9, 6), (23, 6), (17, 16), (23, 26), (9, 26), (15, 16)], gl, shade=0.8)
    s = c.M('#f0c860')
    c.poly([(11, 8), (21, 8), (16, 14)], s, shade=0.8, edge=False)
    c.poly([(16, 19), (21, 25), (11, 25)], s, shade=0.8, edge=False)


def scroll(c):
    p = c.M('#e8d4a0', contrast=0.7)
    c.rect(7, 6, 18, 20, p, shade=0.75, tex=0.1)
    c.cap(5, 6, 27, 6, 2.6, 2.6, c.M('#c8a870'))
    c.cap(5, 26, 27, 26, 2.6, 2.6, c.M('#c8a870'))
    for y in (11, 14, 17, 20):
        c.line(10, y, 22, y, '#6a4a2a')
    c.ell(20, 24, 2.4, 2.4, c.M('#c02020'))


def book(c, col='#7a2a2a'):
    c.poly([(6, 5), (24, 3), (27, 26), (9, 29)], c.M(col), shade=0.6, tex=0.1)
    c.poly([(9, 27), (26, 25), (26, 27), (9, 29)], c.M('#f0e8d0'), shade=0.9)
    c.ell(16.5, 15, 4, 4, c.M('#f0c040'))
    c.px(16.5, 15, '#ff4040')


def portal(c):
    st = c.M('#7a7268')
    c.ell(16, 16, 13, 14, st, tex=0.25)
    c.ell(16, 17, 9, 11, c.M('#8a40e0', contrast=0.8), amb=0.5)
    c.ell(16, 18, 5, 7, c.M('#e0b0ff'), flat=0.95, edge=False)
    c.rect(2, 27, 28, 4, st, shade=0.5)


def castle(c):
    s = c.M('#a8a094')
    c.rect(4, 14, 24, 15, s, shade=0.6, tex=0.15)
    c.rect(4, 6, 7, 23, s, shade=0.7, tex=0.15)
    c.rect(21, 6, 7, 23, s, shade=0.7, tex=0.15)
    r = c.M('#3a5aa8')
    c.poly([(3, 7), (7.5, 0), (12, 7)], r, shade=0.7)
    c.poly([(20, 7), (24.5, 0), (29, 7)], r, shade=0.7)
    c.ell(16, 24, 3.6, 5, c.M('#2a1a10'), flat=0.15, clip=lambda x, y: y < 29)
    c.rect(15, 8, 2, 6, c.M('#c02020'), shade=0.8)


def crossed(c, a='#d8e0ec', h='#7a5434'):
    m = c.M(a, contrast=1.2)
    diag_blade(c, 9, 22, 26, 5, 2, 1.4, m)
    diag_blade(c, 23, 22, 6, 5, 2, 1.4, m)
    c.cap(4, 20, 12, 28, 1.3, 1.3, c.M('#f0c040'))
    c.cap(28, 20, 20, 28, 1.3, 1.3, c.M('#f0c040'))
    c.cap(4, 29, 8, 25, 1.4, 1.4, c.M(h))
    c.cap(28, 29, 24, 25, 1.4, 1.4, c.M(h))


def pick_hammer(c):
    w = c.M('#8a5a34')
    c.cap(6, 28, 22, 8, 1.4, 1.4, w)
    c.chain([(13, 4), (21, 6), (28, 13)], 1.8, 0.7, c.M('#b8c0c8'))
    c.cap(26, 28, 11, 11, 1.3, 1.3, w)
    c.rect(6, 6, 9, 6, c.M('#909aa4'), shade=0.7)


def anvil(c):
    m = c.M('#5a5e6a', contrast=1.2)
    c.poly([(3, 9), (27, 9), (24, 15), (8, 15)], m, shade=0.75)
    c.poly([(27, 9), (31, 10), (27, 13)], m, shade=0.7)
    c.rect(11, 15, 10, 8, m, shade=0.55)
    c.rect(7, 23, 18, 5, m, shade=0.5)
    c.pxs([(22, 6), (25, 4), (19, 5)], '#ffc040')


def cauldron(c):
    c.ell(16, 19, 12, 9, c.M('#3a3a40', contrast=1.2))
    c.ell(16, 12, 10, 3, c.M('#50e060'), flat=0.8)
    for (x, y) in [(12, 8), (18, 5), (21, 9)]:
        c.ell(x, y, 2, 2, c.M('#a0ff90'), amb=0.6)
    c.rect(7, 27, 4, 3, c.M('#3a3a40'), shade=0.5)
    c.rect(21, 27, 4, 3, c.M('#3a3a40'), shade=0.5)


def rod(c):
    c.cap(4, 29, 24, 4, 1.2, 0.7, c.M('#8a5a2c'))
    c.ell(9, 23, 3, 3, c.M('#a0a8b0'))
    c.line(24, 4, 27, 20, '#e8e8e8')
    c.ell(27, 22, 2, 2.4, c.M('#e02020'))


def sickle(c):
    c.cap(8, 29, 13, 20, 1.6, 1.6, c.M('#8a5a2c'))
    c.chain(bez((13, 20), (28, 14), (16, 3), 8), 1.8, 0.6, c.M('#c8d0d8', contrast=1.2))
    for (x, y) in [(5, 10), (8, 6)]:
        c.ell(x, y, 2.6, 1.6, c.M('#60b040'), rot=0.5)


def flag(c):
    c.cap(7, 3, 7, 30, 1.2, 1.2, c.M('#7a5434'))
    c.poly([(8, 4), (27, 7), (22, 12), (27, 17), (8, 17)], c.M('#2a50b0'), shade=0.65, grad=0.3, gdir=(1, 0))
    c.ell(15, 10.5, 2.4, 2.4, c.M('#f0c040'))


def bag(c):
    b = c.M('#8a6440', contrast=1.1)
    c.ell(16, 20, 11, 9.5, b, tex=0.15)
    c.poly([(11, 11), (21, 11), (24, 4), (8, 4)], b, shade=0.6, tex=0.1)
    c.rect(9, 10, 14, 2.5, c.M('#c8a040'), shade=0.8)


def gift(c):
    c.rect(5, 13, 22, 15, c.M('#3a7ad0'), shade=0.6)
    c.rect(4, 10, 24, 5, c.M('#4a8ae0'), shade=0.7)
    g = c.M('#f0c040')
    c.rect(14, 10, 4, 18, g, shade=0.8)
    c.ell(12, 8, 4, 2.6, g, rot=0.4)
    c.ell(20, 8, 4, 2.6, g, rot=-0.4)


def cog(c):
    m = c.M('#a0a4ac', contrast=1.2)
    for a in range(8):
        t = a / 8 * math.tau
        c.cap(16, 16, 16 + math.cos(t) * 12, 16 + math.sin(t) * 12, 2.6, 2.4, m)
    c.ell(16, 16, 9, 9, m)
    c.ell(16, 16, 3.4, 3.4, c.M('#1a1418'), flat=0.1)


def lock(c):
    c.ell(16, 12, 7, 8, c.M('#a0a8b0'), clip=lambda x, y: y < 14)
    c.ell(16, 12, 4, 5, c.M('#1a1418'), flat=0.1, clip=lambda x, y: y < 14)
    c.rect(7, 13, 18, 15, c.M('#e0b040'), shade=0.65)
    c.ell(16, 19, 1.8, 1.8, c.M('#1a1418'), flat=0.1)
    c.rect(15.2, 19, 1.6, 5, c.M('#1a1418'), shade=0.1)


def trophy(c):
    g = c.M('#f0c040', contrast=1.2)
    c.ell(16, 9, 9, 8, g, clip=lambda x, y: y > 6)
    c.rect(7, 4, 18, 4, g, shade=0.8)
    c.cap(7, 8, 3, 13, 1.2, 1.2, g)
    c.cap(25, 8, 29, 13, 1.2, 1.2, g)
    c.rect(14, 16, 4, 7, g, shade=0.6)
    c.rect(9, 23, 14, 5, c.M('#6a4a2a'), shade=0.6)


def map_icon(c):
    p = c.M('#e0cc98', contrast=0.7)
    c.poly([(3, 6), (11, 4), (21, 7), (29, 5), (29, 26), (21, 28), (11, 25), (3, 27)], p, shade=0.75, tex=0.1)
    c.line(11, 4, 11, 25, '#a08a60')
    c.line(21, 7, 21, 28, '#a08a60')
    c.pxs([(7, 12), (9, 14), (12, 15), (15, 15), (17, 17)], '#a02020')
    c.line(22, 18, 26, 22, '#c02020', 1)
    c.line(26, 18, 22, 22, '#c02020', 1)


def mount_icon(P, fn=sprites.quadruped):
    def d(c):
        sub = Canvas(32, 32, design=48, seed=4)
        fn(sub, P)
        c._sub = sub
    return d


def sub_icon(theme, fn, P, seed=0, glow=None):
    sub = Paint(ICON, ICON, design=48, seed=seed, ss=3)
    fn(sub, P)
    fg = sub.render(glow=glow, glow_r=1.4, out_w=0.7)
    b = bg(theme, seed)
    b.alpha_composite(fg)
    return frame(b)


def wolf_head(c):
    fur = c.M('#8a8a96')
    c.ell(16, 18, 9, 8, fur, tex=0.2)
    c.ell(24, 21, 6, 3.6, fur)
    c.poly([(9, 12), (10, 2), (15, 10)], fur, shade=0.6)
    c.poly([(15, 10), (19, 2), (21, 11)], fur, shade=0.6)
    c.pxs([(19, 16), (20, 16)], '#ffd030')
    c.px(29, 20, '#100808')
    c.ell(24, 24.5, 4, 1.4, c.M('#601818'), flat=0.2)
    c.pxs([(22, 24), (25, 24)], '#ffffff')


def beam(c):
    c.poly([(11, 0), (21, 0), (25, 32), (7, 32)], c.M('#fff0a0', contrast=0.6), shade=0.85, alpha=230)
    c.poly([(14, 0), (18, 0), (19, 32), (13, 32)], c.M('#ffffff', contrast=0.3), shade=1.0, edge=False)
    for (x, y) in [(6, 10), (26, 16), (8, 24), (24, 6)]:
        c.px(x, y, '#ffffa0')


def swirl(c, col, core):
    for i in range(3):
        r = 12 - i * 3.6
        pts = [(16 + math.cos(t) * r, 16 + math.sin(t) * r) for t in np.linspace(i, i + 4.6, 9)]
        c.chain(pts, 1.8 - i * 0.3, 0.6, c.M(col))
    c.ell(16, 16, 3.4, 3.4, c.M(core), flat=1.0)


def blades(c):
    m = c.M('#d8e0ec', contrast=1.2)
    for a in range(4):
        t = a / 4 * math.tau + 0.4
        x2, y2 = 16 + math.cos(t) * 13, 16 + math.sin(t) * 13
        diag_blade(c, 16 + math.cos(t) * 3, 16 + math.sin(t) * 3, x2, y2, 1.4, 1.8, m)
    c.ell(16, 16, 3.2, 3.2, c.M('#f0c040'))


def shout(c):
    c.poly([(4, 12), (14, 8), (14, 24), (4, 20)], c.M('#c8a060'), shade=0.7)
    c.ell(14, 16, 2, 8, c.M('#8a6a3a'))
    for i, r in enumerate((6, 10, 14)):
        pts = [(15 + math.cos(t) * r, 16 + math.sin(t) * r) for t in np.linspace(-0.9, 0.9, 6)]
        c.chain(pts, 1.1, 1.1, c.M('#ffd060'), flat=0.9)


def fireball(c):
    o = c.M('#ff6a20')
    c.poly([(2, 30), (10, 14), (20, 22)], o, shade=0.8)
    c.poly([(6, 30), (16, 10), (18, 24)], c.M('#ffa030'), shade=0.85, edge=False)
    c.ell(19, 13, 9, 9, o, amb=0.55)
    c.ell(20, 12, 5.5, 5.5, c.M('#ffe070'), flat=0.95, edge=False)
    c.ell(21, 11, 2.4, 2.4, c.M('#ffffff'), flat=1.0, edge=False)


def ice_shard(c):
    c.poly([(4, 28), (22, 4), (28, 4), (28, 10), (8, 28)], c.M('#80c8ff', contrast=0.9), shade=0.8, grad=0.6, gdir=(1, -1))
    c.poly([(10, 24), (24, 7), (26, 8), (12, 25)], c.M('#ffffff', contrast=0.3), shade=1.0, edge=False)
    for (x, y) in [(8, 10), (20, 22), (26, 18)]:
        c.px(x, y, '#e0ffff')


def target_arrow(c):
    for r, col in ((13, '#c02020'), (9.5, '#f0e8d8'), (6, '#c02020'), (2.6, '#f0e8d8')):
        c.ell(18, 15, r, r, c.M(col), flat=0.7)
    c.cap(2, 30, 18, 15, 0.9, 0.9, c.M('#8a6440'))
    c.poly([(1, 27), (6, 26), (5, 31)], c.M('#e0e0e0'), shade=0.8)


def arrow_rain(c):
    for (x, y) in [(6, 4), (14, 9), (22, 3), (10, 18), (24, 15)]:
        c.cap(x, y, x + 4, y + 10, 0.7, 0.7, c.M('#8a6440'))
        c.poly([(x + 2.5, y + 9), (x + 6, y + 9), (x + 5.4, y + 14)], c.M('#d0d8e0'), shade=0.85)


def shadow_skull(c):
    c.ell(16, 16, 14, 14, c.M('#40186a'), amb=0.4, alpha=255)
    skull(c, '#c8a0f0')


def heal_hands(c):
    g = c.M('#60e060')
    c.rect(13, 4, 6, 24, g, shade=0.85)
    c.rect(4, 13, 24, 6, g, shade=0.85)
    c.rect(14.5, 5.5, 3, 21, c.M('#e0ffd0'), shade=1, edge=False)
    c.rect(5.5, 14.5, 21, 3, c.M('#e0ffd0'), shade=1, edge=False)


def bite(c):
    wolf_head(c)


def boot_wing(c):
    i_feet(TIERS[1])(c)
    w = c.M('#f0f0f0')
    c.poly([(4, 8), (0, 2), (2, 12)], w, shade=0.9)
    c.poly([(4, 13), (0, 8), (3, 16)], w, shade=0.85)


def shield_icon(c):
    c.poly([(5, 3), (27, 3), (27, 16), (16, 30), (5, 16)], c.M('#b8c0cc', contrast=1.2), shade=0.75)
    c.poly([(8, 6), (24, 6), (24, 15), (16, 26), (8, 15)], c.M('#2a50a0'), shade=0.6)
    c.rect(14.5, 7, 3, 17, c.M('#f0c040'), shade=0.8)


def fist(c):
    s = c.M('#e0a070')
    c.ell(16, 18, 9, 8, s)
    for x in (10, 14, 18, 22):
        c.ell(x, 11, 2.6, 3.2, s)
    c.cap(7, 18, 11, 12, 2.6, 2.2, s)
    c.rect(9, 25, 14, 5, c.M('#8a5a34'), shade=0.6)


def raid_head(c):
    sc = c.M('#a02828')
    c.ell(14, 17, 9, 8, sc, tex=0.1)
    c.ell(23, 21, 7.5, 4, sc)
    c.chain([(10, 11), (6, 4), (2, 3)], 2, 0.6, c.M('#f0e8d0'))
    c.chain([(15, 10), (14, 3), (11, 1)], 2, 0.6, c.M('#f0e8d0'))
    c.pxs([(17, 14), (18, 14)], '#ffe040')
    c.ell(24, 24, 5, 1.6, c.M('#401010'), flat=0.2)
    c.pxs([(21, 23), (24, 23), (27, 23)], '#ffffff')


def mats_dust(col):
    def d(c):
        for (x, y, r) in [(11, 20, 6), (20, 21, 6.5), (16, 13, 5.5)]:
            c.ell(x, y, r, r * 0.8, c.M(col, contrast=0.9), amb=0.5)
        for (x, y) in [(8, 12), (24, 10), (22, 28), (6, 26)]:
            c.px(x, y, '#ffffff')
    return d


# --------------------------------------------------------------------------------------------- catalogue
FISH = [
    ('fisch_barsch', '#7a8a50', '#d8d8a0', '#a06030'), ('fisch_forelle', '#8aa0a8', '#f0d0c0', '#c07070'),
    ('fisch_hecht', '#5a7a4a', '#c8d0a0', '#4a6a3a'), ('fisch_karpfen', '#c08a40', '#f0d090', '#a06020'),
    ('fisch_sumpfaal', '#3a5a3a', '#7a9a6a', '#2a4a2a'), ('fisch_wuestenkoi', '#f07a30', '#fff0e0', '#ffffff'),
    ('fisch_eisflosser', '#a0d0f0', '#ffffff', '#6aa0d0'), ('fisch_geisterfisch', '#c0c8e0', '#e8f0ff', '#8090c0'),
    ('fisch_lavaflosser', '#c03018', '#ffb040', '#3a1010'), ('fisch_leerenkrake', '#5a2a8a', '#c080ff', '#30104a'),
    ('fisch_goldschuppe', '#f0c030', '#fff0a0', '#d08010'), ('fisch_sternenwal', '#203a8a', '#a0c0ff', '#f0f0ff'),
]

ORES = [('erz_kupfer', '#d07a40'), ('erz_eisen', '#c0c8d0'), ('erz_silber', '#f0f4ff'), ('erz_mondstahl', '#80c0ff'), ('erz_sternen', '#e080ff')]
HERBS = [('kraut_wiesenklee', '#6ab040', '#f0f0f0'), ('kraut_blutdorn', '#5a8a30', '#e02030'), ('kraut_nebelmoos', '#5a9a7a', '#a0e0f0'),
         ('kraut_sonnenbluete', '#7aa030', '#ffd030'), ('kraut_sternenlotus', '#4a7aa0', '#e080ff')]


def catalogue():
    I = {}
    for t, T in enumerate(TIERS):
        for cls, fn in WEAPON.items():
            I[f'w_{cls}_{t}'] = icon(T['bg'], fn(T), seed=t, glow='#ff9020' if t == 5 else None)
        for slot, fn in ARMOR.items():
            I[f'a_{slot}_{t}'] = icon(T['bg'], fn(T), seed=t + 7, glow='#ff9020' if t == 5 else None)
    I['gold'] = icon('#4a3a10', coins)
    I['xp'] = icon('#2a1a4a', star)
    I['badge'] = icon('#1a2a4a', emblem_shield('#2a5ab0', '#e0b040', sym_sword))
    I['raidmark'] = icon('#3a1040', emblem_shield('#6a2a9a', '#e0b040', sym_dragon))
    I['honor'] = icon('#401010', emblem_shield('#a02020', '#c0c8d0', sym_swords))
    I['key'] = icon('#2a2010', key)
    I['chest'] = icon('#2a1a0a', chest('#8a5a30', '#a0a8b0'))
    I['chest_epic'] = icon('#2a0a3a', chest('#5a2a8a', '#f0c040', '#60fff0'), glow='#a060ff')
    I['chest_gold'] = icon('#3a2a06', chest('#a87a30', '#f0d060', '#ff4040'), glow='#ffd040')
    I['potion_heal'] = icon('#3a0a0a', flask('#e02030'))
    I['elixir_atk'] = icon('#3a1a06', flask('#ff8020', 'tall'))
    I['elixir_xp'] = icon('#0a1a3a', flask('#4080ff', 'tall'))
    I['elixir_luck'] = icon('#0a2a0a', flask('#40d040', 'tall'))
    I['flask_titan'] = icon('#3a2a06', flask('#ffd040'), glow='#ffd040')
    for n, col in ORES:
        I[n] = icon('#2a2622', ore(col))
    for n, leaf, fl in HERBS:
        I[n] = icon('#142a14', herb(leaf, fl))
    for n, b, be, f in FISH:
        I[n] = icon('#0a2a3a', fish(b, be, f), glow='#ffe060' if n in ('fisch_goldschuppe', 'fisch_sternenwal') else None)
    I['food_fish'] = icon('#3a2410', food('fish'))
    I['food_stew'] = icon('#3a2410', food('stew'))
    I['food_meat'] = icon('#3a2410', food('meat'))
    I['dust'] = icon('#2a1a3a', mats_dust('#c090ff'))
    # skills
    I['sk_schmetterhieb'] = icon('#4a1010', i_sword(TIERS[1]))
    I['sk_klingensturm'] = icon('#3a2a1a', blades)
    I['sk_kampfschrei'] = icon('#4a2a06', shout)
    I['sk_feuerkugel'] = icon('#3a1006', fireball, glow='#ff6020')
    I['sk_eislanze'] = icon('#0a1a3a', ice_shard, glow='#80d0ff')
    I['sk_arkanflut'] = icon('#24103a', lambda c: swirl(c, '#c080ff', '#ffffff'), glow='#a060ff')
    I['sk_praeziser_schuss'] = icon('#2a1a10', target_arrow)
    I['sk_pfeilhagel'] = icon('#1a2a1a', arrow_rain)
    I['sk_wolfsbiss'] = icon('#2a2a2a', wolf_head)
    I['sk_lichtstrahl'] = icon('#3a3010', beam, glow='#ffe080')
    I['sk_schattenpein'] = icon('#140a20', shadow_skull, glow='#8040c0')
    I['sk_segnung'] = icon('#0a2a10', heal_hands, glow='#80ff80')
    # stats / ui
    I['st_hp'] = icon('#3a0a10', heart)
    I['st_atk'] = icon('#3a1a10', fist)
    I['st_def'] = icon('#101a3a', shield_icon)
    I['st_crit'] = icon('#3a3006', bolt)
    I['st_haste'] = icon('#0a2a3a', boot_wing)
    I['clock'] = icon('#2a1a10', hourglass)
    I['scroll'] = icon('#2a1a0a', scroll)
    I['book'] = icon('#1a1010', book)
    I['book_blue'] = icon('#0a1424', lambda c: book(c, '#2a4a9a'))
    I['portal'] = icon('#1a1028', portal, glow='#a060ff')
    I['castle'] = icon('#0a1a2a', castle)
    I['swords'] = icon('#2a1010', crossed)
    I['tools'] = icon('#1a1a1a', pick_hammer)
    I['anvil'] = icon('#2a1a10', anvil)
    I['cauldron'] = icon('#0a2010', cauldron, glow='#60ff60')
    I['rod'] = icon('#0a1a2a', rod)
    I['sickle'] = icon('#102010', sickle)
    I['pickaxe'] = icon('#2a2018', lambda c: pick_hammer(c))
    I['flag'] = icon('#1a1a2a', flag)
    I['bag'] = icon('#2a1a0a', bag)
    I['gift'] = icon('#0a1a3a', gift)
    I['cog'] = icon('#1a1a1e', cog)
    I['lock'] = icon('#1a1a1a', lock)
    I['trophy'] = icon('#2a2006', trophy)
    I['map'] = icon('#2a2010', map_icon)
    I['skull'] = icon('#2a0a0a', skull)
    I['raid'] = icon('#2a0a0a', raid_head)
    I['star'] = icon('#2a2006', lambda c: star(c, '#f0c040', '#fff8c0'))
    I['crown'] = icon('#2a1a06', lambda c: sprites.crown(c, 16, 18, 2.4))
    # mounts & companions
    I['m_pferd'] = sub_icon('#2a2a1a', sprites.quadruped, dict(fur='#8a5a30', eye='#201010', snout=5.5, head=5.4, ear_in='#5a3a20', mane='#3a2416', body=12.5))
    I['m_wolf'] = sub_icon('#1a1a24', sprites.quadruped, dict(fur='#6a6a78', eye='#ffd030'))
    I['m_saebelzahn'] = sub_icon('#2a1a06', sprites.quadruped, dict(fur='#e0a040', spots='#3a2010', eye='#40ff60', ears=True, ear_in='#f0c0a0'))
    I['m_widder'] = sub_icon('#1a2a2a', sprites.quadruped, dict(fur='#e0d8c8', horns='#a07a50', eye='#201010', ear_in='#d0a090'))
    I['m_frostwolf'] = sub_icon('#0a1a2a', sprites.quadruped, dict(fur='#d0dcea', eye='#40c8ff', ear_in='#90a8d0'), glow='#80c0ff')
    I['m_drache'] = sub_icon('#1a0a2a', sprites.dragon, dict(scale='#3a2060', belly='#7a50b0', wing='#2a1450', eye='#ff60ff', horn='#c0a0e0'), glow='#9050ff')
    I['m_glutross'] = sub_icon('#2a0a06', sprites.quadruped, dict(fur='#3a2626', eye='#ffd040', cracks='#ff8030', mane='#ff6020', ear_in='#ff6020'), glow='#ff6020')
    return I

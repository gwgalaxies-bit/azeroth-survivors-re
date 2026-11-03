"""Creature, hero and effect sprites. Everything is drawn facing right on a 48-unit design grid
(ground at y=44) and mirrored for monsters, which face the hero from the right."""
import math

from PIL import Image

from px import Canvas, mix, rgb, shade_col

GROUND = 44


def flip(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


# ---------------------------------------------------------------------------------------------
# beasts
# ---------------------------------------------------------------------------------------------
def quadruped(c, P):
    low = P.get('low', False)
    fur = c.M(P['fur'])
    far = c.M(shade_col(P['fur'], 0.72))
    belly = c.M(P.get('belly', mix(P['fur'], '#e8dcc8', 0.35)))
    by = 33 if low else 27
    bry = 5 if low else 7
    brx = P.get('body', 12)
    leg = 41 if low else 42
    tex = P.get('tex', 0.18)
    # tail
    tl = P.get('tail', 1.0)
    if low:
        c.chain([(14, by + 1), (6, by + 4), (1, by + 7)], 4.0, 1.2, fur, tex=tex)
    else:
        c.chain([(14, by - 2), (8, by - 6), (4, by - 12 * tl)], 2.4, 1.2, fur, tex=tex)
    # far legs
    c.cap(30, by + 3, 31.5, leg, 2.6, 2.2, far)
    c.cap(18, by + 3, 16.5, leg, 2.6, 2.2, far)
    # body
    c.ell(24, by, brx, bry, fur, tex=tex)
    c.ell(25, by + bry * 0.55, brx * 0.7, bry * 0.4, belly, tex=tex * 0.5, edge=False)
    if P.get('mane'):
        c.ell(32, by - 3, 6, 7, c.M(P['mane']), tex=0.35)
    if P.get('spikes'):
        sp = c.M(P['spikes'])
        for i in range(5):
            x = 14 + i * 4.4
            c.poly([(x - 1.8, by - bry + 1), (x + 0.6, by - bry - 3.5), (x + 2.2, by - bry + 1)], sp)
    # near legs
    c.cap(32, by + 3, 34, leg, 2.9, 2.5, fur, tex=tex)
    c.cap(20, by + 3, 20, leg, 2.9, 2.5, fur, tex=tex)
    paw = c.M(shade_col(P['fur'], 0.6))
    for x in (34.8, 20.6):
        c.ell(x, leg + 0.5, 3.0, 1.6, paw, edge=False)
    # head
    hx, hy = (38, by - 1) if low else (35, by - 6)
    hr = P.get('head', 6.2)
    c.ell(hx, hy, hr, hr * 0.9, fur, tex=tex)
    sn = P.get('snout', 4.6)
    c.ell(hx + hr * 0.8, hy + 2.6, sn, 2.6 if not low else 2.2, fur, tex=tex * 0.5)
    if low:
        c.ell(hx + hr * 0.8 + 1, hy + 4, sn, 1.4, belly, edge=False)
    if P.get('ears', True) and not low:
        c.poly([(hx - 3.5, hy - 3), (hx - 1.5, hy - 11), (hx + 1.5, hy - 4)], fur)
        c.poly([(hx - 1.5, hy - 4), (hx - 1.0, hy - 8), (hx + 0.5, hy - 4.5)], c.M(P.get('ear_in', '#c08080')), edge=False)
    if P.get('horns'):
        hm = c.M(P['horns'])
        c.chain([(hx - 1, hy - 4), (hx - 4, hy - 9), (hx - 1, hy - 13)], 1.8, 0.7, hm)
    # eye, nose, teeth
    ex, ey = hx + 2.4, hy - 1.6
    c.px(ex, ey, P.get('eye', '#ffd23a'))
    c.px(ex + 1, ey, P.get('eye', '#ffd23a'))
    c.px(hx + hr * 0.8 + sn - 0.6, hy + 1.6, '#1a1014')
    c.px(hx + hr * 0.8 + sn - 1.6, hy + 4.6, '#f0ecd8')
    c.px(hx + hr * 0.8 + sn - 3.6, hy + 4.6, '#f0ecd8')
    if P.get('spots'):
        rng = c.rng
        for _ in range(int(14 * c.k)):
            x = 14 + rng.random() * 20
            y = by - 4 + rng.random() * 7
            c.px(x, y, P['spots'])
    if P.get('cracks'):
        rng = c.rng
        for _ in range(5):
            x, y = 13 + rng.random() * 22, by - 3 + rng.random() * 6
            for s in range(4):
                c.px(x, y, P['cracks'])
                x += rng.random() * 2 - 0.3
                y += rng.random() * 2 - 1
    if P.get('stars'):
        rng = c.rng
        for _ in range(int(10 * c.k)):
            c.px(13 + rng.random() * 24, by - 5 + rng.random() * 9, P['stars'])


def spider(c, P):
    body = c.M(P['body'])
    far = c.M(shade_col(P['body'], 0.65))
    leg = c.M(P.get('leg', P['body']))
    tex = 0.15
    scorp = P.get('scorp', False)
    if scorp:
        # far legs short
        for i in range(3):
            bx = 18 + i * 5
            c.chain([(bx, 35), (bx - 3, 38), (bx - 5, 43)], 1.4, 1.0, far)
        c.ell(20, 35, 12, 5, body, tex=tex)
        for i in range(4):
            c.ell(10 + i * 5, 34, 3.4, 4.4, body, tex=tex)
        # tail
        c.chain([(9, 33), (4, 26), (5, 17), (12, 11), (20, 11)], 3.3, 2.0, body, tex=tex)
        c.poly([(19, 8), (27, 12), (19, 14)], c.M(P.get('sting', '#3a2020')))
        for i in range(3):
            bx = 20 + i * 5
            c.chain([(bx, 37), (bx + 3, 40), (bx + 5, 44)], 1.6, 1.1, leg)
        # pincer arm + claw
        c.chain([(30, 35), (36, 32), (41, 31)], 2.4, 2.0, body, tex=tex)
        c.ell(44, 30, 4, 2.6, body, rot=-0.3)
        c.ell(44, 34, 3.6, 2.0, far, rot=0.3)
        c.ell(32, 35, 4.5, 3.6, body)
        c.px(34.5, 33, P.get('eye', '#ff3020'))
        c.px(35.5, 33, P.get('eye', '#ff3020'))
        return
    # far legs: two reach back, two reach forward
    def legs(m, dy, spread, r):
        for i in range(4):
            d = -1 if i < 2 else 1
            reach = (1.6 - abs(i - 1.5)) if d < 0 else (abs(i - 1.5) + 0.5)
            bx = 24 + (i - 1.5) * 2.0
            kx = bx + d * (5 + reach * 3) * spread
            fx = bx + d * (10 + reach * 7) * spread
            c.chain([(bx, 30 + dy), (kx, 17 + dy + i % 2 * 2), (fx, 44)], r, r * 0.55, m, tex=0.1)
    legs(far, -1, 0.8, 1.5)
    c.ell(14, 26, 11, 9, body, tex=tex)
    if P.get('pattern'):
        pm = c.M(P['pattern'])
        c.ell(13, 23, 6, 3, pm, flat=None, tex=0.1, edge=False)
        c.ell(10, 29, 3, 1.6, pm, edge=False)
    c.ell(28, 30, 6.5, 5.4, body, tex=tex)
    c.ell(35, 31.5, 4.2, 3.6, body)
    legs(leg, 1, 1.0, 1.9)
    eye = P.get('eye', '#ff3020')
    c.pxs([(37, 30), (38.2, 30), (37.6, 31.2), (38.8, 31.4)], eye)
    c.px(39, 34, '#e8e0c0')
    c.px(38, 34.6, '#e8e0c0')


def slime(c, P):
    b = c.M(P['body'], contrast=0.8)
    c.ell(24, 33, 17, 13, b, clip=lambda x, y: y <= 43.5, tex=0.06, dith=0.6)
    c.ell(24, 43, 17, 1.6, b, flat=0.3)
    hi = c.M(mix(P['body'], '#ffffff', 0.55))
    c.ell(16, 26, 4.6, 3, hi, flat=0.9, edge=False)
    c.ell(13, 31, 1.4, 1.4, hi, flat=0.9, edge=False)
    if P.get('inner'):
        im = c.M(P['inner'])
        c.ell(28, 35, 4, 3.5, im, edge=False)
        c.ell(20, 38, 2, 2, im, edge=False)
    for x in (27, 34):
        c.ell(x, 30, 2.6, 3.2, c.M('#f4f0e0', contrast=0.4), flat=0.85)
        c.px(x + 0.9, 30.4, '#101018')
        c.px(x + 0.9, 31.4, '#101018')
    c.line(28, 37, 33, 37, shade_col(P['body'], 0.35))
    if P.get('crown'):
        crown(c, 24, 20, 1.0)


def worm(c, P):
    sand = c.M(P['sand'])
    body = c.M(P['body'])
    ring = shade_col(P['body'], 0.55)
    c.chain([(22, 44), (19, 33), (24, 22), (31, 15)], 8.5, 6.0, body, tex=0.12)
    for (x, y, r) in [(20, 37, 8), (20, 29, 7.5), (25, 21, 7), (30, 16, 6)]:
        c.line(x - r * 0.8, y + 1, x + r * 0.8, y - 1, ring)
    c.ell(34, 13, 5.5, 6, c.M('#3a1010'), rot=0.5)
    for a in range(8):
        t = a / 8 * math.tau
        c.px(34 + math.cos(t) * 4.5, 13 + math.sin(t) * 5, '#f0e8c8')
    c.ell(24, 45, 16, 4.5, sand, tex=0.3)
    for x in (10, 14, 34, 38):
        c.ell(x, 43, 3, 2, sand, tex=0.3)


# ---------------------------------------------------------------------------------------------
# humanoids
# ---------------------------------------------------------------------------------------------
def crown(c, x, y, s=1.0, col='#f0c040', gem='#e03040'):
    g = c.M(col)
    c.poly([(x - 5 * s, y + 2 * s), (x - 5 * s, y - 3 * s), (x - 2.5 * s, y), (x, y - 4 * s), (x + 2.5 * s, y),
            (x + 5 * s, y - 3 * s), (x + 5 * s, y + 2 * s)], g, shade=0.75)
    c.px(x, y, gem)


def humanoid(c, P):
    """Facing right. P keys: skin, cloth, cloth2, pants, boots, metal, scale, w, robe, head features..."""
    s = P.get('scale', 1.0)
    w = P.get('w', 1.0)
    cx = 24

    def T(x, y):
        return cx + (x - cx) * s, GROUND - (GROUND - y) * s

    def ell(x, y, rx, ry, m, **kw):
        X, Y = T(x, y)
        c.ell(X, Y, rx * s, ry * s, m, **kw)

    def cap(x1, y1, x2, y2, r1, r2, m, **kw):
        a, b = T(x1, y1)
        d, e = T(x2, y2)
        c.cap(a, b, d, e, r1 * s, r2 * s, m, **kw)

    def poly(pts, m, **kw):
        c.poly([T(x, y) for x, y in pts], m, **kw)

    def px(x, y, col):
        X, Y = T(x, y)
        c.px(X, Y, col)

    bone = P.get('bones', False)
    skin = c.M(P['skin'])
    cloth = c.M(P['cloth'])
    cloth_far = c.M(shade_col(P['cloth'], 0.7))
    pants = c.M(P.get('pants', shade_col(P['cloth'], 0.8)))
    pants_far = c.M(shade_col(P.get('pants', shade_col(P['cloth'], 0.8)), 0.7))
    boots = c.M(P.get('boots', '#4a3428'))
    hunch = P.get('hunch', 0)
    tex = P.get('tex', 0.1)
    lr = 2.3 if bone else 3.1 * w ** 0.5
    ar = 1.7 if bone else 2.6 * w ** 0.6
    armc = skin if P.get('bare_arms') else cloth
    armc_far = c.M(shade_col(P['skin'], 0.7)) if P.get('bare_arms') else cloth_far
    if bone:
        armc, armc_far = skin, c.M(shade_col(P['skin'], 0.72))
    sx = 24 + hunch  # shoulder centre x
    sy = 18 + hunch * 0.6
    # wings / cape behind
    if P.get('wings'):
        wm = c.M(P['wings'])
        poly([(sx - 2, sy), (sx - 18, sy - 14), (sx - 16, sy - 4), (sx - 22, sy + 2), (sx - 14, sy + 4), (sx - 15, sy + 10), (sx - 4, sy + 6)], wm, shade=0.45)
    if P.get('cape'):
        cm = c.M(P['cape'])
        poly([(sx - 3, sy - 2), (sx - 9, GROUND - 3), (sx - 1, GROUND - 2), (sx + 2, sy)], cm, shade=0.5, tex=0.08)
    if P.get('tail'):
        cap(16, 32, 8, 38, 2, 1, c.M(P['tail']))
    # far arm
    far_hand = P.get('far_hand', (sx - 5, sy + 11))
    cap(sx - 3, sy, far_hand[0], far_hand[1], ar, ar * 0.9, armc_far, tex=tex)
    ell(far_hand[0], far_hand[1] + 1, ar * 0.9, ar * 0.9, c.M(shade_col(P['skin'], 0.75)))
    # legs
    robe = P.get('robe')
    if not robe:
        cap(22, 30, 20, 42, lr, lr * 0.85, pants_far, tex=tex)
        ell(20.5, 42.5, 3.6, 1.8, c.M(shade_col(P.get('boots', '#4a3428'), 0.7)))
    # torso
    tw = (6.5 if not bone else 4.5) * w
    if bone:
        ell(sx, sy + 7, tw, 7.5, cloth if P.get('armor_torso') else skin, tex=tex)
        if not P.get('armor_torso'):
            for i in range(4):
                X1, Y1 = T(sx - 3.5, sy + 3 + i * 2.4)
                X2, Y2 = T(sx + 3.5, sy + 3 + i * 2.4)
                c.line(X1, Y1, X2, Y2, shade_col(P['skin'], 0.45))
        cap(24, 26, 24, 31, 1.6, 1.6, skin)
    else:
        ell(sx, sy + 7, tw, 8.5, cloth, tex=tex)
    if P.get('belt'):
        ell(sx, sy + 13.5, tw * 0.95, 1.5, c.M(P['belt']), edge=False)
    if P.get('tabard'):
        poly([(sx - 2.5, sy + 4), (sx + 3, sy + 4), (sx + 2.5, sy + 22), (sx - 2, sy + 22)], c.M(P['tabard']), shade=0.6)
    if robe:
        rm = c.M(robe)
        poly([(sx - tw + 0.5, sy + 9), (sx + tw - 0.5, sy + 9), (sx + tw + 4, GROUND), (sx - tw - 4, GROUND)], rm, shade=0.6, grad=0.3, gdir=(1, 0.3), tex=0.05)
        if P.get('trim'):
            tm = c.M(P['trim'])
            poly([(sx - tw - 4, GROUND - 2), (sx + tw + 4, GROUND - 2), (sx + tw + 4, GROUND), (sx - tw - 4, GROUND)], tm, shade=0.8)
            poly([(sx + 0.5, sy + 9), (sx + 2.5, sy + 9), (sx + 4, GROUND - 2), (sx + 2, GROUND - 2)], tm, shade=0.8)
    else:
        cap(26, 30, 28, 42, lr, lr * 0.85, pants, tex=tex)
        ell(29, 42.5, 3.8, 1.8, boots)
    # head
    hx, hy = sx + 1 + hunch * 0.6, 9 + hunch * 1.4
    hr = P.get('head', 5.2)
    if P.get('neck', True):
        cap(sx, sy - 2, hx, hy + 3, 1.8, 1.8, skin)
    if P.get('hair') and not P.get('hood'):
        ell(hx - 1.2, hy - 0.8, hr * 1.02, hr * 0.98, c.M(P['hair']), tex=0.2)
    ell(hx, hy, hr * 0.92, hr, skin, tex=0.04)
    if P.get('hood'):
        hm = c.M(P['hood'])
        ell(hx - 1.2, hy - 0.8, hr * 1.18, hr * 1.18, hm, clip=lambda X, Y: ~((X > (cx + (hx + 0.5 - cx) * s)) & (Y > GROUND - (GROUND - (hy - 1.5)) * s)))
    if P.get('helm'):
        hm = c.M(P['helm'])
        ell(hx, hy - 1.2, hr * 1.08, hr * 0.95, hm, clip=lambda X, Y: Y < GROUND - (GROUND - (hy + 1.2)) * s)
        cap(hx + 1, hy + 0.5, hx + hr, hy + 0.5, 0.9, 0.9, hm)
        if P.get('plume'):
            cap(hx - 1, hy - hr, hx - 7, hy - hr - 1, 1.6, 1.0, c.M(P['plume']))
    if P.get('beard'):
        poly([(hx - 1, hy + 2), (hx + hr, hy + 1.5), (hx + 2, hy + 9)], c.M(P['beard']), shade=0.65, tex=0.15)
    if P.get('tusks'):
        px(hx + hr - 0.8, hy + 2.6, '#f4ecd0')
        px(hx + hr - 0.8, hy + 1.6, '#f4ecd0')
    if P.get('fins'):
        poly([(hx - 3, hy - 3), (hx - 8, hy - 8), (hx - 5, hy + 1)], c.M(P['fins']), shade=0.55)
        poly([(sx - 5, sy + 2), (sx - 11, sy + 2), (sx - 6, sy + 10)], c.M(P['fins']), shade=0.5)
    if P.get('ears_long'):
        poly([(hx - 2, hy - 1), (hx - 9, hy - 5), (hx - 2, hy + 2)], skin, shade=0.6)
    if P.get('horns'):
        hm = c.M(P['horns'])
        a = T(hx - 1, hy - 3)
        b = T(hx - 5, hy - 9)
        d = T(hx - 1, hy - 13)
        c.chain([a, b, d], 1.9 * s, 0.6 * s, hm)
    eyes = P.get('eye', '#20160e')
    if bone:
        ell(hx + 1.8, hy - 0.2, 1.4, 1.4, c.M('#141018'), flat=0.2)
        px(hx + 1.8, hy - 0.4, P.get('eye', '#60e0ff'))
        px(hx + hr * 0.6, hy + 2.6, '#1a1418')
        X1, Y1 = T(hx, hy + 3.2)
        X2, Y2 = T(hx + hr * 0.9, hy + 3.2)
        c.line(X1, Y1, X2, Y2, shade_col(P['skin'], 0.4))
    elif not P.get('helm'):
        px(hx + 2.3, hy - 0.6, eyes)
        if P.get('big_eye'):
            px(hx + 3.3, hy - 0.6, eyes)
    else:
        px(hx + 2.5, hy + 0.6, P.get('visor_eye', '#ffd040'))
    if P.get('candle'):
        hm = c.M('#6a5a4a')
        ell(hx - 0.5, hy - 3, hr * 0.95, hr * 0.6, hm, clip=lambda X, Y: Y < GROUND - (GROUND - (hy - 2)) * s)
        cap(hx, hy - 6, hx, hy - 9, 1.1, 1.1, c.M('#f0e8d0'))
        px(hx, hy - 10.5, '#ffe060')
        px(hx, hy - 11.5, '#ff9020')
    if P.get('witch_hat'):
        hm = c.M(P['witch_hat'])
        ell(hx - 0.5, hy - 3.2, hr * 1.7, 1.3, hm)
        poly([(hx - 4, hy - 3.6), (hx + 3, hy - 3.6), (hx - 6, hy - 16)], hm, shade=0.55)
    if P.get('crown'):
        X, Y = T(hx - 0.5, hy - hr - 1)
        crown(c, X, Y, 0.75 * s, P.get('crown_col', '#f0c040'))
    # body extras
    if P.get('shoulders'):
        sm = c.M(P['shoulders'])
        ell(sx + 3, sy + 1, 4.2 * w, 3.0, sm)
    # near arm
    near_hand = P.get('near_hand', (sx + 8, sy + 9))
    cap(sx + 3, sy + 1, near_hand[0], near_hand[1], ar, ar * 0.9, armc, tex=tex)
    if P.get('shoulders'):
        ell(sx + 3.5, sy - 0.2, 4.0 * w, 2.6, sm)
    hand = c.M(P.get('glove', P['skin']))
    ell(near_hand[0], near_hand[1] + 0.5, ar * 0.95, ar * 0.95, hand)
    # weapon
    wpn = P.get('weapon')
    if wpn:
        weapon(c, T, s, wpn, near_hand, far_hand, P)


def weapon(c, T, s, kind, nh, fh, P):
    metal = c.M(P.get('metal', '#b8c0cc'), contrast=1.2)
    wood = c.M(P.get('wood', '#7a5434'))
    gold = c.M(P.get('gold', '#e0b040'))

    def cap(x1, y1, x2, y2, r1, r2, m, **kw):
        a, b = T(x1, y1)
        d, e = T(x2, y2)
        c.cap(a, b, d, e, r1 * s, r2 * s, m, **kw)

    def poly(pts, m, **kw):
        c.poly([T(x, y) for x, y in pts], m, **kw)

    def ell(x, y, rx, ry, m, **kw):
        X, Y = T(x, y)
        c.ell(X, Y, rx * s, ry * s, m, **kw)

    x, y = nh
    if kind == 'sword':
        cap(x - 1, y + 3, x + 1, y - 1, 1.0, 1.0, wood)
        cap(x - 3, y - 1.5, x + 4, y - 0.5, 0.9, 0.9, gold)
        poly([(x - 1, y - 2), (x + 2.4, y - 2), (x + 7, y - 20), (x + 4, y - 21)], metal, shade=0.75, grad=0.4, gdir=(1, 0))
    elif kind == 'axe':
        cap(x - 2, y + 4, x + 3, y - 14, 0.9, 0.9, wood)
        poly([(x + 1, y - 10), (x + 9, y - 16), (x + 10, y - 7), (x + 2, y - 7)], metal, shade=0.7)
    elif kind == 'club':
        cap(x - 1, y + 3, x + 5, y - 13, 1.2, 3.4, wood, tex=0.25)
        for (a, b) in [(x + 4, y - 11), (x + 6.5, y - 9), (x + 3, y - 14)]:
            X, Y = T(a, b)
            c.px(X, Y, '#d8d0c0')
    elif kind == 'pick':
        cap(x - 1, y + 3, x + 3, y - 13, 0.9, 0.9, wood)
        a = T(x - 4, y - 10)
        b = T(x + 3, y - 14)
        d = T(x + 10, y - 9)
        c.chain([a, b, d], 1.4 * s, 0.6 * s, metal)
    elif kind == 'staff':
        cap(x - 1, y + 10, x + 2, y - 20, 1.0, 1.0, wood)
        orb = c.M(P.get('orb', '#8060ff'))
        ell(x + 2.3, y - 22, 2.8, 2.8, orb, amb=0.5)
        X, Y = T(x + 1.6, y - 23)
        c.px(X, Y, '#ffffff')
    elif kind == 'mace':
        cap(x - 1, y + 3, x + 2, y - 9, 0.9, 0.9, wood)
        ell(x + 2.6, y - 11, 3, 3, gold)
        for a in range(6):
            t = a / 6 * math.tau
            X, Y = T(x + 2.6 + math.cos(t) * 3.4, y - 11 + math.sin(t) * 3.4)
            c.px(X, Y, '#fff0a0')
    elif kind == 'bow':
        a = T(x + 1, y - 13)
        b = T(x + 5, y)
        d = T(x + 1, y + 13)
        c.chain([a, b, d], 1.0 * s, 1.0 * s, wood)
        A = T(x + 1, y - 13)
        D = T(x + 1, y + 13)
        F = T(fh[0] + 1, fh[1])
        c.line(A[0], A[1], F[0], F[1], '#e8e0c8')
        c.line(F[0], F[1], D[0], D[1], '#e8e0c8')
        a2 = T(fh[0], fh[1])
        c.line(a2[0], a2[1], T(x + 8, y)[0], T(x + 8, y)[1], '#d0b080')
    elif kind == 'shield_sword':
        # sword raised behind (far hand), shield in front (near)
        fx, fy = fh
        cap(fx - 1, fy + 2, fx + 0.5, fy - 2, 1.0, 1.0, wood)
        cap(fx - 3, fy - 2.5, fx + 3, fy - 2, 0.8, 0.8, gold)
        poly([(fx - 1.2, fy - 3), (fx + 1.6, fy - 3), (fx + 3, fy - 21), (fx + 0.5, fy - 22)], metal, shade=0.75, grad=0.4, gdir=(1, 0))
        sh = c.M(P.get('shield', '#8a2a24'))
        poly([(x - 3, y - 7), (x + 5, y - 7), (x + 5, y + 2), (x + 1, y + 7), (x - 3, y + 2)], sh, shade=0.62, grad=0.3)
        poly([(x - 1.5, y - 6), (x + 3.5, y - 6), (x + 3.5, y - 5), (x - 1.5, y - 5)], gold, shade=0.8, edge=False)
        X, Y = T(x + 1, y - 1)
        c.px(X, Y, P.get('emblem', '#f0d060'))
        X, Y = T(x + 1, y)
        c.px(X, Y, P.get('emblem', '#f0d060'))
    elif kind == 'scythe':
        cap(x - 2, y + 8, x + 3, y - 18, 0.9, 0.9, wood)
        a = T(x + 3, y - 18)
        b = T(x + 12, y - 15)
        d = T(x + 15, y - 8)
        c.chain([a, b, d], 1.6 * s, 0.5 * s, metal)
    elif kind == 'claws':
        for i in range(3):
            X1, Y1 = T(x + 1, y - 1 + i)
            X2, Y2 = T(x + 5, y + i * 1.5)
            c.line(X1, Y1, X2, Y2, '#e8e8f0')


# ---------------------------------------------------------------------------------------------
# magical things
# ---------------------------------------------------------------------------------------------
def elemental(c, P):
    kind = P['kind']
    core = c.M(P['core'], contrast=0.8)
    body = c.M(P['body'], contrast=1.1)
    rng = c.rng
    if kind == 'fire':
        for i in range(7):
            x = 14 + i * 3.4
            h = 6 + rng.random() * 7
            c.poly([(x - 3, 30), (x + 3, 30), (x + rng.random() * 2 - 1, 30 - 14 - h)], body, shade=0.75, grad=0.6)
        c.poly([(16, 30), (32, 30), (24, 45)], body, shade=0.7, grad=0.6)
    elif kind == 'ice':
        for (a, b, d) in [((12, 28), (8, 6), (18, 22)), ((30, 24), (40, 4), (34, 26)), ((18, 34), (24, 47), (30, 34)), ((10, 36), (2, 30), (12, 30))]:
            c.poly([a, b, d], body, shade=0.75, grad=0.5)
    elif kind == 'earth':
        for (x, y, r) in [(16, 40, 4), (24, 43, 4.5), (32, 41, 3.6)]:
            c.ell(x, y, r, r * 0.8, body, tex=0.3)
    elif kind == 'void':
        c.poly([(15, 30), (33, 30), (28, 46), (24, 40), (20, 46)], body, shade=0.5, grad=0.5)
    # torso + head
    c.ell(24, 24, 8.5, 10, body, tex=0.2)
    c.ell(24, 23, 5, 6, core, flat=0.95, edge=False, dith=0.8)
    c.ell(27, 10, 5.2, 5.4, body, tex=0.15)
    # arms
    for side in (-1, 1):
        sx = 24 + side * 8
        pts = [(sx, 17), (sx + side * 5, 23), (sx + side * 6, 30)]
        for j, (x, y) in enumerate(pts):
            c.ell(x, y, 3.6 - j * 0.3, 3.2 - j * 0.3, body, tex=0.25, rot=rng.random())
    if kind == 'fire':
        for i in range(4):
            x = 23 + i * 2.2
            c.poly([(x - 2, 8), (x + 2, 8), (x, -1 - rng.random() * 3)], c.M(P['core']), shade=0.9, edge=False)
    eye = P.get('eye', '#ffffff')
    c.pxs([(28.5, 9.5), (29.5, 9.5), (26, 9.5)], eye)
    if P.get('stars'):
        for _ in range(int(14 * c.k)):
            c.px(16 + rng.random() * 16, 14 + rng.random() * 20, P['stars'])


def ghost(c, P):
    a = P.get('alpha', 215)
    body = c.M(P['body'], contrast=0.8)
    hair = c.M(P.get('hair', shade_col(P['body'], 0.75)))
    c.poly([(30, 6), (12, 8), (4, 18), (10, 20), (6, 28), (16, 22)], hair, shade=0.5, alpha=a, tex=0.1)
    c.poly([(18, 14), (32, 14), (30, 34), (18, 46), (22, 34), (14, 40), (16, 28)], body, shade=0.65, grad=0.5, alpha=a, dith=0.8)
    c.ell(25, 18, 7.5, 7, body, alpha=a)
    c.cap(30, 18, 40, 22, 2.2, 1.6, body, alpha=a)
    c.cap(22, 18, 32, 26, 2.0, 1.4, body, alpha=a)
    c.ell(29, 10, 5.4, 6, body, alpha=a)
    c.ell(31, 10.5, 1.3, 1.8, c.M('#0c0a14'), flat=0.1)
    c.ell(28, 10.5, 1.2, 1.6, c.M('#0c0a14'), flat=0.1)
    c.px(31, 10.5, P.get('eye', '#a0f0ff'))
    c.px(28, 10.5, P.get('eye', '#a0f0ff'))
    c.ell(31, 14.5, 1.2, 1.8, c.M('#100c14'), flat=0.1, edge=False)
    if P.get('crown'):
        crown(c, 29, 3.5, 0.8, P.get('crown_col', '#c0c8d8'))


def dragon(c, P):
    sc = c.M(P['scale'])
    far = c.M(shade_col(P['scale'], 0.65))
    belly = c.M(P['belly'])
    wing = c.M(P['wing'], contrast=0.9)
    horn = c.M(P.get('horn', '#e8dcc0'))
    # far wing
    c.poly([(22, 22), (12, 0), (2, 6), (8, 14), (4, 20), (14, 24)], c.M(shade_col(P['wing'], 0.6)), shade=0.5)
    # tail
    c.chain([(12, 32), (5, 36), (2, 42), (8, 46)], 4.5, 1.2, sc, tex=0.12)
    c.poly([(7, 44), (12, 48), (3, 48)], horn)
    # far legs
    c.cap(28, 34, 31, 43, 2.8, 2.3, far)
    c.cap(15, 34, 13, 43, 3.0, 2.4, far)
    # body
    c.ell(21, 31, 12, 8.5, sc, tex=0.15)
    c.ell(23, 35, 9, 3.4, belly, edge=False)
    # neck + head
    c.chain([(29, 28), (33, 20), (35, 14)], 4.6, 3.2, sc, tex=0.12)
    c.ell(37, 11, 5, 4.2, sc, tex=0.1)
    c.ell(42.5, 13, 4.6, 2.4, sc)
    c.ell(42, 15.8, 4, 1.3, c.M(shade_col(P['scale'], 0.8)))
    c.chain([(35, 8), (31, 4), (28, 4.5)], 1.6, 0.6, horn)
    c.chain([(37.5, 7.5), (35, 2), (33, 0.5)], 1.6, 0.6, horn)
    c.px(39.5, 10, P.get('eye', '#ffe040'))
    c.px(40.5, 10, P.get('eye', '#ffe040'))
    c.px(46.5, 12.5, '#1a1010')
    for x in (41, 43, 45):
        c.px(x, 14.8, '#f0ecd8')
    # near legs
    c.cap(27, 35, 30, 44, 3.2, 2.7, sc, tex=0.1)
    c.cap(16, 35, 17, 44, 3.4, 2.8, sc, tex=0.1)
    for x in (31.5, 18.5):
        c.ell(x, 44.5, 3.4, 1.4, horn, edge=False)
    # near wing
    c.poly([(23, 25), (18, 3), (30, -1), (38, 2), (34, 6), (35, 11), (30, 10), (30, 16), (26, 15), (27, 22)], wing, shade=0.68, grad=0.45, tex=0.05, gdir=(1, 1))
    bone = shade_col(P['wing'], 0.45)
    c.line(24, 24, 20, 3, bone)
    c.line(21, 4, 34, -1, bone)
    c.line(24, 20, 33, 8, bone)
    c.line(26, 21, 35, 14, bone)
    if P.get('glow_pts'):
        rng = c.rng
        for _ in range(10):
            c.px(12 + rng.random() * 18, 27 + rng.random() * 8, P['glow_pts'])


def treant(c, P):
    bark = c.M(P['bark'])
    barkd = c.M(shade_col(P['bark'], 0.7))
    leaf = c.M(P['leaf'])
    leaf2 = c.M(shade_col(P['leaf'], 0.75))
    # far arm + legs
    c.chain([(18, 18), (10, 24), (6, 32)], 2.8, 1.4, barkd, tex=0.3)
    c.chain([(20, 34), (16, 40), (11, 44)], 3.2, 1.6, barkd, tex=0.3)
    c.ell(14, 6, 11, 7, leaf2, tex=0.4, dith=0.8)
    c.chain([(24, 44), (23, 30), (24, 16), (25, 8)], 7.5, 5, bark, tex=0.35)
    c.chain([(27, 34), (31, 40), (36, 44)], 3.4, 1.6, bark, tex=0.3)
    c.chain([(28, 17), (36, 22), (42, 30)], 3.0, 1.4, bark, tex=0.3)
    c.chain([(41, 29), (45, 27)], 1.0, 0.6, bark)
    c.chain([(41, 30), (44, 33)], 1.0, 0.6, bark)
    c.ell(28, 4, 12, 7.5, leaf, tex=0.45, dith=0.8)
    c.ell(18, 2, 7, 5, leaf, tex=0.45, dith=0.8)
    c.ell(37, 20, 5, 3.5, leaf, tex=0.4, dith=0.8)
    eye = P.get('eye', '#c8ff60')
    c.pxs([(27, 16), (28, 16), (31, 16), (32, 16)], eye)
    c.ell(29.5, 22, 3, 1.6, c.M('#1c120c'), flat=0.1)
    for _ in range(int(8 * c.k)):
        c.px(14 + c.rng.random() * 26, 0.5 + c.rng.random() * 9, P.get('flower', '#f0a0c0'))


def golem(c, P):
    st = c.M(P['stone'])
    far = c.M(shade_col(P['stone'], 0.68))
    # far arm
    c.chain([(16, 16), (11, 25), (10, 33)], 4, 3.4, far, tex=0.35)
    c.ell(10, 35, 4.4, 4, far, tex=0.35)
    # legs
    c.cap(19, 32, 18, 42, 4.2, 4.0, far, tex=0.3)
    c.cap(29, 32, 30, 42, 4.4, 4.2, st, tex=0.3)
    # torso
    c.poly([(12, 12), (36, 10), (34, 34), (15, 35)], st, shade=0.62, grad=0.35, tex=0.35)
    c.ell(24, 22, 4, 4, c.M(P['core']), flat=0.95, edge=False)
    c.poly([(19, 4), (30, 3), (31, 12), (20, 13)], st, shade=0.7, tex=0.3)
    c.pxs([(27, 7), (28.5, 7)], P.get('eye', P['core']))
    # shoulder crystals
    if P.get('crystal'):
        cr = c.M(P['crystal'])
        c.poly([(13, 12), (12, 0), (18, 9)], cr, shade=0.8)
        c.poly([(33, 10), (38, -1), (37, 11)], cr, shade=0.8)
        c.poly([(30, 33), (32, 26), (35, 33)], cr, shade=0.8)
    # near arm
    c.chain([(33, 14), (38, 24), (39, 31)], 4.4, 3.8, st, tex=0.35)
    c.ell(39.5, 34, 5, 4.6, st, tex=0.35)
    if P.get('cracks'):
        rng = c.rng
        for _ in range(6):
            x, y = 15 + rng.random() * 18, 14 + rng.random() * 18
            for s in range(5):
                c.px(x, y, P['cracks'])
                x += rng.random() * 2 - 1
                y += rng.random() * 1.6


def eyebeast(c, P):
    fl = c.M(P['flesh'])
    tent = c.M(P.get('tentacle', shade_col(P['flesh'], 0.8)))
    rng = c.rng
    for i in range(6):
        x0 = 14 + i * 4
        ph = rng.random() * 6
        pts = [(x0 + math.sin(ph + j * 1.1) * 3, 30 + j * 4) for j in range(4)]
        c.chain(pts, 2.4, 0.8, tent)
    if P.get('stalks'):
        for (x, y) in [(14, 6), (24, 0), (34, 5)]:
            c.chain([(24, 14), ((24 + x) / 2, (14 + y) / 2 + 2), (x, y)], 1.5, 1.0, tent)
            c.ell(x, y, 2.4, 2.4, c.M('#f0e8e0'), flat=0.9)
            c.px(x + 0.6, y, P.get('iris', '#e03030'))
    c.ell(24, 22, 14, 13, fl, tex=0.18)
    c.ell(27, 19, 7.6, 6.4, c.M('#f2ece4', contrast=0.5))
    c.ell(29, 19, 4.4, 4.4, c.M(P.get('iris', '#e03030')), amb=0.5)
    c.ell(30, 19, 1.4, 2.6, c.M('#0a0606'), flat=0.1, edge=False)
    c.px(27, 17, '#ffffff')
    c.poly([(19, 13), (35, 12), (34, 15), (20, 15)], fl, shade=0.5)
    c.ell(27, 30, 5, 2, c.M('#2a0a10'), flat=0.15)
    for x in range(23, 32, 2):
        c.px(x, 29.2, '#f0e8d0')
    if P.get('crown'):
        crown(c, 24, 9, 1.1, P.get('crown_col', '#f0c040'))


# ---------------------------------------------------------------------------------------------
# effects
# ---------------------------------------------------------------------------------------------
def fx_bolt(w, h, core, outer, kind):
    c = Canvas(w, h)
    o = c.M(outer)
    k = c.M(core)
    if kind == 'fire':
        c.poly([(0, h / 2), (w * 0.55, 1), (w * 0.62, h - 1)], o, shade=0.8)
        c.ell(w * 0.66, h / 2, h * 0.42, h * 0.42, o, amb=0.6)
        c.ell(w * 0.7, h / 2, h * 0.25, h * 0.25, k, flat=1.0, edge=False)
    elif kind == 'frost':
        c.poly([(0, h / 2), (w * 0.6, 1), (w, h / 2), (w * 0.6, h - 1)], o, shade=0.8, grad=0.3)
        c.poly([(w * 0.3, h / 2), (w * 0.65, 3), (w * 0.9, h / 2), (w * 0.65, h - 3)], k, shade=0.95, edge=False)
    elif kind == 'orb':
        c.ell(w / 2, h / 2, w * 0.4, h * 0.4, o, amb=0.6)
        c.ell(w / 2, h / 2, w * 0.22, h * 0.22, k, flat=1.0, edge=False)
    elif kind == 'arrow':
        c.cap(1, h / 2, w - 4, h / 2, 0.6, 0.6, c.M('#8a6440'), flat=0.7)
        c.poly([(w - 5, 0.5), (w, h / 2), (w - 5, h - 0.5)], c.M('#c0c8d0'), shade=0.8)
        c.poly([(0, 0.5), (4, h / 2), (0, h - 0.5)], c.M('#e8e0d0'), shade=0.8)
        return c.render(outline=None)
    return c.render(outline=None, glow=outer, glow_r=1.5, glow_a=0.6)


def fx_slash(size, col):
    from PIL import ImageDraw
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (a, w) in enumerate([(120, 5), (200, 3), (255, 1)]):
        d.arc([2 + i, 2 + i, size - 3 - i, size - 3 - i], 200, 330, fill=rgb(col) + (a,), width=w)
    return img


def fx_ring(size, col):
    from PIL import ImageDraw
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(3):
        r = size / 2 - 1 - i * 4
        d.ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r], outline=rgb(col) + (230 - i * 60,), width=2)
    return img


def fx_whirl(size, col):
    from PIL import ImageDraw
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for k in range(3):
        st = k * 120
        d.arc([2, 2, size - 3, size - 3], st, st + 70, fill=rgb(col) + (255,), width=3)
        d.arc([7, 7, size - 8, size - 8], st + 40, st + 100, fill=rgb('#ffffff') + (200,), width=2)
    return img


def fx_sparkle(size, col):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    c = rgb(col)
    m = size // 2
    for i in range(size):
        dd = abs(i - m)
        a = max(0, 255 - dd * (255 // max(1, m)))
        img.putpixel((i, m), c + (a,))
        img.putpixel((m, i), c + (a,))
    for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        img.putpixel((m + dx, m + dy), c + (160,))
    img.putpixel((m, m), (255, 255, 255, 255))
    return img


def fx_pillar(w, h, col):
    import numpy as np
    arr = np.zeros((h, w, 4), np.uint8)
    c = rgb(col)
    xs = np.abs(np.arange(w) - (w - 1) / 2) / (w / 2)
    for y in range(h):
        fade = (y / h) ** 0.7
        for x in range(w):
            a = max(0.0, 1 - xs[x] ** 1.6) * fade
            a = round(a * 4) / 4
            arr[y, x, :3] = c if xs[x] > 0.3 else (255, 255, 230)
            arr[y, x, 3] = int(a * 220)
    return Image.fromarray(arr, 'RGBA')


def fx_bobber():
    c = Canvas(8, 12)
    r = c.M('#d02820')
    w = c.M('#f0ece0')
    c.cap(4, 1, 4, 4, 0.6, 0.6, c.M('#604020'), flat=0.6)
    c.ell(4, 6, 3, 2.4, r, clip=lambda x, y: y < 6.5)
    c.ell(4, 7, 3, 2.4, w, clip=lambda x, y: y >= 6.5)
    return c.render()


# ---------------------------------------------------------------------------------------------
# catalogue
# ---------------------------------------------------------------------------------------------
def mk(fn, P, size=48, mirror=True, glow=None, seed=3):
    c = Canvas(size, size, design=48, seed=seed)
    fn(c, P)
    img = c.render(glow=glow, glow_r=max(1.5, size / 24))
    # pad top so tall bits (wings, crowns) are not clipped by the outline
    return flip(img) if mirror else img


HERO = dict(
    krieger=dict(skin='#e0a880', cloth='#9aa4b4', pants='#7a8494', boots='#5a5050', metal='#c8d0dc', helm='#b0bac8',
                 plume='#c02828', tabard='#a02424', shoulders='#b8c2d0', weapon='shield_sword', far_hand=(18, 12),
                 near_hand=(31, 25), shield='#8a2420', emblem='#f0c040', belt='#5a3a24', glove='#9aa4b4', w=1.12),
    magier=dict(skin='#e8b894', cloth='#5a3ca8', robe='#4a30a0', trim='#e0b040', hood='#43298a', weapon='staff',
                near_hand=(32, 26), orb='#60c0ff', glove='#e8b894', belt='#e0b040', shoulders='#6a48c0'),
    jaeger=dict(skin='#d8a078', cloth='#5a7a3a', pants='#5a4632', boots='#3a2a20', hood='#4a6a2c', cape='#3a5a28',
                weapon='bow', near_hand=(33, 22), far_hand=(27, 22), wood='#8a5a2c', belt='#4a3020', glove='#6a4a30'),
    priester=dict(skin='#f0c8a0', cloth='#e8e4dc', robe='#e4e0d6', trim='#d8a830', hair='#e8d070', weapon='mace',
                  near_hand=(32, 25), gold='#f0c848', belt='#d8a830', shoulders='#f0ece4'),
)

COMPANION = dict(
    tank=dict(HERO['krieger'], cloth='#5470b0', pants='#3c4c7c', helm='#c0a040', plume='#3050c0', tabard='#2a3c8a',
              shoulders='#d0b050', shield='#24408a', metal='#d8dce4', glove='#5470b0', beard='#8a5a30'),
    heiler=dict(HERO['priester'], cloth='#7ab060', robe='#5a9a48', trim='#f0e0a0', hair='#a05a30', shoulders='#8ac070'),
    schuetze=dict(HERO['jaeger'], cloth='#8a3a2a', hood='#6a2a20', cape='#5a2018', pants='#3a2a24'),
    zauberin=dict(HERO['magier'], cloth='#a03030', robe='#7a1e22', hood='#5a1418', orb='#ff8040', trim='#f0c040',
                  shoulders='#b03838'),
)


def catalogue():
    S = {}
    # heroes & companions (face right)
    for k, P in HERO.items():
        S['hero_' + k] = mk(humanoid, dict(P, head=5.8), 56, mirror=False)
    for k, P in COMPANION.items():
        S['comp_' + k] = mk(humanoid, P, 48, mirror=False)
    # arena rivals face left
    for k, P in HERO.items():
        S['rival_' + k] = mk(humanoid, dict(P, cloth=shade_col(P['cloth'], 0.8)), 48)

    Q = quadruped
    S['waldwolf'] = mk(Q, dict(fur='#8a7a68', eye='#ffd23a'))
    S['graufang'] = mk(Q, dict(fur='#585866', eye='#ff4020', body=13, head=6.8), 56)
    S['hyaene'] = mk(Q, dict(fur='#c09a58', spots='#6a4a28', mane='#7a5a30', eye='#ffe040'))
    S['frostwolf'] = mk(Q, dict(fur='#d0dcea', eye='#40c8ff', ear_in='#90a8d0'))
    S['lavahund'] = mk(Q, dict(fur='#4a3030', eye='#ffb020', cracks='#ff7020', spikes='#2a1a1a', ear_in='#ff6020'), glow=None)
    S['krokilisk'] = mk(Q, dict(fur='#5e8040', low=True, spikes='#3e5a28', ears=False, eye='#ffe020', snout=7, head=5, belly='#c8c890'))
    S['sternenbestie'] = mk(Q, dict(fur='#5a3a8a', eye='#80ffff', stars='#ffffff', horns='#c0a0ff', ear_in='#a080ff'))
    S['magmaul'] = mk(Q, dict(fur='#3a2626', eye='#ffd040', cracks='#ff8030', spikes='#1a1010', horns='#2a1a1a', body=13, head=7), 80, glow='#ff6020')
    S['sternenfresser'] = mk(Q, dict(fur='#3a2470', eye='#ff60ff', stars='#e0e0ff', horns='#e0c0ff', body=13, head=7), 80, glow='#9050ff')
    S['krokilisk_alpha'] = mk(Q, dict(fur='#3e6a50', low=True, spikes='#c8b040', ears=False, eye='#ff3020', snout=7.5, head=5.4, belly='#d8d8a0'), 72)

    Sp = spider
    S['waldspinne'] = mk(Sp, dict(body='#5a4636', pattern='#a04a2a'))
    S['skorpid'] = mk(Sp, dict(body='#c89a48', scorp=True, sting='#5a2a1a'))
    S['skarabaeus'] = mk(Sp, dict(body='#2a8a8a', scorp=True, sting='#f0c040', eye='#f0ff60'), 72)
    S['leerenbrut'] = mk(Sp, dict(body='#3a2a5a', pattern='#a050ff', eye='#60ffe0'), 72, glow='#7040c0')
    S['hoehlenspinne'] = mk(Sp, dict(body='#3a3a50', pattern='#60c0ff', eye='#60e0ff'), 72)
    S['glutweberin'] = mk(Sp, dict(body='#4a2018', pattern='#ff8020', eye='#ffe040'), 80, glow='#ff5010')

    S['moorschleim'] = mk(slime, dict(body='#78b040', inner='#4a7a28'))
    S['schlammbrocken'] = mk(slime, dict(body='#7a6a40', inner='#4a3a20'), 60)
    S['sporenmutter'] = mk(slime, dict(body='#a060c0', inner='#f0a0e0', crown=True), 72)

    S['sandwurm'] = mk(worm, dict(body='#c8a070', sand='#d8b878'))

    H = humanoid
    S['kobold'] = mk(H, dict(skin='#a88a6a', cloth='#8a6a4a', pants='#6a4a30', candle=True, weapon='pick', scale=0.78, head=6.2, big_eye=True, eye='#ffd040', bare_arms=True, ears_long=True))
    S['kragg'] = mk(H, dict(skin='#a07a5a', cloth='#6a4a34', pants='#4a3424', candle=True, weapon='pick', scale=1.0, head=6.2, big_eye=True, eye='#ff6020', bare_arms=True, ears_long=True, belt='#c0a040', w=1.15), 72)
    S['schnarr'] = mk(H, dict(skin='#7a8aa0', cloth='#3a4a6a', pants='#2a3048', candle=True, weapon='pick', scale=0.95, head=6.2, big_eye=True, eye='#60e0ff', bare_arms=True, ears_long=True), 72)
    S['sumpfkriecher'] = mk(H, dict(skin='#4a9a8a', cloth='#4a9a8a', pants='#3a7a6a', bare_arms=True, fins='#d06040', weapon='claws', hunch=3, eye='#ffe040', big_eye=True, w=0.95, boots='#3a7a6a'))
    S['morva'] = mk(H, dict(skin='#90b070', cloth='#4a2a5a', robe='#3a2048', trim='#80c040', witch_hat='#2a1838', weapon='staff', orb='#80ff60', hair='#303030', hunch=2, eye='#c0ff40'), 72, glow='#60c030')
    S['ulgra'] = mk(H, dict(skin='#7ab090', cloth='#2a4a3a', robe='#1e3a2a', trim='#c0a040', witch_hat='#1a2a20', weapon='staff', orb='#c040ff', hair='#c0c0c0', hunch=2, eye='#ff40ff'), 72, glow='#a040e0')
    S['oger'] = mk(H, dict(skin='#c08a5a', cloth='#6a4a30', pants='#5a3c28', bare_arms=True, weapon='club', w=1.45, head=4.6, hunch=3, tusks=True, eye='#201010'))
    S['brug'] = mk(H, dict(skin='#8aa060', cloth='#5a3a5a', pants='#4a2a3a', bare_arms=True, weapon='staff', orb='#ff60a0', w=1.4, head=4.8, hunch=3, tusks=True, horns='#e8e0c8'), 60, glow='#e04090')
    S['gromm'] = mk(H, dict(skin='#b07048', cloth='#5a2a1e', pants='#4a2418', bare_arms=True, weapon='axe', w=1.55, head=4.8, hunch=3, tusks=True, horns='#e8dcc0', crown=True, metal='#a0a8b0'), 76)
    S['mumie'] = mk(H, dict(skin='#c8b890', cloth='#c8b890', pants='#b0a078', bare_arms=True, tex=0.4, eye='#60ff80', big_eye=True, boots='#a89870', hunch=1))
    S['ankhu'] = mk(H, dict(skin='#c8b890', cloth='#3a6a9a', pants='#b0a078', bare_arms=True, tex=0.4, eye='#60ffe0', weapon='scythe', metal='#e0c050', shoulders='#e0b040', helm='#e0b040', boots='#a89870'), 60)
    S['khet'] = mk(H, dict(skin='#c0b088', cloth='#2a4a8a', robe='#e0c060', trim='#3a6ab0', eye='#40ffc0', weapon='staff', orb='#40ffc0', crown=True, crown_col='#f0d050', tex=0.3), 76, glow='#40e0b0')
    S['nefra'] = mk(H, dict(skin='#c8b890', cloth='#e0c060', robe='#d8d0b0', trim='#3070c0', eye='#f060ff', weapon='staff', orb='#f060ff', hair='#202020', tex=0.35), 72, glow='#c040e0')
    S['yeti'] = mk(H, dict(skin='#e4ecf4', cloth='#e4ecf4', pants='#c8d4e4', bare_arms=True, tex=0.35, w=1.4, hunch=3, head=5, horns='#a0b0c0', eye='#2050a0', boots='#a8b8cc', weapon='claws'))
    S['eisklaue'] = mk(H, dict(skin='#c0d8f0', cloth='#c0d8f0', pants='#a0b8d8', bare_arms=True, tex=0.35, w=1.5, hunch=3, head=5, horns='#4080c0', eye='#60e0ff', boots='#8098c0', weapon='claws'), 60)
    S['yeti_boss'] = mk(H, dict(skin='#f0f4f8', cloth='#f0f4f8', pants='#d0dce8', bare_arms=True, tex=0.35, w=1.6, hunch=3, head=5.2, horns='#3060a0', eye='#ff4020', boots='#a8b8cc', weapon='club', wood='#6a8aaa'), 72)
    S['halvar'] = mk(H, dict(skin='#b8d0e8', cloth='#3a5a8a', robe='#2a4a7a', trim='#c0e0ff', hood='#1e3a68', weapon='staff', orb='#a0f0ff', beard='#e0e8f0', eye='#a0f0ff'), 72, glow='#60c0ff')
    S['ghul'] = mk(H, dict(skin='#8aa080', cloth='#5a5a4a', pants='#4a4a3a', bare_arms=True, hunch=4, eye='#ff3020', weapon='claws', tex=0.25, boots='#4a4a3a'))
    S['skelett'] = mk(H, dict(skin='#e0dccc', cloth='#e0dccc', bones=True, weapon='sword', near_hand=(31, 25), metal='#909aa8', eye='#60e0ff', shoulders='#6a6a74', w=1.0))
    S['knochenwaechter'] = mk(H, dict(skin='#d8d4c4', cloth='#4a4a5a', bones=True, armor_torso=True, weapon='axe', helm='#5a5a6a', metal='#8a94a4', eye='#ff4040', shoulders='#5a5a6a', w=1.25), 60)
    S['kryoskelett'] = mk(H, dict(skin='#c8e0f0', cloth='#c8e0f0', bones=True, weapon='scythe', metal='#a0e0ff', eye='#60f0ff', w=1.1), 72, glow='#60c0ff')
    S['knochenkoloss'] = mk(H, dict(skin='#d8d0bc', cloth='#3a3a46', bones=True, armor_torso=True, weapon='club', wood='#d8d0bc', helm='#3a3a46', eye='#ff3030', shoulders='#3a3a46', w=1.6, scale=1.0), 76)
    S['varn'] = mk(H, dict(skin='#d8d4c8', cloth='#2a3a5a', bones=True, armor_torso=True, weapon='sword', near_hand=(31, 25), helm='#2a3a5a', plume='#8090c0', metal='#c0d8f0', eye='#60e0ff', shoulders='#30406a', crown=True, crown_col='#a0c0e0', w=1.3), 80, glow='#5090e0')
    S['mordrek'] = mk(H, dict(skin='#d0ccc0', cloth='#3a1e5a', bones=True, robe='#2e1648', trim='#a080e0', weapon='staff', orb='#60ff80', crown=True, crown_col='#b0b8c8', eye='#60ff80', shoulders='#4a2a6a'), 76, glow='#50e070')
    S['malhar'] = mk(H, dict(skin='#d0c8b8', cloth='#6a1818', bones=True, robe='#4a1010', trim='#f0c040', weapon='scythe', metal='#f0c040', crown=True, eye='#ff5030', shoulders='#7a2020'), 72, glow='#e03020')
    S['nebelkoenig'] = mk(H, dict(skin='#d8e0e8', cloth='#1e3050', bones=True, robe='#18263e', trim='#80c0ff', weapon='sword', near_hand=(31, 25), metal='#a0d8ff', crown=True, crown_col='#a0e0ff', eye='#a0f0ff', shoulders='#2a4060', cape='#101c30'), 84, glow='#60b0ff')
    S['wichtel'] = mk(H, dict(skin='#d04a30', cloth='#d04a30', pants='#a03420', bare_arms=True, horns='#3a2020', tail='#a03420', wings='#7a2a20', eye='#ffe040', big_eye=True, scale=0.75, head=6, ears_long=True, boots='#3a1a14'))
    S['aschenfaust'] = mk(H, dict(skin='#8a2a20', cloth='#3a2a2a', pants='#2a1a1a', bare_arms=True, horns='#1a1010', tail='#6a1a14', wings='#4a1a14', eye='#ffd040', weapon='axe', metal='#ff9040', w=1.4, shoulders='#2a1a1a'), 80, glow='#ff5020')
    S['ignaroth'] = mk(H, dict(skin='#c03018', cloth='#2a1a1a', pants='#1a1010', bare_arms=True, horns='#1a1010', tail='#8a2010', wings='#5a1a10', eye='#fff060', weapon='sword', near_hand=(31, 25), metal='#ff8030', w=1.5, crown=True, crown_col='#ff9030', shoulders='#3a1a14'), 80, glow='#ff6020')

    E = elemental
    S['staubelementar'] = mk(E, dict(kind='earth', body='#9a7a58', core='#e0c090', eye='#ffe080'))
    S['eiselementar'] = mk(E, dict(kind='ice', body='#9ad0f0', core='#f0ffff', eye='#ffffff'), glow='#80d0ff')
    S['feuerelementar'] = mk(E, dict(kind='fire', body='#f06020', core='#ffe070', eye='#ffffff'), glow='#ff7020')
    S['leerwandler'] = mk(E, dict(kind='void', body='#4a2a7a', core='#c080ff', eye='#80ffff', stars='#ffffff'), glow='#8040e0')
    S['ignis'] = mk(E, dict(kind='fire', body='#ff4010', core='#fff0a0', eye='#ffffff'), 84, glow='#ff8020')

    S['banshee'] = mk(ghost, dict(body='#b8c8e0', hair='#8090b0', eye='#a0f0ff'), glow='#80a0e0')
    S['velia'] = mk(ghost, dict(body='#e0a0a0', hair='#a03040', eye='#ff4040', crown=True, crown_col='#e0c0c0'), 72, glow='#e05060')
    S['bleiche_dame'] = mk(ghost, dict(body='#e0e8f0', hair='#c0d0e8', eye='#60d0ff', crown=True), 80, glow='#a0d0ff')

    D = dragon
    S['glaciara'] = mk(D, dict(scale='#90c0e8', belly='#e0f0ff', wing='#6aa0d8', eye='#ffffff', horn='#e8f4ff'), 84, glow='#80c8ff')
    S['nivara'] = mk(D, dict(scale='#5a80c8', belly='#c0d8ff', wing='#3a5aa8', eye='#a0ffff', horn='#e0f0ff'), 84, glow='#60a0ff')
    S['umbrax'] = mk(D, dict(scale='#3a2060', belly='#7a50b0', wing='#2a1450', eye='#ff60ff', horn='#c0a0e0', glow_pts='#e0a0ff'), 84, glow='#8040e0')
    S['xaroth'] = mk(D, dict(scale='#1a3a4a', belly='#40a0a0', wing='#0e2a38', eye='#60ffe0', horn='#a0e0e0', glow_pts='#60ffe0'), 84, glow='#30c0b0')
    S['azurschwinge'] = mk(D, dict(scale='#3a70d0', belly='#a0c8f0', wing='#2a58b0', eye='#ffe040', horn='#f0e8d0'), 84)

    S['eiche'] = mk(treant, dict(bark='#6a4a32', leaf='#5a9a3a', eye='#e0ff60'), 84)
    S['verderbte_eiche'] = mk(treant, dict(bark='#4a3a40', leaf='#6a4a8a', eye='#ff60a0', flower='#40ff80'), 84, glow='#a060c0')

    G = golem
    S['erzkoloss'] = mk(G, dict(stone='#7a7068', core='#40a0ff', crystal='#60c0ff', eye='#80e0ff'), 72)
    S['steinwaechter'] = mk(G, dict(stone='#c8a878', core='#40ffc0', eye='#40ffc0', cracks='#30e0a0'), 72)
    S['magmagolem'] = mk(G, dict(stone='#4a3632', core='#ffa030', cracks='#ff7020', eye='#ffe040'), 60, glow='#ff6020')
    S['augenlose_wache'] = mk(G, dict(stone='#3a3050', core='#c060ff', crystal='#a060ff', eye='#e0a0ff'), 60, glow='#7040c0')
    S['abgrundwaechter'] = mk(G, dict(stone='#2a2440', core='#60ffe0', crystal='#40e0c0', eye='#60ffe0', cracks='#40e0c0'), 80, glow='#30c0a0')
    S['grollhuf'] = mk(G, dict(stone='#6a6a58', core='#e0ff60', crystal='#90c040', eye='#e0ff60'), 84)

    EB = eyebeast
    S['tentakelgrauen'] = mk(EB, dict(flesh='#6a3a6a', iris='#e0e040'))
    S['tentakelmeister'] = mk(EB, dict(flesh='#3a6a4a', iris='#ff4040', stalks=True), 72, glow='#40c070')
    S['zwillingsaugen'] = mk(EB, dict(flesh='#8a2a3a', iris='#ffe040', stalks=True), 80, glow='#e04050')
    S['nhalzor'] = mk(EB, dict(flesh='#4a2a6a', iris='#60ffff', stalks=True, crown=True, crown_col='#c0a0ff'), 88, glow='#8050ff')

    # effects (face right, no mirror)
    S['fx_fire'] = fx_bolt(16, 10, '#fff0a0', '#ff6a20', 'fire')
    S['fx_frost'] = fx_bolt(16, 8, '#ffffff', '#70c8ff', 'frost')
    S['fx_arcane'] = fx_bolt(12, 12, '#ffffff', '#c070ff', 'orb')
    S['fx_holy'] = fx_bolt(12, 12, '#ffffff', '#ffd850', 'orb')
    S['fx_shadow'] = fx_bolt(12, 12, '#e0a0ff', '#50207a', 'orb')
    S['fx_nature'] = fx_bolt(12, 12, '#f0ffc0', '#60d040', 'orb')
    S['fx_arrow'] = fx_bolt(16, 5, '#ffffff', '#ffffff', 'arrow')
    S['fx_slash'] = fx_slash(32, '#fff4d0')
    S['fx_whirl'] = fx_whirl(40, '#e0e8ff')
    S['fx_ring'] = fx_ring(40, '#ffd060')
    S['fx_ring_green'] = fx_ring(40, '#80ff80')
    S['fx_spark'] = fx_sparkle(9, '#fff0a0')
    S['fx_spark_green'] = fx_sparkle(9, '#90ff90')
    S['fx_pillar'] = fx_pillar(24, 64, '#ffd860')
    S['fx_bobber'] = fx_bobber()
    return S

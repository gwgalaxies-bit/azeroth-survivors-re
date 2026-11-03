"""UI textures, painted at 2x the CSS size: stone, parchment and wood surfaces, gilded 9-slice frames with
corner medallions, glossy buttons and bar fills, portrait and minimap rings, the winged elite frame."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from px import Paint, rgb, value_noise


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


GOLD = [(48, 28, 8), (110, 70, 22), (186, 136, 52), (236, 196, 108), (255, 244, 200)]
SILVER = [(22, 24, 30), (70, 74, 86), (140, 146, 160), (200, 206, 220), (250, 252, 255)]
IRON = [(14, 14, 18), (42, 42, 50), (82, 82, 94), (128, 128, 142), (190, 190, 205)]


def ramp_map(v, ramp):
    r = np.array(ramp, float)
    n = len(r)
    p = np.clip(v, 0, 1) * (n - 1)
    i = np.clip(np.floor(p).astype(int), 0, n - 2)
    f = (p - i)[..., None]
    return r[i] * (1 - f) + r[i + 1] * f


def surface(w, h, c1, c2, seed, scale=24, cracks=0.0, grain=0.06):
    n = value_noise(w, h, scale, seed, 5)
    n2 = value_noise(w, h, scale / 4, seed + 9, 3)
    t = np.clip((n - 0.5) * 2.2 + 0.5, 0, 1)
    a = np.array(rgb(c1), float) * (1 - t[..., None]) + np.array(rgb(c2), float) * t[..., None]
    a *= (1 + (n2 - 0.5) * grain * 2)[..., None]
    if cracks:
        n3 = value_noise(w, h, scale * 1.6, seed + 17, 4)
        e = np.exp(-((n3 - 0.5) / 0.012) ** 2) * cracks
        a *= (1 - e)[..., None]
        a += (np.roll(e, 1, axis=0) * 18)[..., None]
    out = np.zeros((h, w, 4), np.uint8)
    out[:, :, :3] = np.clip(a, 0, 255)
    out[:, :, 3] = 255
    return Image.fromarray(out, 'RGBA')


def parchment(w, h, seed=3):
    n = value_noise(w, h, 90, seed, 5, wrap=False)
    n2 = value_noise(w, h, 14, seed + 1, 4, wrap=False)
    y, x = np.mgrid[0:h, 0:w]
    d = np.maximum(np.abs(x - w / 2) / (w / 2), np.abs(y - h / 2) / (h / 2))
    burn = sstep(0.72, 1.0, d + (n - 0.5) * 0.25)
    base = np.array(rgb('#e6d3a8'), float)
    dark = np.array(rgb('#8a5e2c'), float)
    a = base * (0.92 + 0.12 * n[..., None] + 0.05 * (n2[..., None] - 0.5))
    stains = sstep(0.62, 0.75, value_noise(w, h, 60, seed + 5, 4, wrap=False))
    a = a * (1 - 0.12 * stains[..., None])
    a = a + (dark - a) * (burn * 0.75)[..., None]
    out = np.zeros((h, w, 4), np.uint8)
    out[:, :, :3] = np.clip(a, 0, 255)
    out[:, :, 3] = 255
    return Image.fromarray(out, 'RGBA')


def metal_profile(t):
    v = 0.42 + 0.62 * np.exp(-((t - 0.3) / 0.17) ** 2) - 0.32 * np.exp(-((t - 0.64) / 0.06) ** 2) + 0.18 * np.exp(-((t - 0.82) / 0.09) ** 2)
    return v * (0.35 + 0.65 * sstep(0, 0.12, t)) * (0.45 + 0.55 * sstep(1, 0.86, t))


def frame9(size, bar, ramp=GOLD, gem='#b01818', medal=True, seed=5, fill=None, inner_shadow=True):
    y, x = np.mgrid[0:size, 0:size].astype(float) + 0.5
    dl, dt, dr, db = x, y, size - x, size - y
    d = np.minimum(np.minimum(dl, dt), np.minimum(dr, db))
    t = d / bar
    face = np.where(np.minimum(dl, dt) <= np.minimum(dr, db), 1.12, 0.78)
    nz = value_noise(size, size, 6, seed, 3)
    v = metal_profile(np.clip(t, 0, 1)) * face * (0.92 + 0.16 * nz)
    col = ramp_map(v, ramp)
    out = np.zeros((size, size, 4), float)
    out[..., :3] = col
    out[..., 3] = np.where(t < 1, 255, 0)
    if fill is not None:
        m = t >= 1
        out[m, :3] = rgb(fill)
        out[m, 3] = 255
    if inner_shadow:
        sh = np.clip(1 - (t - 1) / 0.5, 0, 1) * (t >= 1)
        out[..., 3] = np.maximum(out[..., 3], sh * 150)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
    if medal:
        r = bar * 0.95
        for (cx, cy) in [(bar / 2 + 1, bar / 2 + 1), (size - bar / 2 - 1, bar / 2 + 1), (bar / 2 + 1, size - bar / 2 - 1), (size - bar / 2 - 1, size - bar / 2 - 1)]:
            img.alpha_composite(medallion(int(r * 2 + 4), ramp, gem, seed), (int(cx - r - 2), int(cy - r - 2)))
    return img


def medallion(s, ramp, gem, seed=1):
    y, x = np.mgrid[0:s, 0:s].astype(float) + 0.5
    c = s / 2
    r = s / 2 - 2
    dx, dy = (x - c) / r, (y - c) / r
    d = np.sqrt(dx ** 2 + dy ** 2)
    z = np.sqrt(np.clip(1 - d ** 2, 0, 1))
    light = np.clip(-dx * 0.5 - dy * 0.6 + z * 0.6, 0, 1.2)
    ring = np.clip(np.abs(d - 0.72) / 0.12, 0, 1)
    v = (0.35 + 0.75 * light) * (0.65 + 0.35 * ring)
    col = ramp_map(v, ramp)
    out = np.zeros((s, s, 4), float)
    out[..., :3] = col
    out[..., 3] = sstep(1.04, 0.96, d) * 255
    # gem
    g = np.array(rgb(gem), float)
    gd = d / 0.5
    gz = np.sqrt(np.clip(1 - gd ** 2, 0, 1))
    gl = np.clip(-dx * 0.8 - dy * 0.8 + gz, 0, 1.5)
    gcol = g * (0.35 + 0.8 * gl[..., None])
    spec = np.exp(-(((dx + 0.18) ** 2 + (dy + 0.18) ** 2) / 0.012)) * 255
    gcol = gcol + spec[..., None]
    m = sstep(1.02, 0.94, gd)[..., None]
    out[..., :3] = out[..., :3] * (1 - m) + gcol * m
    edge = np.exp(-((d - 1) / 0.06) ** 2)
    out[..., :3] *= (1 - 0.6 * edge)[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')


def button(w, h, base, rim_ramp=GOLD, pressed=False, seed=8, r=10):
    y, x = np.mgrid[0:h, 0:w].astype(float) + 0.5
    # rounded rect distance
    qx = np.maximum(np.abs(x - w / 2) - (w / 2 - r), 0)
    qy = np.maximum(np.abs(y - h / 2) - (h / 2 - r), 0)
    dist = r - np.sqrt(qx ** 2 + qy ** 2)
    inner = np.minimum(np.minimum(x, w - x), np.minimum(y, h - y))
    dd = np.where((qx > 0) & (qy > 0), dist, np.minimum(inner, r + 99))
    rim = 5.0
    t = dd / rim
    face = np.where(y < h / 2, 1.1, 0.8)
    v = metal_profile(np.clip(t, 0, 1)) * face
    col = ramp_map(v, rim_ramp)
    b = np.array(rgb(base), float)
    vy = (y - rim) / (h - 2 * rim)
    if pressed:
        shade = 0.55 + 0.35 * vy
    else:
        shade = 1.15 - 0.55 * vy + 0.45 * np.exp(-((vy - 0.12) / 0.1) ** 2)
    nz = value_noise(w, h, 10, seed, 3)
    pan = b * (shade * (0.95 + 0.1 * nz))[..., None]
    inside = sstep(0.9, 1.1, t)[..., None]
    col = col * (1 - inside) + pan * inside
    edge_dark = np.exp(-((t - 1.0) / 0.12) ** 2)[..., None]
    col *= 1 - 0.55 * edge_dark
    out = np.zeros((h, w, 4), float)
    out[..., :3] = col
    out[..., 3] = sstep(-0.5, 0.8, dd) * 255
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')


def bar(col, h=32, w=4):
    base = np.array(rgb(col), float)
    y = (np.arange(h) + 0.5) / h
    f = 1.25 - 0.6 * y + 0.55 * np.exp(-((y - 0.2) / 0.1) ** 2) - 0.25 * np.exp(-((y - 0.92) / 0.06) ** 2)
    arr = np.zeros((h, w, 4), np.uint8)
    arr[:, :, :3] = np.clip(base[None, :] * f[:, None], 0, 255)[:, None, :]
    arr[:, :, 3] = 255
    return Image.fromarray(arr, 'RGBA')


def ring(size, ramp=GOLD, thick=0.16, seed=2, studs=0):
    y, x = np.mgrid[0:size, 0:size].astype(float) + 0.5
    c = size / 2
    d = np.sqrt((x - c) ** 2 + (y - c) ** 2) / (size / 2 - 1)
    t = (1 - d) / thick
    ang = np.arctan2(y - c, x - c)
    face = 0.85 + 0.3 * np.cos(ang + 2.3)
    nz = value_noise(size, size, 8, seed, 3)
    v = metal_profile(np.clip(t, 0, 1)) * face * (0.92 + 0.16 * nz)
    col = ramp_map(v, ramp)
    out = np.zeros((size, size, 4), float)
    out[..., :3] = col
    a = sstep(1.01, 0.99, d) * sstep(-0.05, 0.05, 1 - thick - (1 - d) + thick) * 0 + sstep(1.01, 0.99, d) * sstep(1 - thick - 0.02, 1 - thick + 0.02, d)
    out[..., 3] = a * 255
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
    if studs:
        r = size / 2 - 1 - size * thick / 4
        s = int(size * thick * 0.9)
        for i in range(studs):
            a2 = i / studs * math.tau - math.pi / 2
            px, py = c + math.cos(a2) * r, c + math.sin(a2) * r
            img.alpha_composite(medallion(s + 4, ramp, '#3a2a10', seed), (int(px - s / 2 - 2), int(py - s / 2 - 2)))
    return img


def wings(size=200):
    """Winged elite ornament around a portrait ring (the ring sits centred at the right side)."""
    c = Paint(size, size, design=100, ss=2)
    gold = c.M('#d8a840', gloss=0.8, contrast=1.2)
    dark = c.M('#8a5a18', gloss=0.5)
    cx, cy = 62, 52
    for i, (ang, ln, wd) in enumerate([(-2.35, 44, 7), (-2.75, 48, 7), (-3.1, 46, 6.5), (2.85, 40, 6)]):
        x2, y2 = cx + math.cos(ang) * ln, cy + math.sin(ang) * ln
        nx, ny = -math.sin(ang), math.cos(ang)
        pts = [(cx + nx * wd, cy + ny * wd), (x2 + nx * 1.5, y2 + ny * 1.5), (x2 - math.cos(ang) * 3, y2 - math.sin(ang) * 3), (x2 - nx * 1.5, y2 - ny * 1.5), (cx - nx * wd, cy - ny * wd)]
        c.poly(pts, gold if i % 2 == 0 else dark, shade=0.7, grad=0.5, gdir=(math.cos(ang), math.sin(ang)))
    img = c.render(outline=(30, 16, 4, 230), rim_a=0, out_w=0.6)
    return img


def marker(char, col, size=(40, 64)):
    c = Paint(size[0], size[1], design=10, ss=3)
    m = c.M(col, contrast=1.15, gloss=0.9)
    if char == '!':
        c.poly([(2.4, 1), (7.6, 1), (6.3, 10), (3.7, 10)], m, shade=0.75, grad=0.6, gdir=(1, 0.3))
        c.ell(5, 13.1, 2.3, 2.3, m)
    else:
        c.chain([(2.3, 4.2), (3.2, 1.9), (5, 1.3), (6.8, 1.9), (7.6, 3.8), (6.4, 5.8), (5, 7.2), (5, 9.6)], 1.45, 1.35, m)
        c.ell(5, 13.1, 2.0, 2.0, m)
    return c.render(outline=(26, 14, 4, 255), rim_a=0, out_w=0.9)


def minimap_ring(size=200):
    img = ring(size, GOLD, thick=0.15, studs=8)
    return img


def catalogue():
    U = {}
    U['ui_stone'] = surface(256, 256, '#24232a', '#34323c', 1, 40, cracks=0.22)
    U['ui_stone_dark'] = surface(256, 256, '#121116', '#1e1c24', 2, 48, cracks=0.2)
    U['ui_parch'] = parchment(512, 512)
    w = surface(256, 128, '#3a2416', '#55361f', 4, 30, grain=0.25)
    wa = np.array(w).astype(float)
    yy = np.arange(128)
    grain = value_noise(256, 128, 4, 11, 3)
    stretched = np.repeat(value_noise(256, 16, 30, 12, 3), 8, axis=0)
    wa[..., :3] *= (0.85 + 0.25 * stretched[..., None])
    for y0 in (0, 63, 64, 127):
        wa[y0, :, :3] *= 0.4
    wa[..., :3] *= (0.95 + 0.1 * grain[..., None])
    del yy
    U['ui_wood'] = Image.fromarray(np.clip(wa, 0, 255).astype(np.uint8), 'RGBA')
    U['ui_frame_gold'] = frame9(144, 26, GOLD, '#b01818', True, 5)
    U['ui_frame_iron'] = frame9(64, 12, SILVER, medal=False, seed=6)
    U['ui_frame_item'] = frame9(48, 6, IRON, medal=False, seed=7)
    U['ui_btn'] = button(128, 64, '#9a1810')
    U['ui_btn_down'] = button(128, 64, '#6a100a', pressed=True)
    U['ui_btn_off'] = button(128, 64, '#4a4646', rim_ramp=IRON)
    U['ui_btn_gold'] = button(128, 64, '#b07a14')
    U['ui_btn_blue'] = button(128, 64, '#1e3c7a', rim_ramp=SILVER)
    U['ui_btn_green'] = button(128, 64, '#1e6a24')
    for n, col in [('green', '#24b02c'), ('red', '#c81e1e'), ('blue', '#1f50d8'), ('orange', '#e07818'), ('purple', '#8a3ac8'),
                   ('rested', '#3a7ad8'), ('yellow', '#e0b820'), ('grey', '#4a4a50'), ('teal', '#18a0a0')]:
        U['bar_' + n] = bar(col)
    U['bar_bg'] = bar('#141216')
    U['q_bang'] = marker('!', '#ffd200')
    U['q_turnin'] = marker('?', '#ffd200')
    U['q_daily'] = marker('!', '#40a0ff')
    U['q_grey'] = marker('!', '#8a8a8a')
    U['ui_ring'] = ring(112, GOLD, 0.2)
    U['ui_ring_elite'] = ring(112, GOLD, 0.22, studs=6)
    U['ui_ring_silver'] = ring(112, SILVER, 0.2)
    U['ui_wings'] = wings(200)
    U['ui_minimap'] = minimap_ring(220)
    return U

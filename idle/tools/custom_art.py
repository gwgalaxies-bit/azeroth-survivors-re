"""Painted art supplied as images in idle/art/: backdrops are cropped to the scene's 3:2, characters are cut out
of their (fake-checkerboard or flat) backgrounds, trimmed, mirrored to face the right way and scaled to the
scene's sizes. Anything without a file keeps its procedural art."""
import colorsys
import re
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(os.path.dirname(HERE), 'art')

# horizontal crop anchor (0 = keep left edge, 1 = keep right edge)
BACKDROPS = dict(bg_goldhain=0.4, bg_nebelmoor=0.5, bg_rotfels=0.5, bg_sonnenglut=0.42, bg_frostgipfel=0.5,
                 bg_schattenhain=0.5, bg_glutschlund=0.72, bg_leerenriss=0.5, bg_town=0.5, bg_arena=0.5)

# name: (file, logical box w x h, face the right?, source x-range to keep, face focus (fx, fy, zoom))
CHARACTERS = {
    'hero_krieger': ('hero_krieger', (160, 77), True, None, (0.57, 0.09, 3.2)),
    'hero_magier': ('hero_magier', (160, 71), True, None, (0.67, 0.11, 3.2)),
    'hero_jaeger': ('hero_jaeger', (160, 72), True, None, (0.42, 0.08, 3.2)),
    'hero_priester': ('hero_priester', (160, 71), True, None, (0.49, 0.065, 3.2)),
    'ignaroth': ('ignaroth', (138, 94), False, None, (0.18, 0.2, 1.6)),
    'kragg': ('kragg', (112, 82), False, None, (0.32, 0.25, 2.0)),
    'morva': ('morva', (66, 82), False, (0.0, 0.48), (0.6, 0.2, 2.4)),
    'gromm': ('gromm', (96, 90), False, None, (0.45, 0.15, 2.2)),
    'khet': ('khet', (110, 84), False, None, (0.45, 0.15, 2.2)),
    'glaciara': ('glaciara', (138, 92), False, None, (0.2, 0.2, 1.6)),
    'mordrek': ('mordrek', (114, 88), False, None, (0.42, 0.22, 2.2)),
    'umbrax': ('umbrax', (138, 92), False, None, (0.2, 0.22, 1.6)),
}

HALO = {'hero_magier': 16, 'hero_priester': 22, 'ignaroth': 16, 'kragg': 22, 'morva': 40, 'khet': 22, 'glaciara': 16, 'mordrek': 40, 'umbrax': 16}

# companions and arena rivals are recoloured heroes: (source, hue range to move, target hue, scale)
RACE_HEIGHT = dict(mensch=1.0, zwerg=0.84, elf=1.03, ork=1.08, halbling=0.72, untot=1.0)  # keep in sync with RACES in js/data.js

DERIVED = {
    'comp_tank': ('hero_krieger', (0.94, 0.04), 0.62, 0.9, (0.78, 0.9, 1.22)),
    'comp_heiler': ('hero_priester', (0.09, 0.17), 0.30, 0.9, (0.92, 1.08, 0.9)),
    'comp_schuetze': ('hero_jaeger', (0.18, 0.45), 0.99, 0.9, (1.08, 0.92, 0.9)),
    'comp_zauberin': ('hero_magier', (0.68, 0.86), 0.99, 0.9, (1.1, 0.9, 0.9)),
}


def _src(name):
    for ext in ('.jpg', '.jpeg', '.png'):
        p = os.path.join(ART, name + ext)
        if os.path.exists(p):
            return p
    return None


def backdrop(name, anchor=0.5, size=(960, 640)):
    im = Image.open(_src(name)).convert('RGB')
    w, h = im.size
    tw = int(round(h * size[0] / size[1]))
    if tw <= w:
        x0 = int((w - tw) * anchor)
        im = im.crop((x0, 0, x0 + tw, h))
    else:
        th = int(round(w * size[1] / size[0]))
        y0 = h - th
        im = im.crop((0, y0, w, h))
    return im.resize(size, Image.LANCZOS)


def _grid(lum, bgm, lo, hi):
    """Cell size and phase of the painted checkerboard, measured along the top rows and left columns."""
    mid = (lo + hi) / 2

    def period(sig):
        b = sig > mid
        idx = np.nonzero(b[1:] != b[:-1])[0]
        if len(idx) < 4:
            return None, 0
        d = np.diff(idx)
        c = int(np.median(d))
        return max(4, c), int(idx[0] + 1) % max(4, c)
    cx, px_ = period(np.median(lum[1:5, :], axis=0))
    cy, py_ = period(np.median(lum[:, 1:5], axis=1))
    if not cx or not cy:
        return None
    c = int(round((cx + cy) / 2))
    return c, px_, py_


def _checker_map(a, lo, hi):
    lum = a.mean(axis=2)
    g = _grid(lum, None, lo, hi)
    if not g:
        return None
    c, px_, py_ = g
    h, w = lum.shape
    Y, X = np.mgrid[0:h, 0:w]
    par = ((np.floor((X - px_) / c) + np.floor((Y - py_) / c)) % 2).astype(bool)
    # which parity holds the bright tone: vote over the top-left corner block
    blk = par[2:40, 2:40]
    bright = lum[2:40, 2:40] > (lo + hi) / 2
    bright_is_par = (bright == blk).mean() > 0.5
    tone = np.where(par == bright_is_par, hi, lo)
    return np.repeat(tone[..., None], 3, axis=2).astype(float)


def _cell(lum, lo, hi):
    """Checker cell size in pixels, from the transitions along the top and left border."""
    mid = (lo + hi) / 2
    sizes = []
    for sig in (np.median(lum[1:5, :], axis=0), np.median(lum[:, 1:5], axis=1), np.median(lum[-5:-1, :], axis=0)):
        b = sig > mid
        idx = np.nonzero(b[1:] != b[:-1])[0]
        if len(idx) >= 4:
            sizes.append(float(np.median(np.diff(idx))))
    return int(round(np.median(sizes))) if sizes else 16


def _box_mean(x, r):
    p = np.pad(x, r + 1, mode='edge')
    c = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    s = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    return s[:x.shape[0], :x.shape[1]] / (k * k)


def _checker_like(lum, lo, hi, cell, strict=True):
    """Where the image looks like the checkerboard, also when a painted shadow or glow darkens or tints it:
    the pattern repeats every two cells but flips every cell, and each small window holds two flat tones."""
    c = max(3, int(cell))
    d1 = (np.abs(lum - np.roll(lum, c, 1)) + np.abs(lum - np.roll(lum, c, 0))) / 2
    d2 = (np.abs(lum - np.roll(lum, 2 * c, 1)) + np.abs(lum - np.roll(lum, 2 * c, 0))) / 2
    b1, b2 = _box_mean(d1, c), _box_mean(d2, c)
    periodic = ((b1 - b2) / (b1 + 3) > 0.5) & (b1 > max(3.0, (hi - lo) * 0.12))
    if not strict:
        return periodic
    w = max(5, int(cell * 1.5) | 1)
    L = Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8), 'L')
    mn = np.array(L.filter(ImageFilter.MinFilter(w))).astype(float)
    mx = np.array(L.filter(ImageFilter.MaxFilter(w))).astype(float)
    rng = mx - mn
    t = (lum - mn) / np.maximum(rng, 1)
    mid = ((t > 0.3) & (t < 0.7)).astype(float)
    flat_tones = _box_mean(mid, w // 2) < 0.34
    ok = periodic & flat_tones
    if lo > 20:
        r0 = (hi + 4) / (lo + 4)
        ratio = (mx + 4) / (mn + 4)
        ok &= (ratio > 1 + (r0 - 1) * 0.35) & (ratio < 1 + (r0 - 1) * 3.5)
    return ok


def _drop_specks(fg, frac=0.0005):
    """Remove small detached bits (leftover checker dots, stray particles)."""
    h, w = fg.shape
    f = 4
    small = Image.fromarray((fg * 255).astype(np.uint8), 'L').reduce(f) if hasattr(Image.Image, 'reduce') else None
    sm = np.array(Image.fromarray((fg * 255).astype(np.uint8), 'L').filter(ImageFilter.MaxFilter(3)).resize((w // f, h // f), Image.NEAREST))
    m = Image.fromarray(np.where(sm > 0, 255, 0).astype(np.uint8), 'L')
    thr = max(6, frac * h * w / (f * f))
    arr = np.array(m)
    sizes = []
    ys, xs = np.nonzero(arr == 255)
    for y, x in zip(ys, xs):
        if m.getpixel((int(x), int(y))) != 255:
            continue
        ImageDraw.floodfill(m, (int(x), int(y)), 100)
        a2 = np.array(m)
        n = int((a2 == 100).sum())
        sizes.append(n)
        ImageDraw.floodfill(m, (int(x), int(y)), 50 if n >= thr else 10)
    del small
    keep = np.array(m) == 50
    if not keep.any():
        return fg
    big = np.array(Image.fromarray((keep * 255).astype(np.uint8), 'L').resize((w, h), Image.NEAREST)) > 0
    big = np.array(Image.fromarray((big * 255).astype(np.uint8), 'L').filter(ImageFilter.MaxFilter(5))) > 0
    return fg & big


def _background_mask(a):
    """(background mask, backdrop colour per pixel) of the backdrop the character was painted on."""
    h, w = a.shape[:2]
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    border = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    bsat = border.max(axis=1) - border.min(axis=1)
    flat = np.percentile(bsat, 90) > 12
    if flat:
        ref = np.median(border, axis=0)
        cand = np.sqrt(((a - ref) ** 2).sum(axis=2)) < 34
        tmap = np.broadcast_to(ref, a.shape).astype(float).copy()
        lo = hi = tol = None
    else:
        bl = border.mean(axis=1)
        lo, hi = np.percentile(bl, 15), np.percentile(bl, 85)
        tol = max(10, (hi - lo) * 0.28)
        cell = _cell(lum, lo, hi)
        chk = _checker_like(lum, lo, hi, cell)
        cand = (sat <= 9) & ((np.abs(lum - lo) < tol) | (np.abs(lum - hi) < tol) | ((lum > lo) & (lum < hi)))
        # shadows painted onto the checkerboard: darker, but still the same two-tone pattern
        cand |= (sat <= 16) & _checker_like(lum, lo, hi, cell, strict=False)
        tmap = (lo, hi, cell)
    m = Image.fromarray((cand * 255).astype(np.uint8), 'L').copy()
    seeds = [(x, 0) for x in range(0, w, 3)] + [(x, h - 1) for x in range(0, w, 3)] + [(0, y) for y in range(0, h, 3)] + [(w - 1, y) for y in range(0, h, 3)]
    for sd in seeds:
        if m.getpixel(sd) == 255:
            ImageDraw.floodfill(m, sd, 128)
    # enclosed pockets of backdrop (between legs, under wings): judge each remaining candidate region
    if not flat:
        nearlo = np.abs(lum - lo) < tol
        nearhi = np.abs(lum - hi) < tol
    arr = np.array(m)
    ys, xs = np.nonzero(arr[::4, ::4] == 255)
    for y4, x4 in zip(ys, xs):
        sd = (int(x4 * 4), int(y4 * 4))
        if m.getpixel(sd) != 255:
            continue
        ImageDraw.floodfill(m, sd, 100)
        arr = np.array(m)
        comp = arr == 100
        n = comp.sum()
        ok = False
        if n >= 40:
            if flat:
                ok = True
            else:
                fl, fh = nearlo[comp].mean(), nearhi[comp].mean()
                ok = (fl > 0.18 and fh > 0.18) or chk[comp].mean() > 0.6
        ImageDraw.floodfill(m, sd, 128 if ok else 60)
    bg = np.array(m) == 128
    bgi = Image.fromarray((bg * 255).astype(np.uint8), 'L').filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    return np.array(bgi) > 127, tmap


def _colour_to_alpha(p, t):
    """Smallest alpha such that p = alpha * g + (1 - alpha) * t with g inside the colour cube; returns (alpha, g)."""
    up = np.where(p > t, (p - t) / np.maximum(255 - t, 1), 0)
    dn = np.where(p < t, (t - p) / np.maximum(t, 1), 0)
    al = np.clip(np.maximum(up, dn).max(axis=2), 0, 1)
    g = (p - (1 - al[..., None]) * t) / np.maximum(al[..., None], 1e-3)
    return al, np.clip(g, 0, 255)


def cutout(name, keep=None, halo=False, halo_r=16, restrict=True):
    im = Image.open(_src(name)).convert('RGB')
    if keep:
        w = im.width
        im = im.crop((int(w * keep[0]), 0, int(w * keep[1]), im.height))
    a = np.asarray(im).astype(float)
    bg, tmap = _background_mask(a)
    fg = _drop_specks(~bg)
    fgi = Image.fromarray((fg * 255).astype(np.uint8), 'L').filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    alpha = fgi.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.1))
    al = np.array(alpha).astype(float) / 255
    rgb = a * (0.55 + 0.45 * np.clip((al - 0.2) / 0.6, 0, 1))[..., None]
    if halo:
        # glows painted over the backdrop: turn them into soft alpha so the backdrop does not show through
        near = np.array(Image.fromarray((bg * 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(halo_r))).astype(float) / 255
        band = (near > 0.02) & fg
        if not isinstance(tmap, tuple):
            ca, g = _colour_to_alpha(a, tmap)
            soft = band & (ca < 0.98)
            al = np.where(soft, np.minimum(al, np.clip(ca * 1.1, 0, 1)), al)
            rgb = np.where(soft[..., None], g, rgb)
        else:
            lo, hi, cell = tmap
            lum = a.mean(axis=2)
            chroma = a.max(axis=2) - a.min(axis=2)
            # only where the checkerboard still shows through: a glow, not a dull grey body part
            seen = np.array(Image.fromarray((_checker_like(lum, lo, hi, cell, strict=False) * 255).astype(np.uint8), 'L').filter(ImageFilter.MaxFilter(5))) > 0
            inband = band & (lum > lo - 18) & (seen if restrict else True)
            c0 = max(45.0, float(np.percentile(chroma[inband], 85))) if inband.any() else 60.0
            ca = np.clip((chroma - 8) / (c0 - 8), 0, 1)
            soft = inband & (ca < 0.995)
            # which checker cell is under each pixel: brighter or darker than its neighbourhood
            lm = np.array(Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(9))).astype(float)
            t = np.where(lum >= lm, hi, lo)[..., None]
            g = np.clip((a - (1 - ca[..., None]) * t) / np.maximum(ca[..., None], 0.05), 0, 255)
            # flatten what is left of the cell pattern inside the glow
            gl = g.mean(axis=2, keepdims=True)
            gb = np.dstack([np.array(Image.fromarray(np.clip(g[..., i], 0, 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(7))) for i in range(3)]).astype(float)
            g = np.where((ca < 0.995)[..., None], gb * 0.75 + g * 0.25, g)
            del gl
            al = np.where(soft, np.minimum(al, ca), al)
            rgb = np.where(soft[..., None], g, rgb)
    out = np.dstack([np.clip(rgb, 0, 255), al * 255]).astype(np.uint8)
    img = Image.fromarray(out, 'RGBA')
    bbox = Image.fromarray((al > 0.08).astype(np.uint8) * 255, 'L').getbbox()
    return img.crop(bbox)


def fit(img, box, sc, face_right, src_faces_right=None):
    bw, bh = box
    s = min(bw * sc / img.width, bh * sc / img.height)
    out = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)
    if src_faces_right is not None and src_faces_right != face_right:
        out = out.transpose(Image.FLIP_LEFT_RIGHT)
    return out


def recolour(img, hue_range, target, darken=1.0):
    a = np.asarray(img).astype(float) / 255
    rgb = a[..., :3]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    d = mx - mn + 1e-6
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    hh = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    lo, hi = hue_range
    inr = ((hh >= lo) & (hh <= hi)) if lo < hi else ((hh >= lo) | (hh <= hi))
    sel = inr & (s > 0.22) & (v > 0.12)
    nh = np.where(sel, target, hh)
    # back to rgb
    i = np.floor(nh * 6).astype(int) % 6
    f = nh * 6 - np.floor(nh * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    choices = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    nr = np.select([i == k for k in range(6)], [c[0] for c in choices])
    ng = np.select([i == k for k in range(6)], [c[1] for c in choices])
    nb = np.select([i == k for k in range(6)], [c[2] for c in choices])
    new = np.dstack([nr, ng, nb]) * darken
    out = np.where(sel[..., None], new, rgb * darken)
    return Image.fromarray((np.dstack([np.clip(out, 0, 1), a[..., 3]]) * 255).astype(np.uint8), 'RGBA')


# which way each source image faces (heroes must face right, monsters left)
SOURCE_FACES_RIGHT = dict(hero_krieger=True, hero_magier=True, hero_jaeger=True, hero_priester=True, ignaroth=False,
                          kragg=True, morva=True, gromm=False, khet=False, glaciara=False, mordrek=False, umbrax=False)


def _art_names():
    return sorted({os.path.splitext(f)[0] for f in os.listdir(ART) if f.lower().endswith(('.jpg', '.jpeg', '.png'))})


CACHE = os.path.join(os.path.dirname(HERE), '.art-cache')


def _job(args):
    name, keep, halo, halo_r, restrict = args
    import hashlib
    src = _src(name)
    import inspect
    parts = [_cell, _box_mean, _checker_like, _drop_specks, _background_mask, _colour_to_alpha, cutout]
    code = hashlib.sha1(''.join(inspect.getsource(f) for f in parts).encode()).hexdigest()[:10]
    st = os.stat(src)
    key = hashlib.sha1(repr((name, keep, halo, halo_r, restrict, st.st_size, int(st.st_mtime), code)).encode()).hexdigest()[:16]
    path = os.path.join(CACHE, f'{name}-{key}.png')
    if os.path.exists(path):
        return name, path
    img = cutout(name, keep, halo=halo, halo_r=halo_r, restrict=restrict)
    os.makedirs(CACHE, exist_ok=True)
    img.save(path)
    return name, path


def _cutouts(jobs):
    """Cut out many images in parallel; results are cached by file, settings and this module's code."""
    from multiprocessing import Pool
    with Pool(min(4, os.cpu_count() or 1)) as pool:
        done = dict(pool.map(_job, jobs))
    return {n: _trim(Image.open(p).convert('RGBA')) for n, p in done.items()}


def _trim(img, thr=0.45, pad=4):
    """Crop to the solid part of a cut-out: faint leftovers at the edges no longer widen the sprite."""
    a = np.asarray(img)[..., 3]
    ys, xs = np.nonzero(a > thr * 255)
    if not len(xs):
        return img
    return img.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(img.width, xs.max() + pad + 1), min(img.height, ys.max() + pad + 1)))


def catalogue(sc, known=None):
    """Returns (sprites, backdrops, faces). Sprites are RGBA at `sc` pixels per logical pixel.
    `known` maps procedural sprite names to their (w, h) in pixels; any image in art/ named like one replaces it."""
    S, B, faces = {}, {}, {}
    known = known or {}
    for name, anchor in BACKDROPS.items():
        if _src(name):
            B[name] = backdrop(name, anchor)
    for name in _art_names():
        if name.startswith('bg_') and name not in B:
            B[name] = backdrop(name, 0.5)
    taken = set(CHARACTERS) | {v[0] for v in CHARACTERS.values()}
    race_heroes = [n for n in _art_names() if re.fullmatch(r'hero_(krieger|magier|jaeger|priester)_[a-z]+', n)]
    taken |= set(race_heroes)
    for n in _art_names():
        if n.startswith('npc_'):
            known[n] = (0, int(48 * sc))  # quest givers stand about as tall as the hero
    generic = [n for n in _art_names() if not n.startswith('bg_') and n not in taken and n in known]
    jobs = [(src, keep, name in HALO, HALO.get(name, 16), False) for name, (src, box, right, keep, face) in CHARACTERS.items() if _src(src)]
    jobs += [(n, None, True, 14, True) for n in generic]
    jobs += [(n, None, True, 18, False) for n in race_heroes]
    cuts = _cutouts(jobs)
    for name, (src, box, right, keep, face) in CHARACTERS.items():
        if src not in cuts:
            continue
        img = cuts[src]
        S[name] = fit(img, box, sc, right, SOURCE_FACES_RIGHT.get(src))
        fx, fy, z = face
        if SOURCE_FACES_RIGHT.get(src) != right:
            fx = 1 - fx
        faces[name] = [round(fx, 3), round(fy, 3), z]
    for name in race_heroes:
        # a hero of another people: as tall as the class's hero times the people's height, facing right
        cls, race = name.split('_')[1:]
        box = CHARACTERS['hero_' + cls][1]
        S[name] = fit(cuts[name], (box[0], box[1] * RACE_HEIGHT.get(race, 1.0)), sc, True, True)
    for name in generic:
        # a painted replacement for a procedural sprite: a bit taller than the drawn one, facing as prompted
        w, h = known[name]
        lh = min(100, h / sc * 1.45)
        S[name] = fit(cuts[name], (lh * 1.9, lh), sc, True, True)
        faces[name] = [0.5, 0.22, 2.0]
    for name, (src, hr, target, scale, tint) in DERIVED.items():
        if src in S and name not in S:
            base = S[src]
            img = recolour(base, hr, target)
            t = np.asarray(img).astype(float) * [tint[0], tint[1], tint[2], 1]
            img = Image.fromarray(np.clip(t, 0, 255).astype(np.uint8), 'RGBA')
            S[name] = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
            faces[name] = faces[src]
    for cls in ('krieger', 'magier', 'jaeger', 'priester'):
        src = 'hero_' + cls
        if src in S:
            flipped = np.asarray(S[src].transpose(Image.FLIP_LEFT_RIGHT)).astype(float)
            S['rival_' + cls] = Image.fromarray((flipped * [0.82, 0.78, 0.86, 1]).astype(np.uint8), 'RGBA')
            f = faces[src]
            faces['rival_' + cls] = [round(1 - f[0], 3), f[1], f[2]]
    return S, B, faces


# ------------------------------------------------------------------------------------------------ icons
ICON_FILES = {
    'potion_heal': 'potion_heal', 'swords': 'swords', 'key': 'key', 'chest': 'chest',
}
WEAPON_FILES = {'krieger': ('w_krieger', 'w_krieger_hi'), 'magier': ('w_magier',), 'jaeger': ('w_jaeger',), 'priester': ('w_priester',)}
ARMOR_SLOTS = ('head', 'shoulder', 'chest', 'hands', 'legs', 'feet', 'trinket')


def _icon_src(name):
    for ext in ('.jpg', '.jpeg', '.png'):
        p = os.path.join(ART, 'icons', name + ext)
        if os.path.exists(p):
            return p
    return None


def load_icon(name, cell):
    im = Image.open(_icon_src(name)).convert('RGB')
    w, h = im.size
    m = int(round(w * 0.045))
    im = im.crop((m, m, w - m, h - m)).resize((cell, cell), Image.LANCZOS)
    return im.convert('RGBA')


def _hsv_shift(a, lo, hi, target, min_sat=0.15):
    mx, mn = a.max(axis=2), a.min(axis=2)
    d = mx - mn + 1e-6
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    hh = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    sel = (hh >= lo) & (hh <= hi) & (s > min_sat)
    v = mx
    nh = np.where(sel, target, hh)
    i = np.floor(nh * 6).astype(int) % 6
    f = nh * 6 - np.floor(nh * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    ch = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    out = np.dstack([np.select([i == k for k in range(6)], [c[j] for c in ch]) for j in range(3)])
    return np.where(sel[..., None], out, a)


def tier_variant(img, t):
    """Tier 0 worn bronze, 1 plain iron, 2 as painted, 3 gilded, 4 void-touched violet, 5 legendary ember."""
    a = np.asarray(img.convert('RGB')).astype(float) / 255
    lum = a.mean(axis=2, keepdims=True)
    if t == 0:
        a = (a * 0.35 + lum * np.array([1.12, 0.86, 0.6]) * 0.65) * 0.86
    elif t == 1:
        a = a * 0.55 + lum * np.array([0.96, 0.99, 1.04]) * 0.45
    elif t == 3:
        a = _hsv_shift(a, 0.5, 0.72, 0.11, 0.08)
        a = a * np.array([1.06, 1.0, 0.86])
    elif t == 4:
        a = _hsv_shift(a, 0.45, 0.75, 0.78, 0.06)
        a = a * 0.75 + lum * np.array([0.85, 0.62, 1.2]) * 0.25
    elif t == 5:
        a = _hsv_shift(a, 0.45, 0.75, 0.06, 0.06)
        a = a * 0.7 + lum * np.array([1.3, 0.75, 0.35]) * 0.3
        n = a.shape[0]
        y, x = np.mgrid[0:n, 0:n] / n - 0.5
        rim = np.clip(np.sqrt(x ** 2 + y ** 2) * 2 - 0.55, 0, 1)
        a = a + np.array([1.0, 0.45, 0.05]) * (rim ** 1.5)[..., None] * 0.5
    out = np.clip(a, 0, 1) * 255
    return Image.fromarray(np.dstack([out, np.full(out.shape[:2], 255)]).astype(np.uint8), 'RGBA')


def icons(cell):
    I = {}
    for cls, files in WEAPON_FILES.items():
        have = [f for f in files if _icon_src(f)]
        if not have:
            continue
        for t in range(6):
            src = have[-1] if t >= 3 and len(have) > 1 else have[0]
            I[f'w_{cls}_{t}'] = tier_variant(load_icon(src, cell), t)
    for slot in ARMOR_SLOTS:
        if _icon_src('a_' + slot):
            base = load_icon('a_' + slot, cell)
            for t in range(6):
                I[f'a_{slot}_{t}'] = tier_variant(base, t)
    for name, f in ICON_FILES.items():
        if _icon_src(f):
            I[name] = load_icon(f, cell)
    if 'chest' in I:
        I['chest_epic'] = tier_variant(I['chest'], 4)
        I['chest_gold'] = tier_variant(I['chest'], 3)
    if 'swords' in I:
        I['honor'] = tier_variant(I['swords'], 0)
    # any other icon in art/icons/ named like a game icon (skills, currencies, ores, ...) is used as is
    d = os.path.join(ART, 'icons')
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        name, ext = os.path.splitext(f)
        if ext.lower() not in ('.jpg', '.jpeg', '.png') or name in ICON_FILES.values():
            continue
        if name.startswith(('w_', 'a_')):
            continue
        I[name] = load_icon(name, cell)
    return I

"""A tiny pixel-art painter.

Shapes are rasterised straight into a low-resolution grid. Every shape writes a
material (a 5-step colour ramp) and a light value per pixel; the light comes from
a pseudo surface normal (spheres for ellipses, cylinders for capsules), so the
result is shaded like hand-made pixel art: quantised ramps, ordered dithering,
darkened edges where a part overlaps another, and a dark outline around it all.
"""
import colorsys
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

LIGHT = np.array([-0.55, -0.72, 0.62])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
OUTLINE = (22, 14, 20, 255)


def rgb(h):
    if isinstance(h, tuple):
        return h[:3]
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def shade_col(c, f):
    c = rgb(c)
    return tuple(max(0, min(255, int(v * f))) for v in c)


def _hue_toward(h, target, amt):
    d = ((target - h + 0.5) % 1.0) - 0.5
    return (h + d * amt) % 1.0


def make_ramp(base, n=5, contrast=1.0, hue=0.10):
    """Hue-shifted ramp, darkest first. `base` is roughly the 4th of 5 tones."""
    r, g, b = [c / 255 for c in rgb(base)]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    vf = [0.34, 0.58, 0.80, 1.0, 1.22]
    sf = [1.12, 1.08, 1.02, 1.0, 0.78]
    if n != 5:
        vf = list(np.interp(np.linspace(0, 4, n), range(5), vf))
        sf = list(np.interp(np.linspace(0, 4, n), range(5), sf))
    out = []
    for i in range(n):
        t = i / (n - 1)
        vv = v * (1 + (vf[i] - 1) * contrast)
        ss = min(1, s * sf[i])
        if t < 0.6:
            hh = _hue_toward(h, 0.70, hue * (0.6 - t) * 1.6)
        else:
            hh = _hue_toward(h, 0.13, hue * (t - 0.6) * 2.0)
        if vv > 1:
            ss = max(0, ss - (vv - 1) * 0.9)
            vv = 1
        rr, gg, bb = colorsys.hsv_to_rgb(hh, max(0, ss), max(0, min(1, vv)))
        out.append((int(rr * 255), int(gg * 255), int(bb * 255)))
    return out


def lit(nx, ny, nz, amb=0.20):
    d = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
    return np.clip(d, 0, 1) * 0.86 + amb


class Canvas:
    def __init__(self, w, h=None, design=None, seed=1):
        h = h or w
        self.w, self.h = w, h
        self.k = w / (design or w)
        self.mat = np.full((h, w), -1, np.int32)
        self.sh = np.zeros((h, w))
        self.ordr = np.full((h, w), -1, np.int32)
        self.dith = np.zeros((h, w))
        self.alpha = np.full((h, w), 255, np.int32)
        self.mats = []
        self.edge = []
        self.prim = 0
        Y, X = np.mgrid[0:h, 0:w]
        self.X = X + 0.5
        self.Y = Y + 0.5
        self.ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        self.ovd = ImageDraw.Draw(self.ov)
        self.rng = np.random.default_rng(seed)

    # ----- materials -------------------------------------------------------------------
    def M(self, color, n=5, contrast=1.0, hue=0.10, ramp=None):
        self.mats.append(ramp or make_ramp(color, n, contrast, hue))
        return len(self.mats) - 1

    # ----- core ---------------------------------------------------------------------------
    def _put(self, mask, m, sh, tex=0.0, dith=0.4, edge=True, alpha=255):
        if not mask.any():
            return
        if np.isscalar(sh):
            sh = np.full((self.h, self.w), float(sh))
        if tex:
            sh = sh + (self.rng.random((self.h, self.w)) - 0.5) * tex
        self.mat[mask] = m
        self.sh[mask] = np.clip(sh[mask], 0, 1)
        self.ordr[mask] = self.prim
        self.dith[mask] = dith
        self.alpha[mask] = alpha
        self.edge.append(edge)
        self.prim += 1

    def ell(self, cx, cy, rx, ry, m, rot=0.0, tex=0.0, dith=0.4, edge=True, flat=None,
            amb=0.20, alpha=255, clip=None):
        k = self.k
        cx, cy, rx, ry = cx * k, cy * k, max(0.5, rx * k), max(0.5, ry * k)
        dx, dy = self.X - cx, self.Y - cy
        c, s = math.cos(rot), math.sin(rot)
        u = (dx * c + dy * s) / rx
        v = (-dx * s + dy * c) / ry
        d = u * u + v * v
        mask = d <= 1.0
        if clip is not None:
            mask &= clip(self.X / k, self.Y / k)
        z = np.sqrt(np.clip(1 - d, 0, 1))
        nx, ny = u * c - v * s, u * s + v * c
        sh = lit(nx, ny, z, amb) if flat is None else flat
        self._put(mask, m, sh, tex, dith, edge, alpha)

    def cap(self, x1, y1, x2, y2, r1, r2=None, m=0, tex=0.0, dith=0.4, edge=True, flat=None,
            amb=0.20, alpha=255):
        k = self.k
        r2 = r1 if r2 is None else r2
        x1, y1, x2, y2, r1, r2 = x1 * k, y1 * k, x2 * k, y2 * k, max(0.5, r1 * k), max(0.5, r2 * k)
        vx, vy = x2 - x1, y2 - y1
        L2 = vx * vx + vy * vy or 1e-6
        t = np.clip(((self.X - x1) * vx + (self.Y - y1) * vy) / L2, 0, 1)
        px, py = x1 + t * vx, y1 + t * vy
        r = r1 + (r2 - r1) * t
        dx, dy = self.X - px, self.Y - py
        dist = np.sqrt(dx * dx + dy * dy)
        mask = dist <= r
        nx, ny = dx / r, dy / r
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        sh = lit(nx, ny, nz, amb) if flat is None else flat
        self._put(mask, m, sh, tex, dith, edge, alpha)

    def chain(self, pts, r1, r2, m, **kw):
        """Tapered capsule chain through points."""
        n = len(pts) - 1
        for i in range(n):
            a = r1 + (r2 - r1) * i / n
            b = r1 + (r2 - r1) * (i + 1) / n
            self.cap(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], a, b, m, **kw)

    def poly(self, pts, m, shade=0.62, grad=0.28, tex=0.0, dith=0.4, edge=True, alpha=255,
             gdir=(0, 1)):
        k = self.k
        img = Image.new('L', (self.w, self.h), 0)
        ImageDraw.Draw(img).polygon([(x * k, y * k) for x, y in pts], fill=255)
        mask = np.array(img) > 127
        xs = [p[0] * k for p in pts]
        ys = [p[1] * k for p in pts]
        gx, gy = gdir
        proj = (self.X - min(xs)) * gx + (self.Y - min(ys)) * gy
        span = max(1.0, abs(gx) * (max(xs) - min(xs)) + abs(gy) * (max(ys) - min(ys)))
        sh = shade + grad * (0.5 - proj / span)
        self._put(mask, m, sh, tex, dith, edge, alpha)

    def rect(self, x, y, w, h, m, **kw):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], m, **kw)

    # ----- overlay (direct pixels, always on top) ----------------------------------------------
    def px(self, x, y, col, a=255):
        k = self.k
        xx, yy = int(x * k), int(y * k)
        if 0 <= xx < self.w and 0 <= yy < self.h:
            self.ov.putpixel((xx, yy), rgb(col) + (a,))

    def pxs(self, pts, col, a=255):
        for x, y in pts:
            self.px(x, y, col, a)

    def line(self, x1, y1, x2, y2, col, w=1, a=255):
        k = self.k
        self.ovd.line([(x1 * k, y1 * k), (x2 * k, y2 * k)], fill=rgb(col) + (a,), width=max(1, int(w * k)))

    def dot(self, x, y, r, col, a=255):
        k = self.k
        self.ovd.ellipse([(x - r) * k, (y - r) * k, (x + r) * k - 1, (y + r) * k - 1], fill=rgb(col) + (a,))

    # ----- render ---------------------------------------------------------------------------
    def render(self, outline=OUTLINE, glow=None, glow_r=3, glow_a=0.55, inner=True):
        h, w = self.h, self.w
        out = np.zeros((h, w, 4), np.uint8)
        filled = self.mat >= 0
        bay = BAYER4[np.arange(h)[:, None] % 4, np.arange(w)[None, :] % 4]
        behind = np.zeros((h, w), bool)
        if inner and self.prim:
            edge_arr = np.array(self.edge + [False], bool)
            o = self.ordr
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nb = np.full((h, w), -1, np.int32)
                ys = slice(max(0, dy), h + min(0, dy))
                yd = slice(max(0, -dy), h + min(0, -dy))
                xs = slice(max(0, dx), w + min(0, dx))
                xd = slice(max(0, -dx), w + min(0, -dx))
                nb[yd, xd] = o[ys, xs]
                behind |= filled & (nb > o) & edge_arr[nb]
        for m, rmp in enumerate(self.mats):
            sel = self.mat == m
            if not sel.any():
                continue
            n = len(rmp)
            q = self.sh * (n - 1) + 0.5 + (bay - 0.5) * self.dith
            q = np.floor(q).astype(int)
            q = np.where(behind, q - 1, q)
            q = np.clip(q, 0, n - 1)
            pal = np.array(rmp, np.uint8)
            out[sel, :3] = pal[q[sel]]
            out[sel, 3] = self.alpha[sel]
        img = Image.fromarray(out, 'RGBA')
        img.alpha_composite(self.ov)
        a = np.array(img)[:, :, 3] > 0
        if outline is not None:
            dil = a.copy()
            dil[1:, :] |= a[:-1, :]
            dil[:-1, :] |= a[1:, :]
            dil[:, 1:] |= a[:, :-1]
            dil[:, :-1] |= a[:, 1:]
            ring = dil & ~a
            arr = np.array(img)
            arr[ring] = outline
            img = Image.fromarray(arr, 'RGBA')
        if glow is not None:
            al = Image.fromarray((np.array(img)[:, :, 3] > 0).astype(np.uint8) * 255, 'L')
            bl = np.array(al.filter(ImageFilter.GaussianBlur(glow_r))).astype(float) / 255
            steps = np.where(bl > 0.45, glow_a, np.where(bl > 0.18, glow_a * 0.55, np.where(bl > 0.05, glow_a * 0.25, 0)))
            g = np.zeros((h, w, 4), np.uint8)
            g[:, :, :3] = rgb(glow)
            g[:, :, 3] = (steps * 255).astype(np.uint8)
            base = Image.fromarray(g, 'RGBA')
            base.alpha_composite(img)
            img = base
        return img


def value_noise(w, h, scale, seed=0, octaves=4, wrap=True):
    """Tileable fractal value noise in 0..1."""
    rng = np.random.default_rng(seed)
    total = np.zeros((h, w))
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        gx = max(1, int(round(w / scale * (2 ** o))))
        gy = max(1, int(round(h / scale * (2 ** o))))
        grid = rng.random((gy + 1, gx + 1))
        if wrap:
            grid[-1, :] = grid[0, :]
            grid[:, -1] = grid[:, 0]
        ys = np.linspace(0, gy, h, endpoint=False)
        xs = np.linspace(0, gx, w, endpoint=False)
        y0 = np.floor(ys).astype(int)
        x0 = np.floor(xs).astype(int)
        fy = ys - y0
        fx = xs - x0
        fy = fy * fy * (3 - 2 * fy)
        fx = fx * fx * (3 - 2 * fx)
        a = grid[y0][:, x0]
        b = grid[y0][:, x0 + 1]
        c = grid[y0 + 1][:, x0]
        d = grid[y0 + 1][:, x0 + 1]
        top = a + (b - a) * fx[None, :]
        bot = c + (d - c) * fx[None, :]
        total += (top + (bot - top) * fy[:, None]) * amp
        norm += amp
        amp *= 0.5
    return total / norm


def noise1d(n, scale, seed=0, octaves=4):
    return value_noise(n, 1, scale, seed, octaves, wrap=False)[0]


def quantize_img(arr_rgb, levels=None):
    return arr_rgb

#!/usr/bin/env python3
"""Contact sheet of every round portrait, computed exactly like the game does. python3 tools/faces_sheet.py out.png"""
import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = 0.55  # share of the circle the head fills; keep in sync with face() in js/ui.js


def portrait(atlas, rect, face, box=96):
    x, y, w, h = rect
    fx, fy, fs = face
    s = K * box / (fs * h)
    sw, sh = w * s, h * s
    img = Image.new('RGBA', (box, box), (36, 32, 44, 255))
    spr = atlas.crop((x, y, x + w, y + h)).resize((max(1, round(sw)), max(1, round(sh))), Image.LANCZOS)
    img.paste(spr, (round(box / 2 - sw * fx), round(box / 2 - sh * fy)), spr)
    mask = Image.new('L', (box, box), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, box - 1, box - 1], fill=255)
    out = Image.new('RGBA', (box, box), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    d = ImageDraw.Draw(out)
    d.ellipse([0, 0, box - 1, box - 1], outline=(200, 160, 80, 255), width=2)
    d.line([(box / 2 - 4, box / 2), (box / 2 + 4, box / 2)], fill=(255, 0, 0, 180))
    d.line([(box / 2, box / 2 - 4), (box / 2, box / 2 + 4)], fill=(255, 0, 0, 180))
    return out


def main(out):
    s = open(os.path.join(ROOT, 'js', 'atlas.js')).read()
    d = json.loads(s[s.index('{'):s.rindex('}') + 1])
    M, F = d['sprites']['map'], d['sprites']['faces']
    atlas = Image.open(os.path.join(ROOT, 'assets', 'sprites.webp')).convert('RGBA')
    names = [n for n in sorted(F)]
    cols, box = 10, 96
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * (box + 8), rows * (box + 22)), (0, 0, 0, 255))
    dd = ImageDraw.Draw(sheet)
    for i, n in enumerate(names):
        x, y = (i % cols) * (box + 8), (i // cols) * (box + 22)
        sheet.alpha_composite(portrait(atlas, M[n], F[n], box), (x, y))
        dd.text((x, y + box + 4), n[:16], fill=(255, 255, 255, 255))
    sheet.save(out)
    print(len(names), 'portraits ->', out)


if __name__ == '__main__':
    main(sys.argv[1])

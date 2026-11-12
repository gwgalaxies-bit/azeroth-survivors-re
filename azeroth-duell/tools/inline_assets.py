#!/usr/bin/env python3
"""Bettet alle Bilder aus ../img als CSS-Variablen (data: URIs) in ../index.html ein.

Aufruf:  python3 tools/inline_assets.py
Die Variablen heißen --i-<dateiname> (Unterstrich -> Bindestrich), z. B. img/btn_red.webp -> --i-btn-red.
Der Block zwischen /*ASSETS-START*/ und /*ASSETS-END*/ wird jedes Mal komplett neu geschrieben.
"""
import base64, glob, os, re

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html_path = os.path.join(root, 'index.html')
vars_ = []
for f in sorted(glob.glob(os.path.join(root, 'img', '*.webp'))):
    name = os.path.splitext(os.path.basename(f))[0].replace('_', '-')
    b64 = base64.b64encode(open(f, 'rb').read()).decode()
    vars_.append(f'--i-{name}:url(data:image/webp;base64,{b64});')
block = '/*ASSETS-START*/\n:root{\n' + '\n'.join(vars_) + '\n}\n/*ASSETS-END*/'
s = open(html_path, encoding='utf8').read()
s, n = re.subn(r'/\*ASSETS-START\*/.*?/\*ASSETS-END\*/', lambda m: block, s, flags=re.S)
if n != 1:
    raise SystemExit('Marker /*ASSETS-START*/ ... /*ASSETS-END*/ nicht gefunden')
open(html_path, 'w', encoding='utf8').write(s)
print(f'{len(vars_)} Bilder eingebettet, index.html = {len(s)//1024} KB')

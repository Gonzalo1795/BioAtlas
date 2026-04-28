# -*- coding: utf-8 -*-
import re

with open("atlas/templates/atlas/index.html", encoding="utf-8") as f:
    content = f.read()

# 1. Eliminar todas las reglas CSS de hero-btn-icon que haya
content = re.sub(r'\.about-icon \.hero-btn-icon[^}]*}\n?', '', content)
content = re.sub(r'\.hero-btn-icon-sm[^}]*}\n?', '', content)
content = re.sub(r'\.hero-btn-icon-lg[^}]*}\n?', '', content)
content = re.sub(r'\.hero-btn-icon[^}]*}\n?', '', content)

# 2. Normalizar todas las clases de svg a hero-btn-icon
content = content.replace('class="hero-btn-icon-sm"', 'class="hero-btn-icon"')
content = content.replace('class="hero-btn-icon-lg"', 'class="hero-btn-icon"')

# 3. Añadir CSS limpio antes de @keyframes fadeUp
new_css = (
    '.hero-btn-icon { display:inline-block; vertical-align:middle; flex-shrink:0; color:var(--accent,#2d8a4e); width:24px; height:24px; }\n'
    '.about-icon .hero-btn-icon { display:block; width:80px; height:80px; }\n'
)
content = content.replace('@keyframes fadeUp', new_css + '@keyframes fadeUp', 1)

with open("atlas/templates/atlas/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("OK")
print("hero-btn-icon count:", content.count('hero-btn-icon'))

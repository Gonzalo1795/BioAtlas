# -*- coding: utf-8 -*-

with open("atlas/templates/atlas/index.html", encoding="utf-8") as f:
    content = f.read()

# Cambiar clase de los botones hero a "hero-btn-icon-sm"
content = content.replace(
    'class="hero-btn-icon" aria-hidden="true" version="1.0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024.000000 1024.000000"',
    'class="hero-btn-icon-sm" aria-hidden="true" version="1.0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024.000000 1024.000000"'
)
content = content.replace(
    'class="hero-btn-icon" aria-hidden="true" version="1.0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1254.000000 1254.000000"',
    'class="hero-btn-icon-sm" aria-hidden="true" version="1.0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1254.000000 1254.000000"'
)

# Los iconos de about-card tienen viewBox 1254 y 1024 pero son los mismos SVGs
# Necesitamos identificarlos por contexto - están dentro de about-icon span
# Reemplazar solo los que están dentro de about-icon
import re
def fix_about_icons(m):
    return m.group(0).replace('hero-btn-icon-sm', 'hero-btn-icon-lg')

content = re.sub(
    r'<span class="about-icon">.*?</span>',
    lambda m: m.group(0).replace('hero-btn-icon-sm', 'hero-btn-icon-lg'),
    content,
    flags=re.DOTALL
)

# Actualizar CSS
old_css = '.hero-btn-icon { color:var(--accent,#2d8a4e); width:22px; height:22px; display:inline-block; flex-shrink:0; }\n.about-icon .hero-btn-icon { color:var(--accent,#2d8a4e); }'
new_css = '.hero-btn-icon-sm { color:var(--accent,#2d8a4e); width:24px; height:24px; display:inline-block; flex-shrink:0; vertical-align:middle; }\n.hero-btn-icon-lg { color:var(--accent,#2d8a4e); width:80px; height:80px; display:block; }'

if old_css in content:
    content = content.replace(old_css, new_css)
    print("OK: CSS actualizado")
else:
    # Buscar cualquier combinacion de estas reglas y reemplazar
    content = re.sub(
        r'\.hero-btn-icon[^}]*}[\s\n]*\.about-icon[^}]*}',
        new_css,
        content
    )
    print("OK: CSS actualizado con regex")

with open("atlas/templates/atlas/index.html", "w", encoding="utf-8") as f:
    f.write(content)

# Verificar
with open("atlas/templates/atlas/index.html", encoding="utf-8") as f:
    c = f.read()
print("hero-btn-icon-sm count:", c.count('hero-btn-icon-sm'))
print("hero-btn-icon-lg count:", c.count('hero-btn-icon-lg'))

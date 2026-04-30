# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/base.html', encoding='utf-8') as f:
    c = f.read()

img = '<img src="/static/atlas/img/menu/{svg}" style="width:20px;height:20px;vertical-align:middle;margin-right:6px;object-fit:contain;">'

replacements = [
    ('\U0001f3e0 Inicio', img.format(svg='../logo.svg') + ' Inicio'),
    ('\U0001f50d Explorar', img.format(svg='../buscar_especie.svg') + ' Explorar'),
    ('\U0001f9ec Quiz Visu', img.format(svg='../quiz/Quiz.svg') + ' Quiz Visual'),
    ('\U0001f464 Mi perfil', img.format(svg='Perfil.svg') + ' Mi perfil'),
    ('\U0001f33f Mi Atlas', img.format(svg='Mi_atlas.svg') + ' Mi Atlas'),
    ('\u2764\ufe0f Mis favoritos', img.format(svg='favoritos.svg') + ' Mis favoritos'),
    ('\U0001f4cd Mis avistamientos', img.format(svg='avistamientos.svg') + ' Mis avistamientos'),
    ('\u2728 Hazte Premium', img.format(svg='../premium.svg') + ' Hazte Premium'),
    ('\U0001f6aa Cerrar sesi\u00f3n', img.format(svg='cerrar_sesion.svg') + ' Cerrar sesi\u00f3n'),
    ('\U0001f511 Iniciar sesi\u00f3n', img.format(svg='Perfil.svg') + ' Iniciar sesi\u00f3n'),
]

count = 0
for old, new in replacements:
    if old in c:
        c = c.replace(old, new)
        count += 1
        print(f"OK: {old[:30]}")
    else:
        print(f"NO: {old[:30]}")

with open('atlas/templates/atlas/base.html', 'w', encoding='utf-8') as f:
    f.write(c)
print(f"DONE: {count}")

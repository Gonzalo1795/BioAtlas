# -*- coding: utf-8 -*-

img = '<img src="{{% static \'atlas/img/menu/{file}\' %}}" style="width:18px;height:18px;display:inline-block;vertical-align:middle;margin-right:6px;object-fit:contain;">'

replacements = [
    ('👤 <span data-i18n="menu.perfil">',        img.format(file='Perfil.svg')        + ' <span data-i18n="menu.perfil">'),
    ('🌿 <span data-i18n="menu.atlas">',          img.format(file='Mi_atlas.svg')      + ' <span data-i18n="menu.atlas">'),
    ('❤️ <span data-i18n="menu.favoritos">',      img.format(file='favoritos.svg')     + ' <span data-i18n="menu.favoritos">'),
    ('📍 <span data-i18n="menu.avistamientos">',  img.format(file='avistamientos.svg') + ' <span data-i18n="menu.avistamientos">'),
    ('🚪 <span data-i18n="menu.logout">',         img.format(file='cerrar_sesion.svg') + ' <span data-i18n="menu.logout">'),
    ('👤 Mi perfil',        img.format(file='Perfil.svg')        + ' Mi perfil'),
    ('🌿 Mi Atlas',         img.format(file='Mi_atlas.svg')      + ' Mi Atlas'),
    ('❤️ Mis favoritos',    img.format(file='favoritos.svg')     + ' Mis favoritos'),
    ('📍 Mis avistamientos',img.format(file='avistamientos.svg') + ' Mis avistamientos'),
]

with open("atlas/templates/atlas/base.html", encoding="utf-8") as f:
    c = f.read()

count = 0
for old, new in replacements:
    if old in c:
        c = c.replace(old, new)
        count += 1
        print("OK:", old[:40])
    else:
        print("NO:", old[:40])

with open("atlas/templates/atlas/base.html", "w", encoding="utf-8") as f:
    f.write(c)
print(f"DONE: {count} reemplazos")

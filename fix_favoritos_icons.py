# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/mis_favoritos.html', encoding='utf-8') as f:
    c = f.read()

img_h1 = '<img src="/static/atlas/img/menu/favoritos.svg" style="width:160px;height:160px;vertical-align:middle;margin-right:8px;object-fit:contain;">'
img_empty = '<img src="/static/atlas/img/menu/favoritos.svg" style="width:160px;height:160px;object-fit:contain;">'

c = c.replace('\u2764\ufe0f <span data-i18n="favs.titulo">', img_h1 + '<span data-i18n="favs.titulo">')
c = c.replace('<div style="font-size:3rem; margin-bottom:1rem;">\u2764\ufe0f</div>', '<div style="margin-bottom:1rem;">' + img_empty + '</div>')

with open('atlas/templates/atlas/mis_favoritos.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("DONE")

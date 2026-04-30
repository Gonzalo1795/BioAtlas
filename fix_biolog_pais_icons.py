# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/biolog_pais.html', encoding='utf-8') as f:
    c = f.read()

fav_img = '<img src="/static/atlas/img/menu/favoritos.svg" style="width:34px;height:34px;vertical-align:middle;">'
atlas_img = '<img src="/static/atlas/img/menu/Mi_atlas.svg" style="width:34px;height:34px;vertical-align:middle;">'

c = c.replace(
    '{% if entrada.especie.species_key in especies_favoritas %}\u2764\ufe0f{% else %}\U0001f90d{% endif %}',
    fav_img
)
c = c.replace('>\U0001f33f</button>', '>' + atlas_img + '</button>')

with open('atlas/templates/atlas/biolog_pais.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("DONE")

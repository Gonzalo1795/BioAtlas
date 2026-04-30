# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/pais_detail.html', encoding='utf-8') as f:
    c = f.read()

fav_img = '<img src="/static/atlas/img/menu/favoritos.svg" style="width:34px;height:34px;vertical-align:middle;">'
atlas_img = '<img src="/static/atlas/img/menu/Mi_atlas.svg" style="width:34px;height:34px;vertical-align:middle;">'

old_fav = "function updateCardFav(sk,active){const btn=document.getElementById('qa-fav-'+sk);if(!btn)return;btn.textContent=active?'\u2764\ufe0f':'\U0001f90d';btn.classList.toggle('active-fav',active);}"
new_fav = "function updateCardFav(sk,active){const btn=document.getElementById('qa-fav-'+sk);if(!btn)return;btn.innerHTML='" + fav_img + "';btn.classList.toggle('active-fav',active);}"

old_atlas = "function updateCardAtlas(sk,active){const btn=document.getElementById('qa-atlas-'+sk),badge=document.getElementById('badge-'+sk);if(btn){btn.textContent=active?'\U0001f33f':'\U0001fab4';btn.classList.toggle('active-atlas',active);}if(badge){badge.textContent=active?'\u2713 Atlas':'';badge.classList.toggle('visible',active);}}"
new_atlas = "function updateCardAtlas(sk,active){const btn=document.getElementById('qa-atlas-'+sk),badge=document.getElementById('badge-'+sk);if(btn){btn.innerHTML='" + atlas_img + "';btn.classList.toggle('active-atlas',active);}if(badge){badge.textContent=active?'\u2713 Atlas':'';badge.classList.toggle('visible',active);}}"

if old_fav in c:
    c = c.replace(old_fav, new_fav)
    print("OK: updateCardFav")
else:
    print("NO: updateCardFav")

if old_atlas in c:
    c = c.replace(old_atlas, new_atlas)
    print("OK: updateCardAtlas")
else:
    print("NO: updateCardAtlas")

with open('atlas/templates/atlas/pais_detail.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("DONE")

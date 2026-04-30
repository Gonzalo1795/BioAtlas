# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/biolog_pais.html', encoding='utf-8') as f:
    c = f.read()

fav_img = '<img src="/static/atlas/img/menu/favoritos.svg" style="width:34px;height:34px;vertical-align:middle;">'

old = "function updateCardFav(sk,active){const btn=document.getElementById('qa-fav-'+sk);if(!btn)return;btn.textContent=active?'\u2764\ufe0f':'\U0001f90d';btn.classList.toggle('active-fav',active);}"
new = "function updateCardFav(sk,active){const btn=document.getElementById('qa-fav-'+sk);if(!btn)return;btn.innerHTML='" + fav_img + "';btn.classList.toggle('active-fav',active);}"

if old in c:
    c = c.replace(old, new)
    print("OK: updateCardFav")
else:
    print("NO encontrado - buscando variantes...")
    import re
    match = re.search(r'function updateCardFav[^\}]+\}', c)
    if match:
        print("Encontrado:", match.group(0)[:100])

with open('atlas/templates/atlas/biolog_pais.html', 'w', encoding='utf-8') as f:
    f.write(c)

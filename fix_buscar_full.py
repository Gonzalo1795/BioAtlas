# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/buscar_especie.html', encoding='utf-8') as f:
    c = f.read()

# 1. Añadir botón Mi Atlas a los quick actions
old_actions = """            <div class="sc-quick-actions" onclick="event.stopPropagation()">
                <button class="sc-qa-btn {% if especie.species_key in especies_favoritas %}active-fav{% endif %}" id="qa-fav-{{ especie.species_key }}" title="Favorito" onclick="quickFavorito({{ especie.species_key }}, this)">
                    <img src="/static/atlas/img/menu/favoritos.svg" style="width:34px;height:34px;vertical-align:middle;">
                </button>
                <a class="sc-qa-btn" title="Registrar avistamiento" href="{% url 'atlas:nuevo_avistamiento' especie.species_key %}" onclick="event.stopPropagation()">
                    <img src="/static/atlas/img/menu/avistamientos.svg" style="width:34px;height:34px;vertical-align:middle;">
                </a>
            </div>"""

new_actions = """            <div class="sc-quick-actions" onclick="event.stopPropagation()">
                <button class="sc-qa-btn {% if especie.species_key in especies_favoritas %}active-fav{% endif %}" id="qa-fav-{{ especie.species_key }}" title="Favorito" onclick="quickFavorito({{ especie.species_key }}, this)">
                    <img src="/static/atlas/img/menu/favoritos.svg" style="width:34px;height:34px;vertical-align:middle;">
                </button>
                <button class="sc-qa-btn" id="qa-atlas-{{ especie.species_key }}" title="Mi Atlas" onclick="quickAtlas({{ especie.species_key }}, this)">
                    <img src="/static/atlas/img/menu/Mi_atlas.svg" style="width:34px;height:34px;vertical-align:middle;">
                </button>
                <a class="sc-qa-btn" title="Registrar avistamiento" href="{% url 'atlas:nuevo_avistamiento' especie.species_key %}" onclick="event.stopPropagation()">
                    <img src="/static/atlas/img/menu/avistamientos.svg" style="width:34px;height:34px;vertical-align:middle;">
                </a>
            </div>"""

if old_actions in c:
    c = c.replace(old_actions, new_actions)
    print("OK quick actions")
else:
    print("NO quick actions")

# 2. Arreglar placeholder vacío (quitamos emojis, dejamos vacío limpio)
old_ph = """                <div class="sc-placeholder" id="placeholder-{{ especie.species_key }}">
                </div>"""
new_ph = """                <div class="sc-placeholder" id="placeholder-{{ especie.species_key }}"></div>"""
c = c.replace(old_ph, new_ph)

with open('atlas/templates/atlas/buscar_especie.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("DONE")

# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/buscar_especie.html', encoding='utf-8') as f:
    c = f.read()

old_article = '''        <article class="species-card" data-species-key="{{ especie.species_key }}" data-sci-name="{{ especie.canonical_name|default:especie.scientific_name }}" style="cursor:pointer;">
            <div class="sc-image-wrap">
                <div class="sc-placeholder" id="placeholder-{{ especie.species_key }}">
                    {% if especie.class_name == 'Mammalia' %}\U0001f981{% elif especie.class_name == 'Aves' %}\U0001f985{% elif especie.class_name == 'Reptilia' %}\U0001f98e{% elif especie.class_name == 'Amphibia' %}\U0001f438{% elif especie.class_name == 'Actinopterygii' %}\U0001f41f{% elif especie.class_name == 'Insecta' %}\U0001f98b{% elif especie.class_name == 'Magnoliopsida' %}\U0001f338{% elif especie.class_name == 'Agaricomycetes' %}\U0001f344{% elif especie.class_name == 'Arachnida' %}\U0001f577\ufe0f{% elif especie.kingdom == 'Plantae' %}\U0001f33f{% elif especie.kingdom == 'Fungi' %}\U0001f344{% else %}\U0001f30d{% endif %}
                </div>'''

new_article = '''        <article class="species-card" data-species-key="{{ especie.species_key }}" data-sci-name="{{ especie.canonical_name|default:especie.scientific_name }}" style="cursor:pointer;">
            {% if user.is_authenticated %}
            <div class="sc-quick-actions" onclick="event.stopPropagation()">
                <button class="sc-qa-btn {% if especie.species_key in especies_favoritas %}active-fav{% endif %}" id="qa-fav-{{ especie.species_key }}" title="Favorito" onclick="quickFavorito({{ especie.species_key }}, this)">
                    <img src="/static/atlas/img/menu/favoritos.svg" style="width:34px;height:34px;vertical-align:middle;">
                </button>
                <a class="sc-qa-btn" title="Registrar avistamiento" href="{% url 'atlas:nuevo_avistamiento' especie.species_key %}" onclick="event.stopPropagation()">
                    <img src="/static/atlas/img/menu/avistamientos.svg" style="width:34px;height:34px;vertical-align:middle;">
                </a>
            </div>
            {% endif %}
            <div class="sc-image-wrap">
                <div class="sc-placeholder" id="placeholder-{{ especie.species_key }}">
                </div>'''

if old_article in c:
    c = c.replace(old_article, new_article)
    print("OK article")
else:
    print("NO article - buscando alternativa")
    # Buscar solo el placeholder con emojis
    import re
    c = re.sub(
        r'<div class="sc-placeholder" id="placeholder-\{\{ especie\.species_key \}\}">\s*\{%[^%]+%\}\s*</div>',
        '<div class="sc-placeholder" id="placeholder-{{ especie.species_key }}">\n                </div>',
        c
    )
    print("Placeholder cleaned")

with open('atlas/templates/atlas/buscar_especie.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("DONE")

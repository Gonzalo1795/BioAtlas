# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/mis_favoritos.html', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar las lineas del header viejo
start = None
end = None
for i, line in enumerate(lines):
    if 'max-width:1200px' in line and start is None:
        start = i
    if 'Volver al perfil' in line and start is not None:
        end = i
        break

print(f"Bloque encontrado: lineas {start} a {end}")
if start is not None and end is not None:
    new_lines = [
        '<div class="page-header">\n',
        '    <div class="container">\n',
        '        <nav class="breadcrumb">\n',
        '            <a href="{% url \'atlas:index\' %}" data-i18n="nav.inicio">Inicio</a><span>/</span><a href="{% url \'atlas:perfil\' %}">Mi perfil</a><span>/</span><span data-i18n="favs.titulo">Mis favoritos</span>\n',
        '        </nav>\n',
        '        <h1><img src="/static/atlas/img/menu/favoritos.svg" style="width:160px;height:160px;vertical-align:middle;margin-right:8px;object-fit:contain;"><span data-i18n="favs.titulo">Mis favoritos</span></h1>\n',
        '        <p class="page-subtitle">{{ total }} <span data-i18n="favs.guardadas">especie{{ total|pluralize:"s" }} guardada{{ total|pluralize:"s" }}</span></p>\n',
        '    </div>\n',
        '</div>\n',
        '<div style="max-width:1200px; margin:2.5rem auto; padding:0 1.5rem;">\n',
        '<div style="margin-bottom:1.5rem;">\n',
    ]
    lines = lines[:start] + new_lines + lines[end+1:]
    with open('atlas/templates/atlas/mis_favoritos.html', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("OK")
else:
    print("NO encontrado")

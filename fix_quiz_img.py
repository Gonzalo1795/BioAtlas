# -*- coding: utf-8 -*-
import re

with open("atlas/templates/atlas/quiz.html", encoding="utf-8") as f:
    content = f.read()

# Reemplazar los SVGs enormes por <img> apuntando a los archivos estáticos
# Primero quitar los SVGs actuales dentro de los divs de dificultad

# Patrón para encontrar el div con el SVG dentro de cada tarjeta
replacements = [
    (
        '<div style="margin-bottom:0.5rem;"><svg class="quiz-icon"',
        '<img class="quiz-icon-img" src="{% static \'atlas/img/quiz/facil.svg\' %}" alt="Fácil"><div style="display:none;"><svg class="quiz-icon"'
    ),
]

# Mejor approach: usar regex para reemplazar el bloque completo SVG
# Buscar el patron: <div style="margin-bottom:0.5rem;"><svg...></svg></div>
# y reemplazarlo por <img>

fichas = [
    ('facil',   "{% static 'atlas/img/quiz/facil.svg' %}",   'Fácil'),
    ('normal',  "{% static 'atlas/img/quiz/normal.svg' %}",  'Normal'),
    ('dificil', "{% static 'atlas/img/quiz/Dificil.svg' %}", 'Difícil'),
]

# Encontrar y reemplazar cada bloque SVG en las tarjetas
for nombre, static_path, alt in fichas:
    pattern = r'(<div style="margin-bottom:0\.5rem;">)<svg class="quiz-icon"[\s\S]*?</svg>(</div>)'
    replacement = f'\\1<img class="quiz-icon-img" src="{static_path}" alt="{alt}" style="width:80px;height:80px;object-fit:contain;">\\2'
    new_content = re.sub(pattern, replacement, content, count=1)
    if new_content != content:
        content = new_content
        print(f"OK: {nombre}")
        break

# Hacer los otros dos
for i in range(2):
    pattern = r'(<div style="margin-bottom:0\.5rem;">)<svg class="quiz-icon"[\s\S]*?</svg>(</div>)'
    nombre = fichas[i+1][0]
    static_path = fichas[i+1][1]
    alt = fichas[i+1][2]
    replacement = f'\\1<img class="quiz-icon-img" src="{static_path}" alt="{alt}" style="width:80px;height:80px;object-fit:contain;">\\2'
    new_content = re.sub(pattern, replacement, content, count=1)
    if new_content != content:
        content = new_content
        print(f"OK: {nombre}")

# Copa: reemplazar el SVG del resultado
pattern = r'(<div id="resultado-emoji" style="margin-bottom:1rem;">)<svg class="quiz-icon"[\s\S]*?</svg>(</div>)'
replacement = f'\\1<img src="{{% static \'atlas/img/quiz/copa.svg\' %}}" alt="Copa" id="resultado-emoji-img" style="width:100px;height:100px;object-fit:contain;">\\2'
new_content = re.sub(pattern, replacement, content, count=1)
if new_content != content:
    content = new_content
    print("OK: copa")

with open("atlas/templates/atlas/quiz.html", "w", encoding="utf-8") as f:
    f.write(content)
print("DONE")

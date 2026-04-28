# -*- coding: utf-8 -*-

with open("atlas/templates/atlas/quiz.html", encoding="utf-8") as f:
    content = f.read()

replacements = [
    (
        '<div style="font-size: 2rem; margin-bottom: 0.5rem;">🌱</div>',
        '<div style="margin-bottom: 0.5rem;"><img src="{% static \'atlas/img/quiz/facil.svg\' %}" alt="Fácil" style="width:64px;height:64px;object-fit:contain;"></div>'
    ),
    (
        '<div style="font-size: 2rem; margin-bottom: 0.5rem;">🔬</div>',
        '<div style="margin-bottom: 0.5rem;"><img src="{% static \'atlas/img/quiz/normal.svg\' %}" alt="Normal" style="width:64px;height:64px;object-fit:contain;"></div>'
    ),
    (
        '<div style="font-size: 2rem; margin-bottom: 0.5rem;">💀</div>',
        '<div style="margin-bottom: 0.5rem;"><img src="{% static \'atlas/img/quiz/Dificil.svg\' %}" alt="Difícil" style="width:64px;height:64px;object-fit:contain;"></div>'
    ),
    (
        '<div id="resultado-emoji" style="font-size:4rem; margin-bottom:1rem;">🏆</div>',
        '<div id="resultado-emoji" style="margin-bottom:1rem;"><img src="{% static \'atlas/img/quiz/copa.svg\' %}" alt="Copa" style="width:100px;height:100px;object-fit:contain;"></div>'
    ),
    (
        '🧬 <span data-i18n="quiz.titulo">Quiz Visual</span>',
        '<img src="{% static \'atlas/img/quiz/Quiz.svg\' %}" alt="Quiz" style="width:48px;height:48px;object-fit:contain;vertical-align:middle;margin-right:10px;"> <span data-i18n="quiz.titulo">Quiz Visual</span>'
    ),
]

# Añadir {% load static %} si no está
if '{% load static %}' not in content:
    content = content.replace('{% extends', '{% load static %}\n{% extends', 1)
    print("OK: load static añadido")

count = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new, 1)
        count += 1
        print(f"OK: {old[:40]}")
    else:
        print(f"NO ENCONTRADO: {old[:40]}")

with open("atlas/templates/atlas/quiz.html", "w", encoding="utf-8") as f:
    f.write(content)
print(f"DONE: {count} reemplazos")

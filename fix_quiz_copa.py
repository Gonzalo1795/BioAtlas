# -*- coding: utf-8 -*-

with open("atlas/templates/atlas/quiz.html", encoding="utf-8") as f:
    content = f.read()

old = "    const emojis = puntuacion > 800 ? '🏆' : puntuacion > 500 ? '🎯' : puntuacion > 200 ? '📚' : '🌱';\n    if (re) re.textContent = emojis;"

new = """    const copaUrl = "{% static 'atlas/img/quiz/copa.svg' %}";
    const emojis = puntuacion > 800 ? '<img src="' + copaUrl + '" style="width:80px;height:80px;object-fit:contain;">' : puntuacion > 500 ? '🎯' : puntuacion > 200 ? '📚' : '🌱';
    if (re) re.innerHTML = emojis;"""

if old in content:
    content = content.replace(old, new)
    with open("atlas/templates/atlas/quiz.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("OK")
else:
    print("ERROR: no encontrado")
    print("Buscando fragmento...")
    if "re.textContent = emojis" in content:
        print("Found: re.textContent = emojis")

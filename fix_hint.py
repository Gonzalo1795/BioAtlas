# -*- coding: utf-8 -*-
with open("atlas/templates/atlas/base.html", encoding="utf-8") as f:
    c = f.read()

c = c.replace('\U0001f446 Selecciona una dificultad para continuar', 'Selecciona una dificultad para continuar')
c = c.replace('\U0001f446 Select a difficulty to continue', 'Select a difficulty to continue')
c = c.replace('\U0001f446 S\u00e9lectionnez une difficult\u00e9 pour continuer', 'S\u00e9lectionnez une difficult\u00e9 pour continuer')

with open("atlas/templates/atlas/base.html", "w", encoding="utf-8") as f:
    f.write(c)
print("OK")

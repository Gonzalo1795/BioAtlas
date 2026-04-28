# -*- coding: utf-8 -*-
with open("atlas/templates/atlas/base.html", encoding="utf-8") as f:
    c = f.read()

c = c.replace('"\U0001f3c6 Mejores puntuaciones"', '"Mejores puntuaciones"')
c = c.replace('"\U0001f3c6 Top scores"', '"Top scores"')
c = c.replace('"\U0001f3c6 Meilleures scores"', '"Meilleures scores"')

with open("atlas/templates/atlas/base.html", "w", encoding="utf-8") as f:
    f.write(c)
print("OK: emojis quitados de traducciones")

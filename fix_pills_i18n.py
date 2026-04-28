# -*- coding: utf-8 -*-
with open("atlas/templates/atlas/base.html", encoding="utf-8") as f:
    c = f.read()

replacements = [
    ('\U0001f981 Mam\u00edferos', 'Mam\u00edferos'),
    ('\U0001f985 Aves', 'Aves'),
    ('\U0001f98e Reptiles', 'Reptiles'),
    ('\U0001f438 Anfibios', 'Anfibios'),
    ('\U0001f41f Peces', 'Peces'),
    ('\U0001f98b Insectos', 'Insectos'),
    ('\U0001f338 Plantas', 'Plantas'),
    ('\U0001f981 Mammals', 'Mammals'),
    ('\U0001f985 Birds', 'Birds'),
    ('\U0001f98e Reptiles', 'Reptiles'),
    ('\U0001f438 Amphibians', 'Amphibians'),
    ('\U0001f41f Fish', 'Fish'),
    ('\U0001f98b Insects', 'Insects'),
    ('\U0001f338 Plants', 'Plants'),
    ('\U0001f981 Mammif\u00e8res', 'Mammif\u00e8res'),
    ('\U0001f985 Oiseaux', 'Oiseaux'),
    ('\U0001f98e Reptiles', 'Reptiles'),
    ('\U0001f438 Amphibiens', 'Amphibiens'),
    ('\U0001f41f Poissons', 'Poissons'),
    ('\U0001f98b Insectes', 'Insectes'),
    ('\U0001f338 Plantes', 'Plantes'),
    ('\U0001f310 Todos', 'Todos'),
    ('\U0001f310 All', 'All'),
    ('\U0001f310 Tous', 'Tous'),
]

count = 0
for old, new in replacements:
    if old in c:
        c = c.replace(old, new)
        count += 1
        print("OK:", new)

with open("atlas/templates/atlas/base.html", "w", encoding="utf-8") as f:
    f.write(c)
print(f"DONE: {count} reemplazos")

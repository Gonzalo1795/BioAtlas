# -*- coding: utf-8 -*-
import re

with open('/mnt/user-data/uploads/Quiz.svg') as f:
    content = f.read()

svg = re.search(r'(<svg[\s\S]*?</svg>)', content).group(1)
svg = re.sub(r'\swidth="[^"]*"', '', svg)
svg = re.sub(r'\sheight="[^"]*"', '', svg)
svg = re.sub(r'\s+', ' ', svg).strip()
svg = svg.replace('fill="#000000"', 'fill="currentColor"')
svg = svg.replace('<svg ', '<svg style="width:48px;height:48px;display:inline-block;vertical-align:middle;margin-right:10px;color:var(--accent,#2d8a4e);" ', 1)

old = '<img src="{% static \'atlas/img/quiz/Quiz.svg\' %}" alt="Quiz" style="width:48px;height:48px;object-fit:contain;vertical-align:middle;margin-right:10px;">'

with open("atlas/templates/atlas/quiz.html", encoding="utf-8") as f:
    template = f.read()

if old in template:
    template = template.replace(old, svg)
    with open("atlas/templates/atlas/quiz.html", "w", encoding="utf-8") as f:
        f.write(template)
    print("OK: Quiz.svg inline en verde")
else:
    print("ERROR: no encontrado")

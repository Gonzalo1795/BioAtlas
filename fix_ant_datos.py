# -*- coding: utf-8 -*-
import re

with open("atlas/templates/atlas/antartida_detail.html", encoding="utf-8") as f:
    content = f.read()

pattern = r'\s*<div class="filters-box" style="margin-top:1rem;">[\s\S]*?</div>\s*</div>'
new_content = re.sub(pattern, '', content, count=1)

if new_content != content:
    with open("atlas/templates/atlas/antartida_detail.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("OK: apartado datos eliminado")
else:
    print("ERROR: no encontrado")

# -*- coding: utf-8 -*-
import re

with open("atlas/templates/atlas/antartida_detail.html", encoding="utf-8") as f:
    content = f.read()

# Quitar el banner azul
pattern = r'<div class="container" style="margin-bottom:1\.5rem;">[\s\S]*?</div>\s*</div>\s*\n'
new_content = re.sub(pattern, '', content, count=1)

if new_content != content:
    with open("atlas/templates/atlas/antartida_detail.html", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("OK: banner azul eliminado")
else:
    print("NO ENCONTRADO: intentando otro patron")
    # Patron alternativo
    start = content.find('<div class="container" style="margin-bottom:1.5rem;">')
    if start != -1:
        # Encontrar el cierre correcto
        end = content.find("</div>\n</div>", start)
        if end != -1:
            new_content = content[:start] + content[end+14:]
            with open("atlas/templates/atlas/antartida_detail.html", "w", encoding="utf-8") as f:
                f.write(new_content)
            print("OK: banner eliminado con patron alternativo")
        else:
            print("ERROR: no se encontro el cierre")
    else:
        print("ERROR: no se encontro el inicio del banner")

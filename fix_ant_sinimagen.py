# -*- coding: utf-8 -*-

old = "    especies_qs = especies_qs.order_by('scientific_name')\n    paginator   = Paginator(especies_qs, 25)"

new = "    especies_qs = especies_qs.filter(image_url__isnull=False).exclude(image_url='').order_by('scientific_name')\n    paginator   = Paginator(especies_qs, 25)"

with open('atlas/views.py', encoding='utf-8') as f:
    content = f.read()

# Solo reemplazar en la función antartida_detail
idx = content.find('def antartida_detail(request):')
if idx == -1:
    print("ERROR: función no encontrada")
else:
    section = content[idx:idx+3000]
    if old in section:
        new_section = section.replace(old, new, 1)
        content = content[:idx] + new_section + content[idx+3000:]
        with open('atlas/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("OK: especies sin imagen ocultas")
    else:
        print("ERROR: patrón no encontrado")

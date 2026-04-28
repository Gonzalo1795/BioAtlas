# -*- coding: utf-8 -*-
import re

img_style = 'width:28px;height:28px;display:inline-block;vertical-align:middle;margin-right:4px;object-fit:contain;'

pills = [
    ('pill.mammalia', 'Mamiferos.svg',  'Mamíferos'),
    ('pill.aves',     'Aves.svg',       'Aves'),
    ('pill.reptilia', 'Reptiles.svg',   'Reptiles'),
    ('pill.amphibia', 'Anfibios.svg',   'Anfibios'),
    ('pill.peces',    'Peces.svg',      'Peces'),
    ('pill.insecta',  'Insectos.svg',   'Insectos'),
    ('pill.plantas',  'Planta.svg',     'Plantas'),
]

files = [
    'atlas/templates/atlas/pais_detail.html',
    'atlas/templates/atlas/antartida_detail.html',
]

for filepath in files:
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        count = 0
        for key, svg_file, text in pills:
            img = f'<img src="/static/atlas/img/fauna/{svg_file}" style="{img_style}" alt="{text}">'
            # Buscar el pill y reemplazar todo su contenido interno
            pattern = r'(data-i18n="' + re.escape(key) + r'">)[\s\S]*?(' + re.escape(text) + r')(</a>)'
            replacement = r'\1' + img + r' <span data-i18n="' + key + r'">' + text + r'</span>\3'
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                count += 1
                print(f'OK: {key}')
        # Quitar data-i18n del <a> cuando ya tiene <span data-i18n> dentro
        content = re.sub(
            r'(<a [^>]*) data-i18n="pill\.[^"]*"([^>]*>)(<img [^>]*> <span data-i18n="pill\.[^"]*">)',
            r'\1\2\3',
            content
        )
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'DONE: {filepath} - {count} pills')
    except FileNotFoundError:
        print(f'NO EXISTE: {filepath}')

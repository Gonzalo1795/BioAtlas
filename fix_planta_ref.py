# -*- coding: utf-8 -*-
for filepath in ['atlas/templates/atlas/pais_detail.html', 'atlas/templates/atlas/antartida_detail.html']:
    try:
        with open(filepath, encoding='utf-8') as f:
            c = f.read()
        new_c = c.replace('fauna/Plantas.svg', 'fauna/Planta.svg')
        if new_c != c:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_c)
            print('OK:', filepath)
        else:
            print('SIN CAMBIOS:', filepath)
    except FileNotFoundError:
        print('NO EXISTE:', filepath)

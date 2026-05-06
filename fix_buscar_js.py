# -*- coding: utf-8 -*-
import re

with open('atlas/templates/atlas/buscar_especie.html', encoding='utf-8') as f:
    c = f.read()

# Eliminar el quickFavorito duplicado (el primero que aparece, el viejo)
# Buscar ambas ocurrencias
idx1 = c.find('function quickFavorito(speciesKey,btn){')
idx2 = c.find('function quickFavorito(speciesKey,btn){', idx1+1)

if idx1 != -1 and idx2 != -1:
    # Encontrar el fin del primer bloque (hasta el siguiente \n})
    end1 = c.find('\n}', idx1) + 2
    c = c[:idx1] + c[end1:]
    print("OK: duplicado eliminado")
else:
    print("No duplicado encontrado")

# Añadir quickAtlas después de quickFavorito
quick_atlas = """
function quickAtlas(speciesKey,btn){
    const isAuth = {{ user.is_authenticated|yesno:'true,false' }};
    if(!isAuth){window.location.href='/login/';return;}
    btn.disabled=true;
    fetch('/api/biolog/toggle/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},body:JSON.stringify({species_key:speciesKey,pais_id:0})})
    .then(r=>r.json()).then(data=>{
        btn.disabled=false;
        if(data.success){
            btn.classList.toggle('active-atlas',data.en_biolog);
            BioNotify.toast(data.en_biolog?t('modal.en_miatlas'):t('modal.eliminado_atlas'),data.en_biolog?'\\u2713':'\\u2715');
        } else if(data.limite){BioNotify.limitePremium(data.error);}
    }).catch(()=>{btn.disabled=false;});
}"""

# Insertar después del bloque quickFavorito
idx = c.find('function quickFavorito(speciesKey,btn){')
if idx != -1:
    end = c.find('\n}', idx) + 2
    c = c[:end] + quick_atlas + c[end:]
    print("OK: quickAtlas añadido")
else:
    print("NO: quickFavorito no encontrado")

with open('atlas/templates/atlas/buscar_especie.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("DONE")

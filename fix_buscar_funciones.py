# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/buscar_especie.html', encoding='utf-8') as f:
    c = f.read()

old = """function quickFavorito(speciesKey,btn){
    btn.disabled=true;
    fetch('/api/favorito/toggle/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},body:JSON.stringify({species_key:speciesKey})})
}
function quickAtlas(speciesKey,btn){
    if(!isAuthenticated){window.location.href='/login/';return;}
    btn.disabled=true;
    btn.disabled=false;
    BioNotify.show({title:'Mi Atlas',msg:'Para a\u00f1adir esta especie a Mi Atlas, visita la p\u00e1gina del pa\u00eds donde la encontraste.',actions:[{label:'Entendido',onclick:()=>BioNotify.close()}]});
}"""

new = """function quickFavorito(speciesKey,btn){
    if(!isAuthenticated){window.location.href='/login/';return;}
    btn.disabled=true;
    fetch('/api/favorito/toggle/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},body:JSON.stringify({species_key:speciesKey})})
    .then(r=>r.json()).then(data=>{
        btn.disabled=false;
        if(!data.success){if(data.limite)BioNotify.limitePremium(data.error);return;}
        const img=btn.querySelector('img');
        if(data.es_favorito){btn.classList.add('active-fav');}else{btn.classList.remove('active-fav');}
        BioNotify.toast(data.es_favorito?t('modal.en_favoritos'):t('modal.eliminado_fav'),data.es_favorito?'\u2713':'\u2715');
    }).catch(()=>{btn.disabled=false;});
}
function quickAtlas(speciesKey,btn){
    if(!isAuthenticated){window.location.href='/login/';return;}
    BioNotify.show({title:'Mi Atlas',msg:'Para a\u00f1adir esta especie a Mi Atlas visita la p\u00e1gina del pa\u00eds donde la encontraste.',actions:[{label:'Entendido',onclick:()=>BioNotify.close()}]});
}"""

if old in c:
    c = c.replace(old, new)
    print("OK")
else:
    print("NO - buscando alternativa")
    # Buscar solo quickFavorito incompleto
    import re
    c = re.sub(
        r"function quickFavorito\(speciesKey,btn\)\{[^}]*fetch[^}]*\}\s*function quickAtlas",
        new + "\nfunction quickAtlas_PLACEHOLDER",
        c
    )

with open('atlas/templates/atlas/buscar_especie.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("DONE")

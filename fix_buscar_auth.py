# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/buscar_especie.html', encoding='utf-8') as f:
    c = f.read()

# Unificar: quickFavorito usa isAuth -> cambiar a isAuthenticated
c = c.replace(
    "    const isAuth = {{ user.is_authenticated|yesno:'true,false' }};\n    if(!isAuth){window.location.href='/login/';return;}",
    "    if(!isAuthenticated){window.location.href='/login/';return;}"
)

# quickAtlas igual
c = c.replace(
    "function quickAtlas(speciesKey,btn){\n    const isAuth = {{ user.is_authenticated|yesno:'true,false' }};\n    if(!isAuth){window.location.href='/login/';return;}",
    "function quickAtlas(speciesKey,btn){\n    if(!isAuthenticated){window.location.href='/login/';return;}"
)

# quickAtlas sin pais_id no tiene sentido - cambiar por mensaje informativo
old_atlas_fetch = """    fetch('/api/biolog/toggle/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},body:JSON.stringify({species_key:speciesKey,pais_id:0})})
    .then(r=>r.json()).then(data=>{
        btn.disabled=false;
        if(data.success){
            btn.classList.toggle('active-atlas',data.en_biolog);
            BioNotify.toast(data.en_biolog?t('modal.en_miatlas'):t('modal.eliminado_atlas'),data.en_biolog?'\\u2713':'\\u2715');
        } else if(data.limite){BioNotify.limitePremium(data.error);}
    }).catch(()=>{btn.disabled=false;});"""

new_atlas_fetch = """    btn.disabled=false;
    BioNotify.show({title:'Mi Atlas',msg:'Para añadir esta especie a Mi Atlas, visita la página del país donde la encontraste.',actions:[{label:'Entendido',onclick:()=>BioNotify.close()}]});"""

c = c.replace(old_atlas_fetch, new_atlas_fetch)

with open('atlas/templates/atlas/buscar_especie.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("OK")

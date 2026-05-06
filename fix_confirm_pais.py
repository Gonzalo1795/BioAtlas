# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/pais_detail.html', encoding='utf-8') as f:
    c = f.read()

old_fav = "function quickFavorito(speciesKey,btn){\n    if(!isAuthenticated){window.location.href='/login/';return;}\n    btn.disabled=true;\n    fetch('/api/favorito/toggle/',"

new_fav = """function quickFavorito(speciesKey,btn){
    if(!isAuthenticated){window.location.href='/login/';return;}
    const isActive = btn.classList.contains('active-fav');
    if(isActive){
        BioNotify.show({title:'\u00bfQuitar de favoritos?',msg:'\u00bfEst\u00e1s seguro de que quieres eliminar esta especie de tus favoritos?',actions:[
            {label:'S\u00ed, eliminar',primary:true,onclick:()=>{BioNotify.close();doQuickFavorito(speciesKey,btn);}},
            {label:'Cancelar',onclick:()=>{BioNotify.close();}}
        ]});
    } else {
        doQuickFavorito(speciesKey,btn);
    }
}
function doQuickFavorito(speciesKey,btn){
    btn.disabled=true;
    fetch('/api/favorito/toggle/',"""

old_atlas = "function quickAtlas(speciesKey,paisId,btn){\n    if(!isAuthenticated){window.location.href='/login/';return;}\n    btn.disabled=true;\n    fetch('/api/biolog/toggle/',"

new_atlas = """function quickAtlas(speciesKey,paisId,btn){
    if(!isAuthenticated){window.location.href='/login/';return;}
    const isActive = btn.classList.contains('active-atlas');
    if(isActive){
        BioNotify.show({title:t('atlas.confirm_titulo'),msg:t('atlas.confirm_msg'),actions:[
            {label:t('atlas.confirm_si'),primary:true,onclick:()=>{BioNotify.close();doQuickAtlas(speciesKey,paisId,btn);}},
            {label:t('atlas.confirm_no'),onclick:()=>{BioNotify.close();}}
        ]});
    } else {
        doQuickAtlas(speciesKey,paisId,btn);
    }
}
function doQuickAtlas(speciesKey,paisId,btn){
    btn.disabled=true;
    fetch('/api/biolog/toggle/',"""

count = 0
if old_fav in c:
    c = c.replace(old_fav, new_fav)
    count += 1
    print("OK: quickFavorito")
else:
    print("NO: quickFavorito")

if old_atlas in c:
    c = c.replace(old_atlas, new_atlas)
    count += 1
    print("OK: quickAtlas")
else:
    print("NO: quickAtlas")

with open('atlas/templates/atlas/pais_detail.html', 'w', encoding='utf-8') as f:
    f.write(c)
print(f"DONE: {count}")

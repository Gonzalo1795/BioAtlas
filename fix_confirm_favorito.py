# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/mis_favoritos.html', encoding='utf-8') as f:
    c = f.read()

old = "function quitarFavoritoCard(speciesKey,btn){\n    if(!isAuthenticated){window.location.href='/login/';return;}\n    btn.disabled=true;\n    fetch('/api/favorito/toggle/',"

new = """function quitarFavoritoCard(speciesKey,btn){
    if(!isAuthenticated){window.location.href='/login/';return;}
    BioNotify.show({title:'\\u00bfQuitar de favoritos?',msg:'\\u00bfEst\\u00e1s seguro de que quieres eliminar esta especie de tus favoritos?',actions:[
        {label:'S\\u00ed, eliminar',primary:true,onclick:()=>{BioNotify.close();doQuitarFavoritoCard(speciesKey,btn);}},
        {label:'Cancelar',onclick:()=>{BioNotify.close();}}
    ]});
}
function doQuitarFavoritoCard(speciesKey,btn){
    btn.disabled=true;
    fetch('/api/favorito/toggle/',"""

if old in c:
    c = c.replace(old, new)
    print("OK")
else:
    print("NO encontrado")

with open('atlas/templates/atlas/mis_favoritos.html', 'w', encoding='utf-8') as f:
    f.write(c)

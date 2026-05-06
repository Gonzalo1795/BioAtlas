# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/buscar_especie.html', encoding='utf-8') as f:
    c = f.read()

old = "function getCookie(n){const v=`; ${document.cookie}`,p=v.split(`; ${n}=`);if(p.length===2)return p.pop().split(';').shift();}"

new = """function getCookie(n){const v=`; ${document.cookie}`,p=v.split(`; ${n}=`);if(p.length===2)return p.pop().split(';').shift();}

function quickFavorito(speciesKey,btn){
    const isAuth = """ + "{{ user.is_authenticated|yesno:'true,false' }}" + """;
    if(!isAuth){window.location.href='/login/';return;}
    btn.disabled=true;
    fetch('/api/favorito/toggle/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},body:JSON.stringify({species_key:speciesKey})})
    .then(r=>r.json()).then(data=>{
        btn.disabled=false;
        if(!data.success){if(data.limite)BioNotify.limitePremium(data.error);return;}
        btn.classList.toggle('active-fav',data.es_favorito);
        BioNotify.toast(data.es_favorito?t('modal.en_favoritos'):t('modal.eliminado_fav'),data.es_favorito?'\u2713':'\u2715');
    }).catch(()=>{btn.disabled=false;});
}"""

if old in c:
    c = c.replace(old, new)
    print("OK")
else:
    print("NO encontrado")

with open('atlas/templates/atlas/buscar_especie.html', 'w', encoding='utf-8') as f:
    f.write(c)

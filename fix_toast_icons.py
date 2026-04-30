# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/pais_detail.html', encoding='utf-8') as f:
    c = f.read()

# Favoritos
c = c.replace("BioNotify.toast(t('modal.en_favoritos'),'\u2764\ufe0f')", "BioNotify.toast(t('modal.en_favoritos'),'\u2713')")
c = c.replace("BioNotify.toast('Eliminado de favoritos','\U0001f494')", "BioNotify.toast('Eliminado de favoritos','\u2715')")
c = c.replace("BioNotify.toast(data.es_favorito?t('modal.en_favoritos'):'Eliminado de favoritos',data.es_favorito?'\u2764\ufe0f':'\U0001f494')", "BioNotify.toast(data.es_favorito?t('modal.en_favoritos'):'Eliminado de favoritos',data.es_favorito?'\u2713':'\u2715')")

# Mi Atlas
c = c.replace("BioNotify.toast(t('modal.en_miatlas'),'\U0001f33f')", "BioNotify.toast(t('modal.en_miatlas'),'\u2713')")
c = c.replace("BioNotify.toast('Eliminada de Mi Atlas','\U0001f33f')", "BioNotify.toast('Eliminada de Mi Atlas','\u2715')")
c = c.replace("BioNotify.toast(data.en_biolog?t('modal.en_miatlas'):'Eliminada de Mi Atlas','\U0001f33f')", "BioNotify.toast(data.en_biolog?t('modal.en_miatlas'):'Eliminada de Mi Atlas',data.en_biolog?'\u2713':'\u2715')")

with open('atlas/templates/atlas/pais_detail.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("DONE")

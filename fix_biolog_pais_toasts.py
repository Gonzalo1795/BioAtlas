# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/biolog_pais.html', encoding='utf-8') as f:
    c = f.read()

# Quitar emojis de toasts y usar traducciones
c = c.replace("BioNotify.toast(t('modal.en_favoritos'),'\u2764\ufe0f')", "BioNotify.toast(t('modal.en_favoritos'),'\u2713')")
c = c.replace("BioNotify.toast('Eliminado de favoritos','\U0001f494')", "BioNotify.toast(t('modal.eliminado_fav'),'\u2715')")
c = c.replace("BioNotify.toast('Eliminada de Mi Atlas','\U0001f33f')", "BioNotify.toast(t('modal.eliminado_atlas'),'\u2715')")
c = c.replace(":'Eliminado de favoritos'", ":t('modal.eliminado_fav')")
c = c.replace("?'\u2764\ufe0f':'\U0001f494'", "?'\u2713':'\u2715'")

with open('atlas/templates/atlas/biolog_pais.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("DONE")

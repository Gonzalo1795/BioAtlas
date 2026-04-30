# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/premium.html', encoding='utf-8') as f:
    c = f.read()

img_sm = '<img src="/static/atlas/img/premium.svg" style="width:20px;height:20px;vertical-align:middle;margin-right:4px;object-fit:contain;">'
img_md = '<img src="/static/atlas/img/premium.svg" style="width:28px;height:28px;vertical-align:middle;margin-right:4px;object-fit:contain;">'
img_lg = '<img src="/static/atlas/img/premium.svg" style="width:40px;height:40px;vertical-align:middle;object-fit:contain;">'

replacements = [
    ('>\u2728 BioAtlas Premium</div>', '>' + img_sm + ' BioAtlas Premium</div>'),
    ('<span style="font-size:1.5rem;">\u2728</span>', img_lg),
    ('\u2728 Hazte Premium \u2014 2,99\u20ac/mes', img_sm + ' Hazte Premium \u2014 2,99\u20ac/mes'),
    ('>\u2728 Premium</h3>', '>' + img_sm + ' Premium</h3>'),
]

count = 0
for old, new in replacements:
    if old in c:
        c = c.replace(old, new)
        count += 1
        print(f"OK: {old[:40]}")
    else:
        print(f"NO: {old[:40]}")

with open('atlas/templates/atlas/premium.html', 'w', encoding='utf-8') as f:
    f.write(c)
print(f"DONE: {count} reemplazos")

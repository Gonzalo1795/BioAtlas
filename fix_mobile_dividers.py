# -*- coding: utf-8 -*-
with open('atlas/templates/atlas/base.html', encoding='utf-8') as f:
    c = f.read()

# Quitar linea al inicio y la duplicada despues de quiz
old = '''<div id="nav-mobile-menu" style="display:none;">
    <div class="nav-mobile-divider"></div>
    <a href="{% url 'atlas:index' %}">'''
new = '''<div id="nav-mobile-menu" style="display:none;">
    <a href="{% url 'atlas:index' %}">'''
c = c.replace(old, new)

# Quitar el divisor duplicado dentro del if authenticated
old2 = '''    <div class="nav-mobile-divider"></div>
    {% if user.is_authenticated %}
        <div class="nav-mobile-divider"></div>
        <a href="{% url 'atlas:perfil' %}">'''
new2 = '''    <div class="nav-mobile-divider"></div>
    {% if user.is_authenticated %}
        <a href="{% url 'atlas:perfil' %}">'''
c = c.replace(old2, new2)

with open('atlas/templates/atlas/base.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("OK")

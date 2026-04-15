from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Permite acceder a un diccionario por clave en los templates de Django."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
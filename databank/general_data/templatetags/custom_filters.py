from django import template

register = template.Library()

@register.filter(name='get_key')
def get_key(obj, key):
    if hasattr(obj, 'get') and callable(obj.get):
        return obj.get(key, '')
    else:
        return getattr(obj, key, '')

@register.filter
def get_keyValue(dictionary, key):
    return dictionary.get(key, "")
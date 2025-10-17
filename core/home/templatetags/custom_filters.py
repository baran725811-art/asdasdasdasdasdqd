# home/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='get_range')
def get_range(value):
    """
    Rating sayısı kadar yıldız göstermek için range oluşturur
    """
    try:
        return range(int(value))
    except (TypeError, ValueError):
        return range(0)

@register.filter
def divide_into_groups(items, group_size):
    """
    Verilen listeyi belirtilen boyutta gruplara böler
    Kullanım: {{ products|divide_into_groups:3 }}
    """
    if not items:
        return []
    
    try:
        group_size = int(group_size)
        groups = []
        for i in range(0, len(items), group_size):
            groups.append(items[i:i + group_size])
        return groups
    except (TypeError, ValueError):
        return []

@register.filter
def replace(value, arg):
    """
    String replace filter
    Kullanım: {{ value|replace:"old:new" }}
    """
    if not value or not arg:
        return value
    
    try:
        old, new = arg.split(':', 1)
        return str(value).replace(old, new)
    except ValueError:
        return value

@register.filter
def lookup(dictionary, key):
    """
    Dictionary lookup filter
    Kullanım: {{ dict|lookup:"key" }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''


from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Dictionary lookup filter"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''


register = template.Library()

@register.filter
def divide_into_groups(value, group_size):
    """
    Bir listeyi belirtilen boyutta gruplara böler.
    Kullanım: {{ list|divide_into_groups:3 }}
    """
    if not value:
        return []
    
    group_size = int(group_size)
    groups = []
    
    for i in range(0, len(value), group_size):
        groups.append(value[i:i + group_size])
    
    return groups
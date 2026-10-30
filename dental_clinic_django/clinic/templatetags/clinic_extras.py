from django import template

register = template.Library()

@register.filter(name='dict_lookup')
def dict_lookup(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter(name='get_cond_disp')
def get_cond_disp(record):
    if hasattr(record, 'get_condition_display'):
        return record.get_condition_display()
    return "Sound"

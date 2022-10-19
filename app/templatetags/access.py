from django import template

register = template.Library()


@register.simple_tag
def access(dic, key):
    """Helper to access dictionaries in Django templates"""
    return dic[key]

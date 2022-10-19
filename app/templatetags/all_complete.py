from django import template

register = template.Library()


@register.simple_tag
def all_complete(lst):
    """Checks for comments marked complete"""
    for i in lst:
        if not i['Complete__c']:
            return False
    return True

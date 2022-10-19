from django import template

register = template.Library()


@register.simple_tag
def access_label(dic, key=False):
    """Access label method from a Django question"""
    if key:
        return dic[key].label_tag()
    else:
        return dic.label_tag()

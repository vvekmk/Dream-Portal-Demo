from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.simple_tag
def view_comment(dic, key):
    """Gets comments and preps them for HTML rendering"""
    comment = dic[key].value()
    comment = comment.replace("\r\n", "</span><br><span>")
    return mark_safe(f"<span>{comment}</span>")

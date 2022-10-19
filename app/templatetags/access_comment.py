from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.simple_tag
def access_comment(comment):
    """Replaces Salesforce newlines with HTML new lines"""
    comment = comment.replace("\r\n", "</span><br><span>")
    return mark_safe(f"<span>{comment}</span>")

from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.simple_tag
def row_heads(lst):
    """Get number of assignments"""
    most_records = 0
    for record in lst:
        assignments = record["Scholarship_Assignments__r"]["records"]
        if len(assignments) > most_records:
            most_records = len(assignments)
    return most_records

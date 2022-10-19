from django import template
from django.conf import settings
from app.survey_vars import panelchairs

register = template.Library()


def doc_name(string):
    """Translates the Salesforce name of files"""
    if string == "Essay":
        name = "Scholarship Essay"
    elif string == "HS_Transcript":
        name = "High School Transcript"
    elif string == "C_Transcript":
        name = "College Transcript"
    elif string == "SAT_Score":
        name = "SAT Score (optional)"
    elif string == "ACT_Score":
        name = "ACT Score (optional)"

    return name


register.filter('docname', doc_name)

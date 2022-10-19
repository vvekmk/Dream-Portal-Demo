from django import template

register = template.Library()


def getattribute(obj, arg):
    """Gets objects attribute"""
    return obj[arg]


register.filter('getattribute', getattribute)

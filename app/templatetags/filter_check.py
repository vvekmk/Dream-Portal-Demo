from django import template

register = template.Library()


@register.simple_tag
def filter_check(original_lst, mx):
    """Takes the list of decisions and determines what category an application belongs in"""
    temp = []
    for i in original_lst:
        if i["Decision__c"]:
            temp.append(int(i["Decision__c"]))

    lst = temp
    if len(original_lst) < int(mx):
        return "noint"
    if not lst:
        return "none"

    if lst.count(lst[0]) == len(lst):
        if lst[0] == 1:
            return "maybe"
        elif lst[0] == 2:
            return "pass"
        elif lst[0] == 0:
            return "fail"
    else:
        if len(lst) == 1:
            return "none"
        return "disagree"

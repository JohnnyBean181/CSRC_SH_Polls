from django import template

register = template.Library()

@register.filter
def index(value, i):
    try:
        return value[int(i)]  # 索引 i
    except (IndexError, ValueError, TypeError):
        return None

@register.filter
def previous(value, i):
    try:
        return value[int(i) - 1]  # 索引 i-1
    except (IndexError, ValueError, TypeError):
        return None
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

@register.filter
def has_errors(formset, range):
    try:
        forms_in_range = [formset[i] for i in range ]
        has_errors = any(form.errors for form in forms_in_range)
        return has_errors
    except (IndexError, ValueError, TypeError):
        return None

@register.filter
def safe(original_string):
    formatted_string = original_string.replace("\n", "<br>")
    return formatted_string

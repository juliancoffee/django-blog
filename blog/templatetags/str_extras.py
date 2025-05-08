from django import template

register = template.Library()


@register.filter(name="is_multiline")
def is_multiline(string) -> bool:
    return "\n" in string

from django import template


register = template.Library()

@register.filter(name='multiply')
def multiply(x, y):
    return x * y

@register.filter(name='width')
def width(entry):
    return entry['count'] * 2 + 10 + len(entry['flag']) * 8

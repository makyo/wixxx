from django import template


register = template.Library()

@register.filter(name='multiply')
def multiply(x, y):
    return x * y

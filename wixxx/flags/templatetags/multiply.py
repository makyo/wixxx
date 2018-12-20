from django import template


register = template.Library()

@register.filter(name='multiply')
def multiply(x, y):
    return x * y

@register.filter(name='width')
def width(data):
    BAR_FACTOR = 2
    PADDING = 10
    EM = 8
    max_width = -1
    for datum in data:
        curr_width = datum['count'] * BAR_FACTOR +\
            PADDING +\
            len(datum['flag']) * EM
        if curr_width > max_width:
            max_width = curr_width
    return max_width

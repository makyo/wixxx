from django import template


register = template.Library()
PADDING = 10
EM = 8
DOMAIN_MAX = 500
DOMAIN_MIN = 1

@register.filter(name='multiply')
def multiply(x, y):
    return x * y

@register.filter(name='scale')
def scale(data, datum):
    range_max = data[0]['count']
    range_min = data[-1]['count']
    range_size = float(range_max - range_min)
    percentage = float(datum['count']) / range_size
    return DOMAIN_MIN + (percentage * (DOMAIN_MAX - DOMAIN_MIN))

@register.filter(name='width')
def width(data):
    max_width = -1
    numbers = num_width(data)
    for datum in data:
        curr_width = (
            numbers +
            PADDING +
            scale(data, datum) +
            PADDING / 2 +
            len(datum['flag']) * EM)
        if curr_width > max_width:
            max_width = curr_width
    return max_width

@register.filter(name='num_width')
def num_width(data):
    return len(str(data[0]['count'])) * EM

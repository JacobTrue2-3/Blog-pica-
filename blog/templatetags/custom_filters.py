from django import template

register = template.Library()

@register.filter
def mod(value, arg):
    """Остаток от деления: value % arg"""
    try:
        return int(value) % int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def sub(value, arg):
    """Вычитание: value - arg"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def mul(value, arg):
    """Умножение: value * arg"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def gt(value, arg):
    """Сравнение: value > arg (возвращает True/False)"""
    try:
        return int(value) > int(arg)
    except (ValueError, TypeError):
        return False
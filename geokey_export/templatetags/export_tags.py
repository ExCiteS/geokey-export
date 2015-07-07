from django import template

register = template.Library()


@register.filter(name='expiry')
def expiry(export):
    if export.isoneoff:
        return 'One off'
    elif export.expiration:
        return export.expiration
    else:
        return 'Never'

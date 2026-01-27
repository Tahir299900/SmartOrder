from django import template

register = template.Library()


@register.filter(name='is_admin')
def is_admin(user):
    """Check if user is admin (superuser or in Admin group)"""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='Admin').exists()


@register.filter(name='in_group')
def in_group(user, group_name):
    """Check if user is in a specific group"""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def employee_required(view_func):
    """
    Decorator to allow both employees and admins.
    Requires user to be authenticated.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_only(view_func):
    """
    Decorator to allow only admins (superusers or users in Admin group).
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='Admin').exists():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden(
            "<h1>403 Forbidden</h1>"
            "<p>You don't have permission to access this resource.</p>"
            "<p>Only administrators can access this page.</p>"
        )
    return wrapper


def is_admin(user):
    """
    Helper function to check if user is admin.
    Can be used in templates or views.
    """
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='Admin').exists()
    )

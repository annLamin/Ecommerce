from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrapper_func
    return decorator
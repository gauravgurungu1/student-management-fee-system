from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def teacher_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, "teacher_profile"):
            messages.error(
                request,
                "You do not have permission to access the teacher area.",
            )
            return redirect("dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, "teacher_profile"):
            messages.error(
                request,
                "You do not have permission to access the administrator area.",
            )
            return redirect("teacher_dashboard")

        return view_func(request, *args, **kwargs)

    return wrapper
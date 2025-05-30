from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            messages.error(request, "You do not have permission to access this page.")
            # Redirect to login page if not authenticated at all, else to index.
            if not request.session.get('snipeit_authenticated'):
                return redirect(reverse('login') + f'?next={request.path}')
            return redirect('index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

from django.http import HttpResponseBadRequest
from django.core.exceptions import PermissionDenied

from functools import wraps

from search.http import HttpJSONResponse

def require_ajax(func):
    """
    AJAX request required decorator. Use it in your views:

    @ajax_required
    def my_view(request):
        ....
    """
    @wraps(func)
    def _inner(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return func(request, *args, **kwargs)
    return _inner

def json_response(func):
    @wraps(func)
    def _inner(request, *args, **kwargs):
        return HttpJSONResponse(func(request, *args, **kwargs))
    return _inner
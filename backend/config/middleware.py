from django.http import HttpResponseRedirect


class Redirect404ToHomeMiddleware:
    """Redirect all 404 responses to the main page."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            return HttpResponseRedirect("/")
        return response

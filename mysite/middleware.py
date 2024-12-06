from django.http import JsonResponse


class CrashMiddleware:
    def __init__(self, get_response):
        # I probably don't need this, but ChatGPT wrote this for me anyway
        self.get_response = get_response

    def __call__(self, request):
        # Originally I wanted this to return meta info, but instead it just
        # crashes Django
        #
        # But when Django crashes, it gives you all this info anyway, so it's
        # a win-win situation.
        headers = dict(request.META)

        return JsonResponse(headers, safe=False)

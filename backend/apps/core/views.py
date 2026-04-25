from django.http import JsonResponse


def health_check(request):
    """Simple health check endpoint for Docker."""
    return JsonResponse(
        {'status': 'healthy', 'service': 'medisoft-backend'},
        status=200,
    )

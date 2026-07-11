from django.http import JsonResponse


def home(request):
    return JsonResponse(
        {
            "project": "GenRec-AI",
            "status": "Backend is running",
            "version": "0.1.0",
        }
    )

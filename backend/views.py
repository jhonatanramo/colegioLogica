from django.http import JsonResponse

def home(request):
    return JsonResponse({"mensaje": "API de BACKCOROJUVENIL activa"})

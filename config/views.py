from django.http import HttpResponse

def home(request):
    return HttpResponse("Bienvenido al servidor Django del coro juvenil 🎶")

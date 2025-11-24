from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Persona

@api_view(['POST'])
def Login(request):
    try:
        data = request.data
        clave = data.get('clave')
        materia = Persona.objects.filter(clave=clave).first()
        
        if not materia:
            return Response({"error": "Usuario no encontrado"}, status=404)

        user = {
            "nombre": materia.nombre,
            "apellidop": materia.apellido_paterno,
            "apellidom": materia.apellido_materno,
            "correo": materia.correo,
        }

        return Response(user, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Persona
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

# ---------------------------------------
# CREAR USUARIO
# ---------------------------------------

@api_view(['POST'])
def usuarioNormal(request):
    print("DATA RECIBIDA:", request.data)  # <-- MOSTRAR LO QUE ENVÍAS
    try:
        materia = Persona.objects.create(
            nombre=request.data.get('nombre'),
            apellido_paterno=request.data.get('apellido_paterno'),
            apellido_materno=request.data.get('apellido_materno'),
            ci=request.data.get('ci'),
            correo=request.data.get('correo'),
            clave=request.data.get('clave'),
        )
        return Response({"message": "notificacion creado", "id": materia.id})
    
    except Exception as e:
        print("ERROR EXACTO:", str(e))     # <--- AQUI APARECERA EL MOTIVO DEL 400
        return Response({"error": str(e)}, status=400)

# ---------------------------------------
# ELIMINAR USUARIO
# ---------------------------------------
@api_view(['DELETE'])
def materiaEliminar(request):
    id = request.data.get('id')  # leer desde body
    if not id:
        return Response({"error": "ID no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        noti = Persona.objects.get(id=id)
        noti.delete()
        return Response({"message": "materia eliminada"}, status=status.HTTP_200_OK)
    except Persona.DoesNotExist:
        return Response({"error": "Materia no encontrada"}, status=status.HTTP_404_NOT_FOUND)

# ---------------------------------------
# LISTAR USUARIOS
# ---------------------------------------
@api_view(['GET'])
def materiaListar(request):
    try:
        materia = Persona.objects.all()  # Más recientes primero
        # Crear lista con fecha y hora separadas
        lista = []
        for n in materia:
            lista.append({
                'id': n.id,
                'nombre': n.nombre,
            })

        return Response(lista, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Curso
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

# ---------------------------------------
# CREAR USUARIO
# ---------------------------------------

@api_view(['POST'])
def CursoCrear(request):
    print("DATA RECIBIDA:", request.data)  # <-- MOSTRAR LO QUE ENVÍAS
    try:
        materia = Curso.objects.create(
            nombre=request.data.get('nombre'),
        )
        return Response({"message": "Curso creado", "id": materia.id})
    
    except Exception as e:
        print("ERROR EXACTO:", str(e))     # <--- AQUI APARECERA EL MOTIVO DEL 400
        return Response({"error": str(e)}, status=400)

# ---------------------------------------
# ELIMINAR USUARIO
# ---------------------------------------
@api_view(['DELETE'])
def CursoEliminar(request):
    id = request.data.get('id')  # leer desde body
    if not id:
        return Response({"error": "ID no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        noti = Curso.objects.get(id=id)
        noti.delete()
        return Response({"message": "Curso eliminada"}, status=status.HTTP_200_OK)
    except Curso.DoesNotExist:
        return Response({"error": "Curso no encontrada"}, status=status.HTTP_404_NOT_FOUND)

# ---------------------------------------
# LISTAR USUARIOS
# ---------------------------------------
@api_view(['GET'])
def CursoListar(request):
    try:
        materia = Curso.objects.all()  # Más recientes primero
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
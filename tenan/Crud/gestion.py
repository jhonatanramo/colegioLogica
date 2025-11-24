from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Gestion
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

# ---------------------------------------
# CREAR USUARIO
# ---------------------------------------

@api_view(['POST'])
def gestionCrear(request):
    print("DATA RECIBIDA:", request.data)  # <-- MOSTRAR LO QUE ENVÍAS
    try:
        notificaciones = Gestion.objects.create(
            nombre=request.data.get('nombre'),
            fecha_inicio=request.data.get('fecha_inicio'),
            fecha_fin=request.data.get('fecha_fin'),
        )
        return Response({"message": "notificacion creado", "id": notificaciones.id})
    
    except Exception as e:
        print("ERROR EXACTO:", str(e))     # <--- AQUI APARECERA EL MOTIVO DEL 400
        return Response({"error": str(e)}, status=400)

# ---------------------------------------
# ELIMINAR USUARIO
# ---------------------------------------
@api_view(['DELETE'])
def gestionEliminar(request):
    id = request.data.get('id')  # leer desde body
    if not id:
        return Response({"error": "ID no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        noti = Gestion.objects.get(id=id)
        noti.delete()
        return Response({"message": "Gestion eliminada"}, status=status.HTTP_200_OK)
    except Gestion.DoesNotExist:
        return Response({"error": "Gestion no encontrada"}, status=status.HTTP_404_NOT_FOUND)

# ---------------------------------------
# LISTAR USUARIOS
# ---------------------------------------
@api_view(['GET'])
def gestionListar(request):
    try:
        notificaciones = Gestion.objects.all() # Más recientes primero

        # Crear lista con fecha y hora separadas
        lista = []
        for n in notificaciones:
            lista.append({
                'id': n.id,
                'nombre': n.nombre,
            })

        return Response(lista, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
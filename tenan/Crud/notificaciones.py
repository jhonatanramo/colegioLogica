from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Notificaciones
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

# ---------------------------------------
# CREAR USUARIO
# ---------------------------------------

@api_view(['POST'])
def notiCrear(request):
    print("DATA RECIBIDA:", request.data)  # <-- MOSTRAR LO QUE ENVÍAS
    try:
        notificaciones = Notificaciones.objects.create(
            titulo=request.data.get('titulo'),
            mensaje=request.data.get('mensaje'),
        )
        return Response({"message": "notificacion creado", "id": notificaciones.id})
    
    except Exception as e:
        print("ERROR EXACTO:", str(e))     # <--- AQUI APARECERA EL MOTIVO DEL 400
        return Response({"error": str(e)}, status=400)

# ---------------------------------------
# ELIMINAR USUARIO
# ---------------------------------------
@api_view(['DELETE'])
def notiEliminar(request):
    id = request.data.get('id')  # leer desde body
    if not id:
        return Response({"error": "ID no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        noti = Notificaciones.objects.get(id=id)
        noti.delete()
        return Response({"message": "Notificación eliminada"}, status=status.HTTP_200_OK)
    except Notificaciones.DoesNotExist:
        return Response({"error": "Notificación no encontrada"}, status=status.HTTP_404_NOT_FOUND)

# ---------------------------------------
# LISTAR USUARIOS
# ---------------------------------------
@api_view(['GET'])
def notiListar(request):
    try:
        notificaciones = Notificaciones.objects.all().order_by('-fecha_envio')  # Más recientes primero

        # Crear lista con fecha y hora separadas
        lista = []
        for n in notificaciones:
            lista.append({
                'id': n.id,
                'titulo': n.titulo,
                'mensaje': n.mensaje,
                'fechaCreada': n.fecha_envio.date(),
                'horaCreada': n.fecha_envio.time().strftime("%H:%M:%S"),
            })

        return Response(lista, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
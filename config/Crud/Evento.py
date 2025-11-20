from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Evento
from ..serializers import EventoSerializer

# -----------------------------
# Crear evento
# -----------------------------
@api_view(['POST'])
def crear_evento(request):
    nombre = request.data.get('nombre')
    detalle = request.data.get('detalle')
    nombre_del_lugar = request.data.get('nombre_del_lugar')
    ubicacion = request.data.get('ubicacion')
    longitud = request.data.get('longitud')
    latitud = request.data.get('latitud')

    if not all([nombre, detalle, nombre_del_lugar, ubicacion, longitud, latitud]):
        return Response({"error": "Debe proporcionar todos los campos"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = EventoSerializer(data={
        "nombre": nombre,
        "detalle": detalle,
        "nombre_del_lugar": nombre_del_lugar,
        "ubicacion": ubicacion,
        "longitud": longitud,
        "latitud": latitud
    })

    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Evento creado exitosamente", "evento": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# Obtener todos los eventos
# -----------------------------
@api_view(['GET'])
def obtener_eventos(request):
    eventos = Evento.objects.all()
    serializer = EventoSerializer(eventos, many=True)
    return Response(serializer.data)

# -----------------------------
# Obtener un evento por ID
# -----------------------------
@api_view(['GET'])
def obtener_evento(request):
    id_evento = request.GET.get('id')
    if not id_evento:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)

    evento = Evento.objects.filter(id=id_evento).first()
    if not evento:
        return Response({"error": "Evento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventoSerializer(evento)
    return Response(serializer.data)

# -----------------------------
# Editar evento
# -----------------------------
@api_view(['PUT'])
def editar_evento(request):
    id_evento = request.data.get('id')
    if not id_evento:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)

    evento = Evento.objects.filter(id=id_evento).first()
    if not evento:
        return Response({"error": "Evento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventoSerializer(evento, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Evento actualizado exitosamente", "evento": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# Eliminar evento
# -----------------------------
@api_view(['DELETE'])
def eliminar_evento(request):
    id_evento = request.GET.get('id')
    if not id_evento:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        evento = Evento.objects.get(id=id_evento)
        evento.delete()
        return Response({"mensaje": "Evento eliminado exitosamente"})
    except Evento.DoesNotExist:
        return Response({"error": "Evento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import EventoRepertorio
from ..serializers import EventoRepertorioSerializer

# -----------------------------
# Crear relación evento-repertorio
# -----------------------------
@api_view(['POST'])
def crear_evento_repertorio(request):
    orden = request.data.get('orden')
    evento_id = request.data.get('evento')
    repertorio_id = request.data.get('repertorio')

    if orden is None or not evento_id or not repertorio_id:
        return Response({"error": "Debe proporcionar orden, evento y repertorio"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = EventoRepertorioSerializer(data={
        "orden": orden,
        "evento": evento_id,
        "repertorio": repertorio_id
    })

    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Relación creada exitosamente", "evento_repertorio": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# Obtener todas las relaciones
# -----------------------------
@api_view(['GET'])
def obtener_eventos_repertorios(request):
    relaciones = EventoRepertorio.objects.all()
    serializer = EventoRepertorioSerializer(relaciones, many=True)
    return Response(serializer.data)

# -----------------------------
# Obtener relación por ID
# -----------------------------
@api_view(['GET'])
def obtener_evento_repertorio(request):
    id_relacion = request.GET.get('id')
    if not id_relacion:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)

    relacion = EventoRepertorio.objects.filter(id=id_relacion).first()
    if not relacion:
        return Response({"error": "Relación no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventoRepertorioSerializer(relacion)
    return Response(serializer.data)

# -----------------------------
# Editar relación
# -----------------------------
@api_view(['PUT'])
def editar_evento_repertorio(request):
    id_relacion = request.data.get('id')
    relacion = EventoRepertorio.objects.filter(id=id_relacion).first()
    if not relacion:
        return Response({"error": "Relación no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventoRepertorioSerializer(relacion, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Relación actualizada exitosamente", "evento_repertorio": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# Eliminar relación
# -----------------------------
@api_view(['DELETE'])
def eliminar_evento_repertorio(request):
    id_relacion = request.GET.get('id')
    try:
        relacion = EventoRepertorio.objects.get(id=id_relacion)
        relacion.delete()
        return Response({"mensaje": "Relación eliminada exitosamente"})
    except EventoRepertorio.DoesNotExist:
        return Response({"error": "Relación no encontrada"}, status=status.HTTP_404_NOT_FOUND)

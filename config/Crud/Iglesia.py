from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Iglesia
from ..serializers import IglesiaSerializer

@api_view(['GET'])
def obtener_iglesias(request):
    iglesias = Iglesia.objects.all()
    serializer = IglesiaSerializer(iglesias, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def obtener_iglesia(request):
    id_iglesia = request.GET.get('id')
    if not id_iglesia:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)
    iglesia = Iglesia.objects.filter(id=id_iglesia).first()
    if not iglesia:
        return Response({"error": "Iglesia no encontrada"}, status=status.HTTP_404_NOT_FOUND)
    serializer = IglesiaSerializer(iglesia)
    return Response(serializer.data)

@api_view(['POST'])
def crear_iglesia(request):
    data = request.data
    nombre = data.get("nombre")
    
    if not nombre:
        return Response(
            {"error": "El campo 'nombre' es obligatorio."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    iglesia = Iglesia.objects.create(nombre=nombre)
    
    return Response(
        {"success": True, "id": iglesia.id, "nombre": iglesia.nombre},
        status=status.HTTP_201_CREATED
    )
@api_view(['PUT'])
def editar_iglesia(request):
    id_iglesia = request.data.get('id')
    iglesia = Iglesia.objects.filter(id=id_iglesia).first()
    if not iglesia:
        return Response({"error": "Iglesia no encontrada"}, status=status.HTTP_404_NOT_FOUND)
    nombre = request.data.get('nombre', iglesia.nombre)
    serializer = IglesiaSerializer(iglesia, data={"nombre": nombre}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Iglesia actualizada", "iglesia": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def eliminar_iglesia(request):
    data=request.data
    id_iglesia = data.get('id')
    try:
        iglesia = Iglesia.objects.get(id=id_iglesia)
        iglesia.delete()
        return Response({"mensaje": "Iglesia eliminada"})
    except Iglesia.DoesNotExist:
        return Response({"error": "Iglesia no encontrada"}, status=status.HTTP_404_NOT_FOUND)

from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Repertorio ,Parrafo
from ..serializers import RepertorioSerializer
import json

# -----------------------------
# Crear un nuevo repertorio
# -----------------------------
@api_view(['POST'])
def crear_repertorio(request):
    data = request.data
    nombre = data.get('nombre')
    parrafos = data.get('parrafo')
    coro = data.get('coro')
    if not nombre or not parrafos or not coro:
        return Response({"error": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST)
    repertorio = Repertorio.objects.create(
        nombre=nombre,
        coro=coro
    )
    listas = [p.strip() for p in parrafos.split(",,,") if p.strip()]
    for texto in listas:
        Parrafo.objects.create(
            repertorio=repertorio,
            parrafo=texto
        )
    return Response({"mensaje": "Repertorio creado correctamente"}, status=status.HTTP_201_CREATED)

# -----------------------------
# Obtener todos los repertorios
# -----------------------------
@api_view(['GET'])
def obtener_repertorios(request):
    repertorios = Repertorio.objects.all()
    serializer = RepertorioSerializer(repertorios, many=True)
    return Response(serializer.data)

# -----------------------------
# Obtener un repertorio por ID
# -----------------------------
@api_view(['GET'])
def obtener_repertorio(request):
    id_repertorio = request.GET.get('id')
    if not id_repertorio:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)
    
    repertorio = Repertorio.objects.filter(id=id_repertorio).first()
    if not repertorio:
        return Response({"error": "Repertorio no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = RepertorioSerializer(repertorio)
    return Response(serializer.data)

# -----------------------------
# Editar un repertorio existente
# -----------------------------
@api_view(['PUT'])
def editar_repertorio(request):
    id_repertorio = request.data.get('id')
    if not id_repertorio:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)

    repertorio = Repertorio.objects.filter(id=id_repertorio).first()
    if not repertorio:
        return Response({"error": "Repertorio no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    nombre = request.data.get('nombre', repertorio.nombre)
    coro = request.data.get('coro', repertorio.coro)

    serializer = RepertorioSerializer(repertorio, data={"nombre": nombre, "coro": coro}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Repertorio actualizado exitosamente", "repertorio": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------
# Eliminar un repertorio
# -----------------------------
@csrf_exempt

@api_view(['DELETE'])
def eliminar_repertorio(request):
    try:
        # ✅ Parseamos el body como JSON
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({"error": "Body inválido, se esperaba JSON"}, status=status.HTTP_400_BAD_REQUEST)

    id_repertorio = data.get('id')
    if not id_repertorio:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        repertorio = Repertorio.objects.get(id=id_repertorio)
        repertorio.delete()
        return Response({"mensaje": "Repertorio eliminado exitosamente"})
    except Repertorio.DoesNotExist:
        return Response({"error": "Repertorio no encontrado"}, status=status.HTTP_404_NOT_FOUND)
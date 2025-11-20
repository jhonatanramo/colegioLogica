from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Rol
from ..serializers import RolSerializer

# Crear Rol
@api_view(['POST'])
def crear_rol(request):
    nombre = request.data.get('nombre')
    if not nombre:
        return Response({"error": "Debe proporcionar un nombre"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = RolSerializer(data={"nombre": nombre})
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Rol creado exitosamente", "rol": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Obtener todos los roles
@api_view(['GET'])
def obtener_roles(request):
    roles = Rol.objects.all()
    serializer = RolSerializer(roles, many=True)
    return Response(serializer.data)

# Obtener un rol por ID
@api_view(['GET'])
def obtener_rol(request):
    id_rol = request.GET.get('id')
    if not id_rol:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)
    rol = Rol.objects.filter(id=id_rol).first()
    if not rol:
        return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    serializer = RolSerializer(rol)
    return Response(serializer.data)

# Editar Rol
@api_view(['PUT'])
def editar_rol(request):
    id_rol = request.data.get('id')
    if not id_rol:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)
    rol = Rol.objects.filter(id=id_rol).first()
    if not rol:
        return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    nombre = request.data.get('nombre', rol.nombre)
    serializer = RolSerializer(rol, data={"nombre": nombre}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Rol actualizado exitosamente", "rol": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Eliminar Rol
@api_view(['DELETE'])
def eliminar_rol(request):
    id_rol = request.GET.get('id')
    if not id_rol:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        rol = Rol.objects.get(id=id_rol)
        rol.delete()
        return Response({"mensaje": "Rol eliminado exitosamente"})
    except Rol.DoesNotExist:
        return Response({"error": "Rol no encontrado"}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import RolUsuario, Usuario, Rol
from ..serializers import RolUsuarioSerializer

# Crear relación usuario-rol
@api_view(['POST'])
def crear_rol_usuario(request):
    usuario_id = request.data.get('usuario')
    rol_id = request.data.get('rol')
    if not usuario_id or not rol_id:
        return Response({"error": "Debe proporcionar usuario y rol"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = RolUsuarioSerializer(data={"usuario": usuario_id, "rol": rol_id})
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "RolUsuario creado exitosamente", "rol_usuario": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Obtener todas las relaciones
@api_view(['GET'])
def obtener_roles_usuarios(request):
    relaciones = RolUsuario.objects.all()
    serializer = RolUsuarioSerializer(relaciones, many=True)
    return Response(serializer.data)

# Eliminar relación
@api_view(['DELETE'])
def eliminar_rol_usuario(request):
    id_relacion = request.GET.get('id')
    if not id_relacion:
        return Response({"error": "Debe proporcionar un id"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        relacion = RolUsuario.objects.get(id=id_relacion)
        relacion.delete()
        return Response({"mensaje": "RolUsuario eliminado exitosamente"})
    except RolUsuario.DoesNotExist:
        return Response({"error": "RolUsuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

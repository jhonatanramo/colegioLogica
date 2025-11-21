from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Gestion

# ---------------------------------------
# CREAR USUARIO
# ---------------------------------------
@api_view(['POST'])
def usuarioCrear(request):
    data = request.data

    try:
        
        gestion = Gestion.objects.create(
            nombre=data.get('nombre'),
        )
        return Response({
            "message": "Usuario creado correctamente",
            "id": gestion.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------
# ELIMINAR USUARIO
# ---------------------------------------
@api_view(['DELETE'])
def usuarioEliminar(request, id):
    try:
        usuario = Gestion.objects.get(id=id)
        usuario.delete()

        return Response({"message": "Usuario eliminado"}, status=status.HTTP_200_OK)

    except Gestion.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------------------
# LISTAR USUARIOS
# ---------------------------------------
@api_view(['GET'])
def usuarioListar(request):
    try:
        getion = Gestion.objects.all().values(
            'id',
            'nombre'
        ).order_by('id')

        return Response(list(getion), status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
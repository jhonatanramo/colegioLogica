from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Materia

# ------------------------------------------------
# CREAR MATERIA
# ------------------------------------------------
@api_view(['POST'])
def materiaCrear(request):
    data = request.data

    try:
        materia = Materia.objects.create(
            nombre=data.get('nombre')
        )
        return Response({
            "message": "Materia creada correctamente",
            "id": materia.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------
# ELIMINAR MATERIA
# ------------------------------------------------
@api_view(['DELETE'])
def materiaEliminar(request, id):
    try:
        materia = Materia.objects.get(id=id)
        materia.delete()
        return Response({"message": "Materia eliminada"}, status=status.HTTP_200_OK)

    except Materia.DoesNotExist:
        return Response({"error": "Materia no encontrada"}, status=status.HTTP_404_NOT_FOUND)


# ------------------------------------------------
# LISTAR MATERIAS
# ------------------------------------------------
@api_view(['GET'])
def materiaListar(request):
    try:
        materias = Materia.objects.all().values(
            'id',
            'nombre',
        ).order_by('id')

        return Response(list(materias), status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

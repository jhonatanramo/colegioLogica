from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Persona

# ---------------------------------------
# CREAR USUARIO
# ---------------------------------------

@api_view(['POST'])
def usuarioCrear(request):
    print("DATA RECIBIDA:", request.data)  # <-- MOSTRAR LO QUE ENVÍAS
    try:
        usuario = Persona.objects.create(
            nombre=request.data.get('nombre'),
            apellido_paterno=request.data.get('apellido_paterno'),
            apellido_materno=request.data.get('apellido_materno'),
            ci=request.data.get('ci'),
            correo=request.data.get('correo'),
            clave=request.data.get('clave'),
        )
        return Response({"message": "Usuario creado", "id": usuario.id})
    
    except Exception as e:
        print("ERROR EXACTO:", str(e))     # <--- AQUI APARECERA EL MOTIVO DEL 400
        return Response({"error": str(e)}, status=400)

# ---------------------------------------
# ELIMINAR USUARIO
# ---------------------------------------
@api_view(['DELETE'])
def usuarioEliminar(request, id):
    try:
        usuario = Persona.objects.get(id=id)
        usuario.delete()

        return Response({"message": "Usuario eliminado"}, status=status.HTTP_200_OK)

    except Persona.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------------------
# LISTAR USUARIOS
# ---------------------------------------
@api_view(['GET'])
def usuarioListar(request):
    try:
        usuarios = Persona.objects.all().values(
            'id',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'ci',
            'correo',
        ).order_by('id')

        return Response(list(usuarios), status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

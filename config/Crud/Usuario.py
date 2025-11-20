from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Usuario
import json

from ..serializers import UsuarioSerializer

@api_view(['GET'])
def obtener_usuarios(request):
    usuarios = Usuario.objects.all()
    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def obtener_usuario(request):
    usuario_id = request.GET.get('id')
    usuario = Usuario.objects.filter(id=usuario_id).first()
    if not usuario:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    serializer = UsuarioSerializer(usuario)
    return Response(serializer.data)
@api_view(['POST'])
def crear_usuario(request):
    data = request.data

    try:
        usuario = Usuario.objects.create(
            url=data.get('url'),
            apellido_p=data.get('apellido_p'),
            apellido_m=data.get('apellido_m'),
            nombre=data.get('nombre'),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            iglesia_id=data.get('iglesia')  # <-- si envías el ID de la iglesia
        )

        return Response({
            "mensaje": "Usuario creado",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellido_p": usuario.apellido_p,
                "apellido_m": usuario.apellido_m,
                "fecha_nacimiento": str(usuario.fecha_nacimiento),
                "iglesia": usuario.iglesia_id,
                "url": usuario.url
            }
        }, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)
@api_view(['POST'])
def crear_usuario_adm(request):
    data = request.data

    try:
        usuario = Usuario.objects.create(
            url=data.get('url'),
            apellido_p=data.get('apellido_p'),
            apellido_m=data.get('apellido_m'),
            nombre=data.get('nombre'),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            iglesia_id=data.get('iglesia') ,
            rol=True
        )

        return Response({
            "mensaje": "Usuario creado",
            "usuario": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellido_p": usuario.apellido_p,
                "apellido_m": usuario.apellido_m,
                "fecha_nacimiento": str(usuario.fecha_nacimiento),
                "iglesia": usuario.iglesia_id,
                "url": usuario.url
            }
        }, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['PUT'])
def editar_usuario(request):
    usuario_id = request.data.get('id')
    usuario = Usuario.objects.filter(id=usuario_id).first()
    if not usuario:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"mensaje": "Usuario actualizado", "usuario": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def eliminar_usuario(request):
    try:
        data = json.loads(request.body)
        usuario_id = data.get("id")
        
        if not usuario_id:
            return Response({"error": "ID no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
        
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.delete()
        return Response({"mensaje": "Usuario eliminado"})
    
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    except json.JSONDecodeError:
        return Response({"error": "JSON inválido"}, status=status.HTTP_400_BAD_REQUEST)

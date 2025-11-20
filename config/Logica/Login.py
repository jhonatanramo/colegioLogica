from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Usuario

@api_view(['POST'])
def login(request):
    fecha = request.data.get('fecha_nacimiento')
    usuario = Usuario.objects.filter(fecha_nacimiento=fecha).first()

    if not usuario:
        return Response(
            {'error': 'No se encuentra registrada esa fecha de nacimiento'},
            status=status.HTTP_404_NOT_FOUND
        )

    request.session['usuario_id'] = usuario.id
    request.session['nombre'] = usuario.nombre
    request.session['paterno'] = usuario.apellido_p
    request.session['materno'] = usuario.apellido_m

    return Response({
        'message': 'Inicio de sesión exitoso',
        'usuario': {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'apellido_p': usuario.apellido_p,
            'apellido_m': usuario.apellido_m,
            'rol': usuario.rol,
            'url': usuario.url,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def session(request):
    return Response({
        "nombre": request.session.get('nombre'),
        "paterno": request.session.get('paterno'),
        "materno": request.session.get('materno'),
    })

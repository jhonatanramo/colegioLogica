from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Usuario,Rol

@api_view(['GET'])
def usuario(request):
    data=request.data
    usuario=Usuario.objects.create(
        nombre=data.get('nombre'), 
        apellido_paterno=data.get('apellido_paterno'), 
        apellido_materno=data.get('apellido_materno'), 
        ci=data.get('ci'), 
        correo=data.get('correo'), 
        clave=data.get('clave')
    )

from django.urls import path
from .Crud.usuario import usuarioCrear,usuarioListar
from .Crud.notificaciones import notiCrear,notiListar,notiEliminar

urlpatterns = [

    path('usuario/crear/',usuarioCrear),
    path('usuario/listar/',usuarioListar),

    #-----   Notificaciones
    path('notificacion/crear/',notiCrear),
    path('notificacion/listar/',notiListar),
    path('notificacion/eliminar/',notiEliminar),
]

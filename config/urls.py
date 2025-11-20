from django.urls import path
from .Crud.Repertorio import *
from .Crud.Iglesia import *
from .Crud.Usuario import *
from .Crud.Parrafos import *
from .Crud.Evento import *
from .Crud.Rol import *
from .Crud.RolUsuario import *
from .Crud.EventoRepertorio import *
from .Logica.Login import *

urlpatterns = [
    path('login/',login),
    path('session/',session),

    # -----------------------
    # Iglesia
    # -----------------------
    path('iglesias/', obtener_iglesias),
    path('iglesia/', obtener_iglesia),
    path('iglesia/crear/', crear_iglesia),
    path('iglesia/editar/', editar_iglesia),
    path('iglesia/eliminar/', eliminar_iglesia),

    # -----------------------
    # Usuario
    # -----------------------
    path('usuarios/', obtener_usuarios),
    path('usuario/', obtener_usuario),
    path('usuario/crear/', crear_usuario),
    path('usuario/crear/adm/', crear_usuario_adm),
    path('usuario/editar/', editar_usuario),
    path('usuario/eliminar/', eliminar_usuario),

    # -----------------------
    # Repertorio
    # -----------------------
    path('repertorios/', obtener_repertorios),
    path('repertorio/', obtener_repertorio),
    path('repertorio/crear/', crear_repertorio),
    path('repertorio/editar/', editar_repertorio),
    path('repertorios/eliminar/', eliminar_repertorio),

    # -----------------------
    # Parrafo
    # -----------------------
    path('parrafos/<int:nro>/', obtener_parrafos),
    path('parrafos/todos', obtener_parrafos_todos),
    path('parrafo/crear/', crear_parrafo),
    path('parrafo/eliminar/', eliminar_parrafo),

    # -----------------------
    # Evento
    # -----------------------
    path('eventos/', obtener_eventos),
    path('evento/', obtener_evento),
    path('evento/crear/', crear_evento),
    path('evento/editar/', editar_evento),
    path('evento/eliminar/', eliminar_evento),

    # -----------------------
    # Rol
    # -----------------------
    path('roles/', obtener_roles),
    path('rol/', obtener_rol),
    path('rol/crear/', crear_rol),
    path('rol/editar/', editar_rol),
    path('rol/eliminar/', eliminar_rol),

    # -----------------------
    # RolUsuario (relación)
    # -----------------------
    path('roles_usuarios/', obtener_roles_usuarios),
    path('rol_usuario/crear/', crear_rol_usuario),
    path('rol_usuario/eliminar/', eliminar_rol_usuario),
    # -----------------------
    # EventoRepertorio (relación)
    # -----------------------
    path('eventos_repertorios/', obtener_eventos_repertorios),
    path('evento_repertorio/', obtener_evento_repertorio),
    path('evento_repertorio/crear/', crear_evento_repertorio),
    path('evento_repertorio/editar/', editar_evento_repertorio),
    path('evento_repertorio/eliminar/', eliminar_evento_repertorio),

]

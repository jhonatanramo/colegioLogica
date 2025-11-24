from django.urls import path
from .Crud.usuario import usuarioCrearEstudiante, usuarioListar, usuarioEliminar, usuarioCrearDocente
from .Crud.notificaciones import notiCrear, notiListar, notiEliminar
from .Crud.materia import materiaCrear, materiaListar, materiaEliminar
from .Crud.gestion import gestionCrear, gestionListar, gestionEliminar
from .Crud.Grado import CursoCrear, CursoListar, CursoEliminar
from .Crud.usuarioComun import usuarioNormal
from .Crud.Login import Login
from . import views

urlpatterns = [
     #-----   Login
    path('login/', Login),

    #-----   Usuarios
    path('usuario/crear/Docente/', usuarioCrearDocente),
    path('usuario/crear/HijoPadre/', usuarioCrearEstudiante),
    path('usuario/listar/', usuarioListar),
    path('usuario/eliminar/', usuarioEliminar),

    path('usuario/usuarioNormal/', usuarioNormal),


    #-----   Notificaciones
    path('notificacion/crear/', notiCrear),
    path('notificacion/listar/', notiListar),
    path('notificacion/eliminar/', notiEliminar),

    #-----   Materias
    path('materia/crear/', materiaCrear),
    path('materia/listar/', materiaListar),
    path('materia/eliminar/', materiaEliminar),

    #-----   Gestiones
    path('gestion/crear/', gestionCrear),
    path('gestion/listar/', gestionListar),
    path('gestion/eliminar/', gestionEliminar),

    #-----   Curso
    path('Curso/crear/', CursoCrear),
    path('Curso/listar/', CursoListar),
    path('Curso/eliminar/', CursoEliminar),

    #-----   Vistas de procesamiento de prompts y reportes
    path('ai-reports/generate/', views.generate_ai_report, name='generate_ai_report'),
    path('ai-reports/entities/', views.get_available_entities, name='get_entities'),
    path('ai-reports/analyze-trends/', views.analyze_trends, name='analyze_trends'),
]
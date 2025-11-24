from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Gestion)
class GestionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_inicio', 'fecha_fin']
    list_filter = ['fecha_inicio']

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido_paterno', 'apellido_materno', 'ci', 'rol']
    list_filter = ['rol']
    search_fields = ['nombre', 'apellido_paterno', 'ci']

@admin.register(SentralizadoNota)
class SentralizadoNotaAdmin(admin.ModelAdmin):
    list_display = ['persona', 'materia', 'curso', 'gestion', 'promedio_anual']
    list_filter = ['curso', 'materia', 'gestion']
    search_fields = ['persona__nombre', 'materia__nombre']
    readonly_fields = ['t1_promedio', 't2_promedio', 't3_promedio', 'promedio_anual']

@admin.register(CobroPago)
class CobroPagoAdmin(admin.ModelAdmin):
    list_display = ['persona', 'cobro', 'estado', 'monto_pagado', 'fecha_pago']
    list_filter = ['estado', 'fecha_pago']
    search_fields = ['persona__nombre']

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['alumno', 'curso', 'materia', 'fecha', 'estado']
    list_filter = ['estado', 'fecha', 'curso']
    search_fields = ['alumno__nombre']

# Registrar otros modelos
admin.site.register(Materia)
admin.site.register(ServiciosPago)
admin.site.register(padres)
admin.site.register(Pago)
admin.site.register(Tramites)
admin.site.register(Documento)
admin.site.register(PersonaDocumento)
admin.site.register(TramitePersona)
admin.site.register(CursoPersona)
admin.site.register(Cobro)
admin.site.register(Clase)
admin.site.register(Notificaciones)
from rest_framework import serializers
from .models import (
    Persona, SentralizadoNota, CobroPago, Asistencia, 
    Curso, Materia, Gestion, ServiciosPago
)

class PersonaSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Persona
        fields = ['id', 'nombre', 'apellido_paterno', 'apellido_materno', 'nombre_completo', 'ci', 'correo', 'rol']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido_paterno} {obj.apellido_materno}"

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['id', 'nombre']

class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ['id', 'nombre']

class GestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gestion
        fields = ['id', 'nombre', 'fecha_inicio', 'fecha_fin']

class NotaSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer()
    curso = CursoSerializer()
    materia = MateriaSerializer()
    gestion = GestionSerializer()
    
    class Meta:
        model = SentralizadoNota
        fields = '__all__'

class CobroPagoSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer()
    
    class Meta:
        model = CobroPago
        fields = '__all__'

class AsistenciaSerializer(serializers.ModelSerializer):
    alumno = PersonaSerializer()
    curso = CursoSerializer()
    materia = MateriaSerializer()
    gestion = GestionSerializer()
    
    class Meta:
        model = Asistencia
        fields = '__all__'
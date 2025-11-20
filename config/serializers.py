from rest_framework import serializers
from .models import (
    Iglesia,
    Usuario,
    Rol,
    RolUsuario,
    Repertorio,
    Parrafo,
    Evento,
    EventoRepertorio
)

# Serializer de Iglesia
class IglesiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Iglesia
        fields = '__all__'

# Serializer de Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    iglesia_nombre = serializers.CharField(source='iglesia.nombre', read_only=True)
    class Meta:
        model = Usuario
        fields = '__all__'

# Serializer de Rol
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

# Serializer de RolUsuario
class RolUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolUsuario
        fields = '__all__'

# Serializer de Repertorio
class RepertorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repertorio
        fields = '__all__'

# Serializer de Parrafo
class ParrafoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parrafo
        fields = '__all__'

# Serializer de Evento
class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'

# Serializer de EventoRepertorio
class EventoRepertorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventoRepertorio
        fields = '__all__'

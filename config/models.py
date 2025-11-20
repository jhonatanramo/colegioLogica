from django.db import models

# Tabla de iglesias
class Iglesia(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


# Tabla de usuarios
class Usuario(models.Model):
    nombre = models.CharField(max_length=30)
    apellido_p = models.CharField(max_length=30)
    apellido_m = models.CharField(max_length=30)
    fecha_nacimiento = models.DateField()
    iglesia = models.ForeignKey(Iglesia, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    rol=models.BooleanField(default=False)
    url = models.CharField(null=True ,max_length=1750)
    def __str__(self):
        return f"{self.nombre} {self.apellido_p}"


# Tabla de roles
class Rol(models.Model):
    nombre = models.CharField(max_length=30)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


# Relación usuario - rol
class RolUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)


# Tabla de repertorios
class Repertorio(models.Model):
    nombre = models.CharField(max_length=30)
    coro = models.CharField(max_length=30)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


# Párrafos asociados al repertorio
class Parrafo(models.Model):
    parrafo = models.CharField(max_length=200)
    repertorio = models.ForeignKey(Repertorio, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['id']  # Ordenar por ID por defecto

    def __str__(self):
        return f"Párrafo {self.id} - {self.parrafo[:50]}..."

# Tabla de eventos
class Evento(models.Model):
    nombre = models.CharField(max_length=150)
    detalle = models.CharField(max_length=350)
    nombre_del_lugar = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=160)
    longitud = models.CharField(max_length=200)
    latitud = models.CharField(max_length=200)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


# Relación evento - repertorio
class EventoRepertorio(models.Model):
    orden = models.IntegerField()  # <-- Cambiado a IntegerField
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    repertorio = models.ForeignKey(Repertorio, on_delete=models.CASCADE)

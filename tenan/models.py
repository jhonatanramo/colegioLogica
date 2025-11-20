from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone 

class Curso(models.Model):
    nombre = models.CharField(max_length=80)

    def __str__(self):
        return self.nombre


class Gestion(models.Model):
    nombre = models.CharField(max_length=80)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class ServiciosPago(models.Model):
    nombre = models.CharField(max_length=80)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE, related_name="servicios_pago", null=True)

    def __str__(self):
        return self.nombre


class Materia(models.Model):
    nombre = models.CharField(max_length=80)
    materia_fechaInicio = models.DateField(null=True, blank=True)
    materia_fechaFin = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Persona(models.Model):
    nombre = models.CharField(max_length=80)
    apellido_paterno = models.CharField(max_length=80)
    apellido_materno = models.CharField(max_length=80)
    ci = models.CharField(max_length=80)
    correo = models.CharField(max_length=100, default='sin_correo@ejemplo.com')  # <--- importante
    clave = models.CharField(max_length=800, default='sin_clave', null=True)
    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"

class padres(models.Model):
    padre = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="padres_persona")
    hijo = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="hijos_persona")

class Pago(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=200)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="pagos_persona", null=True)
    servicio= models.ForeignKey(ServiciosPago, on_delete=models.CASCADE, related_name="pagos_servicio", null=True)
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE, related_name="pagos", null=True)
    def __str__(self):
        return self.nombre

# -------------------------------
# Modelo de notas centralizadas
# -------------------------------
class SentralizadoNota(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="notas")
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="notas")
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="notas")
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE, related_name="notas")
    fecha_registro = models.DateTimeField(auto_now_add=True,null=True)
    # Trimestre 1
    t1_f1 = models.FloatField(null=True, blank=True)
    t1_f2 = models.FloatField(null=True, blank=True)
    t1_f3 = models.FloatField(null=True, blank=True)
    t1_promedio = models.FloatField(null=True, blank=True)
    t1_auto_evaluacion = models.FloatField(null=True, blank=True)

    # Trimestre 2
    t2_f1 = models.FloatField(null=True, blank=True)
    t2_f2 = models.FloatField(null=True, blank=True)
    t2_f3 = models.FloatField(null=True, blank=True)
    t2_promedio = models.FloatField(null=True, blank=True)
    t2_auto_evaluacion = models.FloatField(null=True, blank=True)

    # Trimestre 3
    t3_f1 = models.FloatField(null=True, blank=True)
    t3_f2 = models.FloatField(null=True, blank=True)
    t3_f3 = models.FloatField(null=True, blank=True)
    t3_promedio = models.FloatField(null=True, blank=True)
    t3_auto_evaluacion = models.FloatField(null=True, blank=True)

    # Promedio anual
    promedio_anual = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.persona} - {self.materia.nombre} ({self.curso.nombre}) [{self.gestion.nombre}]"


# -------------------------------
# Otros modelos
# -------------------------------
class Colegio(models.Model):
    nombre = models.CharField(max_length=80)
    direccion = models.CharField(max_length=80)
    director = models.CharField(max_length=80)
    ubicacion = models.CharField(max_length=80)

    def __str__(self):
        return self.nombre


class Tramites(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=80)

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=80)

    def __str__(self):
        return self.nombre


class Documento(models.Model):
    tipo_documento = models.CharField(max_length=80, unique=True)
    descripcion = models.CharField(max_length=80)
    rutas = models.CharField(max_length=150, default="/ruta/por/defecto")

    def __str__(self):
        return self.tipo_documento


# -------------------------------
# Relaciones ManyToMany a través de modelos
# -------------------------------
class PersonaDocumento(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="documentos")
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE, related_name="persona_documentos")

    def __str__(self):
        return f"{self.persona} - {self.documento.tipo_documento}"


class PersonaRol(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="roles_persona")
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name="persona_roles_rel")

    def __str__(self):
        return f"{self.persona} - {self.rol.nombre}"


class TramitePersona(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="tramites_persona")
    tramite = models.ForeignKey(Tramites, on_delete=models.CASCADE, related_name="persona_tramites")

    def __str__(self):
        return f"{self.persona} - {self.tramite.nombre}"


class CursoPersona(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="cursos_persona")
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="persona_cursos")

    def __str__(self):
        return f"{self.persona} - {self.curso.nombre}"

# -------------------------------
# COBROS Y PAGOS (CORRECTO)
# -------------------------------
class Cobro(models.Model):
    detalle = models.CharField(max_length=200)
    servicio_pago = models.ForeignKey(ServiciosPago, on_delete=models.CASCADE, related_name="cobros")
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    fecha_cobro_inicio = models.DateTimeField()
    fecha_cobro_fin = models.DateTimeField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="cobros", null=True)

    es_obligatorio = models.BooleanField(default=True)

    def __str__(self):  
        return f"{self.detalle} - {self.servicio_pago.nombre} - {self.monto}"


class CobroPago(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="cobro_pagos")
    cobro = models.ForeignKey(Cobro, on_delete=models.CASCADE, related_name="pagos", null=True)

    fecha_pago = models.DateTimeField(auto_now_add=True,null=True)  # <-- este campo NO acepta null
    estado = models.CharField(max_length=20, choices=[("Pagado","Pagado"),("Pendiente","Pendiente"),("Anulado","Anulado")], default="Pagado")
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)

    
class Asistencia(models.Model):
    """Registro de asistencia de un alumno en una clase"""
    alumno = models.ForeignKey('Persona', on_delete=models.CASCADE, related_name="asistencias")
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name="asistencias")
    materia = models.ForeignKey('Materia', on_delete=models.CASCADE, related_name="asistencias")
    gestion = models.ForeignKey('Gestion', on_delete=models.CASCADE, related_name="asistencias")
    fecha = models.DateField(default=timezone.now)
    
    # Estado de asistencia
    ESTADO_CHOICES = [
        ("Presente", "Presente"),
        ("Ausente", "Ausente"),
        ("Tarde", "Tarde"),
        ("Justificado", "Justificado"),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Presente")
    
    observaciones = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.alumno} - {self.materia.nombre} - {self.fecha} ({self.estado})"
class Clase(models.Model):
    """Opcional: Para planificar clases"""
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="clases")
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="clases")
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE, related_name="clases")
    fecha = models.DateField(default=timezone.now)
    tema = models.CharField(max_length=150, null=True, blank=True)
    
    def __str__(self):
        return f"{self.materia.nombre} - {self.curso.nombre} ({self.fecha})"

class Notificaciones(models.Model):
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.titulo} - {self.persona.nombre if self.persona else 'General'}"
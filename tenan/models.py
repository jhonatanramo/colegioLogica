from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
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
    def __str__(self):
        return self.nombre


class Persona(models.Model):
    nombre = models.CharField(max_length=80)
    apellido_paterno = models.CharField(max_length=80)
    apellido_materno = models.CharField(max_length=80)
    ci = models.CharField(max_length=80)
    correo = models.CharField(max_length=100, default='sin_correo@ejemplo.com')  # <--- importante
    ESTADO_CHOICES = [
        ("Admin", "admin"),
        ("Padre", "padre"),
        ("Madre", "madre"),
        ("Docente", "docente"),
        ("Alumno", "Alumno"),
    ]
    rol = models.CharField(max_length=20, null=True ,choices=ESTADO_CHOICES, default="Alumno")
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
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True)
    
    # Validación de rango para todas las notas (0-100)
    def nota_validator():
        return [MinValueValidator(0), MaxValueValidator(100)]
    
    # Trimestre 1
    t1_f1 = models.FloatField(
        null=True, blank=True, 
        validators=nota_validator(),
        verbose_name="Trimestre 1 - Faceta 1"
    )
    t1_f2 = models.FloatField(
        null=True, blank=True, 
        validators=nota_validator(),
        verbose_name="Trimestre 1 - Faceta 2"
    )
    t1_f3 = models.FloatField(
        null=True, blank=True, 
        validators=nota_validator(),
        verbose_name="Trimestre 1 - Faceta 3"
    )
    t1_promedio = models.FloatField(
        null=True, blank=True, 
        editable=False,  # ← No editable manualmente
        verbose_name="Promedio Trimestre 1"
    )
    t1_auto_evaluacion = models.FloatField(
        null=True, blank=True, 
        validators=nota_validator(),
        verbose_name="Auto evaluación Trimestre 1"
    )

    # Trimestre 2 (misma estructura)
    t2_f1 = models.FloatField(null=True, blank=True, validators=nota_validator())
    t2_f2 = models.FloatField(null=True, blank=True, validators=nota_validator())
    t2_f3 = models.FloatField(null=True, blank=True, validators=nota_validator())
    t2_promedio = models.FloatField(null=True, blank=True, editable=False)
    t2_auto_evaluacion = models.FloatField(null=True, blank=True, validators=nota_validator())

    # Trimestre 3 (misma estructura)
    t3_f1 = models.FloatField(null=True, blank=True, validators=nota_validator())
    t3_f2 = models.FloatField(null=True, blank=True, validators=nota_validator())
    t3_f3 = models.FloatField(null=True, blank=True, validators=nota_validator())
    t3_promedio = models.FloatField(null=True, blank=True, editable=False)
    t3_auto_evaluacion = models.FloatField(null=True, blank=True, validators=nota_validator())

    # Promedio anual
    promedio_anual = models.FloatField(null=True, blank=True, editable=False)

    class Meta:
        # Evitar duplicados
        unique_together = ['persona', 'materia', 'gestion', 'curso']
        # Mejorar rendimiento de consultas
        indexes = [
            models.Index(fields=['persona', 'gestion']),
            models.Index(fields=['curso', 'materia']),
        ]
        verbose_name = "Nota Centralizada"
        verbose_name_plural = "Notas Centralizadas"

    def __str__(self):
        return f"{self.persona} - {self.materia.nombre} ({self.curso.nombre}) [{self.gestion.nombre}]"

    # --- MÉTODOS DE CÁLCULO AUTOMÁTICO ---
    
    def calcular_promedio_trimestre(self, trimestre):
        """Calcula el promedio de un trimestre basado en sus 3 facetas"""
        facetas = []
        
        if trimestre == 1:
            facetas = [self.t1_f1, self.t1_f2, self.t1_f3]
        elif trimestre == 2:
            facetas = [self.t2_f1, self.t2_f2, self.t2_f3]
        elif trimestre == 3:
            facetas = [self.t3_f1, self.t3_f2, self.t3_f3]
        
        # Filtrar valores None y calcular promedio
        facetas_validas = [f for f in facetas if f is not None]
        
        if len(facetas_validas) == 0:
            return None
        
        promedio = sum(facetas_validas) / len(facetas_validas)
        return round(promedio, 2)

    def calcular_promedio_anual(self):
        """Calcula el promedio anual basado en los 3 trimestres"""
        promedios_trimestres = []
        
        if self.t1_promedio is not None:
            promedios_trimestres.append(self.t1_promedio)
        if self.t2_promedio is not None:
            promedios_trimestres.append(self.t2_promedio)
        if self.t3_promedio is not None:
            promedios_trimestres.append(self.t3_promedio)
        
        if len(promedios_trimestres) == 0:
            return None
        
        promedio_anual = sum(promedios_trimestres) / len(promedios_trimestres)
        return round(promedio_anual, 2)

    def actualizar_promedios(self):
        """Actualiza todos los promedios automáticamente"""
        # Promedios por trimestre
        self.t1_promedio = self.calcular_promedio_trimestre(1)
        self.t2_promedio = self.calcular_promedio_trimestre(2)
        self.t3_promedio = self.calcular_promedio_trimestre(3)
        
        # Promedio anual
        self.promedio_anual = self.calcular_promedio_anual()

    # --- OVERRIDE DEL MÉTODO SAVE ---
    
    def save(self, *args, **kwargs):
        """Override para calcular promedios automáticamente al guardar"""
        self.actualizar_promedios()
        super().save(*args, **kwargs)

    # --- PROPIEDADES ÚTILES ---
    
    @property
    def tiene_notas_completas(self):
        """Verifica si tiene al menos una nota en cada trimestre"""
        return all([
            any([self.t1_f1, self.t1_f2, self.t1_f3]),
            any([self.t2_f1, self.t2_f2, self.t2_f3]),
            any([self.t3_f1, self.t3_f2, self.t3_f3])
        ])

    @property
    def estado_academico(self):
        """Determina el estado académico basado en promedios"""
        if self.promedio_anual is None:
            return "Sin calificar"
        elif self.promedio_anual >= 70:
            return "Aprobado"
        elif self.promedio_anual >= 50:
            return "En recuperación"
        else:
            return "Reprobado"

    # --- MÉTODOS ESTÁTICOS ---
    
    @classmethod
    def promedio_curso_materia(cls, curso, materia, gestion):
        """Calcula el promedio general de un curso en una materia"""
        notas = cls.objects.filter(
            curso=curso, 
            materia=materia, 
            gestion=gestion,
            promedio_anual__isnull=False
        )
        
        if not notas.exists():
            return None
            
        promedio_general = notas.aggregate(
            avg=Avg('promedio_anual')
        )['avg']
        
        return round(promedio_general, 2)

    @classmethod
    def mejores_promedios(cls, gestion, curso=None, limite=10):
        """Obtiene los mejores promedios de una gestión"""
        queryset = cls.objects.filter(
            gestion=gestion,
            promedio_anual__isnull=False
        ).select_related('persona', 'materia')
        
        if curso:
            queryset = queryset.filter(curso=curso)
            
        return queryset.order_by('-promedio_anual')[:limite]

# -------------------------------
# Otros modelos
# -------------------------------


class Tramites(models.Model):
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

    fecha_cobro_inicio = models.DateTimeField(default=timezone.now)
    fecha_cobro_fin = models.DateTimeField()
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="cobros", null=True)

    es_obligatorio = models.BooleanField(default=True)

    def __str__(self):  
        return f"{self.detalle} - {self.servicio_pago.nombre} - {self.monto}"


class CobroPago(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="cobro_pagos")
    cobro = models.ForeignKey(Cobro, on_delete=models.CASCADE, related_name="pagos", null=True)

    fecha_pago = models.DateTimeField(auto_now_add=True)  # ✅ REMOVER null=True
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
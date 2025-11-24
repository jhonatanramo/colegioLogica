from .base_processor import BaseProcessor
from ..models import Asistencia, Persona, Curso, Gestion
from ..serializers import AsistenciaSerializer
from django.db.models import Count, Q
from django.db.models.functions import ExtractWeekDay

class AsistenciasProcessor(BaseProcessor):
    def puede_procesar(self, prompt):
        palabras_clave = [
            'asistencia', 'presente', 'ausente', 'tarde', 'falta',
            'asistió', 'asistieron', 'presencia'
        ]
        return any(palabra in prompt.lower() for palabra in palabras_clave)
    
    def procesar(self, prompt, parametros):
        prompt_lower = prompt.lower()
        
        if 'porcentaje' in prompt_lower or 'día' in prompt_lower:
            return self._procesar_asistencia_dia_semana(prompt, parametros)
        elif 'baja' in prompt_lower or 'poca' in prompt_lower:
            return self._procesar_baja_asistencia(prompt, parametros)
        else:
            return self._procesar_estadisticas_generales(prompt, parametros)
    
    def _procesar_asistencia_dia_semana(self, prompt, parametros):
        curso_nombre = parametros.get('curso', '')
        
        queryset = Asistencia.objects.all()
        
        if curso_nombre:
            queryset = queryset.filter(curso__nombre__icontains=curso_nombre)
        
        # Agrupar por día de la semana
        resultados = queryset.annotate(
            dia_semana=ExtractWeekDay('fecha')
        ).values('dia_semana').annotate(
            total=Count('id'),
            presentes=Count('id', filter=Q(estado="Presente")),
            porcentaje_presentes=(Count('id', filter=Q(estado="Presente")) * 100.0 / Count('id'))
        ).order_by('dia_semana')
        
        # Mapear números de día a nombres
        dias_map = {
            1: 'Domingo', 2: 'Lunes', 3: 'Martes', 4: 'Miércoles',
            5: 'Jueves', 6: 'Viernes', 7: 'Sábado'
        }
        
        datos_formateados = []
        for resultado in resultados:
            datos_formateados.append({
                'dia': dias_map.get(resultado['dia_semana'], f"Día {resultado['dia_semana']}"),
                'total_clases': resultado['total'],
                'presentes': resultado['presentes'],
                'porcentaje_asistencia': round(resultado['porcentaje_presentes'], 2)
            })
        
        return {
            'tipo': 'asistencia_dia_semana',
            'datos': datos_formateados,
            'total': len(datos_formateados),
            'configuracion_grafico': {
                'tipo': 'barras',
                'titulo': 'Asistencia por día de la semana',
                'eje_x': 'dia',
                'eje_y': 'porcentaje_asistencia'
            }
        }
    
    def _procesar_baja_asistencia(self, prompt, parametros):
        # Estudiantes con menos del 80% de asistencia
        curso_nombre = parametros.get('curso', '')
        
        # Obtener todas las personas (estudiantes)
        personas = Persona.objects.filter(rol="Alumno")
        
        if curso_nombre:
            personas = personas.filter(cursos_persona__curso__nombre__icontains=curso_nombre)
        
        datos_baja_asistencia = []
        
        for persona in personas:
            total_asistencias = Asistencia.objects.filter(alumno=persona).count()
            if total_asistencias == 0:
                continue
                
            asistencias_presente = Asistencia.objects.filter(
                alumno=persona, 
                estado="Presente"
            ).count()
            
            porcentaje_asistencia = (asistencias_presente / total_asistencias) * 100
            
            if porcentaje_asistencia < 80:
                datos_baja_asistencia.append({
                    'persona': {
                        'id': persona.id,
                        'nombre_completo': f"{persona.nombre} {persona.apellido_paterno}",
                        'ci': persona.ci
                    },
                    'total_clases': total_asistencias,
                    'asistencias': asistencias_presente,
                    'porcentaje_asistencia': round(porcentaje_asistencia, 2)
                })
        
        # Ordenar por menor porcentaje de asistencia
        datos_baja_asistencia.sort(key=lambda x: x['porcentaje_asistencia'])
        
        return {
            'tipo': 'baja_asistencia',
            'datos': datos_baja_asistencia[:15],  # Limitar a 15 resultados
            'total': len(datos_baja_asistencia),
            'configuracion_grafico': {
                'tipo': 'barras',
                'titulo': 'Estudiantes con baja asistencia (<80%)',
                'eje_x': 'persona.nombre_completo',
                'eje_y': 'porcentaje_asistencia'
            }
        }
    
    def _procesar_estadisticas_generales(self, prompt, parametros):
        # Estadísticas generales de asistencia
        total_asistencias = Asistencia.objects.count()
        total_presentes = Asistencia.objects.filter(estado="Presente").count()
        total_ausentes = Asistencia.objects.filter(estado="Ausente").count()
        total_tardes = Asistencia.objects.filter(estado="Tarde").count()
        
        porcentaje_presentes = (total_presentes / total_asistencias * 100) if total_asistencias > 0 else 0
        
        return {
            'tipo': 'estadisticas_asistencia',
            'datos': [],
            'metricas': {
                'total_registros': total_asistencias,
                'presentes': total_presentes,
                'ausentes': total_ausentes,
                'tardes': total_tardes,
                'porcentaje_presentes': round(porcentaje_presentes, 2)
            },
            'configuracion_grafico': {
                'tipo': 'pastel',
                'titulo': 'Distribución de asistencias',
                'datos': [
                    {'name': 'Presentes', 'value': total_presentes},
                    {'name': 'Ausentes', 'value': total_ausentes},
                    {'name': 'Tardes', 'value': total_tardes}
                ]
            }
        }
    
    @property
    def tipo_reporte(self):
        return 'asistencia'
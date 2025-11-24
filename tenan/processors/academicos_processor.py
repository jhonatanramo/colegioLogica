from .base_processor import BaseProcessor
from ..models import SentralizadoNota, Materia, Gestion, Curso
from ..serializers import NotaSerializer

class AcademicosProcessor(BaseProcessor):
    def puede_procesar(self, prompt):
        palabras_clave = [
            'nota', 'promedio', 'calificación', 'rendimiento', 
            'reprobar', 'aprobado', 'matemáticas', 'física', 'química'
        ]
        return any(palabra in prompt.lower() for palabra in palabras_clave)
    
    def procesar(self, prompt, parametros):
        prompt_lower = prompt.lower()
        
        if 'mejor' in prompt_lower or 'mejores' in prompt_lower:
            return self._procesar_mejores_promedios(prompt, parametros)
        elif 'reprobar' in prompt_lower or 'riesgo' in prompt_lower:
            return self._procesar_riesgo_reprobacion(prompt, parametros)
        elif 'comparar' in prompt_lower:
            return self._procesar_comparacion(prompt, parametros)
        else:
            return self._procesar_general(prompt, parametros)
    
    def _procesar_mejores_promedios(self, prompt, parametros):
        materia_nombre = parametros.get('materia', '')
        gestion_nombre = parametros.get('gestion', '2024')
        curso_nombre = parametros.get('curso', '')
        
        queryset = SentralizadoNota.objects.filter(
            promedio_anual__isnull=False
        ).select_related('persona', 'curso', 'materia', 'gestion')
        
        if materia_nombre:
            queryset = queryset.filter(materia__nombre__icontains=materia_nombre)
        
        if curso_nombre:
            queryset = queryset.filter(curso__nombre__icontains=curso_nombre)
        
        # Intentar obtener la gestión
        try:
            gestion = Gestion.objects.get(nombre__icontains=gestion_nombre)
            queryset = queryset.filter(gestion=gestion)
        except Gestion.DoesNotExist:
            # Usar la gestión más reciente
            gestion = Gestion.objects.order_by('-fecha_inicio').first()
            if gestion:
                queryset = queryset.filter(gestion=gestion)
        
        resultados = queryset.order_by('-promedio_anual')[:10]
        serializer = NotaSerializer(resultados, many=True)
        
        return {
            'tipo': 'mejores_promedios',
            'datos': serializer.data,
            'total': len(serializer.data),
            'configuracion_grafico': {
                'tipo': 'barras',
                'titulo': f'Mejores promedios en {materia_nombre or "todas las materias"}',
                'eje_x': 'persona.nombre_completo',
                'eje_y': 'promedio_anual'
            }
        }
    
    def _procesar_riesgo_reprobacion(self, prompt, parametros):
        materia_nombre = parametros.get('materia', '')
        
        queryset = SentralizadoNota.objects.filter(
            promedio_anual__lt=50
        ).select_related('persona', 'curso', 'materia', 'gestion')
        
        if materia_nombre:
            queryset = queryset.filter(materia__nombre__icontains=materia_nombre)
        
        resultados = queryset.order_by('promedio_anual')[:15]
        serializer = NotaSerializer(resultados, many=True)
        
        return {
            'tipo': 'riesgo_reprobacion',
            'datos': serializer.data,
            'total': len(serializer.data),
            'configuracion_grafico': {
                'tipo': 'barras',
                'titulo': f'Estudiantes en riesgo de reprobar {materia_nombre or ""}',
                'eje_x': 'persona.nombre_completo',
                'eje_y': 'promedio_anual'
            }
        }
    
    def _procesar_comparacion(self, prompt, parametros):
        # Implementar comparación entre cursos
        cursos = Curso.objects.all()[:3]  # Limitar a 3 cursos para ejemplo
        datos_comparacion = []
        
        for curso in cursos:
            promedio = SentralizadoNota.promedio_curso_materia(
                curso=curso, 
                materia=None,  # Todas las materias
                gestion=Gestion.objects.order_by('-fecha_inicio').first()
            )
            if promedio:
                datos_comparacion.append({
                    'curso': curso.nombre,
                    'promedio_general': promedio
                })
        
        return {
            'tipo': 'comparacion_cursos',
            'datos': datos_comparacion,
            'total': len(datos_comparacion),
            'configuracion_grafico': {
                'tipo': 'barras',
                'titulo': 'Comparación de promedios por curso',
                'eje_x': 'curso',
                'eje_y': 'promedio_general'
            }
        }
    
    def _procesar_general(self, prompt, parametros):
        # Procesamiento general para consultas académicas
        return self._procesar_mejores_promedios(prompt, parametros)
    
    @property
    def tipo_reporte(self):
        return 'academico'
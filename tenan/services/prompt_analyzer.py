import re
from datetime import datetime

class PromptAnalyzer:
    def __init__(self):
        self.materias = ['matemáticas', 'física', 'química', 'historia', 'lenguaje', 'biología']
        self.cursos = ['1ro', '2do', '3ro', '4to', '5to', '6to', 'primero', 'segundo', 'tercero', 'cuarto', 'quinto', 'sexto']
    
    def analizar_prompt(self, prompt_texto):
        prompt = prompt_texto.lower()
        parametros = {}
        
        # Extraer materia
        for materia in self.materias:
            if materia in prompt:
                parametros['materia'] = materia.capitalize()
                break
        
        # Extraer curso
        for curso in self.cursos:
            if curso in prompt:
                # Convertir texto a número
                curso_map = {
                    '1ro': '1ro', 'primero': '1ro',
                    '2do': '2do', 'segundo': '2do', 
                    '3ro': '3ro', 'tercero': '3ro',
                    '4to': '4to', 'cuarto': '4to',
                    '5to': '5to', 'quinto': '5to',
                    '6to': '6to', 'sexto': '6to'
                }
                parametros['curso'] = curso_map.get(curso, curso)
                break
        
        # Extraer gestión/temporalidad
        año_actual = datetime.now().year
        if 'este año' in prompt or 'año actual' in prompt:
            parametros['gestion'] = str(año_actual)
        elif 'último mes' in prompt:
            parametros['periodo'] = 'mensual'
        elif 'semana' in prompt:
            parametros['periodo'] = 'semanal'
        
        # Extraer tipo de acción
        if any(palabra in prompt for palabra in ['mejor', 'mejores', 'top', 'alto']):
            parametros['accion'] = 'mejores'
        elif any(palabra in prompt for palabra in ['peor', 'peores', 'bajo']):
            parametros['accion'] = 'peores'
        elif any(palabra in prompt for palabra in ['pendiente', 'deuda', 'mora']):
            parametros['accion'] = 'pendientes'
        
        # Determinar categoría principal
        categorias = {
            'academico': ['nota', 'promedio', 'calificación', 'rendimiento', 'reprobar', 'aprobado'],
            'financiero': ['pago', 'cobro', 'mora', 'deuda', 'pendiente', 'dinero'],
            'asistencia': ['asistencia', 'presente', 'ausente', 'tarde', 'falta'],
            'comparativo': ['comparar', 'entre', 'vs', 'versus', 'paralelos'],
            'predictivo': ['podrían', 'riesgo', 'predicción', 'posible']
        }
        
        for categoria, palabras in categorias.items():
            if any(palabra in prompt for palabra in palabras):
                parametros['categoria'] = categoria
                break
        else:
            parametros['categoria'] = 'general'
        
        return parametros
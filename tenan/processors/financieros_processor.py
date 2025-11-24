from .base_processor import BaseProcessor
from ..models import CobroPago, Persona, Curso
from ..serializers import CobroPagoSerializer
from django.db.models import Sum, Count
from django.utils import timezone

class FinancierosProcessor(BaseProcessor):
    def puede_procesar(self, prompt):
        palabras_clave = [
            'pago', 'cobro', 'mora', 'deuda', 'pendiente', 'dinero',
            'cuota', 'mensualidad', 'debe', 'pagado'
        ]
        return any(palabra in prompt.lower() for palabra in palabras_clave)
    
    def procesar(self, prompt, parametros):
        prompt_lower = prompt.lower()
        
        if 'pendiente' in prompt_lower or 'deuda' in prompt_lower:
            return self._procesar_pagos_pendientes(prompt, parametros)
        elif 'mejor' in prompt_lower or 'al día' in prompt_lower:
            return self._procesar_mejores_pagadores(prompt, parametros)
        else:
            return self._procesar_estado_financiero(prompt, parametros)
    
    def _procesar_pagos_pendientes(self, prompt, parametros):
        curso_nombre = parametros.get('curso', '')
        
        queryset = CobroPago.objects.filter(
            estado="Pendiente"
        ).select_related('persona', 'cobro')
        
        if curso_nombre:
            # Asumiendo que hay relación entre persona y curso
            personas_curso = Persona.objects.filter(
                cursos_persona__curso__nombre__icontains=curso_nombre
            )
            queryset = queryset.filter(persona__in=personas_curso)
        
        resultados = queryset.order_by('-monto_pagado')[:20]
        serializer = CobroPagoSerializer(resultados, many=True)
        
        total_deuda = queryset.aggregate(total=Sum('monto_pagado'))['total'] or 0
        
        return {
            'tipo': 'pagos_pendientes',
            'datos': serializer.data,
            'total': len(serializer.data),
            'metricas': {
                'total_deuda': float(total_deuda),
                'total_personas': queryset.values('persona').distinct().count()
            },
            'configuracion_grafico': {
                'tipo': 'barras',
                'titulo': 'Deudas pendientes por persona',
                'eje_x': 'persona.nombre_completo',
                'eje_y': 'monto_pagado'
            }
        }
    
    def _procesar_mejores_pagadores(self, prompt, parametros):
        # Personas sin deudas pendientes
        personas_con_deuda = CobroPago.objects.filter(
            estado="Pendiente"
        ).values_list('persona_id', flat=True).distinct()
        
        personas_al_dia = Persona.objects.exclude(id__in=personas_con_deuda)
        
        datos = []
        for persona in personas_al_dia[:10]:
            total_pagado = CobroPago.objects.filter(
                persona=persona, 
                estado="Pagado"
            ).aggregate(total=Sum('monto_pagado'))['total'] or 0
            
            datos.append({
                'persona': {
                    'id': persona.id,
                    'nombre_completo': f"{persona.nombre} {persona.apellido_paterno}",
                    'ci': persona.ci
                },
                'total_pagado': float(total_pagado),
                'estado': 'Al día'
            })
        
        return {
            'tipo': 'mejores_pagadores',
            'datos': datos,
            'total': len(datos),
            'configuracion_grafico': {
                'tipo': 'barras',
                'titulo': 'Mejores pagadores',
                'eje_x': 'persona.nombre_completo',
                'eje_y': 'total_pagado'
            }
        }
    
    def _procesar_estado_financiero(self, prompt, parametros):
        # Estado financiero general
        total_pagado = CobroPago.objects.filter(estado="Pagado").aggregate(
            total=Sum('monto_pagado')
        )['total'] or 0
        
        total_pendiente = CobroPago.objects.filter(estado="Pendiente").aggregate(
            total=Sum('monto_pagado')
        )['total'] or 0
        
        total_personas = Persona.objects.count()
        personas_con_deuda = CobroPago.objects.filter(estado="Pendiente").values('persona').distinct().count()
        
        return {
            'tipo': 'estado_financiero',
            'datos': [],
            'metricas': {
                'total_recaudado': float(total_pagado),
                'total_deuda': float(total_pendiente),
                'personas_al_dia': total_personas - personas_con_deuda,
                'personas_con_deuda': personas_con_deuda
            },
            'configuracion_grafico': {
                'tipo': 'pastel',
                'titulo': 'Estado financiero general',
                'datos': [
                    {'name': 'Pagado', 'value': float(total_pagado)},
                    {'name': 'Pendiente', 'value': float(total_pendiente)}
                ]
            }
        }
    
    @property
    def tipo_reporte(self):
        return 'financiero'
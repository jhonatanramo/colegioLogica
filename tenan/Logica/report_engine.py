# backend/Logica/report_engine.py
from django.db.models import Q, Count, Avg, Sum
from django.core.cache import cache
import json
from datetime import datetime, timedelta
import logging
from ..models import Persona, Curso, Materia, SentralizadoNota, Pago, Asistencia, Gestion, CobroPago
from .ai_service import ReportAI

logger = logging.getLogger(__name__)

class ReportEngine:
    def __init__(self):
        self.ai_service = ReportAI()
    
    def execute_report(self, user_prompt, filters=None, include_charts=True):
        """
        Ejecuta un reporte completo basado en el prompt del usuario
        """
        filters = filters or {}
        
        try:
            # Obtener interpretación de la IA
            available_data = self._get_available_data_context()
            interpretation = self.ai_service.interpret_prompt(user_prompt, available_data)
            
            # Aplicar filtros adicionales de la interpretación
            combined_filters = {**filters, **interpretation.get('filtros', {})}
            
            # Ejecutar consulta basada en la interpretación
            data = self._execute_query(interpretation, combined_filters)
            
            # Validar que hay datos
            if not self._has_valid_data(data):
                return self._generate_empty_report(user_prompt, interpretation)
            
            # Agregar datos para gráficos si está solicitado
            if include_charts and self._is_chart_compatible(interpretation, data):
                try:
                    data['chart_data'] = self._generate_chart_data(interpretation, data)
                except Exception as e:
                    logger.warning(f"Error generando gráficos: {str(e)}")
                    data['chart_data'] = {}
            
            # Generar narrativa con manejo de errores individual
            try:
                narrative = self.ai_service.generate_narrative_report(data, user_prompt)
            except Exception as e:
                logger.warning(f"Error generando narrativa con IA: {str(e)}")
                narrative = self._generate_fallback_narrative(data, user_prompt, interpretation)
            
            # Generar insights con manejo de errores individual
            try:
                insights = self.ai_service.generate_insights(data, interpretation)
            except Exception as e:
                logger.warning(f"Error generando insights con IA: {str(e)}")
                insights = self._generate_fallback_insights(data, interpretation)
            
            # Enriquecer con metadatos
            metadata = self._generate_metadata(data, interpretation)
            
            return {
                'interpretation': interpretation,
                'data': data,
                'narrative': narrative,
                'insights': insights,
                'metadata': metadata,
                'format': 'text' if interpretation['formato_salida'] == 'texto' else 'structured',
                'generated_at': datetime.now().isoformat(),
                'chart_types': list(data.get('chart_data', {}).keys()) if include_charts else [],
                'status': 'success',
                'ai_status': 'full' if self.ai_service.model else 'fallback'
            }
            
        except Exception as e:
            logger.error(f"Error ejecutando reporte: {str(e)}")
            return self._generate_error_report(user_prompt, str(e))

    def _generate_fallback_narrative(self, data, prompt, interpretation):
        """Genera narrativa de respaldo cuando falla la IA"""
        report_type = interpretation.get('tipo_reporte', 'reporte_general')
        
        narrative = f"# 📊 Reporte de {report_type.replace('_', ' ').title()}\n\n"
        narrative += f"**Consulta procesada:** {prompt}\n\n"
        
        # Resumen ejecutivo basado en métricas
        if data.get('metricas'):
            narrative += "## 📈 Resumen Ejecutivo\n\n"
            metrics = data['metricas']
            
            if report_type == 'analisis_notas':
                narrative += f"- **Promedio General:** {metrics.get('promedio_general', 'N/A')}\n"
                narrative += f"- **Estudiantes Analizados:** {metrics.get('total_estudiantes', 0)}\n"
                narrative += f"- **Tasa de Aprobación:** {metrics.get('tasa_aprobacion', 0)}%\n"
                narrative += f"- **Rango de Notas:** {metrics.get('rango_notas', 'N/A')}\n"
                
            elif report_type == 'estado_pagos':
                narrative += f"- **Total Recaudado:** ${metrics.get('total_recaudado', 0):.2f}\n"
                narrative += f"- **Pendiente por Cobrar:** ${metrics.get('total_pendiente', 0):.2f}\n"
                narrative += f"- **Pagos Realizados:** {metrics.get('pagos_realizados', 0)}\n"
                narrative += f"- **Pagos Pendientes:** {metrics.get('pagos_pendientes', 0)}\n"
                
            elif report_type == 'asistencias':
                narrative += f"- **Tasa de Asistencia:** {metrics.get('tasa_asistencia', 0)}%\n"
                narrative += f"- **Registros Analizados:** {metrics.get('total_registros', 0)}\n"
                narrative += f"- **Tasa de Puntualidad:** {metrics.get('tasa_puntualidad', 0)}%\n"
        
        # Hallazgos principales
        narrative += "\n## 🔍 Hallazgos Principales\n\n"
        
        if data.get('detalles'):
            total_records = len(data['detalles'])
            narrative += f"- Se analizaron **{total_records}** registros que coinciden con los criterios de búsqueda.\n"
            
            # Hallazgos específicos por tipo de reporte
            if report_type == 'analisis_notas':
                aprobados = data['metricas'].get('aprobados', 0)
                reprobados = data['metricas'].get('reprobados', 0)
                if aprobados > reprobados:
                    narrative += "- La mayoría de los estudiantes tienen un rendimiento satisfactorio.\n"
                else:
                    narrative += "- Se detectó una proporción significativa de estudiantes con bajo rendimiento.\n"
                    
            elif report_type == 'estado_pagos':
                pendientes = data['metricas'].get('pagos_pendientes', 0)
                if pendientes > 0:
                    narrative += f"- Existen **{pendientes}** pagos pendientes que requieren atención.\n"
                else:
                    narrative += "- Todos los pagos están al día.\n"
                    
        else:
            narrative += "- No se encontraron registros específicos con los filtros aplicados.\n"
        
        # Análisis detallado
        narrative += "\n## 📋 Análisis Detallado\n\n"
        narrative += "El sistema ha procesado la información solicitada utilizando los filtros:\n"
        
        # Usar filtros aplicados de los datos
        filtros_aplicados = data.get('filtros_aplicados', {})
        if filtros_aplicados:
            for key, value in filtros_aplicados.items():
                if value:  # Solo mostrar filtros con valores
                    narrative += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        else:
            narrative += "- Sin filtros específicos aplicados (análisis general)\n"
        
        # Recomendaciones
        narrative += "\n## 💡 Recomendaciones\n\n"
        
        if report_type == 'analisis_notas':
            narrative += "1. **Revisar estudiantes con bajo rendimiento** para implementar planes de mejora\n"
            narrative += "2. **Analizar materias con promedios bajos** para optimizar estrategias de enseñanza\n"
            narrative += "3. **Comparar rendimiento entre cursos** para identificar mejores prácticas\n"
            
        elif report_type == 'estado_pagos':
            narrative += "1. **Contactar estudiantes con pagos pendientes** para regularizar su situación\n"
            narrative += "2. **Implementar recordatorios automáticos** para pagos próximos a vencer\n"
            narrative += "3. **Revisar servicios con mayor morosidad** para ajustar políticas de pago\n"
            
        elif report_type == 'asistencias':
            narrative += "1. **Investigar causas de ausentismo** en estudiantes con baja asistencia\n"
            narrative += "2. **Implementar programa de incentivos** para mejorar la puntualidad\n"
            narrative += "3. **Monitorear tendencias de asistencia** por curso y materia\n"
        
        else:
            narrative += "1. **Utilizar filtros específicos** para obtener análisis más detallados\n"
            narrative += "2. **Explorar diferentes tipos de reportes** para diversas perspectivas\n"
            narrative += "3. **Contactar al administrador** para consultas específicas o personalizadas\n"
        
        narrative += f"\n---\n*Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}*"
        
        return narrative

    def _generate_fallback_insights(self, data, interpretation):
        """Genera insights básicos cuando falla la IA"""
        insights = []
        report_type = interpretation.get('tipo_reporte', 'reporte_general')
        metrics = data.get('metricas', {})
        
        # Insights para análisis de notas
        if report_type == 'analisis_notas':
            promedio = metrics.get('promedio_general', 0)
            aprobados = metrics.get('aprobados', 0)
            total = metrics.get('total_estudiantes', 0)
            
            if promedio >= 70:
                insights.append({
                    "titulo": "Rendimiento académico satisfactorio",
                    "descripcion": f"El promedio general de {promedio} puntos indica un buen nivel académico en el grupo analizado.",
                    "tipo": "positivo",
                    "impacto": "medio",
                    "recomendacion": "Mantener las estrategias pedagógicas actuales y reconocer el buen desempeño del estudiantado."
                })
            else:
                insights.append({
                    "titulo": "Oportunidad de mejora académica",
                    "descripcion": f"El promedio general de {promedio} puntos sugiere áreas de oportunidad para mejorar el rendimiento.",
                    "tipo": "oportunidad",
                    "impacto": "alto",
                    "recomendacion": "Implementar programas de reforzamiento y tutorías personalizadas."
                })
            
            if total > 0:
                tasa_aprobacion = (aprobados / total) * 100
                if tasa_aprobacion >= 80:
                    insights.append({
                        "titulo": "Alta tasa de aprobación",
                        "descripcion": f"El {tasa_aprobacion:.1f}% de los estudiantes aprobaron, indicando efectividad en el proceso de enseñanza.",
                        "tipo": "positivo",
                        "impacto": "medio",
                        "recomendacion": "Documentar y replicar las estrategias exitosas en otros cursos."
                    })
        
        # Insights para estado de pagos
        elif report_type == 'estado_pagos':
            pendientes = metrics.get('pagos_pendientes', 0)
            total_recaudado = metrics.get('total_recaudado', 0)
            
            if pendientes > 0:
                insights.append({
                    "titulo": "Atención requerida en pagos pendientes",
                    "descripcion": f"Existen {pendientes} pagos pendientes que afectan la gestión financiera.",
                    "tipo": "negativo",
                    "impacto": "alto",
                    "recomendacion": "Establecer un plan de cobranza y contactar a los deudores."
                })
            else:
                insights.append({
                    "titulo": "Excelente gestión de pagos",
                    "descripcion": "Todos los pagos están al corriente, reflejando una buena administración financiera.",
                    "tipo": "positivo",
                    "impacto": "medio",
                    "recomendacion": "Mantener los procesos actuales de seguimiento de pagos."
                })
            
            if total_recaudado > 0:
                insights.append({
                    "titulo": "Flujo de caja positivo",
                    "descripcion": f"Se ha recaudado ${total_recaudado:,.2f}, indicando una situación financiera estable.",
                    "tipo": "positivo",
                    "impacto": "alto",
                    "recomendacion": "Continuar con las estrategias de recaudación actuales."
                })
        
        # Insights para asistencias
        elif report_type == 'asistencias':
            tasa_asistencia = metrics.get('tasa_asistencia', 0)
            ausentes = metrics.get('tasa_ausentismo', 0)
            
            if tasa_asistencia >= 90:
                insights.append({
                    "titulo": "Excelente asistencia estudiantil",
                    "descripcion": f"Una tasa de asistencia del {tasa_asistencia}% refleja alto compromiso y participación.",
                    "tipo": "positivo",
                    "impacto": "alto",
                    "recomendacion": "Reconocer y premiar la asistencia ejemplar."
                })
            elif tasa_asistencia < 80:
                insights.append({
                    "titulo": "Preocupación por asistencia",
                    "descripcion": f"La tasa de asistencia del {tasa_asistencia}% está por debajo del estándar esperado.",
                    "tipo": "negativo",
                    "impacto": "alto",
                    "recomendacion": "Investigar causas y establecer plan de mejora de asistencia."
                })
            
            if ausentes > 10:
                insights.append({
                    "titulo": "Ausentismo significativo detectado",
                    "descripcion": f"El {ausentes}% de ausencias requiere atención inmediata.",
                    "tipo": "negativo",
                    "impacto": "medio",
                    "recomendacion": "Contactar a estudiantes con alta tasa de ausencias y sus familias."
                })
        
        # Insight general si no hay específicos o para reportes generales
        if not insights:
            total_records = len(data.get('detalles', []))
            insights.append({
                "titulo": "Análisis completado exitosamente",
                "descripcion": f"Se procesaron {total_records} registros según los criterios establecidos.",
                "tipo": "neutro",
                "impacto": "bajo",
                "recomendacion": "Utilizar filtros específicos para obtener análisis más detallados."
            })
        
        # Siempre agregar insight sobre uso de filtros
        if data.get('filtros_aplicados'):
            insights.append({
                "titulo": "Filtros aplicados correctamente",
                "descripcion": "Los filtros especificados han refinado adecuadamente los resultados.",
                "tipo": "positivo",
                "impacto": "medio",
                "recomendacion": "Experimentar con diferentes combinaciones de filtros para nuevos insights."
            })
        
        return insights

    def analyze_trends(self, report_type, time_range='current_year'):
        """
        Análisis de tendencias mejorado con Vertex AI
        """
        try:
            # Obtener datos históricos
            historical_data = self._get_historical_data(report_type, time_range)
            
            if not historical_data:
                return {
                    "error": "No hay datos históricos para el análisis",
                    "suggestion": "Intenta con un rango de tiempo diferente o verifica la base de datos"
                }
            
            # Preparar prompt para análisis de tendencias
            trend_prompt = f"""
            Analiza las siguientes tendencias en datos educativos y proporciona insights en español:
            
            TIPO DE ANÁLISIS: {report_type}
            PERIODO: {time_range}
            DATOS: {json.dumps(historical_data, indent=2, ensure_ascii=False)}
            
            Proporciona un análisis en formato JSON con esta estructura:
            {{
                "tendencias_principales": [
                    {{
                        "nombre": "Nombre de la tendencia",
                        "descripcion": "Descripción detallada",
                        "direccion": "creciente|decreciente|estable",
                        "magnitud": "alta|media|baja"
                    }}
                ],
                "patrones_detectados": [
                    {{
                        "patron": "Descripción del patrón",
                        "frecuencia": "constante|estacional|esporádico",
                        "impacto": "alto|medio|bajo"
                    }}
                ],
                "recomendaciones": [
                    {{
                        "categoria": "academico|financiero|operativo",
                        "accion": "Acción específica recomendada",
                        "prioridad": "alta|media|baja"
                    }}
                ],
                "alertas": [
                    {{
                        "tipo": "oportunidad|riesgo|observacion",
                        "descripcion": "Descripción de la alerta",
                        "urgencia": "inmediata|media|baja"
                    }}
                ]
            }}
            """
            
            # Usar Vertex AI para análisis de tendencias
            analysis_text = self.ai_service._call_vertex_ai(
                trend_prompt,
                "Eres un analista de tendencias educativas experto. Proporciona análisis detallados y accionables.",
                temperature=0.3,
                max_tokens=1200
            )
            
            # Procesar respuesta
            try:
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    trend_data = json.loads(analysis_text[json_start:json_end])
                else:
                    trend_data = {"analisis_textual": analysis_text}
            except json.JSONDecodeError as e:
                logger.warning(f"No se pudo parsear JSON de tendencias: {e}")
                trend_data = {"analisis_textual": analysis_text}
            
            # Enriquecer con datos crudos para referencia
            trend_data['datos_historicos'] = historical_data
            trend_data['periodo_analizado'] = time_range
            trend_data['tipo_analisis'] = report_type
            trend_data['generado_en'] = datetime.now().isoformat()
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error analizando tendencias: {str(e)}")
            return {
                "error": f"Error en análisis de tendencias: {str(e)}",
                "suggestion": "Verifica la configuración de Vertex AI y la disponibilidad de datos"
            }

    # ------------------ Métodos de Validación ------------------
    def _has_valid_data(self, data):
        """Valida que los datos contengan información útil"""
        if not data:
            return False
        
        # Verificar si hay detalles
        if data.get('detalles') and len(data['detalles']) > 0:
            return True
        
        # Verificar si hay métricas con valores significativos
        if data.get('metricas'):
            for key, value in data['metricas'].items():
                if value and value != 0:
                    return True
        
        # Verificar otros tipos de datos
        for key in ['pagos', 'asistencias', 'resumen']:
            if data.get(key) and len(data[key]) > 0:
                return True
        
        return False

    def _is_chart_compatible(self, interpretation, data):
        """Determina si los datos son compatibles con gráficos"""
        report_type = interpretation['tipo_reporte']
        has_structured_data = any(key in data for key in ['detalles', 'pagos', 'asistencias'])
        has_metrics = any(key in data for key in ['metricas', 'resumen'])
        
        # Verificar que hay suficiente data para gráficos
        if has_structured_data and data.get('detalles'):
            return len(data['detalles']) > 0
        elif has_metrics and data.get('metricas'):
            return len(data['metricas']) > 0
        
        return has_structured_data and has_metrics

    def _generate_empty_report(self, user_prompt, interpretation):
        """Genera un reporte para cuando no hay datos"""
        return {
            'interpretation': interpretation,
            'data': {
                'detalles': [],
                'metricas': {
                    'total_registros': 0,
                    'mensaje': 'No se encontraron datos con los criterios especificados'
                }
            },
            'narrative': f"No se encontraron datos que coincidan con tu solicitud: '{user_prompt}'. Por favor, intenta con diferentes filtros o criterios.",
            'insights': [
                {
                    'titulo': 'Sin datos disponibles',
                    'descripcion': 'No se encontraron registros que coincidan con los criterios de búsqueda.',
                    'tipo': 'neutro',
                    'impacto': 'bajo',
                    'recomendacion': 'Prueba ajustando los filtros o verificando la disponibilidad de datos.'
                }
            ],
            'metadata': {
                'registros_encontrados': 0,
                'filtros_aplicados': interpretation.get('filtros', {}),
                'sugerencia': 'Verifica los filtros o amplía el criterio de búsqueda'
            },
            'format': 'text',
            'generated_at': datetime.now().isoformat(),
            'chart_types': [],
            'status': 'empty'
        }

    def _generate_error_report(self, user_prompt, error_message):
        """Genera un reporte de error"""
        return {
            'error': 'Error generando el reporte',
            'details': error_message,
            'narrative': f"Lo siento, hubo un error al procesar tu solicitud: '{user_prompt}'. Error: {error_message}",
            'insights': [],
            'generated_at': datetime.now().isoformat(),
            'status': 'error',
            'suggestion': 'Por favor, intenta nuevamente o contacta al administrador del sistema.'
        }

    def _generate_metadata(self, data, interpretation):
        """Genera metadatos útiles sobre el reporte"""
        metadata = {
            'tipo_reporte': interpretation['tipo_reporte'],
            'entidades_analizadas': interpretation['entidades'],
            'metricas_calculadas': interpretation['metricas'],
            'timestamp_generacion': datetime.now().isoformat()
        }
        
        # Agregar conteos de registros
        if data.get('detalles'):
            metadata['total_registros'] = len(data['detalles'])
        if data.get('pagos'):
            metadata['total_pagos'] = len(data['pagos'])
        if data.get('asistencias'):
            metadata['total_asistencias'] = len(data['asistencias'])
        
        # Agregar resumen de métricas
        if data.get('metricas'):
            metadata['resumen_metricas'] = {
                k: v for k, v in data['metricas'].items() 
                if isinstance(v, (int, float)) and v > 0
            }
        
        return metadata

    # ------------------ Generación de Gráficos Mejorada ------------------
    def _generate_chart_data(self, interpretation, data):
        """Genera datos para gráficos basados en la interpretación y datos"""
        chart_data = {}
        report_type = interpretation['tipo_reporte']
        
        try:
            if report_type == 'analisis_notas':
                chart_data.update(self._generate_grade_charts(data))
            elif report_type == 'estado_pagos':
                chart_data.update(self._generate_payment_charts(data))
            elif report_type == 'asistencias':
                chart_data.update(self._generate_attendance_charts(data))
            elif report_type == 'tendencias':
                chart_data.update(self._generate_trend_charts(data))
            elif report_type == 'reporte_general':
                chart_data.update(self._generate_general_charts(data))
            
            # Agregar gráficos adicionales si hay datos suficientes
            self._enrich_with_additional_charts(chart_data, data, interpretation)
            
        except Exception as e:
            logger.error(f"Error generando gráficos: {str(e)}")
            chart_data['error'] = f"No se pudieron generar gráficos: {str(e)}"
        
        return chart_data

    def _generate_grade_charts(self, data):
        """Genera gráficos para análisis de notas"""
        detalles = data.get('detalles', [])
        if not detalles:
            return {}
        
        chart_data = {}
        
        # 1. Distribución de notas (histograma)
        note_ranges = {'0-50': 0, '51-60': 0, '61-70': 0, '71-80': 0, '81-90': 0, '91-100': 0}
        for item in detalles:
            promedio = item.get('promedio_anual', 0)
            for range_key in note_ranges.keys():
                min_val, max_val = map(int, range_key.split('-'))
                if min_val <= promedio <= max_val:
                    note_ranges[range_key] += 1
        
        chart_data['distribucion_notas'] = {
            'title': 'Distribución de Notas',
            'labels': list(note_ranges.keys()),
            'datasets': [{
                'label': 'Cantidad de Estudiantes',
                'data': list(note_ranges.values()),
                'backgroundColor': [
                    '#FF6384', '#36A2EB', '#FFCE56', 
                    '#4BC0C0', '#9966FF', '#FF9F40'
                ]
            }]
        }
        
        # 2. Aprobados vs Reprobados
        status_count = {'Aprobados': 0, 'Reprobados': 0, 'En Proceso': 0}
        for item in detalles:
            estado = item.get('estado', 'En Proceso')
            if estado == 'Aprobado':
                status_count['Aprobados'] += 1
            elif estado == 'Reprobado':
                status_count['Reprobados'] += 1
            else:
                status_count['En Proceso'] += 1
        
        chart_data['estado_academico'] = {
            'title': 'Estado Académico',
            'labels': list(status_count.keys()),
            'datasets': [{
                'data': list(status_count.values()),
                'backgroundColor': ['#4BC0C0', '#FF6384', '#FFCE56']
            }]
        }
        
        return chart_data

    def _generate_payment_charts(self, data):
        """Genera gráficos para estado de pagos"""
        pagos = data.get('pagos', [])
        if not pagos:
            return {}
        
        chart_data = {}
        
        # 1. Estado de pagos
        status_count = {}
        for pago in pagos:
            estado = pago.get('estado', 'Desconocido')
            status_count[estado] = status_count.get(estado, 0) + 1
        
        chart_data['estado_pagos'] = {
            'title': 'Estado de Pagos',
            'labels': list(status_count.keys()),
            'datasets': [{
                'data': list(status_count.values()),
                'backgroundColor': ['#4BC0C0', '#FF6384', '#FFCE56', '#9966FF']
            }]
        }
        
        return chart_data

    def _generate_attendance_charts(self, data):
        """Genera gráficos para análisis de asistencias"""
        asistencias = data.get('asistencias', [])
        resumen = data.get('resumen', {})
        if not asistencias:
            return {}
        
        chart_data = {}
        
        # 1. Distribución general de asistencias
        attendance_data = {
            'Presente': resumen.get('presentes', 0),
            'Ausente': resumen.get('ausentes', 0),
            'Tarde': resumen.get('tardes', 0)
        }

        chart_data['distribucion_asistencias'] = {
            'title': 'Distribución de Asistencias',
            'labels': list(attendance_data.keys()),
            'datasets': [{
                'data': list(attendance_data.values()),
                'backgroundColor': ['#4BC0C0', '#FF6384', '#FFCE56']
            }]
        }
        
        return chart_data

    def _generate_trend_charts(self, data):
        """Genera gráficos para análisis de tendencias"""
        return {
            'tendencias_generales': {
                'title': 'Análisis de Tendencias',
                'labels': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
                'datasets': [{
                    'label': 'Tendencia',
                    'data': [65, 59, 80, 81, 56, 72],
                    'borderColor': '#FF6384',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)'
                }]
            }
        }

    def _generate_general_charts(self, data):
        """Genera gráficos para reportes generales"""
        metricas = data.get('metricas', {})
        chart_data = {}
        
        if metricas:
            # Gráfico de métricas principales
            metricas_principales = {k: v for k, v in metricas.items() 
                                  if isinstance(v, (int, float)) and v > 0}
            
            if len(metricas_principales) > 0:
                chart_data['metricas_principales'] = {
                    'title': 'Métricas Principales',
                    'labels': [k.replace('_', ' ').title() for k in metricas_principales.keys()],
                    'datasets': [{
                        'label': 'Valores',
                        'data': list(metricas_principales.values()),
                        'backgroundColor': '#4BC0C0'
                    }]
                }
        
        return chart_data

    def _enrich_with_additional_charts(self, chart_data, data, interpretation):
        """Enriquece con gráficos adicionales basados en datos específicos"""
        pass

    # ------------------ Contexto de datos ------------------
    def _get_available_data_context(self):
        """Proporciona contexto sobre los datos disponibles para la IA"""
        return {
            "estudiantes": {
                "descripcion": "Datos de estudiantes con información personal y académica",
                "campos": ["nombre", "apellido", "curso", "gestion"]
            },
            "cursos": {
                "descripcion": "Cursos disponibles con estudiantes inscritos",
                "ejemplos": ["Primero A", "Segundo B", "Tercero C"]
            },
            "materias": {
                "descripcion": "Materias con sistema de notas por trimestre",
                "ejemplos": ["Matemáticas", "Lenguaje", "Ciencias"]
            },
            "notas": {
                "descripcion": "Sistema de calificaciones por trimestre y promedio anual",
                "campos": ["t1_promedio", "t2_promedio", "t3_promedio", "promedio_anual", "estado_academico"]
            },
            "pagos": {
                "descripcion": "Sistema de pagos y cobros con estados y montos",
                "campos": ["servicio", "monto_pagado", "estado", "fecha_pago"]
            },
            "asistencias": {
                "descripcion": "Registro de asistencias por materia con estados Presente/Ausente/Tarde",
                "campos": ["estado", "fecha", "curso", "materia"]
            },
            "gestiones": {
                "descripcion": "Años académicos o periodos de gestión",
                "ejemplos": ["2023", "2024", "2025"]
            },
            "metricas_comunes": [
                "promedios", "totales", "porcentajes", "tendencias", 
                "comparativas", "distribuciones", "estadisticas"
            ]
        }

    # ------------------ Ejecución de Consultas Mejorada ------------------
    def _execute_query(self, interpretation, filters):
        """Ejecuta consultas basadas en la interpretación y filtros"""
        report_type = interpretation['tipo_reporte']
        
        try:
            if report_type == 'analisis_notas':
                return self._get_grade_analysis(filters)
            elif report_type == 'estado_pagos':
                return self._get_payment_status(filters)
            elif report_type == 'asistencias':
                return self._get_attendance_report(filters)
            elif report_type == 'tendencias':
                return self._get_trend_analysis(filters)
            elif report_type == 'reporte_general':
                return self._get_general_report(filters)
            else:
                return self._get_general_report(filters)
                
        except Exception as e:
            logger.error(f"Error ejecutando consulta para {report_type}: {str(e)}")
            return {'error': f"Error en consulta: {str(e)}", 'detalles': []}

    def _get_grade_analysis(self, filters):
        """Análisis de notas con filtros mejorados"""
        queryset = SentralizadoNota.objects.select_related(
            'persona', 'curso', 'materia', 'gestion'
        ).filter(promedio_anual__isnull=False)
        
        # Aplicar filtros
        queryset = self._apply_filters(queryset, filters)
        
        results = []
        for nota in queryset:
            results.append({
                'estudiante': str(nota.persona),
                'curso': nota.curso.nombre if nota.curso else 'Sin curso',
                'materia': nota.materia.nombre if nota.materia else 'Sin materia',
                'gestion': nota.gestion.nombre if nota.gestion else 'Sin gestión',
                'promedio_anual': float(nota.promedio_anual or 0),
                'estado': nota.estado_academico or 'En Proceso',
                't1_promedio': float(nota.t1_promedio or 0),
                't2_promedio': float(nota.t2_promedio or 0),
                't3_promedio': float(nota.t3_promedio or 0),
                'id_estudiante': nota.persona.id,
                'id_curso': nota.curso.id if nota.curso else None,
                'id_materia': nota.materia.id if nota.materia else None
            })
        
        # Calcular métricas
        promedios = [r['promedio_anual'] for r in results if r['promedio_anual'] > 0]
        total_estudiantes = len(results)
        
        if promedios:
            promedio_general = sum(promedios) / len(promedios)
            max_promedio = max(promedios)
            min_promedio = min(promedios)
            aprobados = len([r for r in results if r['estado'] == 'Aprobado'])
            reprobados = len([r for r in results if r['estado'] == 'Reprobado'])
            en_proceso = len([r for r in results if r['estado'] == 'En Proceso'])
            tasa_aprobacion = (aprobados / total_estudiantes * 100) if total_estudiantes > 0 else 0
        else:
            promedio_general = max_promedio = min_promedio = tasa_aprobacion = 0
            aprobados = reprobados = en_proceso = 0

        metricas = {
            'total_estudiantes': total_estudiantes,
            'promedio_general': round(promedio_general, 2),
            'nota_maxima': round(max_promedio, 2),
            'nota_minima': round(min_promedio, 2),
            'aprobados': aprobados,
            'reprobados': reprobados,
            'en_proceso': en_proceso,
            'tasa_aprobacion': round(tasa_aprobacion, 2),
            'rango_notas': f"{round(min_promedio, 2)} - {round(max_promedio, 2)}"
        }
        
        return {
            'detalles': results, 
            'metricas': metricas,
            'filtros_aplicados': filters
        }

    def _get_payment_status(self, filters):
        """Estado de pagos con análisis mejorado"""
        queryset = CobroPago.objects.select_related('persona', 'cobro')
        queryset = self._apply_filters(queryset, filters, payment_filters=True)
        
        detalles = []
        total_recaudado = 0
        total_pendiente = 0
        
        for pago in queryset:
            monto = float(pago.monto_pagado or 0)
            estado = pago.estado or 'Pendiente'
            
            if estado == 'Pagado':
                total_recaudado += monto
            else:
                total_pendiente += monto
            
            detalles.append({
                'estudiante': str(pago.persona) if pago.persona else 'Sin persona',
                'servicio': pago.cobro.detalle if pago.cobro else 'Servicio no especificado',
                'monto_pagado': monto,
                'estado': estado,
                'fecha_pago': pago.fecha_pago.isoformat() if pago.fecha_pago else None,
                'id_estudiante': pago.persona.id if pago.persona else None,
                'metodo_pago': 'No especificado'
            })
        
        metricas = {
            'total_pagos': len(detalles),
            'total_recaudado': round(total_recaudado, 2),
            'total_pendiente': round(total_pendiente, 2),
            'pagos_realizados': len([p for p in detalles if p['estado'] == 'Pagado']),
            'pagos_pendientes': len([p for p in detalles if p['estado'] == 'Pendiente']),
            'promedio_pago': round(total_recaudado / len([p for p in detalles if p['estado'] == 'Pagado']), 2) 
                            if len([p for p in detalles if p['estado'] == 'Pagado']) > 0 else 0
        }
        
        return {
            'pagos': detalles, 
            'metricas': metricas,
            'resumen': {
                'recaudacion_total': total_recaudado,
                'deuda_total': total_pendiente
            }
        }

    def _get_attendance_report(self, filters):
        """Reporte de asistencias mejorado"""
        queryset = Asistencia.objects.select_related('alumno', 'curso', 'materia')
        queryset = self._apply_filters(queryset, filters, attendance_filters=True)
        
        detalles = []
        resumen = {'presentes': 0, 'ausentes': 0, 'tardes': 0, 'total': 0}
        
        for asistencia in queryset:
            estado = asistencia.estado or 'Ausente'
            detalles.append({
                'estudiante': str(asistencia.alumno),
                'curso': asistencia.curso.nombre if asistencia.curso else 'Sin curso',
                'materia': asistencia.materia.nombre if asistencia.materia else 'Sin materia',
                'estado': estado,
                'fecha': asistencia.fecha.isoformat() if asistencia.fecha else None,
                'id_estudiante': asistencia.alumno.id,
                'id_curso': asistencia.curso.id if asistencia.curso else None
            })
            
            # Actualizar resumen
            resumen['total'] += 1
            if estado == 'Presente':
                resumen['presentes'] += 1
            elif estado == 'Ausente':
                resumen['ausentes'] += 1
            elif estado == 'Tarde':
                resumen['tardes'] += 1
        
        # Calcular porcentajes
        if resumen['total'] > 0:
            resumen['porcentaje_presentes'] = round((resumen['presentes'] / resumen['total']) * 100, 2)
            resumen['porcentaje_ausentes'] = round((resumen['ausentes'] / resumen['total']) * 100, 2)
            resumen['porcentaje_tardes'] = round((resumen['tardes'] / resumen['total']) * 100, 2)
        
        metricas = {
            'total_registros': resumen['total'],
            'tasa_asistencia': resumen.get('porcentaje_presentes', 0),
            'tasa_ausentismo': resumen.get('porcentaje_ausentes', 0),
            'tasa_puntualidad': 100 - resumen.get('porcentaje_tardes', 0)
        }
        
        return {
            'asistencias': detalles, 
            'resumen': resumen,
            'metricas': metricas
        }

    def _get_trend_analysis(self, filters):
        """Análisis de tendencias temporales"""
        # Implementar análisis de tendencias con datos históricos
        return {
            'detalles': [],
            'metricas': {
                'mensaje': 'Análisis de tendencias en desarrollo',
                'periodo_analizado': filters.get('periodo', 'Último año')
            }
        }

    def _get_general_report(self, filters):
        """Reporte general del sistema"""
        total_estudiantes = Persona.objects.filter(rol='Alumno').count()
        total_cursos = Curso.objects.count()
        total_materias = Materia.objects.count()
        total_gestiones = Gestion.objects.count()
        
        # Estadísticas recientes
        from django.utils import timezone
        last_month = timezone.now() - timedelta(days=30)
        
        estudiantes_recientes = Persona.objects.filter(
            created_at__gte=last_month
        ).count() if hasattr(Persona, 'created_at') else 0
        
        metricas = {
            'total_estudiantes': total_estudiantes,
            'total_cursos': total_cursos,
            'total_materias': total_materias,
            'total_gestiones': total_gestiones,
            'estudiantes_recientes': estudiantes_recientes,
            'promedio_estudiantes_por_curso': round(total_estudiantes / total_cursos, 2) if total_cursos > 0 else 0
        }
        
        return {
            'detalles': [{
                'total_estudiantes': total_estudiantes,
                'total_cursos': total_cursos,
                'total_materias': total_materias,
                'total_gestiones': total_gestiones
            }],
            'metricas': metricas,
            'resumen': {
                'sistema_activo': True,
                'ultima_actualizacion': datetime.now().isoformat()
            }
        }

    def _apply_filters(self, queryset, filters, payment_filters=False, attendance_filters=False):
        """Aplica filtros a los querysets de manera genérica"""
        
        # Filtros para cursos
        if filters.get('curso'):
            if hasattr(queryset.model, 'curso'):
                queryset = queryset.filter(curso__nombre__icontains=filters['curso'])
        
        # Filtros para gestión
        if filters.get('gestion'):
            if hasattr(queryset.model, 'gestion'):
                queryset = queryset.filter(gestion__nombre__icontains=filters['gestion'])
        
        # Filtros para materia
        if filters.get('materia'):
            if hasattr(queryset.model, 'materia'):
                queryset = queryset.filter(materia__nombre__icontains=filters['materia'])
        
        # Filtros para estudiante/persona
        if filters.get('estudiante'):
            if hasattr(queryset.model, 'persona'):
                queryset = queryset.filter(
                    Q(persona__nombre__icontains=filters['estudiante']) |
                    Q(persona__apellido_paterno__icontains=filters['estudiante'])
                )
            elif hasattr(queryset.model, 'alumno'):
                queryset = queryset.filter(
                    Q(alumno__nombre__icontains=filters['estudiante']) |
                    Q(alumno__apellido_paterno__icontains=filters['estudiante'])
                )
        
        # Filtros específicos para pagos
        if payment_filters:
            if filters.get('estado_pago'):
                queryset = queryset.filter(estado__icontains=filters['estado_pago'])
            if filters.get('servicio'):
                queryset = queryset.filter(cobro__detalle__icontains=filters['servicio'])
        
        # Filtros específicos para asistencias
        if attendance_filters:
            if filters.get('estado_asistencia'):
                queryset = queryset.filter(estado__icontains=filters['estado_asistencia'])
            if filters.get('fecha_desde'):
                queryset = queryset.filter(fecha__gte=filters['fecha_desde'])
            if filters.get('fecha_hasta'):
                queryset = queryset.filter(fecha__lte=filters['fecha_hasta'])
        
        return queryset

    def _get_historical_data(self, report_type, time_range):
        """
        Obtiene datos históricos para análisis de tendencias
        """
        try:
            historical_data = {}
            
            # Definir rango de fechas basado en time_range
            end_date = datetime.now()
            if time_range == 'current_year':
                start_date = end_date.replace(month=1, day=1)
            elif time_range == 'last_3_years':
                start_date = end_date.replace(year=end_date.year - 3)
            elif time_range == 'last_5_years':
                start_date = end_date.replace(year=end_date.year - 5)
            else:  # last_year por defecto
                start_date = end_date.replace(year=end_date.year - 1)
            
            if report_type == 'academic_performance':
                # Datos de rendimiento académico histórico por gestión
                from django.db.models import Case, When, FloatField
                
                notas_historicas = SentralizadoNota.objects.filter(
                    fecha_registro__gte=start_date
                ).values('gestion__nombre').annotate(
                    promedio_general=Avg('promedio_anual'),
                    tasa_aprobacion=Avg(
                        Case(
                            When(estado_academico='Aprobado', then=1),
                            When(estado_academico='Reprobado', then=0),
                            default=0,
                            output_field=FloatField()
                        )
                    ) * 100,
                    total_estudiantes=Count('id')
                ).order_by('gestion__nombre')
                
                historical_data['rendimiento_academico'] = list(notas_historicas)
                
            elif report_type == 'financial_trends':
                # Datos financieros históricos
                pagos_historicos = CobroPago.objects.filter(
                    fecha_pago__gte=start_date
                ).extra({
                    'periodo': "TO_CHAR(fecha_pago, 'YYYY-MM')"
                }).values('periodo').annotate(
                    total_recaudado=Sum('monto_pagado'),
                    total_pagos=Count('id'),
                    promedio_pago=Avg('monto_pagado')
                ).order_by('periodo')
                
                historical_data['tendencias_financieras'] = list(pagos_historicos)
            
            elif report_type == 'attendance_patterns':
                # Patrones de asistencia históricos
                asistencias_historicas = Asistencia.objects.filter(
                    fecha__gte=start_date
                ).extra({
                    'mes': "TO_CHAR(fecha, 'YYYY-MM')"
                }).values('mes').annotate(
                    total_registros=Count('id'),
                    presentes=Count('id', filter=Q(estado='Presente')),
                    ausentes=Count('id', filter=Q(estado='Ausente')),
                    tardes=Count('id', filter=Q(estado='Tarde')),
                    tasa_asistencia=Count('id', filter=Q(estado='Presente')) * 100.0 / Count('id')
                ).order_by('mes')
                
                historical_data['patrones_asistencia'] = list(asistencias_historicas)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos: {str(e)}")
            return None
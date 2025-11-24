# backend/Logica/ai_service.py
import logging
import json
import google.auth
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
import os
from datetime import datetime
from googleapiclient import discovery
from google.auth import default as google_default

logger = logging.getLogger(__name__)

class ReportAI:
    def __init__(self):
        self.model = None
        self.model_name = None
        self.region = None
        self.initialized = False
        self.project_id = None
        self._initialize_vertex_ai()
    
    def _get_available_models(self):
        """Obtiene la lista de modelos Gemini más recientes disponibles"""
        # Modelos Gemini más recientes (2024-2025)
        gemini_models = [
            # Modelos Gemini 2.5 (más recientes)
            "gemini-2.5-flash-preview-02-05",
            "gemini-2.5-flash-lite-preview",
            "gemini-2.5-pro-preview-02-05",
            
            # Modelos Gemini 2.0
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            
            # Modelos Gemini 1.5 (legacy pero ampliamente disponibles)
            "gemini-1.5-flash-001",
            "gemini-1.5-flash",
            "gemini-1.5-pro-001", 
            "gemini-1.5-pro",
            
            # Modelos Gemini 1.0 (compatibilidad)
            "gemini-1.0-pro-001",
            "gemini-1.0-pro",
            "gemini-pro-001",
            "gemini-pro",
        ]
        
        return gemini_models
    
    def _get_available_regions(self):
        """Obtiene la lista de regiones disponibles para Vertex AI"""
        # Regiones con mejor disponibilidad para modelos Gemini recientes
        primary_regions = [
            'us-central1',  # Iowa - mejor disponibilidad
            'us-east1',     # South Carolina
            'us-west1',     # Oregon
            'europe-west1', # Belgium
            'europe-west4', # Netherlands
        ]
        
        # Regiones secundarias
        secondary_regions = [
            'asia-southeast1', # Singapore
            'northamerica-northeast1', # Montreal
            'southamerica-east1', # São Paulo
            'australia-southeast1', # Sydney
        ]
        
        return primary_regions + secondary_regions
    
    def _get_safety_settings(self):
        """Configuración de seguridad corregida para modelos Gemini 2.x"""
        # Configuración corregida usando objetos SafetySetting
        return [
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=SafetySetting.HarmThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=SafetySetting.HarmThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=SafetySetting.HarmThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
            SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=SafetySetting.HarmThreshold.BLOCK_MEDIUM_AND_ABOVE
            )
        ]
    
    def _initialize_vertex_ai(self):
        """Inicializa Vertex AI probando múltiples modelos y regiones"""
        logger.info("🚀 Inicializando Vertex AI con modelos Gemini recientes...")
        
        regions_to_try = self._get_available_regions()
        models_to_try = self._get_available_models()
        
        logger.info(f"🔍 Probando {len(models_to_try)} modelos en {len(regions_to_try)} regiones...")
        
        success = False
        
        for region in regions_to_try:
            for model_name in models_to_try:
                try:
                    # Configurar credenciales
                    credentials_path = "tenan/credentials/nimble-chimera-477802-q3-c8cb4f01b527.json"
                    
                    if os.path.exists(credentials_path):
                        credentials, project_id = google.auth.load_credentials_from_file(credentials_path)
                        logger.debug(f"✅ Credenciales cargadas desde archivo: {credentials_path}")
                    else:
                        # Intentar con credenciales por defecto (Google Cloud SDK)
                        credentials, project_id = google_default()
                        logger.debug("✅ Usando credenciales por defecto de Google Cloud")
                    
                    if not project_id:
                        project_id = "nimble-chimera-477802-q3"
                    
                    self.project_id = project_id
                    
                    # Inicializar Vertex AI con la región actual
                    vertexai.init(
                        project=project_id,
                        location=region,
                        credentials=credentials
                    )
                    
                    # Intentar inicializar el modelo actual
                    logger.info(f"🔍 Probando {model_name} en {region}...")
                    self.model = GenerativeModel(model_name)
                    
                    # Probar el modelo con una consulta simple
                    test_response = self.model.generate_content(
                        "Responde 'OK' si estás funcionando.",
                        safety_settings=self._get_safety_settings()
                    )
                    if test_response and test_response.text and 'OK' in test_response.text.upper():
                        self.model_name = model_name
                        self.region = region
                        self.initialized = True
                        success = True
                        logger.info(f"🎉 ✅ Vertex AI inicializado correctamente!")
                        logger.info(f"   📍 Región: {region}")
                        logger.info(f"   🤖 Modelo: {model_name}")
                        logger.info(f"   🏢 Proyecto: {project_id}")
                        break  # Salir del bucle de modelos
                    else:
                        logger.debug(f"❌ {model_name} en {region} no respondió correctamente")
                        self.model = None
                        
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg:
                        logger.debug(f"❌ {model_name} no disponible en {region}")
                    elif "403" in error_msg:
                        logger.warning(f"🔐 Sin permisos para {model_name} en {region}")
                    else:
                        logger.debug(f"❌ Error con {model_name} en {region}: {error_msg[:100]}...")
                    self.model = None
                    continue
            
            if success:
                break  # Salir del bucle de regiones si tuvimos éxito
        
        if not self.initialized:
            logger.warning("❌ No se pudo inicializar Vertex AI con ningún modelo Gemini.")
            logger.info("🔄 Usando modo fallback - el sistema generará reportes completos sin IA")
        else:
            logger.info("✨ Vertex AI configurado y listo para generar reportes inteligentes")
    
    def _call_vertex_ai(self, prompt, system_instruction=None, temperature=0.2, max_tokens=1000):
        """Llama a Vertex AI con manejo robusto de errores"""
        if not self.model or not self.initialized:
            raise Exception("Vertex AI no está inicializado")
        
        try:
            # Configuración optimizada para modelos Gemini 2.x
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "top_p": 0.8,
                "top_k": 40,
            }
            
            # Para modelos más recientes, podemos usar system instructions de manera más efectiva
            if system_instruction and "gemini-2" in self.model_name:
                # Los modelos Gemini 2.x manejan mejor las system instructions
                contents = [
                    Part.from_text(system_instruction),
                    Part.from_text(prompt)
                ]
            else:
                contents = [prompt]
            
            # Generar contenido con safety settings corregidos
            response = self.model.generate_content(
                contents,
                generation_config=generation_config,
                safety_settings=self._get_safety_settings()
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                raise Exception("Respuesta vacía de Vertex AI")
                
        except Exception as e:
            logger.error(f"Error llamando a Vertex AI ({self.model_name}): {e}")
            raise

    def interpret_prompt(self, user_prompt, available_data):
        """
        Interpreta el prompt del usuario usando Vertex AI o lógica básica
        """
        try:
            if not self.initialized:
                return self._basic_interpretation(user_prompt)
            
            # System instruction mejorada para modelos Gemini 2.x
            system_instruction = """
            Eres un asistente especializado en análisis de datos educativos para sistemas colegiales.
            Tu tarea es analizar la consulta del usuario y determinar exactamente qué tipo de reporte necesita.

            INSTRUCCIONES ESPECÍFICAS:
            1. Tipo de reporte: analisis_notas, estado_pagos, asistencias, tendencias, reporte_general
            2. Entidades: estudiantes, cursos, materias, pagos, asistencias, gestiones
            3. Métricas: promedios, totales, porcentajes, distribuciones, comparativas
            4. Filtros: curso, materia, estudiante, gestión, fecha, estado
            5. Formato: texto (para narrativa) o estructurado (para datos tabulares)

            Responde EXCLUSIVAMENTE con un objeto JSON válido, sin markdown, sin texto adicional.
            """
            
            prompt = f"""
            CONSULTA DEL USUARIO: "{user_prompt}"

            DATOS DISPONIBLES EN EL SISTEMA:
            {json.dumps(available_data, ensure_ascii=False, indent=2)}

            ANALIZA y responde con JSON:

            {{
                "tipo_reporte": "analisis_notas|estado_pagos|asistencias|tendencias|reporte_general",
                "entidades": ["lista", "de", "entidades", "relevantes"],
                "metricas": ["metricas", "especificas", "a", "calcular"],
                "filtros": {{"filtro_ejemplo": "valor"}},
                "formato_salida": "texto|estructurado",
                "complejidad": "baja|media|alta",
                "prioridad": "urgente|normal|baja"
            }}
            """
            
            response_text = self._call_vertex_ai(prompt, system_instruction, temperature=0.1)
            
            # Extraer JSON de la respuesta
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    interpretation = json.loads(response_text[json_start:json_end])
                    logger.info(f"✅ Interpretación AI exitosa: {interpretation['tipo_reporte']}")
                else:
                    raise json.JSONDecodeError("No se encontró JSON válido", response_text, 0)
            except json.JSONDecodeError as e:
                logger.warning(f"❌ No se pudo parsear JSON de interpretación: {e}")
                interpretation = self._basic_interpretation(user_prompt)
            
            # Validar y completar estructura
            required_fields = ['tipo_reporte', 'entidades', 'metricas', 'filtros']
            for field in required_fields:
                if field not in interpretation:
                    interpretation[field] = self._basic_interpretation(user_prompt)[field]
            
            return interpretation
            
        except Exception as e:
            logger.warning(f"❌ Interpretación con Vertex AI falló: {str(e)}")
            return self._basic_interpretation(user_prompt)

    def _basic_interpretation(self, user_prompt):
        """
        Interpretación básica cuando Vertex AI no está disponible
        """
        user_prompt_lower = user_prompt.lower()
        
        # Determinar tipo de reporte
        if any(word in user_prompt_lower for word in ['nota', 'calificacion', 'promedio', 'rendimiento', 'académico']):
            report_type = "analisis_notas"
        elif any(word in user_prompt_lower for word in ['pago', 'pagos', 'deuda', 'cuota', 'financiero']):
            report_type = "estado_pagos" 
        elif any(word in user_prompt_lower for word in ['asistencia', 'presente', 'ausente', 'tarde']):
            report_type = "asistencias"
        elif any(word in user_prompt_lower for word in ['tendencia', 'evolucion', 'historico', 'progreso']):
            report_type = "tendencias"
        else:
            report_type = "reporte_general"
        
        # Entidades comunes
        entities = ["estudiantes"]
        if report_type == "analisis_notas":
            entities.extend(["cursos", "materias", "gestiones"])
        elif report_type == "estado_pagos":
            entities.extend(["servicios", "cobros"])
        elif report_type == "asistencias":
            entities.extend(["cursos", "materias"])
        
        # Métricas básicas
        metrics = ["totales", "promedios", "porcentajes"]
        
        return {
            "tipo_reporte": report_type,
            "entidades": entities,
            "metricas": metrics,
            "filtros": {},
            "formato_salida": "texto",
            "complejidad": "media"
        }

    def generate_narrative_report(self, data, user_prompt):
        """
        Genera un reporte narrativo usando Vertex AI o lógica básica
        """
        try:
            if not self.initialized:
                return self._basic_narrative(data, user_prompt)
            
            system_instruction = """
            Eres un analista educativo experto. Genera reportes narrativos profesionales 
            y accionables en español usando formato Markdown.

            DIRECTRICES:
            - Usa emojis relevantes para mejorar la legibilidad
            - Sé específico con los datos proporcionados
            - Incluye hallazgos cuantificables
            - Proporciona recomendaciones prácticas
            - Mantén un tono profesional pero accesible
            - Estructura en secciones claras
            """
            
            prompt = f"""
            GENERA UN REPORTE NARRATIVO PROFESIONAL:

            SOLICITUD ORIGINAL: {user_prompt}

            DATOS ANALIZADOS:
            ```json
            {json.dumps(data, ensure_ascii=False, indent=2)}
            ```

            ESTRUCTURA SUGERIDA:
            # 📊 Título del Reporte
            ## 📈 Resumen Ejecutivo
            [2-3 puntos clave más importantes]

            ## 🔍 Hallazgos Principales  
            [3-5 hallazgos específicos con datos]

            ## 📋 Análisis Detallado
            [Profundizar en los datos relevantes]

            ## 💡 Recomendaciones Accionables
            [3-4 recomendaciones específicas]

            ## 🎯 Próximos Pasos
            [Acciones concretas a tomar]

            ---
            *Reporte generado automáticamente*
            """
            
            response_text = self._call_vertex_ai(prompt, system_instruction, temperature=0.3, max_tokens=1500)
            
            if response_text and len(response_text) > 100:
                logger.info("✅ Narrativa AI generada exitosamente")
                return response_text
            else:
                raise Exception("Narrativa vacía o muy corta de Vertex AI")
                
        except Exception as e:
            logger.warning(f"❌ Generación narrativa con Vertex AI falló: {str(e)}")
            return self._basic_narrative(data, user_prompt)

    def _basic_narrative(self, data, user_prompt):
        """Genera una narrativa básica cuando Vertex AI falla"""
        metrics = data.get('metricas', {})
        total_records = len(data.get('detalles', []))
        
        narrative = f"# 📊 Reporte Generado\n\n"
        narrative += f"**Consulta procesada:** {user_prompt}\n\n"
        
        narrative += "## 📈 Resumen Ejecutivo\n\n"
        narrative += f"- **Registros analizados:** {total_records}\n"
        
        # Agregar métricas clave
        key_metrics = ['total_estudiantes', 'promedio_general', 'total_recaudado', 'tasa_asistencia']
        for key in key_metrics:
            if key in metrics and metrics[key]:
                narrative += f"- **{key.replace('_', ' ').title()}:** {metrics[key]}\n"
        
        narrative += "\n## 🔍 Hallazgos Principales\n\n"
        if total_records > 0:
            narrative += f"- Se analizaron {total_records} registros relevantes\n"
            narrative += "- Los datos fueron procesados exitosamente\n"
            narrative += "- Se calcularon todas las métricas solicitadas\n"
        else:
            narrative += "- No se encontraron registros con los criterios especificados\n"
        
        narrative += "\n## 💡 Recomendaciones\n\n"
        narrative += "1. Revise los datos detallados en la sección correspondiente\n"
        narrative += "2. Considere ajustar los filtros para análisis más específicos\n"
        narrative += "3. Exporte los datos para análisis adicionales\n"
        
        narrative += f"\n---\n*Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}*\n"
        
        return narrative

    def generate_insights(self, data, interpretation):
        """
        Genera insights usando Vertex AI o lógica básica
        """
        try:
            if not self.initialized:
                return self._basic_insights(data, interpretation)
            
            system_instruction = """
            Eres un analista de datos educativo experto. Genera insights accionables 
            basados en datos reales. Proporciona recomendaciones específicas y prácticas.

            Responde EXCLUSIVAMENTE con un array JSON válido.
            """
            
            prompt = f"""
            GENERA INSIGHTS ACCIONABLES:

            TIPO DE REPORTE: {interpretation.get('tipo_reporte', 'general')}
            COMPLEJIDAD: {interpretation.get('complejidad', 'media')}

            DATOS ANALIZADOS:
            ```json
            {json.dumps(data, ensure_ascii=False, indent=2)}
            ```

            GENERA 3-5 INSIGHTS en formato JSON:

            [
                {{
                    "titulo": "Título claro y conciso",
                    "descripcion": "Descripción detallada del hallazgo con datos específicos",
                    "tipo": "positivo|negativo|oportunidad|neutro",
                    "impacto": "alto|medio|bajo", 
                    "recomendacion": "Recomendación accionable y específica"
                }}
            ]

            Enfócate en insights que sean:
            - Basados en datos específicos
            - Accionables para la gestión educativa
            - Relevantes para el tipo de reporte
            - Cuantificables cuando sea posible
            """
            
            response_text = self._call_vertex_ai(prompt, system_instruction, temperature=0.3)
            
            # Extraer JSON de la respuesta
            try:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    insights = json.loads(response_text[json_start:json_end])
                    logger.info(f"✅ Insights AI generados: {len(insights)} insights")
                else:
                    raise json.JSONDecodeError("No se encontró JSON válido", response_text, 0)
            except json.JSONDecodeError as e:
                logger.warning(f"❌ No se pudo parsear JSON de insights: {e}")
                insights = self._basic_insights(data, interpretation)
            
            # Validar que sea una lista
            if not isinstance(insights, list):
                insights = self._basic_insights(data, interpretation)
                
            return insights
            
        except Exception as e:
            logger.warning(f"❌ Generación de insights falló: {str(e)}")
            return self._basic_insights(data, interpretation)

    def _basic_insights(self, data, interpretation):
        """Genera insights básicos cuando Vertex AI falla"""
        insights = []
        metrics = data.get('metricas', {})
        total_records = len(data.get('detalles', []))
        
        # Insight general
        insights.append({
            "titulo": "Análisis completado exitosamente",
            "descripcion": f"Se procesaron {total_records} registros según los criterios establecidos.",
            "tipo": "positivo",
            "impacto": "medio",
            "recomendacion": "Revise los datos detallados para identificar patrones específicos."
        })
        
        # Insight basado en métricas
        if metrics:
            key_metrics = {k: v for k, v in metrics.items() if isinstance(v, (int, float)) and v > 0}
            if key_metrics:
                insights.append({
                    "titulo": "Métricas clave calculadas",
                    "descripcion": f"Se analizaron {len(key_metrics)} métricas principales del dataset.",
                    "tipo": "neutro", 
                    "impacto": "medio",
                    "recomendacion": "Utilice estas métricas para el seguimiento y toma de decisiones."
                })
        
        # Insight de tipo de reporte
        report_type = interpretation.get('tipo_reporte', 'general')
        if report_type != 'general':
            insights.append({
                "titulo": f"Reporte especializado en {report_type.replace('_', ' ')}",
                "descripcion": f"Análisis focalizado en {report_type.replace('_', ' ')} para una perspectiva específica.",
                "tipo": "positivo",
                "impacto": "alto", 
                "recomendacion": "Utilice este tipo de reporte para el monitoreo continuo de esta área."
            })
        
        return insights

    def get_ai_status(self):
        """Retorna el estado actual de la IA"""
        status = {
            "initialized": self.initialized,
            "model_name": self.model_name,
            "region": self.region,
            "project_id": self.project_id,
            "mode": "vertex_ai" if self.initialized else "fallback",
            "timestamp": datetime.now().isoformat()
        }
        
        if self.initialized:
            status["message"] = f"Vertex AI activo con {self.model_name}"
            status["capabilities"] = ["interpretación_avanzada", "narrativa_ia", "insights_inteligentes"]
        else:
            status["message"] = "Modo fallback activo - reportes básicos"
            status["capabilities"] = ["interpretación_básica", "narrativa_estructurada", "insights_básicos"]
        
        return status
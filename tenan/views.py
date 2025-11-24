# tenan/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .Logica.report_engine import ReportEngine
from .models import Curso, Gestion, Materia

@csrf_exempt
@require_http_methods(["POST"])
def generate_ai_report(request):
    """
    Vista para generar reportes con IA
    """
    try:
        data = json.loads(request.body)
        user_prompt = data.get('prompt', '')
        filters = data.get('filters', {})
        include_charts = data.get('include_charts', True)
        
        if not user_prompt:
            return JsonResponse({
                'error': 'Prompt es requerido',
                'details': 'Debes proporcionar un prompt para generar el reporte'
            }, status=400)
        
        report_engine = ReportEngine()
        result = report_engine.execute_report(user_prompt, filters, include_charts)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido',
            'details': 'El cuerpo de la solicitud debe ser un JSON válido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_available_entities(request):
    """
    Vista para obtener entidades disponibles para filtros
    """
    try:
        cursos = list(Curso.objects.values_list('nombre', flat=True))
        gestiones = list(Gestion.objects.values_list('nombre', flat=True))
        materias = list(Materia.objects.values_list('nombre', flat=True))
        
        return JsonResponse({
            'cursos': cursos,
            'gestiones': gestiones,
            'materias': materias
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Error obteniendo entidades',
            'details': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def analyze_trends(request):
    """
    Vista para análisis de tendencias
    """
    try:
        data = json.loads(request.body)
        report_type = data.get('report_type', 'academic_performance')
        time_range = data.get('time_range', 'current_year')
        
        report_engine = ReportEngine()
        result = report_engine.analyze_trends(report_type, time_range)
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido',
            'details': 'El cuerpo de la solicitud debe ser un JSON válido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Error interno del servidor',
            'details': str(e)
        }, status=500)
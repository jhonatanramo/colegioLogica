"""
Django settings for backend project.
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-y_2fk#jetyjb^wlwc-@=#av$xrfde2lmc3^3f4#%ki6$fh@r6p')

DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME: 
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tenan',
    'rest_framework',
    'corsheaders',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://colegiovista.vercel.app",
    "https://coro-juvenil.vercel.app",
    "https://coro-juvenil-git-main-jhonatanramos-projects.vercel.app",
    "https://coro-juvenil-11c7cukbc-jhonatanramos-projects.vercel.app",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.parse(
        'postgresql://postgres:tfWuDZkOxEZTSRrRklxetCKNNaOcjcxD@metro.proxy.rlwy.net:18948/railway',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Si hay DATABASE_URL en entorno, usar esa
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Google Cloud Vertex AI Configuration
# En tu settings.py, actualiza la configuración de Vertex AI:

# Google Cloud Vertex AI Configuration
GOOGLE_CLOUD_PROJECT_ID = "nimble-chimera-477802-q3"
VERTEX_AI_LOCATION = 'us-central1'
VERTEX_AI_MODEL_NAME = 'gemini-1.5-flash'  # Modelo que SÍ está disponible

# Configuración de credenciales de Google Cloud
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, 'tenan', 'credentials', 'nimble-chimera-477802-q3-c8cb4f01b527.json')

# Verificar si el archivo de credenciales existe
if os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS
    print(f"✅ Credenciales de Google Cloud configuradas: {GOOGLE_APPLICATION_CREDENTIALS}")
    
    # Inicializar Vertex AI
    try:
        import vertexai
        vertexai.init(project=GOOGLE_CLOUD_PROJECT_ID, location=VERTEX_AI_LOCATION)
        print(f"✅ Vertex AI inicializado correctamente con modelo: {VERTEX_AI_MODEL_NAME}")
    except Exception as e:
        print(f"⚠️  Vertex AI no pudo inicializarse: {e}")
        print("El sistema funcionará en modo básico sin IA")
else:
    print(f"⚠️  Advertencia: Archivo de credenciales no encontrado en {GOOGLE_APPLICATION_CREDENTIALS}")
    print("El sistema funcionará en modo básico sin IA")
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'tenan': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
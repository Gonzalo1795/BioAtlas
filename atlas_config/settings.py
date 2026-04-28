"""
Django settings for atlas_config project — BioAtlas
Seguridad mejorada para producción
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ═══════════════════════════════════════════════════════════════
# VARIABLES DE ENTORNO
# Las claves secretas se leen de variables de entorno para no
# exponerlas en el código fuente. En desarrollo se usan valores
# por defecto.
# ═══════════════════════════════════════════════════════════════

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════
# ENTORNO
# ═══════════════════════════════════════════════════════════════

DEBUG = True

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ═══════════════════════════════════════════════════════════════
# APLICACIONES
# ═══════════════════════════════════════════════════════════════

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'atlas',
]

# ═══════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'atlas_config.urls'

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

WSGI_APPLICATION = 'atlas_config.wsgi.application'

# ═══════════════════════════════════════════════════════════════
# BASE DE DATOS
# ═══════════════════════════════════════════════════════════════

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ═══════════════════════════════════════════════════════════════
# VALIDACIÓN DE CONTRASEÑAS
# ═══════════════════════════════════════════════════════════════

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ═══════════════════════════════════════════════════════════════
# INTERNACIONALIZACIÓN
# ═══════════════════════════════════════════════════════════════

LANGUAGE_CODE = 'es-es'
TIME_ZONE     = 'Europe/Madrid'
USE_I18N      = True
USE_TZ        = True

# ═══════════════════════════════════════════════════════════════
# ARCHIVOS ESTÁTICOS Y MEDIA
# ═══════════════════════════════════════════════════════════════

STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ═══════════════════════════════════════════════════════════════
# AUTENTICACIÓN
# ═══════════════════════════════════════════════════════════════

LOGIN_URL          = '/login'
LOGIN_REDIRECT_URL = 'perfil'

# ═══════════════════════════════════════════════════════════════
# STRIPE — desde variables de entorno
# ═══════════════════════════════════════════════════════════════

SECRET_KEY = os.environ.get('SECRET_KEY', '')

STRIPE_SECRET_KEY      = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_PRICE_ID        = os.environ.get('STRIPE_PRICE_ID', '')
STRIPE_WEBHOOK_SECRET  = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

# ═══════════════════════════════════════════════════════════════
# SEGURIDAD — HEADERS HTTP
# ═══════════════════════════════════════════════════════════════

# Previene que la página se cargue en un iframe (clickjacking)
X_FRAME_OPTIONS = 'DENY'

# Fuerza al navegador a detectar el tipo de contenido correctamente
# Previene ataques MIME sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Activa el filtro XSS del navegador en navegadores antiguos
SECURE_BROWSER_XSS_FILTER = True

# ═══════════════════════════════════════════════════════════════
# SEGURIDAD — HTTPS (solo en producción)
# En desarrollo estas opciones están desactivadas.
# En producción se activan via variables de entorno.
# ═══════════════════════════════════════════════════════════════

# Fuerza HTTPS durante 1 año (HSTS)
SECURE_HSTS_SECONDS            = int(os.environ.get('SECURE_HSTS_SECONDS', 0))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False') == 'True'
SECURE_HSTS_PRELOAD            = os.environ.get('SECURE_HSTS_PRELOAD', 'False') == 'True'

# Redirige HTTP → HTTPS automáticamente
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'

# Cookies solo por HTTPS
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE    = os.environ.get('CSRF_COOKIE_SECURE',    'False') == 'True'

# ═══════════════════════════════════════════════════════════════
# SEGURIDAD — COOKIES DE SESIÓN
# ═══════════════════════════════════════════════════════════════

# La cookie de sesión NO es accesible desde JavaScript
# Previene robo de sesión mediante XSS
SESSION_COOKIE_HTTPONLY = True

# La cookie CSRF debe ser False para que el JS pueda leerla en las APIs AJAX
CSRF_COOKIE_HTTPONLY = False

# Tiempo de vida de la sesión: 2 semanas
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14

# ═══════════════════════════════════════════════════════════════
# SEGURIDAD — LÍMITE DE INTENTOS DE LOGIN
# Variable que usa views.py para limitar intentos fallidos
# ═══════════════════════════════════════════════════════════════

LOGIN_MAX_ATTEMPTS = 5
"""
Configuración de Django para el proyecto "Chile Explorer".

Proyecto académico (Evaluación Sumativa 2): sitio informativo con
base de datos relacional, modelos Django, ORM, migraciones y Django Admin.
Las configuraciones sensibles se leen desde variables de entorno (.env).
"""

import os
from pathlib import Path

import pymysql

from dotenv import load_dotenv

# PyMySQL se instala como reemplazo del driver MySQLdb (más simple de instalar).
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables de entorno desde .env (si existe).
load_dotenv(BASE_DIR / '.env')


def _env_bool(name: str, default: bool = False) -> bool:
    """Convierte una variable de entorno booleana a bool."""
    valor = os.environ.get(name)
    if valor is None:
        return default
    return valor.strip().lower() in {'1', 'true', 'yes', 'on'}


def _env_list(name: str, default: str = '') -> list[str]:
    """Convierte una variable de entorno separada por comas a lista."""
    valor = os.environ.get(name, default)
    return [item.strip() for item in valor.split(',') if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
# Se lee desde .env — nunca debe quedar hardcodeado en producción.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-only-cambiar-en-produccion',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _env_bool('DEBUG', default=True)

ALLOWED_HOSTS = _env_list('ALLOWED_HOSTS', default='localhost,127.0.0.1')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'destinos',
    'gastronomia',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chile_explorer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Directorio global para templates compartidos (base.html).
        'DIRS': [BASE_DIR / 'templates'],
        # APP_DIRS permite usar templates dentro de cada aplicación.
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

WSGI_APPLICATION = 'chile_explorer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases
#
# Configuración mediante variables de entorno (.env):
# - Por defecto: SQLite local (db.sqlite3) para desarrollo.
# - En EC2 con phpMyAdmin: MySQL/MariaDB configurado vía .env.
DB_ENGINE = os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3')

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': os.environ.get('DB_NAME', str(BASE_DIR / 'db.sqlite3')),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),
        'PORT': os.environ.get('DB_PORT', ''),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'

# Carpetas globales de estáticos (css, js y bootstrap local).
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/6.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

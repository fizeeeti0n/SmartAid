from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ====================================================================
# FIX: ENVIRONMENT VARIABLE LOADING (MUST BE AT THE TOP)
# Load environment variables from .env file located in the project root
# This ensures that OS.environ.get('GEMINI_API_KEY') works in ai_app/services.py
# ====================================================================
load_dotenv(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0^@4g&9e094i$t#^8$3ors%m2_mn=a!*b86e*+y4q$b@mv_r&c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'planner',
    'users',
    'peer_connect',
    'ai_app',
    'channels',
    'study_tools',
    'rest_framework',
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

ROOT_URLCONF = 'mysite.urls'

# ====================================================================
# TEMPLATES FIX: Point Django to the top-level 'templates' directory
# ====================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # FIX: BASE_DIR / 'templates' points to G:\SmartAid\mysite\templates
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'mysite.wsgi.application'
# Channels configuration
ASGI_APPLICATION = 'mysite.asgi.application'

# Use an in-memory channel layer for development.
# For production, use Redis (pip install channels_redis)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
        # For production:
        # "BACKEND": "channels_redis.pubsub.RedisChannelLayer",
        # "CONFIG": {"hosts": [("localhost", 6379)]},
    },
}


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

# Authentication URL Redirects (Good practice to define)
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login_view' # Assuming 'login_view' is the name of your login URL
LOGIN_URL = 'login_view' # Ensure this points to your login page

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

# ========================================================================
# STATIC FIX: Point Django to the top-level 'static' directory in your app
# ========================================================================
# This tells Django to look for static files (like style.css) in this list of directories
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Points to G:\SmartAid\mysite\static
]

# ========================================================================
# MEDIA/FILE UPLOADS FIX: Define where user-uploaded files are stored/served
# ========================================================================
# The URL prefix for media files (e.g., accessed at http://127.0.0.1:8000/media/...)
MEDIA_URL = '/media/'
# The absolute path to the directory where uploaded files will be saved on the file system
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

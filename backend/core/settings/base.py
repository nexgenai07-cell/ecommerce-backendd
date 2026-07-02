"""
Django base settings — shared across development and production.
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

# -------------------------------------------------
# BASE DIRECTORY + ENV
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Force correct .env loading
from dotenv import load_dotenv
import os

load_dotenv()
# -------------------------------------------------
# SECURITY
# -------------------------------------------------

SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-default-key-change-me')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# -------------------------------------------------
# EMAIL
# -------------------------------------------------
# FIX: EMAIL_BACKEND pehle hardcoded 'console.EmailBackend' tha, jo emails
# ko sirf server logs mein print karta hai — kabhi kisi ke inbox mein nahi
# jaate. .env mein already sahi Gmail SMTP credentials maujood hain, lekin
# wo kahin read hi nahi ho rahe the. Ab EMAIL_BACKEND aur baaki SMTP settings
# .env se aa rahi hain. Agar .env mein EMAIL_BACKEND set nahi hai, to dev
# ke liye console backend pe hi fallback hoga (taake local testing na tootay).
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# FIX: verification/reset links poore project mein hardcoded
# 'http://localhost:5173/...' the — production mein galat domain pe
# point karte. Ab ek hi jagah se control hota hai. .env mein
# FRONTEND_URL=https://your-real-frontend-domain.com set kar dena
# production ke liye; dev ke liye localhost pe hi fallback rahega.
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# -------------------------------------------------
# APPS
# -------------------------------------------------

INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    # NOTE: 'daphne' and 'channels' removed here — Vercel serverless
    # does not support long-running ASGI processes. These will be added
    # back when the project moves to Railway/Render for WebSocket support.

    # Local apps
    'apps.users',
    'apps.stores',
    'apps.categories',
    'apps.products',
    'apps.orders',
    'apps.cart',
    'apps.notifications',
    'apps.returns',
    'apps.analytics',
    'apps.ai',
    'apps.social',
    'apps.whatsapp',
]

# -------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # must be on top
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'
# -------------------------------------------------
# TEMPLATES
# -------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'
# ASGI_APPLICATION = 'core.asgi.application'  # enabled when moving to Railway/Render

# -------------------------------------------------
# DATABASE (POSTGRESQL)
# -------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# -------------------------------------------------
# AUTH
# -------------------------------------------------

AUTH_USER_MODEL = 'users.User'

# -------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------
# REST FRAMEWORK
# -------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    # NOTE: DEFAULT_PAGINATION_CLASS jaan-bujh kar yahan GLOBALLY set nahi
    # ki gayi. API doc mein sirf kuch specific endpoints (Products list/
    # search, My Orders, Admin Orders, Admin Orders filter) {count, next,
    # previous, results} shape promise karte hain — baaki (Categories,
    # Discounts, Returns, Complaints, Notifications, etc.) plain array
    # promise karte hain. Isliye pagination_class un views mein manually
    # laga di gayi hai (dekho core/pagination.py), globally nahi — warna
    # sab "sahi" plain-array endpoints bhi zabardasti wrap ho jate.
}

# -------------------------------------------------
# JWT SETTINGS
# -------------------------------------------------

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# -------------------------------------------------
# CORS
# -------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]

# -------------------------------------------------
# CHANNELS (Redis)
# -------------------------------------------------

import os

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# -------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------
# STATIC + MEDIA
# -------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------
# CACHE (Redis)
# -------------------------------------------------

# -------------------------------------------------
# CACHE
# Redis agar available ho toh use karo (production server pe),
# warna DummyCache — Vercel pe Redis nahi hota, is wajah se
# REDIS_URL na hone pe server crash karta tha.
# -------------------------------------------------

REDIS_URL = os.getenv("REDIS_URL", "")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    # DummyCache — caching nahi hogi lekin server crash nahi karega
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
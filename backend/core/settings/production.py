# PATH: core/settings/production.py
from .base import *

DEBUG = False

# Static files — already configured in base.py with WhiteNoise
# DO NOT add WhiteNoise to MIDDLEWARE again here — it's already in base.py MIDDLEWARE.
# Adding it twice caused admin CSS/JS to break (duplicate middleware conflict).
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS — allow Vercel production URL + localhost for frontend dev
CORS_ALLOWED_ORIGINS = [
    "https://ecommerce-backendd-o29p.vercel.app",   # apna Vercel backend URL
    "http://localhost:5173",                          # React dev server
    "http://localhost:3000",
]
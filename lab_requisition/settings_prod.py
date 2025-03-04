"""
Production settings for lab_requisition project.
"""
from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Set ALLOWED_HOSTS to your domain or IP
ALLOWED_HOSTS = ['your-domain.com', 'localhost', '127.0.0.1']

# Database settings
# Use environment variables for database credentials in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'lab_requisition_db'),
        'USER': os.environ.get('DB_USER', 'admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'LETMEIN'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Security settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "https://your-frontend-domain.com",
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
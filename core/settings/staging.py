"""
Staging settings for core project.
"""
from .production import *

# Staging-specific overrides
DEBUG = False
ALLOWED_HOSTS = os.getenv('STAGING_ALLOWED_HOSTS', '').split(',')

# Less restrictive security for staging
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0

# Staging CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('STAGING_CORS_ORIGINS', '').split(',')

# Staging logging - more verbose than production
LOGGING['handlers']['console'] = {
    'level': 'INFO',
    'class': 'logging.StreamHandler',
    'formatter': 'verbose',
}

LOGGING['loggers']['django']['handlers'] = ['console', 'file', 'error_file']
LOGGING['loggers']['accounts']['handlers'] = ['console', 'file', 'error_file']
LOGGING['loggers']['products']['handlers'] = ['console', 'file', 'error_file']

# Staging cache settings - shorter cache times
CACHE_MIDDLEWARE_SECONDS = 60  # 1 minute
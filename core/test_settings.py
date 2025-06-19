from .settings import *

# Use in-memory sqlite database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Simplify file storage during tests
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Allow anonymous access in tests unless views specify otherwise
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = []

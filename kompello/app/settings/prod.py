import os

from .shared import *

SECRET_KEY = os.getenv("KOMPELLO_SECRET", "")
if SECRET_KEY == "":
    raise Exception("This is not allowed!")

ALLOWED_HOSTS = ["0.0.0.0", "localhost"]
DEBUG = False
SECURE_SSL_REDIRECT = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000/",
    "http://127.0.0.1:3000/",
]
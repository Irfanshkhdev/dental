import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-aura-dental-spa-luxury-crm-2026')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://dentalclinicdjango.vercel.app',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Optional External CRM Webhook URL (GoHighLevel, NexHealth, HubSpot, Zapier)
CRM_WEBHOOK_URL = os.environ.get('CRM_WEBHOOK_URL', '')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clinic',
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

ROOT_URLCONF = 'aura_dental.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'aura_dental.wsgi.application'
ASGI_APPLICATION = 'aura_dental.asgi.application'

# ==============================================================================
# DATABASE CONFIGURATION (SERVERLESS-AWARE FOR VERCEL & LOCAL ENVIRONMENT)
# ==============================================================================
# On Vercel / AWS Lambda, the root deployment (/var/task) is mounted read-only.
# Any SQLite write (or lock/journal creation) in /var/task raises:
#   sqlite3.OperationalError: attempt to write a readonly database
# The only read-write filesystem available in serverless is /tmp.
# We copy the bundled seeded database to /tmp so all writes succeed without errors.

IS_VERCEL = bool(
    os.environ.get('VERCEL')
    or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
    or str(BASE_DIR).startswith('/var/task')
)

if IS_VERCEL:
    tmp_db = Path('/tmp') / 'lumina_dental_crm.sqlite3'
    candidates = [
        BASE_DIR / 'lumina_dental_crm.sqlite3',
        BASE_DIR / 'dental_clinic_django' / 'lumina_dental_crm.sqlite3',
        Path('/var/task/lumina_dental_crm.sqlite3'),
        Path('/var/task/dental_clinic_django/lumina_dental_crm.sqlite3'),
    ]
    orig_db = None
    for cand in candidates:
        if cand.exists():
            orig_db = cand
            break

    if orig_db:
        try:
            # Copy to /tmp if missing or updated
            if not tmp_db.exists() or (orig_db.stat().st_size != tmp_db.stat().st_size):
                shutil.copyfile(orig_db, tmp_db)
                os.chmod(tmp_db, 0o666)
        except Exception as e:
            print(f"Warning: could not copy sqlite db to /tmp: {e}")

    DB_PATH = tmp_db
else:
    DB_PATH = BASE_DIR / 'lumina_dental_crm.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}

# ==============================================================================
# STATELESS SIGNED COOKIE SESSIONS
# ==============================================================================
# Stores session data in cryptographically signed cookies on the client's browser.
# Eliminates database writes for logins and session cycles, making auth 100% resilient
# across multiple serverless lambda instances and cold-starts on Vercel.
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600  # 14 days

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

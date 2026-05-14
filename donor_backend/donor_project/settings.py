"""
Django settings for donor_project.

This version is Docker + PostgreSQL ready and supports schema separation:
- donor service uses donor_schema
- removes accidental multiple DATABASES blocks (a common silent bug)
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ CHANGE: use env var for secret in Docker; fallback for dev.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-me")

# ✅ CHANGE: DEBUG controlled through env var
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# ✅ CHANGE: allow Docker hostnames during development
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "donor_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]
ROOT_URLCONF = "donor_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # If you have templates inside app/templates, APP_DIRS is enough.
        # Add DIRS only if you have a custom templates folder.
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "donor_project.wsgi.application"

# ✅ CHANGE (IMPORTANT): Use ONE DATABASES block only.
# Multiple DATABASES blocks cause silent overriding (last one wins),
# which is how SQLite accidentally replaces Postgres.
# ✅ CHANGE: schema separation via search_path: donor_schema first.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "blood_db"),
        "USER": os.getenv("DB_USER", "blood_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "blood_pass"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            "options": "-c search_path=donor_schema,public"
        },
    }
}

HOSPITAL_SERVICE_BASE_URL = os.environ.get("HOSPITAL_SERVICE_BASE_URL", "http://hospital:8000")


# ✅ KEEP: Your custom router
DATABASE_ROUTERS = ["donor_project.db_routers.DonorRouter"]

# ✅ KEEP: donor custom user model
AUTH_USER_MODEL = "donor_app.DonorUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ✅ KEEP: gRPC config (default host should be docker service name "ai")
AI_SERVICE_HOST = os.environ.get("AI_SERVICE_HOST", "ai")
AI_SERVICE_PORT = os.environ.get("AI_SERVICE_PORT", "50051")
AI_SERVICE_TARGET = f"{AI_SERVICE_HOST}:{AI_SERVICE_PORT}"

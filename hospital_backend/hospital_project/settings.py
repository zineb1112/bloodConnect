"""
Django settings for hospital_project.

This version is Docker + PostgreSQL ready and supports schema separation:
- hospital service uses hospital_schema
- no SQLite
- safe defaults for Docker networking
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ CHANGE: Move secrets to env variables when possible.
# For dev, we keep a fallback value so the container can still run.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-me")

# ✅ CHANGE: Control DEBUG using env vars in Docker
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

# ✅ CHANGE: In Docker, requests can come from different hostnames.
# For dev it's fine to allow all. (For production, restrict this.)
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "hospital_app",
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

ROOT_URLCONF = "hospital_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Keeping DIRS empty is fine because you're using APP_DIRS templates.
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

WSGI_APPLICATION = "hospital_project.wsgi.application"

# ✅ CHANGE (IMPORTANT): Switch from SQLite to PostgreSQL (shared DB).
# - HOST comes from docker-compose: DB_HOST=db
# - NAME comes from docker-compose: DB_NAME=blood_db
# ✅ CHANGE: Use schema separation via search_path:
#   hospital_schema first, then public as fallback.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "blood_db"),
        "USER": os.getenv("DB_USER", "blood_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "blood_pass"),
        "HOST": os.getenv("DB_HOST", "db"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            "options": "-c search_path=hospital_schema,public"
        },
    }
}

# Donor Service base URL inside Docker network
DONOR_SERVICE_BASE_URL = "http://donor:8000"

# ✅ KEEP: Your custom database router (enforces schema routing logic).
DATABASE_ROUTERS = ["hospital_project.db_routers.HospitalRouter"]

# ✅ KEEP (IMPORTANT): Your custom user model.
# Must be set BEFORE first migrations for a clean project.
AUTH_USER_MODEL = "hospital_app.HospitalUser"

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

# ✅ KEEP: gRPC config, but make the default host "ai" (docker service name),
# not "localhost" (localhost inside a container = itself).
AI_SERVICE_HOST = os.environ.get("AI_SERVICE_HOST", "ai")
AI_SERVICE_PORT = os.environ.get("AI_SERVICE_PORT", "50051")
AI_SERVICE_TARGET = f"{AI_SERVICE_HOST}:{AI_SERVICE_PORT}"

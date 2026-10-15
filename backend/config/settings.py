
import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------
# SECURITY SETTINGS
# --------------------------------------------------

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "dev-only-insecure-key"
)

DEBUG = os.environ.get("DEBUG", "True").strip().lower() in (
    "true", "1", "yes", "on"
)

if not DEBUG and SECRET_KEY == "dev-only-insecure-key":
    raise RuntimeError(
        "Production requires a secure SECRET_KEY environment variable."
    )

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1,.onrender.com"
    ).split(",")
    if host.strip()
]


# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "core",
]


# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# --------------------------------------------------
# URLS AND TEMPLATES
# --------------------------------------------------

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
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


# --------------------------------------------------
# DATABASE
# Supports DATABASE_URL, MySQL environment variables,
# and local SQLite for development.
# --------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
DATABASE_ENGINE = os.environ.get("DATABASE_ENGINE", "").strip().lower()

if DATABASE_URL:
    parsed_db = urlparse(DATABASE_URL)
    scheme = parsed_db.scheme.lower()

    if scheme in ("postgres", "postgresql", "postgresql+psycopg"):
        query_params = parse_qs(parsed_db.query)

        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": unquote(parsed_db.path.lstrip("/")),
                "USER": unquote(parsed_db.username or ""),
                "PASSWORD": unquote(parsed_db.password or ""),
                "HOST": parsed_db.hostname or "",
                "PORT": str(parsed_db.port or 5432),
                "CONN_MAX_AGE": 60,
                "OPTIONS": (
                    {"sslmode": query_params["sslmode"][0]}
                    if "sslmode" in query_params
                    else {}
                ),
            }
        }

    elif scheme in ("mysql", "mysql2"):
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": unquote(parsed_db.path.lstrip("/")),
                "USER": unquote(parsed_db.username or ""),
                "PASSWORD": unquote(parsed_db.password or ""),
                "HOST": parsed_db.hostname or "",
                "PORT": str(parsed_db.port or 3306),
                "CONN_MAX_AGE": 60,
            }
        }

    else:
        raise RuntimeError(
            "Unsupported DATABASE_URL scheme. Use PostgreSQL or MySQL."
        )

elif DATABASE_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["DATABASE_NAME"],
            "USER": os.environ["DATABASE_USER"],
            "PASSWORD": os.environ.get("DATABASE_PASSWORD", ""),
            "HOST": os.environ.get("DATABASE_HOST", "127.0.0.1"),
            "PORT": os.environ.get("DATABASE_PORT", "3306"),
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# --------------------------------------------------
# USER MODEL AND PASSWORD VALIDATION
# --------------------------------------------------

AUTH_USER_MODEL = "core.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            + validator
        )
    }
    for validator in (
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    )
]


# --------------------------------------------------
# STATIC AND MEDIA FILES
# --------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------------
# FRONTEND CONNECTION: CORS AND CSRF
# --------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,https://smart-house-managements-system.vercel.app"
    ).split(",")
    if origin.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "https://smart-house-managements-system.vercel.app"
    ).split(",")
    if origin.strip()
]


# --------------------------------------------------
# REST API
# --------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 20,
}


# --------------------------------------------------
# JWT TOKENS
# --------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}


# --------------------------------------------------
# PRODUCTION SECURITY
# --------------------------------------------------

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"


# --------------------------------------------------
# OPTIONAL AI CONFIGURATION
# --------------------------------------------------

AI_API_KEY = os.environ.get("AI_API_KEY", "")

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
INSTALLED_APPS = ["django.contrib.admin","django.contrib.auth","django.contrib.contenttypes","django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles","corsheaders","rest_framework","core"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware","django.middleware.security.SecurityMiddleware","django.contrib.sessions.middleware.SessionMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
if os.environ.get("DATABASE_ENGINE") == "mysql":
    DATABASES = {"default": {"ENGINE":"django.db.backends.mysql","NAME":os.environ["DATABASE_NAME"],"USER":os.environ["DATABASE_USER"],"PASSWORD":os.environ.get("DATABASE_PASSWORD",""),"HOST":os.environ.get("DATABASE_HOST","127.0.0.1"),"PORT":os.environ.get("DATABASE_PORT","3306")}}
else:
    DATABASES = {"default": {"ENGINE":"django.db.backends.sqlite3","NAME":BASE_DIR/"db.sqlite3"}}
AUTH_USER_MODEL = "core.User"
AUTH_PASSWORD_VALIDATORS = [{"NAME":"django.contrib.auth.password_validation."+n} for n in ("UserAttributeSimilarityValidator","MinimumLengthValidator","CommonPasswordValidator","NumericPasswordValidator")]
STATIC_URL = "static/"; MEDIA_URL = "/media/"; MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
REST_FRAMEWORK = {
  "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
  "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
  "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination", "PAGE_SIZE": 20,
}
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(hours=2), "REFRESH_TOKEN_LIFETIME": timedelta(days=7)}
AI_API_KEY = os.environ.get("AI_API_KEY", "")

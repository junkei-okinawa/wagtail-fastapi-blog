import os
from pathlib import Path

from dotenv import load_dotenv

from .base import *  # noqa: F403, F401

# 環境変数を読み込み
load_dotenv()

# dev.py 独自の BASE_DIR (settings ディレクトリの親の親の親)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

DEBUG = True

# セキュリティ設定: 環境変数から読み込み、デフォルトは安全な設定
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# セキュリティヘッダー（開発環境でも有効）
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# CSRF設定
CSRF_COOKIE_SECURE = False  # 開発環境ではHTTPを許可
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
).split(",")

# セッション設定
SESSION_COOKIE_SECURE = False  # 開発環境ではHTTPを許可
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1時間

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # manage.pyから見たパス
        "OPTIONS": {
            "timeout": 20,
            "isolation_level": None,  # Autocommit mode for better performance
        },
        "CONN_MAX_AGE": 60,  # Connection pooling
    }
}

# キャッシュ設定（開発環境用）
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,  # 5分
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
            "CULL_FREQUENCY": 3,
        },
    }
}

# セッションキャッシュ
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# パフォーマンス最適化設定
# テンプレートキャッシュ（開発環境では軽く）
TEMPLATE_CACHE_TIMEOUT = 60

# Wagtailキャッシュ設定
WAGTAIL_CACHE = True
WAGTAIL_CACHE_BACKEND = "default"

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "django_project" / "staticfiles"  # django_project内に収集
STATICFILES_DIRS = [
    BASE_DIR / "django_project" / "static",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "django_project" / "media"

# 開発環境用のログ設定
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "fastapi_app": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Wagtail settings
# WAGTAIL_SITE_NAME は base.py からインポート済み

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = "http://localhost:8000"

# ログ設定（開発環境：シンプルに）
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# dev.py で INSTALLED_APPS に追加するアプリがあれば記述
# INSTALLED_APPS += []

# dev.py で MIDDLEWARE に追加するものがあれば記述
# MIDDLEWARE += []

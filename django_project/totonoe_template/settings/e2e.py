"""E2E test settings for Django."""

import os
from pathlib import Path

from .dev import *

# E2E環境固有の設定
ALLOWED_HOSTS = ["*"]
DEBUG = True

# E2E環境フラグを設定（conftest.pyからも設定されるが、念のため）
os.environ.setdefault("E2E_TESTING", "true")

# E2E用データベース設定（永続的なファイルベース）
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_e2e.sqlite3",  # E2E専用のDBファイル
        "OPTIONS": {
            "timeout": 20,
            "isolation_level": None,
        },
        "CONN_MAX_AGE": 60,
    }
}

# E2E用静的ファイル設定
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "django_project" / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "django_project" / "static",
]

# メディアファイル設定
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "django_project" / "media"

# ログ設定を調整（E2E用）
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "django_project" / "logs" / "e2e.log",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# キャッシュ無効化（E2E時の一貫性のため）
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

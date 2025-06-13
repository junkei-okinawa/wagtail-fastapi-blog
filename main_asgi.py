import os
import django
from pathlib import Path
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Django 設定を先に初期化
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.totonoe_template.settings.dev")
django.setup()

# Django ASGI アプリケーションを取得
django_asgi_app = get_asgi_application()

# FastAPI アプリケーションをインポート（Django 設定初期化後）
from fastapi_app.app.main import app as fastapi_app

# メイン ASGI アプリケーションの作成
app = FastAPI(
    title="totonoe_template Main App",
    description="Django (Wagtail) + FastAPI 統合アプリケーション",
    version="0.1.0"
)

# FastAPI ルーターを /api パスにマウント
app.mount("/api", fastapi_app)

# 開発時の静的ファイル配信（本番では Nginx などで処理）
BASE_DIR = Path(__file__).resolve().parent
# 静的ファイル用のディレクトリパス
static_dir = BASE_DIR / "django_project" / "static"  # 開発時の静的ファイル
staticfiles_dir = BASE_DIR / "django_project" / "staticfiles"  # collectstaticで収集されたファイル
media_dir = BASE_DIR / "django_project" / "media"

# collectstaticで収集されたファイルを優先
if staticfiles_dir.exists():
    app.mount("/static", StaticFiles(directory=str(staticfiles_dir)), name="static")
elif static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

if media_dir.exists():
    app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

# Django アプリケーションをルートパスにマウント
# 注意: これは最後に行う必要がある（他のパターンがキャッチされる前に）
app.mount("/", django_asgi_app)

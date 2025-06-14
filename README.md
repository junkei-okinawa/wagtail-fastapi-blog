# Django + Wagtail + FastAPI Blog

統合ブログサイト with 非同期処理、決済機能、パフォーマンス最適化

## 🚀 Features

- **Django + Wagtail CMS**: パワフルなコンテンツ管理システム
- **FastAPI**: 高性能な非同期API
- **Stripe決済**: セキュアな決済処理
- **パフォーマンス最適化**: キャッシュ、DB最適化、レスポンシブデザイン
- **セキュリティ**: CORS、CSRF、HTTPS対応
- **テスト環境**: 包括的なunit/integrationテスト

## 🛠️ セットアップ

### 前提条件
- Python 3.12+
- uv (Python package manager)

### インストールと起動
```bash
# 1. 依存関係のインストール
uv sync

# 2. 環境変数設定
cp .env.example .env
# .envファイルを編集してStripe APIキー等を設定

# 3. データベースセットアップ
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py collectstatic

# 4. 開発サーバー起動
uv run uvicorn main_asgi:app --reload --host 127.0.0.1 --port 8000
# または: make dev
```

## 🧪 テスト環境

### クイックスタート
```bash
# テスト依存関係インストール
uv sync --group test

# 動作確認済みテストの実行
uv run python working_tests_demo.py

# 全テスト実行（一部失敗含む）
make test-unit
```

### テスト実行方法

| コマンド | 説明 | 状況 |
|---------|------|------|
| `make test` | 全テスト実行 | ⚠️ 一部失敗 |
| `make test-unit` | ユニットテストのみ | ⚠️ 一部失敗 |
| `make test-integration` | 統合テストのみ | ❌ 要修正 |
| `make test-coverage` | カバレッジ付き | ⚠️ 一部失敗 |
| `uv run python working_tests_demo.py` | 動作確認済みのみ | ✅ 正常動作 |

### テスト現状

**✅ 動作中（13テスト）**
- FastAPI基本エンドポイント（health, stats, count, cache, debug）
- APIスキーマ検証
- 基本的なモック機能

**⚠️ 修正が必要（16テスト）**
- Django モデルテスト → データベースマイグレーション要
- 統合テスト → アプリケーションインポート要  
- 決済APIテスト → Stripeモック設定要

### テスト構成
```
tests/
├── conftest.py              # テスト設定・fixtures
├── unit/                    # 単体テスト
│   ├── test_blog_models.py        # ❌ DB設定要
│   ├── test_posts_api.py          # ✅ 動作確認済み
│   └── test_payments_api.py       # ⚠️ 一部動作
├── integration/             # 統合テスト
│   └── test_full_integration.py   # ❌ 修正要
└── fixtures/                # テストデータ
```

## 🌐 API エンドポイント

### Posts API
- `GET /api/posts/` - 記事一覧（ページネーション、検索対応）
- `GET /api/posts/{id}` - 記事詳細
- `GET /api/posts/health` - ヘルスチェック
- `GET /api/posts/stats` - パフォーマンス統計
- `GET /api/posts/count` - 記事数取得
- `POST /api/posts/cache/clear` - キャッシュクリア

### Payments API
- `POST /api/payments/create-checkout-session` - Stripe決済セッション作成
- `POST /api/payments/webhook` - Stripe Webhook処理

### 管理画面
- `/admin/` - Django管理画面
- `/cms/` - Wagtail CMS管理画面

## 🏗️ アーキテクチャ

```
my-wagtail-fastapi-blog/
├── main_asgi.py              # メインASGIアプリ（Django+FastAPI統合）
├── manage.py                 # Django管理スクリプト
├── pyproject.toml            # 依存関係・プロジェクト設定
├── django_project/           # Djangoプロジェクト
│   ├── totonoe_template/     # Django設定（base/dev/prod/test）
│   ├── templates/            # Djangoテンプレート
│   ├── static/               # 静的ファイル
│   └── staticfiles/          # collectstaticで収集されたファイル
├── blog/                     # Wagtailブログアプリ
│   ├── models.py             # ブログモデル（DBインデックス最適化済み）
│   └── templates/            # ブログテンプレート
├── fastapi_app/              # FastAPIアプリケーション
│   └── app/
│       ├── main.py           # FastAPIアプリ設定
│       ├── routers/          # APIルーター（posts, payments）
│       ├── schemas/          # Pydanticスキーマ
│       └── utils/            # パフォーマンス監視等
└── tests/                    # テストスイート
    ├── unit/                 # 単体テスト
    ├── integration/          # 統合テスト
    └── conftest.py           # テスト設定
```

## 📈 パフォーマンス機能

- **LRUキャッシュ**: 記事取得の高速化（functools.lru_cache）
- **DB最適化**: select_related、only、インデックス活用
- **非同期処理**: FastAPIでの並行処理、sync_to_async
- **静的ファイル最適化**: collectstatic、効率的な配信
- **レスポンシブデザイン**: モバイル対応、Critical CSS

## 🔒 セキュリティ機能

- **CORS**: クロスオリジン制御（CORSMiddleware）
- **CSRF**: リクエスト偽造対策
- **ホスト検証**: TrustedHostMiddleware（本番環境）
- **レート制限**: API濫用防止
- **入力検証**: Pydanticスキーマによる厳密な検証
- **HTTPS対応**: 本番環境での暗号化通信

## 🔧 開発支援

### Makefile コマンド
```bash
make help          # 利用可能なコマンド一覧
make install       # 依存関係インストール
make dev           # 開発サーバー起動
make test          # テスト実行
make lint          # コード品質チェック
make format        # コードフォーマット
make clean         # 一時ファイル削除
```

### 設定管理
- **開発環境**: `settings/dev.py`
- **本番環境**: `settings/prod.py`  
- **テスト環境**: `settings/test.py`
- **共通設定**: `settings/base.py`

## 🚧 今後の改善点

1. **テスト環境の完全化**
   - Djangoモデルテストのデータベース設定
   - 統合テストの結合問題解決
   - CI/CD連携

2. **本番環境対応**
   - PostgreSQL移行
   - Docker化
   - AWS/GCP デプロイ

3. **機能拡張**
   - ユーザー認証システム
   - コメント機能
   - 記事の多言語対応

## 📝 ライセンス

MIT License

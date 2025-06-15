# Django + Wagtail + FastAPI Blog - 開発ガイド

## 🚀 開発環境セットアップ

### 前提条件
- Python 3.12+
- uv (Python package manager)
- Git

### 初回セットアップ
```bash
# 1. リポジトリクローン
git clone <repository-url>
cd my-wagtail-fastapi-blog

# 2. 依存関係インストール
make install

# 3. Pre-commit hooks設定
make setup-hooks

# 4. 環境変数設定
cp .env.example .env
# .envファイルを編集してAPIキー等を設定

# 5. データベースセットアップ
make migrate
make createsuperuser

# 6. 開発サーバー起動
make dev
```

## 🔧 Makeコマンド一覧

### **基本コマンド**
| コマンド | 説明 |
|---------|------|
| `make help` | 利用可能なコマンド一覧表示 |
| `make install` | 全依存関係インストール |
| `make dev` | 開発サーバー起動 (http://localhost:8000) |

### **テスト関連**
| コマンド | 説明 |
|---------|------|
| `make test` | 全テスト実行 |
| `make test-unit` | 単体テストのみ実行 |
| `make test-integration` | 統合テストのみ実行 |
| `make test-e2e` | E2Eテスト実行（Playwright） |
| `make test-coverage` | カバレッジ付きテスト実行 |
| `make test-quick` | 高速テスト実行（並列） |

### **Docker関連**
| コマンド | 説明 |
|---------|------|
| `make docker-build` | Dockerイメージビルド |
| `make docker-dev` | 開発環境起動（SQLite） |
| `make docker-full` | 本格環境起動（PostgreSQL + Redis） |
| `make docker-down` | コンテナ停止・削除 |
| `make docker-clean` | イメージ・ボリューム完全削除 |

### **コード品質 - 段階的品質管理**
| コマンド | 説明 | 使用タイミング |
|---------|------|-------------|
| `make lint` | **完全品質チェック** (pre-commit全実行) | コミット前・PR前 |
| `make lint-core` | **コアコード厳格チェック** (fastapi_app/, blog/) | 日常開発・機能実装時 |
| `make lint-quick` | **高速チェック** (ruff + black基本チェック) | リアルタイム確認 |
| `make lint-full` | **全体統合チェック** (lint + lint-e2e) | リリース前・CI/CD |
| `make lint-e2e` | **E2Eテスト緩和チェック** (非ブロッキング警告) | E2E修正時 |
| `make format` | **自動フォーマット** (lint経由実行) | コード整形 |
| `make setup-hooks` | **Pre-commit hooks インストール** | 初回セットアップ |
| `make check-hooks` | **Pre-commit hooks 手動実行** | 確認・デバッグ |
| `make audit` | **セキュリティ監査** (pip-audit) | 定期的セキュリティチェック |

### **Django管理**
| コマンド | 説明 |
|---------|------|
| `make migrate` | データベースマイグレーション |
| `make createsuperuser` | スーパーユーザー作成 |
| `make collectstatic` | 静的ファイル収集 |
| `make shell` | Django shell起動 |

### **開発支援**
| コマンド | 説明 |
|---------|------|
| `make clean` | 一時ファイル削除 |
| `make logs` | 開発サーバーログ表示 |

## 📝 開発フロー

### **1. 新機能開発**
```bash
# ブランチ作成
git checkout -b feature/new-feature

# 開発環境確認
make dev

# テスト実行
make test

# コード品質チェック
make lint
make format

# コミット（pre-commit自動実行）
git add .
git commit -m "feat: 新機能実装"
```

### **2. プルリクエスト前チェック**
```bash
# 全体チェック
make check-hooks
make test-coverage
make lint

# 問題なければプッシュ
git push origin feature/new-feature
```

## 🧪 テスト戦略

### **テストファイル構成**
```
tests/
├── conftest.py              # テスト設定・fixtures
├── unit/                    # 単体テスト
│   ├── test_blog_models.py  # ブログモデルテスト
│   ├── test_posts_api.py    # 投稿APIテスト
│   └── test_payments_api.py # 決済APIテスト
├── integration/             # 統合テスト
│   └── test_full_integration.py
└── e2e/                     # E2Eテスト（Playwright）
    ├── conftest.py          # E2E環境設定
    ├── test_basic_e2e.py    # 基本動作テスト
    └── test_blog_e2e.py     # ブログ機能テスト
```

### **テスト実行パターン**
```bash
# 開発中（高速）
make test-unit

# 機能完成時（完全）
make test

# E2Eテスト（ブラウザ自動化）
make test-e2e

# リリース前（詳細）
make test-coverage
```

### **E2Eテスト詳細**
```bash
# E2E環境セットアップ
uv run python scripts/setup_e2e_db.py

# ブラウザ別テスト
make test-e2e  # 全ブラウザ
pytest tests/e2e/ --browser=chromium  # Chrome系
pytest tests/e2e/ --browser=firefox   # Firefox
pytest tests/e2e/ --browser=webkit    # Safari系

# ヘッドレス/ヘッドフルモード
pytest tests/e2e/ --headed           # ブラウザ表示あり
pytest tests/e2e/ --video=on         # 動画記録
```

**E2E環境の特徴:**
- **専用DB**: `db_e2e.sqlite3`で本番データと完全分離
- **CORS対応**: 実際のフロントエンド・バックエンド通信テスト
- **自動サーバー起動**: テスト開始時に自動でサーバー起動・停止
- **並列実行**: 複数ブラウザでの同時テスト対応

## 🐳 Docker開発環境

### **コンテナ構成**
- **docker-dev**: Django+FastAPI（SQLite）
- **docker-full**: Django+FastAPI+PostgreSQL+Redis

### **基本的な使い方**
```bash
# 開発環境起動（SQLite）
make docker-dev

# 本格環境起動（PostgreSQL + Redis）
make docker-full

# コンテナ状況確認
docker ps

# ログ確認
docker logs docker-web-1

# 環境停止
make docker-down
```

### **Docker環境のメリット**
- 🏗️ **環境統一**: チーム全員で同じ環境
- 🚀 **高速起動**: 依存関係インストール不要
- 🔒 **隔離性**: ホスト環境に影響しない
- 📦 **本番同等**: PostgreSQL + Redis構成可能

## 🔧 トラブルシューティング

### **よくある問題**

**1. 依存関係エラー**
```bash
# 依存関係再インストール
uv sync --reinstall
```

**2. データベースエラー**
```bash
# マイグレーション初期化
rm db.sqlite3
make migrate
```

**3. 静的ファイルエラー**
```bash
# 静的ファイル再収集
make collectstatic
```

**4. Pre-commit失敗**
```bash
# フォーマット自動修正
make format
git add .
git commit
```

**5. E2Eテスト失敗**
```bash
# E2E専用DB再作成
uv run python scripts/setup_e2e_db.py

# サーバー起動確認
make dev  # 別ターミナルで
pytest tests/e2e/test_basic_e2e.py  # 基本テストのみ
```

**6. Dockerエラー**
```bash
# イメージ・コンテナ完全削除
make docker-clean

# 再ビルド
make docker-build
make docker-dev
```

## 📊 開発メトリクス

### **現在の実績（2025年6月15日時点）**
- ✅ **テスト成功率**: 100% (41/41件)
- ✅ **コードカバレッジ**: 82%
- ✅ **E2Eテスト**: 14件（全成功）
- ✅ **レスポンス時間**: <100ms
- ✅ **エラー率**: 0%
- ✅ **Lint**: 全エラー解消済み

### **品質基準**
| 指標 | 最低基準 | 推奨基準 | 現在値 |
|------|----------|----------|---------|
| テスト成功率 | 95% | 100% | **100%** ✅ |
| コードカバレッジ | 70% | 80%+ | **82%** ✅ |
| E2Eテスト | 5件 | 10件+ | **14件** ✅ |
| Lint エラー | 0 | 0 | **0** ✅ |

## 🔗 関連リンク

### **開発環境**
- **開発サーバー**: http://localhost:8000
- **Django管理画面**: http://localhost:8000/django-admin/
- **Wagtail CMS**: http://localhost:8000/admin/
- **FastAPI仕様書**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### **API エンドポイント**
- **ブログ投稿API**: http://localhost:8000/api/posts/
- **決済API**: http://localhost:8000/api/payments/
- **ヘルスチェック**: http://localhost:8000/api/posts/health

### **開発ツール**
- **テストカバレッジレポート**: ./htmlcov/index.html
- **E2E テストレポート**: ./test-results/
- **ログファイル**: ./django_project/logs/

### **設定ファイル**
- **Django設定**: `django_project/totonoe_template/settings/`
- **E2E設定**: `tests/e2e/conftest.py`
- **Docker設定**: `docker/`
- **品質管理**: `.pre-commit-config.yaml`

## 🚀 次のステップ

開発環境が整ったら、以下のタスクに取り組むことができます：

1. **新機能開発**: `ROADMAP.md`参照
2. **テストカバレッジ向上**: 未カバー部分の特定・テスト追加
3. **パフォーマンス最適化**: レスポンス時間・メモリ使用量改善
4. **CI/CD導入**: GitHub Actions設定
5. **本番環境準備**: PostgreSQL移行・クラウドデプロイ

## 🐛 問題報告・提案

開発中に問題が発生した場合や改善提案がある場合は、適切なissue templateを使用してください：

- 🐛 **バグ報告**: [Bug Report Template](../../issues/new?template=bug_report.md)
- ✨ **新機能提案**: [Feature Request Template](../../issues/new?template=feature_request.md)
- ⚡ **パフォーマンス問題**: [Performance Issue Template](../../issues/new?template=performance_issue.md)
- 🔒 **セキュリティ脆弱性**: [Security Template](../../issues/new?template=security_vulnerability.md)

詳細は `CONTRIBUTING.md` と `ROADMAP.md` を参照してください。

## 🔍 品質管理ガイド

### **段階的品質管理アプローチ**

本プロジェクトでは、開発効率と品質のバランスを取るため、段階的な品質管理を採用しています。

#### **1. 日常開発** - `make lint-core`
```bash
# コアコード（fastapi_app/, blog/）の厳格チェック
make lint-core
```
- **対象**: プロダクションコード (`fastapi_app/`, `blog/`, `main_asgi.py`, `manage.py`)
- **ツール**: flake8, black, ruff (RUF005, RUF012等の現代的品質基準)
- **方針**: 厳格 - 全エラーでビルド停止
- **用途**: 機能実装時、プルリクエスト前

#### **2. 高速確認** - `make lint-quick`
```bash
# ruff + blackの基本チェック（高速）
make lint-quick
```
- **対象**: コアコード + 単体・統合テスト
- **ツール**: ruff (自動修正付き), black
- **方針**: 基本的な品質確保、軽量
- **用途**: コーディング中のリアルタイム確認

#### **3. 完全チェック** - `make lint`
```bash
# pre-commit全フック実行
make lint
```
- **対象**: 全ファイル
- **ツール**: 全品質ツール (trim whitespace, yaml check, black, isort, flake8, pytest-quick)
- **方針**: コミット可能状態の確保
- **用途**: コミット前、プルリクエスト前

#### **4. 統合チェック** - `make lint-full`
```bash
# 全体品質チェック（E2E含む）
make lint-full
```
- **対象**: 全ファイル + E2Eテスト
- **ツール**: lint + lint-e2e (E2Eは警告のみ)
- **方針**: リリース前品質保証
- **用途**: リリース前、CI/CD最終チェック

#### **5. E2E品質** - `make lint-e2e`
```bash
# E2Eテストの緩和チェック（非ブロッキング）
make lint-e2e
```
- **対象**: `tests/e2e/`
- **ツール**: black, flake8 (緩和されたルール)
- **方針**: 警告のみ - ビルドを停止しない
- **用途**: E2Eテスト修正時

### **推奨開発ワークフロー**

```bash
# 1. 開発開始
git checkout -b feature/new-feature

# 2. 機能実装中（リアルタイム品質確認）
make lint-quick     # 高速チェック

# 3. 機能完成時（厳格品質確認）
make lint-core      # コアコード厳格チェック
make test-unit      # 単体テスト

# 4. コミット前（完全品質確認）
make lint           # 全品質チェック
make test           # 全テスト

# 5. プルリクエスト前（統合品質確認）
make lint-full      # E2E含む全体チェック
make test-coverage  # カバレッジ確認
make audit          # セキュリティ監査

# 6. コミット（自動品質チェック）
git add .
git commit -m "feat: 新機能実装"  # pre-commit自動実行
```

### **品質基準**

#### **コアコード品質基準 (厳格)**
- **RUF005**: イテラブルアンパック推奨 (`[*list1, item1]`)
- **RUF012**: Mutableクラス属性の`typing.ClassVar`アノテーション
- **E501/E203**: 行長・空白はblackに委任
- **F403/F405**: Django settings等の必要な箇所で許可
- **Import順序**: isortによる自動整理

#### **E2E品質基準 (緩和)**
- **基本フォーマット**: blackによる最低限整形
- **import/style警告**: 非ブロッキング（警告のみ）
- **プラグマ**: テスト特化の柔軟性を許可

#### **セキュリティ基準**
```bash
# 依存関係脆弱性監査
make audit
```
- **pip-audit**: 既知脆弱性の定期チェック
- **定期実行**: 週次または依存関係更新時

### **トラブルシューティング**

#### **よくある品質エラーと解決方法**

1. **RUF005 (イテラブルアンパック)**
```python
# ❌ 古い書き方
content_panels = Page.content_panels + [FieldPanel("intro")]

# ✅ 現代的な書き方
content_panels = [*Page.content_panels, FieldPanel("intro")]
```

2. **RUF012 (ClassVar)**
```python
# ❌ 警告が出る書き方
class MyModel(Page):
    subpage_types = ["app.MyPage"]

# ✅ 型アノテーション付き
class MyModel(Page):
    subpage_types: ClassVar[list[str]] = ["app.MyPage"]
```

3. **Import順序 (isort)**
```python
# ✅ 自動修正
make format

# または手動実行
uv run isort fastapi_app/ blog/
```

4. **pre-commitでファイル変更された場合**
```bash
# 修正されたファイルを再コミット
git add .
git commit -m "fix: 品質修正適用"
```

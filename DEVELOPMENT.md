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

### **コード品質**
| コマンド | 説明 |
|---------|------|
| `make lint` | コード品質チェック (flake8, ruff) |
| `make format` | コードフォーマット (black, isort, ruff) |
| `make setup-hooks` | Pre-commit hooks インストール |
| `make check-hooks` | Pre-commit hooks 手動実行 |

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

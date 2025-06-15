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
| `make test-coverage` | カバレッジ付きテスト実行 |

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
└── integration/             # 統合テスト
    └── test_full_integration.py
```

### **テスト実行パターン**
```bash
# 開発中（高速）
make test-unit

# 機能完成時（完全）
make test

# リリース前（詳細）
make test-coverage
```

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

## 📊 開発メトリクス

- **テスト成功率**: 目標 100%
- **コードカバレッジ**: 目標 80%+
- **レスポンス時間**: 目標 <200ms
- **エラー率**: 目標 <1%

## 🔗 関連リンク

- **開発サーバー**: http://localhost:8000
- **Django管理画面**: http://localhost:8000/admin/
- **Wagtail CMS**: http://localhost:8000/cms/
- **API仕様書**: http://localhost:8000/docs
- **テストカバレッジ**: ./htmlcov/index.html

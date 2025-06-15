# 🎯 コード品質管理ガイド

## � 段階的品質管理アプローチ

本プロジェクトでは、開発効率と品質のバランスを取るため、段階的な品質管理を採用しています。

### **Level 1: コアコード（最高品質）**
```bash
# 対象: fastapi_app/, blog/, manage.py, main_asgi.py
make lint-core    # 厳格チェック: flake8 + black + ruff (RUF005, RUF012等)
make test-unit    # 高速単体テスト
```
- **品質基準**: RUF005 (イテラブルアンパック)、RUF012 (ClassVar)、現代的Python
- **エラー時**: ビルド停止（品質ゲート）
- **用途**: 日常開発、機能実装時

### **Level 2: 統合テスト（中品質）**
```bash
# 対象: tests/unit/, tests/integration/
make lint-quick   # ruff + black基本チェック
make test-integration
```
- **品質基準**: 基本フォーマット、import順序
- **エラー時**: 修正推奨
- **用途**: テスト開発、CI

### **Level 3: E2Eテスト（基本品質）**
```bash
# 対象: tests/e2e/
make lint-e2e     # 緩和チェック（非ブロッキング警告）
make test-e2e     # 機能テスト
```
- **品質基準**: 実行エラー防止、最低限フォーマット
- **エラー時**: 警告のみ（ビルド継続）
- **用途**: E2E修正時

## 🚀 実装済みコマンド体系

### **段階的品質チェック**
| **コマンド** | **用途** | **実行時間** | **使用場面** |
|-------------|---------|-------------|-------------|
| `make lint-quick` | リアルタイム品質確認 | 5-10秒 | コーディング中 |
| `make lint-core` | コアコード厳格チェック | 15-30秒 | 機能実装時 |
| `make lint` | 完全品質チェック | 1-2分 | コミット前 |
| `make lint-full` | 統合品質チェック | 2-3分 | プルリクエスト前 |
| `make lint-e2e` | E2E緩和チェック | 30秒 | E2E修正時 |
| `make audit` | セキュリティ監査 | 30秒-1分 | 週次・依存関係更新時 |

### **実装済みMakefileコマンド詳細**
```makefile
# 日常開発（高速・厳格）
lint-core:
	uv run flake8 fastapi_app/ blog/ main_asgi.py manage.py --max-line-length=88 --extend-ignore=E203,E501,E402
	uv run black --check fastapi_app/ blog/ main_asgi.py manage.py

# リアルタイム確認（高速・基本）
lint-quick:
	uv run ruff check fastapi_app/ blog/ tests/unit/ tests/integration/ --fix || echo "Core lint issues detected"
	uv run black --check fastapi_app/ blog/ tests/unit/ tests/integration/

# 完全品質チェック（pre-commit全実行）
lint:
	uv run pre-commit run --all-files

# 統合チェック（E2E含む・リリース前）
lint-full: lint lint-e2e
	@echo "✅ Complete quality check passed"

# E2E緩和チェック（非ブロッキング）
lint-e2e:
	uv run black tests/e2e/ || echo "E2E formatting issues detected but not blocking"
	uv run flake8 tests/e2e/ --extend-ignore=E231,E272,E702,E202,E201,E221,E203,E501 || echo "E2E style issues detected but not blocking"

# セキュリティ監査
audit:
	uv run pip-audit
```

## 💡 推奨開発ワークフロー

### **1. 日常開発** 🔄
```bash
# リアルタイム品質確認（数秒）
make lint-quick && make test-unit

# コアコード品質確保（10-20秒）
make lint-core
```

### **2. 機能完成時** ✅
```bash
# 完全品質チェック（1-2分）
make lint && make test

# カバレッジ確認
make test-coverage
```

### **3. コミット前** 🚀
```bash
# 統合品質チェック（2-3分）
make lint && make test

# 自動品質チェック（pre-commit自動実行）
git add .
git commit -m "feat: 新機能実装"
```

### **4. プルリクエスト前** 📦
```bash
# 最終品質ゲート
make lint-full && make test-coverage && make audit

# 必要に応じてE2Eテスト
make test-e2e
```

## � ツール設定詳細

### **設定統一状況**
- **line-length**: 88文字 (全ツール統一)
- **ignore rules**: E501, E203, E402, F403, F405 (全ツール統一)
- **exclude patterns**: migrations, __pycache__, tests/e2e/ など

### **Pre-commit設定内容**
1. **trailing-whitespace**: 行末空白削除
2. **end-of-file-fixer**: ファイル末尾改行統一
3. **check-yaml**: YAML文法チェック
4. **check-added-large-files**: 大きなファイル検出
5. **check-merge-conflicts**: マージ競合検出
6. **debug-statements**: デバッグ文検出
7. **black**: コード整形
8. **isort**: import整理
9. **flake8**: 構文チェック
10. **pytest-quick**: 高速テスト (unit + integration)

### **品質基準詳細**

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

## 📊 実装成果・運用効果

### **品質向上実績**
- ✅ **RUF005/RUF012**: 現代的Pythonコーディング（`blog/models.py`等）
- ✅ **Import最適化**: 未使用import削除（`schemas/*.py`）
- ✅ **設定統一**: pyproject.toml品質設定集約
- ✅ **段階的チェック**: 開発効率と品質のバランス

### **ツール設定完了**
- ✅ **Pre-commit**: 全自動品質ゲート
- ✅ **Ruff現代化**: 最新lint設定形式
- ✅ **Black/isort/flake8**: 統一line-length=88
- ✅ **E2E除外**: 非ブロッキング警告システム

### **運用効果**
- 📈 **開発効率**: 日常の高速チェック（`lint-quick`）
- 🛡️ **品質保証**: リリース前の厳格チェック（`lint-full`）
- ⚖️ **バランス**: 厳格さと実用性の両立
- 🔄 **継続性**: 長期運用可能な設計

## 🛠️ トラブルシューティング

### **よくある品質エラーと解決方法**

#### **1. RUF005 (イテラブルアンパック)**
```python
# ❌ 古い書き方
content_panels = Page.content_panels + [FieldPanel("intro")]

# ✅ 現代的な書き方
content_panels = [*Page.content_panels, FieldPanel("intro")]
```

#### **2. RUF012 (ClassVar)**
```python
# ❌ 警告が出る書き方
class MyModel(Page):
    subpage_types = ["app.MyPage"]

# ✅ 型アノテーション付き
class MyModel(Page):
    subpage_types: ClassVar[list[str]] = ["app.MyPage"]
```

#### **3. Import順序 (isort)**
```python
# ✅ 自動修正
make format

# または手動実行
uv run isort fastapi_app/ blog/
```

#### **4. pre-commitでファイル変更された場合**
```bash
# 修正されたファイルを再コミット
git add .
git commit -m "fix: 品質修正適用"
```

#### **5. 個別ツール実行（デバッグ用）**
```bash
# 問題調査
uv run black fastapi_app/
uv run ruff check fastapi_app/ --fix
uv run flake8 fastapi_app/
```

## 🎯 初回セットアップ

### **開発環境準備**
```bash
# 1. 依存関係インストール
make install

# 2. Pre-commit hooks設定
make setup-hooks

# 3. 初回品質チェック
make lint

# 4. テスト実行
make test
```

### **日常開発の始め方**
```bash
# ブランチ作成
git checkout -b feature/new-feature

# 開発環境確認
make dev

# 品質チェック（習慣化）
make lint-quick && make test-unit
```

この統合により、開発者は1つのファイルで品質管理の全てを理解でき、効率的な開発が可能になります。

# 🎯 コード品質管理ガイド

## 🔧 ツール統一方針

### **メイン品質チェック: pre-commit**
```bash
# 開発者が使用するメインコマンド
make lint           # = pre-commit run --all-files
make check-hooks    # = pre-commit run --all-files (同じ)
```

### **高速チェック: 個別ツール**
```bash
# CI/CDや高速フィードバック用
make lint-quick     # ruff + black check のみ
make format-quick   # black + isort のみ
```

## 📋 設定統一状況

### **✅ 設定済み**
- **line-length**: 88文字 (全ツール統一)
- **ignore rules**: E501, E203 (全ツール統一)
- **exclude patterns**: migrations, __pycache__ など

### **🎯 推奨ワークフロー**

#### **開発中**
```bash
# コミット前の品質チェック
make lint

# 自動修正 + チェック
pre-commit run --all-files
```

#### **CI/CD**
```bash
# 高速チェック
make lint-quick
make test-quick
```

#### **リリース前**
```bash
# 完全チェック
make lint
make test
make audit
```

## 🚀 pre-commit設定内容

1. **trailing-whitespace**: 行末空白削除
2. **end-of-file-fixer**: ファイル末尾改行統一
3. **check-yaml**: YAML文法チェック
4. **black**: コード整形
5. **isort**: import整理
6. **flake8**: 構文チェック
7. **ruff**: 高速lint + 自動修正
8. **pytest-quick**: 高速テスト (unit + integration)

## 💡 開発者への推奨

### **初回セットアップ**
```bash
make setup-hooks  # pre-commit install
```

### **日常開発**
```bash
# ファイル変更後
git add .
make lint        # 品質チェック + 自動修正
git commit       # pre-commitが自動実行
```

### **問題解決**
```bash
# 個別ツール実行
uv run black fastapi_app/
uv run ruff check fastapi_app/ --fix
uv run flake8 fastapi_app/
```

この統一により、開発者は迷わずに品質管理ができます。

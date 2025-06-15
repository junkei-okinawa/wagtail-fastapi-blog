# Contributing to Django + Wa### 🐛 **バグ報告**
- 専用の[Bug Report Template](https://github.com/yourrepo/issues/new?template=bug_report.md)を使用
- 再現手順を詳細に記載
- 環境情報（OS、Python版数等）を含める

### ✨ **新機能提案**
- [Feature Request Template](https://github.com/yourrepo/issues/new?template=feature_request.md)で提案
- 実装前に設計について相談
- ROADMAPとの整合性を確認

### ⚡ **パフォーマンス問題**
- [Performance Issue Template](https://github.com/yourrepo/issues/new?template=performance_issue.md)を使用
- ベンチマーク結果やプロファイリング情報を添付

### 🔒 **セキュリティ脆弱性**
- [Security Vulnerability Template](https://github.com/yourrepo/issues/new?template=security_vulnerability.md)を使用
- 機密情報は直接メール連絡

### 🔧 **コード貢献**
- 以下のエリアで特に歓迎：
  - CI/CD自動化（GitHub Actions）
  - プルリクエストテンプレート作成
  - PostgreSQL移行対応
  - パフォーマンス最適化
  - セキュリティ強化
  - ドキュメント改善・翻訳
  - 新機能開発（`ROADMAP.md`参照）g

🎉 **ご協力いただき、ありがとうございます！**

このプロジェクトへの貢献を歓迎します。以下のガイドラインに従って、効果的な協力をお願いします。

## 🚀 クイックスタート

### 開発環境のセットアップ
```bash
# 1. リポジトリをフォーク・クローン
git clone https://github.com/yourusername/my-wagtail-fastapi-blog.git
cd my-wagtail-fastapi-blog

# 2. 依存関係のインストール
make install

# 3. Pre-commit hooks の設定
make setup-hooks

# 4. 開発サーバーの起動
make dev

# 5. テストの実行
make test
```

## 📋 コントリビューション の種類

### 🐛 **バグ報告**
- [Issues](https://github.com/yourrepo/issues) でバグを報告
- 再現手順を詳細に記載
- 環境情報（OS、Python版数等）を含める

### ✨ **新機能提案**
- [Discussions](https://github.com/yourrepo/discussions) で議論を開始
- 実装前に設計について相談
- ROADMAPとの整合性を確認

### 🔧 **コード貢献**
- 以下のエリアで特に歓迎：
  - CI/CD自動化（GitHub Actions）
  - issue template作成
  - PostgreSQL移行対応
  - パフォーマンス最適化
  - セキュリティ強化
  - ドキュメント改善・翻訳
  - 新機能開発（`ROADMAP.md`参照）

### 🧪 **テスト貢献**
- **単体テスト**: 新機能・既存機能のテスト追加
- **E2Eテスト**: ブラウザ自動化テストの拡充
- **パフォーマンステスト**: 負荷テスト・ベンチマーク
- **セキュリティテスト**: 脆弱性検査・ペネトレーション

## 📝 開発フロー

### **1. Issue作成・確認**
```bash
# 作業前に関連Issueを確認・作成
# 既存の作業と重複しないよう注意
```

### **2. ブランチ作成**
```bash
# feature/issue-number-description の形式
git checkout -b feature/123-add-user-authentication

# 命名規則:
# feature/xxx - 新機能
# fix/xxx - バグ修正
# docs/xxx - ドキュメント
# test/xxx - テスト追加
# refactor/xxx - リファクタリング
```

### **3. 開発・テスト**
```bash
# 開発環境で動作確認
make dev

# または Docker環境で
make docker-dev   # SQLite環境
make docker-full  # PostgreSQL + Redis環境

# コード品質チェック
make lint
make format

# テスト実行
make test           # 単体・統合テスト
make test-e2e       # E2Eテスト
make test-coverage  # カバレッジ付きテスト

# 新機能の場合は適切なテストも追加
# - 単体テスト: tests/unit/
# - 統合テスト: tests/integration/
# - E2Eテスト: tests/e2e/
```

### **4. コミット**
```bash
# Conventional Commitsに従う
git commit -m "feat: ユーザー認証機能を追加

- JWT認証の実装
- ログイン・ログアウト機能
- ユーザー権限管理
- 関連テストを追加

Fixes #123"
```

### **5. プルリクエスト**
- 自己レビューを実施
- テストが全て通ることを確認
- 分かりやすい説明を記載
- 関連Issueにリンク

## 🧪 テスト要件

### **新機能の場合**
- [ ] 単体テスト追加
- [ ] 統合テスト追加
- [ ] E2Eテスト追加（必要に応じて）
- [ ] カバレッジ低下なし

### **バグ修正の場合**
- [ ] 再発防止テスト追加
- [ ] 既存テストが通ること

### **実行コマンド**
```bash
# 全テスト実行
make test

# カバレッジ確認
make test-coverage

# E2Eテスト
make test-e2e
```

## 📊 コード品質基準

### **現在の品質実績（2025年6月15日時点）**
- ✅ **テスト成功率**: 100% (41/41件)
- ✅ **コードカバレッジ**: 82%
- ✅ **E2Eテスト**: 14件（全成功）
- ✅ **Lint エラー**: 0件
- ✅ **型チェック**: pre-commit自動実行

### **必須チェック項目**
- [ ] `make lint` が通る（エラー0件を維持）
- [ ] `make format` が適用済み
- [ ] Pre-commit hooks が設定済み・動作確認
- [ ] 全テストが通る（100%成功率を維持）
- [ ] コードカバレッジが82%以上を維持
- [ ] 新機能にはE2Eテストも追加

### **推奨品質基準**
| 項目 | 最低基準 | 推奨基準 | 現在値 |
|------|----------|----------|---------|
| テスト成功率 | 95% | 100% | **100%** ✅ |
| カバレッジ | 70% | 80%+ | **82%** ✅ |
| E2Eテスト | 5件 | 10件+ | **14件** ✅ |
| レスポンス時間 | <500ms | <200ms | **<100ms** ✅ |
| Lint エラー | 0 | 0 | **0** ✅ |

### **コーディング規約**
- **Python**: PEP 8 準拠（Black, isort, Ruff自動適用）
- **型ヒント**: 推奨（mypy対応）
- **コメント**: 日本語OK、複雑な処理は英語併記
- **変数名**: 英語、分かりやすい名前
- **関数**: 単一責任の原則
- **ファイル**: 適切な分割、依存関係を考慮
- **テスト**: 新機能は単体・統合・E2Eすべて追加

## 🔍 レビュープロセス

### **レビュー観点**
1. **機能**: 要件を満たしているか
2. **品質**: コード品質、テスト品質
3. **パフォーマンス**: 性能に影響がないか
4. **セキュリティ**: 脆弱性がないか
5. **保守性**: 他の開発者が理解しやすいか

### **レビュー者**
- メンテナー（@maintainer）が最終確認
- 他のコントリビューターからのフィードバック歓迎

## 🆘 ヘルプが必要な場合

### **質問・相談**
- [Discussions](https://github.com/yourrepo/discussions) で質問
- Discord（準備中）でリアルタイム相談
- 日本語・英語どちらでもOK

### **メンター制度**
- 初回コントリビューターには メンターをアサイン
- ペアプログラミング・コードレビューサポート

## 🏆 貢献者の表彰

### **Contributors Wall**
- 貢献者はREADMEに記載
- 定期的に感謝のツイート

### **特別な貢献**
- 大きな機能追加・改善にはスペシャルサンクス
- カンファレンス発表での紹介

## 📄 ライセンス

このプロジェクトはMITライセンスです。コントリビューションも同じライセンスになります。

## 🙏 行動規範

### **尊重・協力**
- 建設的なフィードバック
- 多様性の尊重
- 学習意欲のサポート

### **禁止事項**
- 攻撃的・差別的な言動
- スパム・宣伝行為
- 他者の知的財産権侵害

---

**🎉 一緒に素晴らしいブログプラットフォームを作りましょう！**

質問があれば、いつでもお気軽にお聞かせください。

# ERPilot - SAP導入PMO AI

SAP S/4HANA導入プロジェクトのPMO業務をAIで自動化・効率化するSaaS。
月額300万円のSAPコンサルの仕事をAIで代替し、月額50万円で提供。

## 機能

### 1. Fit/Gap分析AI
- チャット形式で業務プロセスをヒアリング
- SAP S/4HANAの9モジュール（SD/MM/PP/FI/CO/WM/QM/PM/HR）の標準機能とマッチング
- 各モジュール20-25の標準機能を定義済み
- Fit率の自動算出、Fit/Gapレポート生成

### 2. PMOダッシュボード
- SAP導入プロジェクトのフェーズ管理（構想→要件定義→設計→開発→テスト→本番稼働→保守）
- タスク・課題・リスクのCRUD管理
- AIによる遅延リスクスコア予測
- 週次ステータスレポート自動生成（日英両言語）

### 3. テストケース自動生成
- SD/MM/FIの標準テストシナリオテンプレート
- 業務要件からのテストケース自動生成
- T-code、入力値、期待結果を含むステップ定義
- UATシナリオの自動生成

### 4. トレーニング資料自動生成
- SAP画面の操作手順書テンプレート（SD受注、MM発注、FI仕訳）
- 業務フロー別マニュアル生成
- 日英両言語対応

### 5. 日英ブリッジ
- SAP専門用語集（50+用語）
- 用語集ベースの自動翻訳
- 会議議事録の要約・翻訳
- LLM連携用プロンプトテンプレート

## 技術スタック

- **Backend**: Python, FastAPI
- **Frontend**: Streamlit
- **Database**: SQLite
- **AI**: Anthropic Claude API (プロンプトテンプレート準備済み)
- **Knowledge Base**: SAP S/4HANA 9モジュール × 20-25標準機能 = 195+機能定義

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# ANTHROPIC_API_KEY を設定

# APIサーバー起動
uvicorn app.main:app --reload --port 8000

# Streamlit UI起動
streamlit run ui/streamlit_app.py

# テスト実行
python -m pytest tests/ -v
```

## API エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| GET | /api/modules | SAPモジュール一覧 |
| GET | /api/modules/{id} | モジュール詳細 |
| POST | /api/projects | プロジェクト作成 |
| POST | /api/fitgap/start | Fit/Gap分析開始 |
| POST | /api/fitgap/answer | 回答送信 |
| POST | /api/tasks | タスク作成 |
| POST | /api/issues | 課題作成 |
| POST | /api/risks | リスク作成 |
| GET | /api/dashboard/{id} | ダッシュボード |
| POST | /api/reports/weekly | 週次レポート生成 |
| POST | /api/testcases/generate | テストケース生成 |
| POST | /api/training/generate | トレーニング資料生成 |
| POST | /api/bridge/translate | 翻訳 |
| GET | /api/bridge/glossary | SAP用語集 |

## ライセンス

Proprietary - All rights reserved.

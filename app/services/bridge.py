"""Japanese-English Bridge Service.

Provides:
- Meeting minutes summarization and translation
- Requirements document translation
- Issue management bilingual support
- SAP-specific terminology glossary
"""

from __future__ import annotations


from app.models import (
    Language,
    MeetingMinutes,
    TranslationRequest,
    TranslationResponse,
)


# ---------------------------------------------------------------------------
# SAP-specific bilingual glossary
# ---------------------------------------------------------------------------
SAP_GLOSSARY: list[dict[str, str]] = [
    {"ja": "受注伝票", "en": "Sales Order", "context": "SD"},
    {"ja": "出荷伝票", "en": "Delivery Document", "context": "SD"},
    {"ja": "請求伝票", "en": "Billing Document", "context": "SD"},
    {"ja": "得意先", "en": "Customer", "context": "SD"},
    {"ja": "品目", "en": "Material", "context": "MM"},
    {"ja": "購買依頼", "en": "Purchase Requisition", "context": "MM"},
    {"ja": "発注伝票", "en": "Purchase Order", "context": "MM"},
    {"ja": "入庫", "en": "Goods Receipt", "context": "MM"},
    {"ja": "出庫", "en": "Goods Issue", "context": "MM"},
    {"ja": "請求照合", "en": "Invoice Verification", "context": "MM"},
    {"ja": "仕入先", "en": "Vendor / Supplier", "context": "MM"},
    {"ja": "総勘定元帳", "en": "General Ledger", "context": "FI"},
    {"ja": "買掛金", "en": "Accounts Payable", "context": "FI"},
    {"ja": "売掛金", "en": "Accounts Receivable", "context": "FI"},
    {"ja": "固定資産", "en": "Fixed Assets", "context": "FI"},
    {"ja": "減価償却", "en": "Depreciation", "context": "FI"},
    {"ja": "勘定科目", "en": "GL Account", "context": "FI"},
    {"ja": "原価センター", "en": "Cost Center", "context": "CO"},
    {"ja": "利益センター", "en": "Profit Center", "context": "CO"},
    {"ja": "内部指図", "en": "Internal Order", "context": "CO"},
    {"ja": "製造指図", "en": "Production Order", "context": "PP"},
    {"ja": "部品表", "en": "Bill of Materials (BOM)", "context": "PP"},
    {"ja": "作業手順", "en": "Routing", "context": "PP"},
    {"ja": "所要量計画", "en": "Material Requirements Planning (MRP)", "context": "PP"},
    {"ja": "検査ロット", "en": "Inspection Lot", "context": "QM"},
    {"ja": "品質通知", "en": "Quality Notification", "context": "QM"},
    {"ja": "保全指図", "en": "Maintenance Order", "context": "PM"},
    {"ja": "予防保全", "en": "Preventive Maintenance", "context": "PM"},
    {"ja": "移送依頼", "en": "Transport Request", "context": "BASIS"},
    {"ja": "本番稼働", "en": "Go-Live", "context": "Project"},
    {"ja": "要件定義", "en": "Requirements Definition", "context": "Project"},
    {"ja": "基本設計", "en": "Basic Design", "context": "Project"},
    {"ja": "詳細設計", "en": "Detailed Design", "context": "Project"},
    {"ja": "単体テスト", "en": "Unit Test", "context": "Project"},
    {"ja": "結合テスト", "en": "Integration Test", "context": "Project"},
    {"ja": "受入テスト", "en": "User Acceptance Test (UAT)", "context": "Project"},
    {"ja": "カスタマイズ", "en": "Configuration / Customizing", "context": "SAP"},
    {"ja": "アドオン", "en": "Add-on / Custom Development", "context": "SAP"},
    {"ja": "トランザクションコード", "en": "Transaction Code (T-code)", "context": "SAP"},
    {"ja": "ユーザ出口", "en": "User Exit / BAdI", "context": "SAP"},
    {"ja": "Fit/Gap分析", "en": "Fit/Gap Analysis", "context": "Project"},
    {"ja": "カットオーバー", "en": "Cutover", "context": "Project"},
    {"ja": "データ移行", "en": "Data Migration", "context": "Project"},
    {"ja": "権限設計", "en": "Authorization Design", "context": "BASIS"},
    {"ja": "組織構造", "en": "Organizational Structure", "context": "SAP"},
    {"ja": "会社コード", "en": "Company Code", "context": "FI"},
    {"ja": "プラント", "en": "Plant", "context": "MM/PP"},
    {"ja": "保管場所", "en": "Storage Location", "context": "MM"},
    {"ja": "販売組織", "en": "Sales Organization", "context": "SD"},
    {"ja": "流通チャネル", "en": "Distribution Channel", "context": "SD"},
    {"ja": "製品部門", "en": "Division", "context": "SD"},
    {"ja": "購買組織", "en": "Purchasing Organization", "context": "MM"},
    {"ja": "購買グループ", "en": "Purchasing Group", "context": "MM"},
]


def get_glossary(context: str | None = None) -> list[dict[str, str]]:
    """Get the SAP bilingual glossary, optionally filtered by context."""
    if context is None:
        return SAP_GLOSSARY
    context_upper = context.upper()
    return [g for g in SAP_GLOSSARY if context_upper in g["context"].upper()]


def translate_with_glossary(
    text: str,
    source_lang: Language,
    target_lang: Language,
) -> tuple[str, list[dict[str, str]]]:
    """Apply glossary-based term replacement.

    Returns the text with glossary terms replaced and the list of terms used.
    This is a simple prototype; production uses LLM with glossary context.
    """
    used_terms: list[dict[str, str]] = []
    result = text

    src_key = "ja" if source_lang == Language.JA else "en"
    tgt_key = "en" if source_lang == Language.JA else "ja"

    for term in SAP_GLOSSARY:
        if term[src_key] in result:
            result = result.replace(term[src_key], term[tgt_key])
            used_terms.append(term)

    return result, used_terms


def translate_text(request: TranslationRequest) -> TranslationResponse:
    """Translate text between Japanese and English.

    Prototype uses glossary replacement. Production integrates LLM.
    """
    translated, glossary_used = translate_with_glossary(
        request.text, request.source_language, request.target_language
    )
    return TranslationResponse(
        original_text=request.text,
        translated_text=translated,
        source_language=request.source_language,
        target_language=request.target_language,
        glossary_used=glossary_used,
    )


def summarize_meeting(
    project_id: str,
    title: str,
    date: str,
    attendees: list[str],
    raw_text: str,
    original_language: Language = Language.JA,
) -> MeetingMinutes:
    """Summarize meeting minutes and provide bilingual output.

    Prototype extracts key patterns. Production uses LLM.
    """
    # Simple extraction for prototype
    lines = raw_text.strip().split("\n")
    action_items_raw = [
        line.strip().lstrip("- ").lstrip("* ")
        for line in lines
        if any(kw in line for kw in ["TODO", "アクション", "Action", "対応", "確認"])
    ]

    # Create basic summary
    word_count = len(raw_text)
    summary_ja = f"会議「{title}」の議事録 ({date})。参加者: {', '.join(attendees)}。内容: {word_count}文字のディスカッション。"
    summary_en = f"Meeting minutes for '{title}' ({date}). Attendees: {', '.join(attendees)}. Content: discussion of {word_count} characters."

    # Translate action items
    action_items_ja = action_items_raw if original_language == Language.JA else []
    action_items_en = action_items_raw if original_language == Language.EN else []

    if original_language == Language.JA:
        for item in action_items_raw:
            translated, _ = translate_with_glossary(item, Language.JA, Language.EN)
            action_items_en.append(translated)
    else:
        for item in action_items_raw:
            translated, _ = translate_with_glossary(item, Language.EN, Language.JA)
            action_items_ja.append(translated)

    return MeetingMinutes(
        project_id=project_id,
        title=title,
        date=date,
        attendees=attendees,
        original_text=raw_text,
        original_language=original_language,
        summary_ja=summary_ja,
        summary_en=summary_en,
        action_items_ja=action_items_ja,
        action_items_en=action_items_en,
    )


def build_translation_prompt(
    text: str,
    source_lang: Language,
    target_lang: Language,
    document_type: str = "general",
) -> str:
    """Build prompt for LLM-based translation."""
    glossary_text = "\n".join(
        f"- {g['ja']} = {g['en']}" for g in SAP_GLOSSARY
    )

    source_name = "日本語" if source_lang == Language.JA else "English"
    target_name = "English" if source_lang == Language.JA else "日本語"

    return f"""あなたはSAP導入プロジェクトの専門翻訳者です。
以下のテキストを{source_name}から{target_name}に翻訳してください。

## 文書タイプ: {document_type}

## SAP用語集（必ずこの訳語を使用してください）
{glossary_text}

## 翻訳元テキスト
{text}

## 翻訳ルール
1. SAP用語は上記用語集の訳語を使用する
2. 技術的な正確性を最優先する
3. 文書タイプに適した文体を使用する
4. 略語はそのまま残す（例: SD, MM, FI, T-code）
5. 固有名詞（会社名、人名）はそのまま残す
"""


def build_meeting_summary_prompt(
    raw_text: str,
    original_language: Language = Language.JA,
) -> str:
    """Build prompt for LLM-based meeting summarization."""
    return f"""あなたはSAP導入プロジェクトのPMOアシスタントです。
以下の会議メモから、構造化された議事録を日本語と英語の両方で作成してください。

## 会議メモ
{raw_text}

## 出力形式
### 1. サマリー（日本語 / Summary in English）
- 3-5行で会議の概要

### 2. 主要な議論ポイント / Key Discussion Points
- 箇条書きで主要な議論ポイント（日英両方）

### 3. 決定事項 / Decisions Made
- 箇条書き（日英両方）

### 4. アクションアイテム / Action Items
- 担当者、期限を含める（日英両方）
- 形式: [担当者] [内容] [期限]

### 5. 次回会議予定 / Next Meeting
"""

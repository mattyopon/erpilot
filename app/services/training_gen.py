"""Training Material Auto-Generation Service.

Generates SAP operation manuals and training documents:
- Step-by-step procedure guides
- Business flow manuals
- Bilingual (Japanese/English) support
"""

from __future__ import annotations

from typing import Any

from app.knowledge.sap_modules import get_functions_for_module, get_module
from app.models import Language, TrainingMaterial, TrainingStep


# ---------------------------------------------------------------------------
# Standard training templates per process
# ---------------------------------------------------------------------------
_TRAINING_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "SD-ORDER": {
        "title": "Sales Order Creation Procedure",
        "title_ja": "販売伝票登録 操作手順書",
        "target": "SD End User",
        "prerequisites": "SAP GUI access, VA01 authorization, Customer/Material master maintained",
        "steps": [
            {"instruction": "Open transaction VA01 (Create Sales Order)",
             "instruction_ja": "トランザクション VA01（販売伝票登録）を開く",
             "t_code": "VA01", "screen_area": "Command field",
             "field_actions": ["Enter VA01 in command field", "Press Enter"],
             "tips": "You can also use menu: Logistics > Sales > Order > Create"},
            {"instruction": "Enter order header data",
             "instruction_ja": "伝票ヘッダ情報を入力する",
             "t_code": "VA01", "screen_area": "Initial screen",
             "field_actions": ["Order Type: OR (Standard Order)", "Sales Organization", "Distribution Channel", "Division"],
             "tips": "Order type determines the document flow and pricing"},
            {"instruction": "Enter sold-to party and purchase order number",
             "instruction_ja": "受注先と客先発注番号を入力する",
             "t_code": "VA01", "screen_area": "Header data",
             "field_actions": ["Sold-to party: Customer number", "PO Number: Customer's PO reference"],
             "tips": "Ship-to party defaults from customer master"},
            {"instruction": "Enter line items",
             "instruction_ja": "明細情報を入力する",
             "t_code": "VA01", "screen_area": "Item overview",
             "field_actions": ["Material: Material number", "Order Quantity", "Plant"],
             "tips": "Pricing is determined automatically from condition records"},
            {"instruction": "Check availability and pricing",
             "instruction_ja": "在庫引当と価格を確認する",
             "t_code": "VA01", "screen_area": "Item detail",
             "field_actions": ["Check ATP result", "Verify net price"],
             "tips": "Yellow traffic light indicates partial availability"},
            {"instruction": "Save the sales order",
             "instruction_ja": "販売伝票を保存する",
             "t_code": "VA01", "screen_area": "Toolbar",
             "field_actions": ["Click Save button or Ctrl+S"],
             "tips": "Note the order number displayed in the status bar"},
        ],
    },
    "MM-PO": {
        "title": "Purchase Order Creation Procedure",
        "title_ja": "発注伝票登録 操作手順書",
        "target": "MM End User / Buyer",
        "prerequisites": "SAP GUI access, ME21N authorization, Vendor/Material master maintained",
        "steps": [
            {"instruction": "Open transaction ME21N (Create Purchase Order)",
             "instruction_ja": "トランザクション ME21N（発注伝票登録）を開く",
             "t_code": "ME21N", "screen_area": "Command field",
             "field_actions": ["Enter ME21N in command field", "Press Enter"],
             "tips": "ME21N is the new PO creation screen"},
            {"instruction": "Enter PO header data",
             "instruction_ja": "発注ヘッダ情報を入力する",
             "t_code": "ME21N", "screen_area": "Header",
             "field_actions": ["Vendor number", "Purchasing Organization", "Purchasing Group", "Company Code"],
             "tips": "Payment terms default from vendor master"},
            {"instruction": "Enter line items",
             "instruction_ja": "明細情報を入力する",
             "t_code": "ME21N", "screen_area": "Item overview",
             "field_actions": ["Material", "PO Quantity", "Delivery Date", "Net Price", "Plant"],
             "tips": "Info records and contracts can be referenced for pricing"},
            {"instruction": "Check and save",
             "instruction_ja": "確認して保存する",
             "t_code": "ME21N", "screen_area": "Toolbar",
             "field_actions": ["Review totals", "Click Check button", "Click Save"],
             "tips": "Release strategy may require approval before the PO is active"},
        ],
    },
    "FI-POSTING": {
        "title": "GL Journal Entry Procedure",
        "title_ja": "仕訳伝票登録 操作手順書",
        "target": "FI End User / Accountant",
        "prerequisites": "SAP GUI access, FB50 authorization",
        "steps": [
            {"instruction": "Open transaction FB50 (G/L Account Document Entry)",
             "instruction_ja": "トランザクション FB50（G/L勘定伝票入力）を開く",
             "t_code": "FB50", "screen_area": "Command field",
             "field_actions": ["Enter FB50 in command field", "Press Enter"],
             "tips": "FB50 is the simplified GL posting screen"},
            {"instruction": "Enter document header",
             "instruction_ja": "伝票ヘッダを入力する",
             "t_code": "FB50", "screen_area": "Header",
             "field_actions": ["Document Date", "Posting Date", "Company Code", "Currency", "Reference"],
             "tips": "Posting period must be open"},
            {"instruction": "Enter debit and credit line items",
             "instruction_ja": "借方・貸方の明細を入力する",
             "t_code": "FB50", "screen_area": "Line items",
             "field_actions": ["GL Account", "D/C indicator", "Amount", "Cost Center (if required)"],
             "tips": "Debit and credit totals must balance"},
            {"instruction": "Simulate and post",
             "instruction_ja": "シミュレーションして転記する",
             "t_code": "FB50", "screen_area": "Toolbar",
             "field_actions": ["Click Simulate", "Review posting preview", "Click Post"],
             "tips": "Document number displayed in status bar after posting"},
        ],
    },
}


def get_available_templates() -> list[dict[str, str]]:
    """Get list of available training templates."""
    return [
        {"id": tid, "title": t["title"], "title_ja": t["title_ja"]}
        for tid, t in _TRAINING_TEMPLATES.items()
    ]


def generate_training_material(
    project_id: str,
    module_id: str,
    process_name: str,
    target_audience: str = "end_user",
    language: Language = Language.JA,
) -> TrainingMaterial:
    """Generate training material for a SAP process.

    Uses templates for known processes, generates basic structure for others.
    """
    module_id = module_id.upper()

    # Try to find a matching template
    template_key = f"{module_id}-{process_name.upper()}"
    template = _TRAINING_TEMPLATES.get(template_key)

    if template:
        return _from_template(project_id, module_id, template, target_audience, language)

    # Generate basic training material from module knowledge
    return _generate_basic(project_id, module_id, process_name, target_audience, language)


def _from_template(
    project_id: str,
    module_id: str,
    template: dict[str, Any],
    target_audience: str,
    language: Language,
) -> TrainingMaterial:
    """Create training material from a predefined template."""
    steps = [
        TrainingStep(
            step_number=i + 1,
            instruction=s["instruction"],
            instruction_ja=s["instruction_ja"],
            t_code=s["t_code"],
            screen_area=s["screen_area"],
            field_actions=s["field_actions"],
            tips=s["tips"],
        )
        for i, s in enumerate(template["steps"])
    ]

    return TrainingMaterial(
        project_id=project_id,
        module_id=module_id,
        title=template["title"],
        title_ja=template["title_ja"],
        description=f"Step-by-step guide for {template['title']}",
        target_audience=target_audience,
        prerequisites=template["prerequisites"],
        steps=steps,
        language=language,
    )


def _generate_basic(
    project_id: str,
    module_id: str,
    process_name: str,
    target_audience: str,
    language: Language,
) -> TrainingMaterial:
    """Generate basic training material from module knowledge."""
    functions = get_functions_for_module(module_id)
    mod = get_module(module_id)
    module_name_ja = mod["name_ja"] if mod else module_id

    # Find relevant functions by process name keywords
    relevant = [
        f for f in functions
        if process_name.lower() in f["name"].lower()
        or process_name in f["name_ja"]
        or process_name.lower() in f.get("category", "").lower()
    ]

    if not relevant:
        # Use first 5 core functions
        relevant = functions[:5]

    steps = []
    for i, func in enumerate(relevant):
        t_codes = func.get("t_codes", [])
        main_tcode = t_codes[0] if t_codes else ""
        steps.append(TrainingStep(
            step_number=i + 1,
            instruction=f"Execute {func['name']}: {func['description']}",
            instruction_ja=f"{func['name_ja']}を実行: {func['description']}",
            t_code=main_tcode,
            screen_area="Main screen",
            field_actions=[f"Use T-code: {main_tcode}"],
            tips=f"Related T-codes: {', '.join(t_codes)}",
        ))

    return TrainingMaterial(
        project_id=project_id,
        module_id=module_id,
        title=f"{module_id} - {process_name} Procedure",
        title_ja=f"{module_name_ja} - {process_name} 操作手順書",
        description=f"Generated procedure guide for {process_name}",
        target_audience=target_audience,
        prerequisites=f"SAP GUI access, {module_id} module authorization",
        steps=steps,
        language=language,
    )


def build_training_prompt(
    module_id: str,
    process_name: str,
    target_audience: str = "end_user",
    language: Language = Language.JA,
) -> str:
    """Build prompt for LLM-based training material generation."""
    mod = get_module(module_id)
    if mod is None:
        return ""

    functions_summary = "\n".join(
        f"- {f['id']}: {f['name_ja']} (T-code: {', '.join(f.get('t_codes', []))})"
        for f in mod["standard_functions"]
    )

    lang_instruction = "日本語で" if language == Language.JA else "in English"

    return f"""あなたはSAP S/4HANAのトレーニング資料作成の専門家です。
以下の条件で操作手順書を{lang_instruction}作成してください。

## モジュール: {mod['name_ja']} ({module_id})
## 対象プロセス: {process_name}
## 対象読者: {target_audience}

## SAP {module_id} 標準機能
{functions_summary}

## 出力形式
### タイトル
### 前提条件
### 手順
各ステップに以下を含めてください:
1. ステップ番号
2. 操作内容（日本語/英語）
3. トランザクションコード
4. 画面エリア
5. フィールドの操作（具体的な入力値の例）
6. 注意事項・ヒント

### 確認ポイント
### よくある質問（FAQ）
"""

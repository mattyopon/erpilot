"""Fit/Gap Analysis AI Service.

Conducts interactive Fit/Gap analysis by:
1. Asking structured questions about business processes per SAP module
2. Matching answers against SAP standard functions AND SAP Best Practices Scope Items
3. Generating a Fit/Gap analysis report with fit rate
4. Applying Fit-to-Standard methodology (SAP Activate) for gap resolution

Enhanced in v2 to use SAP Best Practices Scope Items as the primary matching basis,
with Fit-to-Standard challenge questions and gap resolution recommendations.
"""

from __future__ import annotations

from typing import Any

from app.knowledge.sap_modules import get_functions_for_module, get_module
from app.models import (
    FitGapItem,
    FitGapReport,
    FitGapSession,
    FitGapStatus,
)

# ---------------------------------------------------------------------------
# Module-specific interview questions
# ---------------------------------------------------------------------------
INTERVIEW_QUESTIONS: dict[str, list[dict[str, str]]] = {
    "SD": [
        {"id": "q1", "ja": "受注から出荷までの業務フローを教えてください。", "en": "Describe your order-to-delivery process."},
        {"id": "q2", "ja": "見積プロセスはありますか？見積の有効期限管理は必要ですか？", "en": "Do you have a quotation process? Do you need validity period management?"},
        {"id": "q3", "ja": "特殊な価格設定ルール（数量割引、顧客別価格等）はありますか？", "en": "Do you have special pricing rules (volume discounts, customer-specific prices)?"},
        {"id": "q4", "ja": "与信管理は行っていますか？与信チェックのタイミングは？", "en": "Do you perform credit checks? At what point in the process?"},
        {"id": "q5", "ja": "出荷時のピッキング・梱包プロセスを教えてください。", "en": "Describe your picking and packing process at shipment."},
        {"id": "q6", "ja": "返品処理はどのように行っていますか？", "en": "How do you handle returns?"},
        {"id": "q7", "ja": "請求書のパターンは？（都度請求、締め請求、マイルストーン請求等）", "en": "What are your billing patterns? (Per delivery, periodic, milestone-based?)"},
        {"id": "q8", "ja": "海外取引はありますか？通貨や貿易条件は？", "en": "Do you have international transactions? What currencies and trade terms?"},
        {"id": "q9", "ja": "直送（サプライヤーから顧客への直接出荷）はありますか？", "en": "Do you have drop shipments (direct from supplier to customer)?"},
        {"id": "q10", "ja": "リベートやボリュームディスカウント契約はありますか？", "en": "Do you have rebate or volume discount agreements?"},
        {"id": "q11", "ja": "会社間取引（グループ内販売）はありますか？", "en": "Do you have intercompany sales (within group)?"},
        {"id": "q12", "ja": "委託販売や消化仕入のプロセスはありますか？", "en": "Do you use consignment sales processes?"},
    ],
    "MM": [
        {"id": "q1", "ja": "購買依頼から発注までのフローを教えてください。承認プロセスは？", "en": "Describe your purchase requisition to PO flow. What approval process?"},
        {"id": "q2", "ja": "仕入先の選定・評価プロセスはありますか？", "en": "Do you have a vendor selection/evaluation process?"},
        {"id": "q3", "ja": "基本契約（年間契約等）の管理は必要ですか？", "en": "Do you need to manage framework agreements (annual contracts)?"},
        {"id": "q4", "ja": "入庫検品のプロセスを教えてください。", "en": "Describe your goods receipt inspection process."},
        {"id": "q5", "ja": "請求照合（3点照合: 発注・入庫・請求書）は行っていますか？", "en": "Do you perform 3-way matching (PO, GR, invoice)?"},
        {"id": "q6", "ja": "在庫評価方法は？（標準原価、移動平均等）", "en": "What is your inventory valuation method? (Standard cost, moving average?)"},
        {"id": "q7", "ja": "ロット管理やシリアル番号管理は必要ですか？", "en": "Do you need batch or serial number management?"},
        {"id": "q8", "ja": "棚卸のプロセスは？（年次、循環棚卸等）", "en": "What is your physical inventory process? (Annual, cycle count?)"},
        {"id": "q9", "ja": "外注加工（支給材を含む）はありますか？", "en": "Do you have subcontracting (with provided materials)?"},
        {"id": "q10", "ja": "サービス調達（工事、コンサルティング等）のプロセスはありますか？", "en": "Do you procure services (construction, consulting)?"},
        {"id": "q11", "ja": "自動発注（MRP連動）は必要ですか？", "en": "Do you need automatic PO generation (MRP-driven)?"},
        {"id": "q12", "ja": "購買承認フロー（金額別、部門別）を教えてください。", "en": "Describe your purchase approval workflow (by amount, department)."},
    ],
    "FI": [
        {"id": "q1", "ja": "勘定科目体系はどのようになっていますか？（IFRS/日本基準等）", "en": "What is your chart of accounts structure? (IFRS/J-GAAP?)"},
        {"id": "q2", "ja": "買掛金管理のプロセスを教えてください。支払サイクルは？", "en": "Describe your AP process. What is your payment cycle?"},
        {"id": "q3", "ja": "売掛金管理と入金消込のプロセスは？", "en": "Describe your AR and incoming payment clearing process."},
        {"id": "q4", "ja": "固定資産管理は必要ですか？減価償却方法は？", "en": "Do you need asset management? What depreciation methods?"},
        {"id": "q5", "ja": "銀行口座管理と入出金管理のプロセスは？", "en": "Describe your bank account and cash management process."},
        {"id": "q6", "ja": "月次決算のプロセスと締め日程を教えてください。", "en": "Describe your monthly closing process and timeline."},
        {"id": "q7", "ja": "外貨取引はありますか？為替評価は必要ですか？", "en": "Do you have foreign currency transactions? Need revaluation?"},
        {"id": "q8", "ja": "会社間取引（内部取引消去）はありますか？", "en": "Do you have intercompany transactions (elimination)?"},
        {"id": "q9", "ja": "税務処理の要件は？（消費税、源泉税、インボイス制度等）", "en": "What are your tax requirements? (Consumption tax, withholding, invoice system?)"},
        {"id": "q10", "ja": "自動支払プログラムは必要ですか？支払方法は？", "en": "Do you need automatic payment program? What payment methods?"},
        {"id": "q11", "ja": "督促管理は必要ですか？", "en": "Do you need dunning management?"},
        {"id": "q12", "ja": "財務諸表のフォーマットと報告要件を教えてください。", "en": "Describe your financial statement format and reporting requirements."},
    ],
    "CO": [
        {"id": "q1", "ja": "原価センターの構成を教えてください。", "en": "Describe your cost center structure."},
        {"id": "q2", "ja": "原価配分のルールは？（配賦基準等）", "en": "What are your cost allocation rules?"},
        {"id": "q3", "ja": "利益センター管理は必要ですか？", "en": "Do you need profit center accounting?"},
        {"id": "q4", "ja": "製品原価計算は必要ですか？（標準原価、実際原価）", "en": "Do you need product costing? (Standard/actual?)"},
        {"id": "q5", "ja": "内部指図の用途は？（プロジェクト、修繕等）", "en": "What do you use internal orders for? (Projects, maintenance?)"},
        {"id": "q6", "ja": "予算管理は必要ですか？予算超過チェックは？", "en": "Do you need budgeting? Budget availability control?"},
        {"id": "q7", "ja": "収益性分析（CO-PA）は必要ですか？分析軸は？", "en": "Do you need profitability analysis? What dimensions?"},
        {"id": "q8", "ja": "月次決算での間接費配賦プロセスは？", "en": "Describe your overhead allocation in monthly closing."},
        {"id": "q9", "ja": "移転価格の管理は必要ですか？", "en": "Do you need transfer pricing management?"},
        {"id": "q10", "ja": "管理会計レポートの要件を教えてください。", "en": "Describe your management accounting reporting requirements."},
    ],
    "PP": [
        {"id": "q1", "ja": "生産計画のプロセスを教えてください。（見込生産/受注生産）", "en": "Describe your production planning. (Make-to-stock/Make-to-order?)"},
        {"id": "q2", "ja": "MRP（資材所要量計画）は使用していますか？", "en": "Do you use MRP?"},
        {"id": "q3", "ja": "BOM（部品表）の管理は必要ですか？何階層？", "en": "Do you need BOM management? How many levels?"},
        {"id": "q4", "ja": "作業手順（ルーティング）の管理は必要ですか？", "en": "Do you need routing management?"},
        {"id": "q5", "ja": "製造指図の運用プロセスを教えてください。", "en": "Describe your production order operation process."},
        {"id": "q6", "ja": "能力計画（キャパシティプランニング）は必要ですか？", "en": "Do you need capacity planning?"},
        {"id": "q7", "ja": "繰返生産（大量生産）のプロセスはありますか？", "en": "Do you have repetitive manufacturing?"},
        {"id": "q8", "ja": "プロセス製造（レシピベース）はありますか？", "en": "Do you have process manufacturing (recipe-based)?"},
        {"id": "q9", "ja": "安全在庫の管理方法は？", "en": "How do you manage safety stock?"},
        {"id": "q10", "ja": "生産実績の確認・報告プロセスは？", "en": "Describe your production confirmation/reporting process."},
    ],
    "WM": [
        {"id": "q1", "ja": "入荷から格納までのプロセスを教えてください。", "en": "Describe your inbound to putaway process."},
        {"id": "q2", "ja": "倉庫のロケーション管理方法は？", "en": "How do you manage warehouse locations?"},
        {"id": "q3", "ja": "ピッキング方法は？（個別、ウェーブ、バッチ等）", "en": "What is your picking method? (Individual, wave, batch?)"},
        {"id": "q4", "ja": "棚卸のプロセスを教えてください。", "en": "Describe your physical inventory process."},
        {"id": "q5", "ja": "倉庫間の在庫移動はありますか？", "en": "Do you have inter-warehouse stock transfers?"},
        {"id": "q6", "ja": "危険物の取り扱いはありますか？", "en": "Do you handle hazardous materials?"},
        {"id": "q7", "ja": "クロスドッキングのプロセスはありますか？", "en": "Do you have cross-docking?"},
        {"id": "q8", "ja": "モバイルデバイス（ハンディターミナル）は使用していますか？", "en": "Do you use mobile devices (handheld terminals)?"},
        {"id": "q9", "ja": "ヤード管理（トラック・バースの管理）は必要ですか？", "en": "Do you need yard management (truck/dock management)?"},
        {"id": "q10", "ja": "返品の倉庫受入プロセスは？", "en": "Describe your returns receiving process."},
    ],
    "QM": [
        {"id": "q1", "ja": "品質検査のプロセスを教えてください。（受入検査、工程内検査等）", "en": "Describe your quality inspection process. (Incoming, in-process?)"},
        {"id": "q2", "ja": "検査項目と検査基準の管理方法は？", "en": "How do you manage inspection items and criteria?"},
        {"id": "q3", "ja": "不良品の処理プロセスは？", "en": "Describe your defective product handling process."},
        {"id": "q4", "ja": "品質通知（クレーム管理）のプロセスは？", "en": "Describe your quality notification (complaint) process."},
        {"id": "q5", "ja": "是正措置・予防措置（CAPA）の管理は？", "en": "How do you manage CAPA?"},
        {"id": "q6", "ja": "品質証明書の発行は必要ですか？", "en": "Do you need to issue quality certificates?"},
        {"id": "q7", "ja": "仕入先の品質評価は行っていますか？", "en": "Do you perform vendor quality evaluation?"},
        {"id": "q8", "ja": "監査管理（内部/外部）のプロセスは？", "en": "Describe your audit management process (internal/external)."},
        {"id": "q9", "ja": "統計的品質管理（管理図等）は使用していますか？", "en": "Do you use statistical quality control (control charts)?"},
        {"id": "q10", "ja": "サンプリング検査の基準は？", "en": "What are your sampling inspection criteria?"},
    ],
    "PM": [
        {"id": "q1", "ja": "設備管理のプロセスを教えてください。", "en": "Describe your equipment management process."},
        {"id": "q2", "ja": "予防保全の計画はありますか？（時間ベース/状態ベース）", "en": "Do you have preventive maintenance? (Time-based/condition-based?)"},
        {"id": "q3", "ja": "保全指図の運用プロセスは？", "en": "Describe your maintenance order process."},
        {"id": "q4", "ja": "故障時の対応プロセスは？", "en": "Describe your breakdown response process."},
        {"id": "q5", "ja": "保全のコスト管理は必要ですか？", "en": "Do you need maintenance cost tracking?"},
        {"id": "q6", "ja": "スペアパーツの管理方法は？", "en": "How do you manage spare parts?"},
        {"id": "q7", "ja": "保全履歴の管理と分析は？", "en": "How do you manage and analyze maintenance history?"},
        {"id": "q8", "ja": "設備のKPI（MTBF、MTTR等）は管理していますか？", "en": "Do you track equipment KPIs (MTBF, MTTR)?"},
        {"id": "q9", "ja": "外部委託保全のプロセスは？", "en": "Describe your outsourced maintenance process."},
        {"id": "q10", "ja": "保証管理は必要ですか？", "en": "Do you need warranty management?"},
    ],
    "HR": [
        {"id": "q1", "ja": "組織構造の管理方法を教えてください。", "en": "Describe your organizational structure management."},
        {"id": "q2", "ja": "人事管理のプロセスは？（採用～退職）", "en": "Describe your HR process. (Hire to retire)"},
        {"id": "q3", "ja": "勤怠管理のプロセスを教えてください。", "en": "Describe your time management process."},
        {"id": "q4", "ja": "給与計算のプロセスは？（社会保険、税金控除等）", "en": "Describe your payroll process. (Social insurance, tax deductions?)"},
        {"id": "q5", "ja": "休暇管理の要件は？", "en": "What are your leave management requirements?"},
        {"id": "q6", "ja": "研修・教育管理のプロセスは？", "en": "Describe your training management process."},
        {"id": "q7", "ja": "人事考課・目標管理のプロセスは？", "en": "Describe your performance appraisal/goal management process."},
        {"id": "q8", "ja": "出張管理・経費精算のプロセスは？", "en": "Describe your travel and expense management process."},
        {"id": "q9", "ja": "従業員セルフサービスは必要ですか？", "en": "Do you need employee self-service?"},
        {"id": "q10", "ja": "人事レポートの要件を教えてください。", "en": "Describe your HR reporting requirements."},
    ],
}


def get_questions_for_module(module_id: str) -> list[dict[str, str]]:
    """Get interview questions for a specific SAP module."""
    return INTERVIEW_QUESTIONS.get(module_id.upper(), [])


def start_session(project_id: str, module_id: str) -> FitGapSession:
    """Start a new Fit/Gap analysis session."""
    module_id = module_id.upper()
    session = FitGapSession(
        project_id=project_id,
        module_id=module_id,
    )
    questions = get_questions_for_module(module_id)
    if questions:
        first_q = questions[0]
        session.messages.append({
            "role": "assistant",
            "content": first_q["ja"],
        })
    return session


def process_answer(session: FitGapSession, answer: str) -> FitGapSession:
    """Process user's answer and advance to next question or complete."""
    module_id = session.module_id.upper()
    questions = get_questions_for_module(module_id)

    # Record the answer
    q_index = session.current_question_index
    if q_index < len(questions):
        q_id = questions[q_index]["id"]
        session.answers[q_id] = answer
        session.messages.append({"role": "user", "content": answer})

    # Move to next question
    session.current_question_index = q_index + 1

    if session.current_question_index < len(questions):
        next_q = questions[session.current_question_index]
        session.messages.append({
            "role": "assistant",
            "content": next_q["ja"],
        })
    else:
        session.is_complete = True
        # Generate the report
        session.report = _generate_report(session)
        session.messages.append({
            "role": "assistant",
            "content": f"ヒアリングが完了しました。Fit/Gap分析レポートを生成しました。\n\n"
                       f"Fit率: {session.report.fit_rate}%\n"
                       f"Fit: {session.report.fit_count}件 / "
                       f"Partial Fit: {session.report.partial_fit_count}件 / "
                       f"Gap: {session.report.gap_count}件",
        })

    return session


def _generate_report(session: FitGapSession) -> FitGapReport:
    """Generate Fit/Gap report based on session answers.

    Uses rule-based matching against SAP standard functions.
    In production, this would be augmented with LLM analysis.
    """
    module_id = session.module_id.upper()
    mod = get_module(module_id)
    if mod is None:
        return FitGapReport(
            project_id=session.project_id,
            module_id=module_id,
            module_name="Unknown",
            module_name_ja="不明",
        )

    functions = get_functions_for_module(module_id)
    items: list[FitGapItem] = []
    answers_text = " ".join(session.answers.values()).lower()

    for func in functions:
        status = _match_function(func, answers_text, module_id)
        items.append(FitGapItem(
            module_id=module_id,
            function_id=func["id"],
            function_name=func["name"],
            function_name_ja=func["name_ja"],
            status=status,
            gap_description=_get_gap_reason(func, status),
            gap_description_ja=_get_gap_reason_ja(func, status),
            customization_effort=_estimate_effort(status),
            priority="high" if func.get("category") in ("order", "procurement", "gl", "production") else "medium",
        ))

    report = FitGapReport(
        project_id=session.project_id,
        module_id=module_id,
        module_name=mod["name"],
        module_name_ja=mod["name_ja"],
        items=items,
    )
    report.calculate_fit_rate()
    report.summary = (
        f"Fit/Gap analysis for {mod['name']} module completed. "
        f"Fit rate: {report.fit_rate}%. "
        f"Fit: {report.fit_count}, Partial Fit: {report.partial_fit_count}, Gap: {report.gap_count}."
    )
    report.summary_ja = (
        f"{mod['name_ja']}モジュールのFit/Gap分析が完了しました。"
        f"Fit率: {report.fit_rate}%。"
        f"Fit: {report.fit_count}件、Partial Fit: {report.partial_fit_count}件、Gap: {report.gap_count}件。"
    )
    return report


# ---------------------------------------------------------------------------
# Rule-based matching (prototype; LLM-augmented in production)
# ---------------------------------------------------------------------------

# Keywords that indicate a business need is present
_POSITIVE_KEYWORDS: dict[str, list[str]] = {
    "order": ["受注", "注文", "order", "オーダー"],
    "pre-sales": ["見積", "引合", "quotation", "inquiry"],
    "pricing": ["価格", "割引", "リベート", "price", "discount", "rebate"],
    "credit": ["与信", "credit", "クレジット"],
    "shipping": ["出荷", "配送", "delivery", "ship", "ピッキング", "梱包"],
    "billing": ["請求", "invoice", "billing", "請求書"],
    "returns": ["返品", "return"],
    "trade": ["海外", "外国", "輸出", "輸入", "export", "import", "foreign", "通貨", "currency"],
    "procurement": ["購買", "発注", "purchase", "調達", "承認"],
    "inventory": ["在庫", "棚卸", "stock", "ロット", "batch", "シリアル", "入庫", "出庫"],
    "invoice": ["請求照合", "invoice verification", "照合"],
    "valuation": ["評価", "原価", "valuation", "standard cost", "移動平均"],
    "master-data": ["マスタ", "master", "勘定科目", "品目"],
    "gl": ["総勘定", "仕訳", "journal", "GL", "元帳"],
    "ap": ["買掛", "支払", "payable", "payment"],
    "ar": ["売掛", "入金", "receivable", "収入"],
    "asset": ["固定資産", "資産", "asset", "減価償却", "depreciation"],
    "bank": ["銀行", "口座", "bank", "現金"],
    "closing": ["決算", "closing", "月次", "年次"],
    "tax": ["税", "tax", "消費税", "源泉"],
    "cost-center": ["原価センター", "cost center", "コストセンター"],
    "profit-center": ["利益センター", "profit center"],
    "copa": ["収益性", "profitability", "CO-PA"],
    "product-cost": ["製品原価", "product cost", "標準原価"],
    "internal-order": ["内部指図", "internal order"],
    "budget": ["予算", "budget"],
    "allocation": ["配賦", "配分", "allocation"],
    "demand": ["需要", "demand", "見込"],
    "mrp": ["MRP", "所要量", "資材所要"],
    "production": ["製造", "生産", "production", "製造指図"],
    "capacity": ["能力", "capacity", "キャパ"],
    "inbound": ["入荷", "inbound", "受入"],
    "outbound": ["出荷", "outbound", "出庫"],
    "execution": ["実行", "タスク", "作業"],
    "optimization": ["最適", "補充", "クロスドッキング"],
    "quality": ["品質", "検査", "quality", "inspection"],
    "inspection": ["検査", "inspection", "検品"],
    "notification": ["通知", "不良", "クレーム", "defect"],
    "certificate": ["証明書", "certificate"],
    "planning": ["計画", "plan"],
    "audit": ["監査", "audit"],
    "org-mgmt": ["組織", "organization"],
    "personnel": ["人事", "personnel", "採用", "退職"],
    "time": ["勤怠", "time", "出退勤", "残業"],
    "payroll": ["給与", "payroll", "賃金"],
    "benefits": ["福利", "benefit"],
    "recruitment": ["採用", "recruit"],
    "development": ["研修", "training", "教育", "人事考課"],
    "compensation": ["報酬", "compensation", "昇給"],
    "travel": ["出張", "travel", "経費"],
    "self-service": ["セルフサービス", "self-service", "ポータル"],
    "reporting": ["レポート", "report", "分析", "analytics"],
    "compliance": ["コンプライアンス", "危険物", "hazardous"],
    "yard": ["ヤード", "yard", "バース", "dock"],
    "integration": ["連携", "integration"],
}

# Categories considered "core" for each module - likely to be Fit
_CORE_CATEGORIES: dict[str, list[str]] = {
    "SD": ["order", "shipping", "billing", "pricing"],
    "MM": ["procurement", "inventory", "invoice", "master-data"],
    "FI": ["gl", "ap", "ar", "closing", "master-data"],
    "CO": ["cost-center", "allocation", "closing", "reporting"],
    "PP": ["production", "mrp", "master-data", "demand"],
    "WM": ["inbound", "outbound", "inventory", "execution"],
    "QM": ["inspection", "notification", "planning"],
    "PM": ["master-data", "order", "planning", "notification"],
    "HR": ["org-mgmt", "personnel", "time", "payroll"],
}


def _match_function(
    func: dict[str, Any],
    answers_text: str,
    module_id: str,
) -> FitGapStatus:
    """Match a single SAP function against user answers."""
    category = func.get("category", "")
    keywords = _POSITIVE_KEYWORDS.get(category, [])
    core_cats = _CORE_CATEGORIES.get(module_id, [])

    # Check if any keyword is mentioned in answers
    mentioned = any(kw in answers_text for kw in keywords)

    # Core functions of the module are usually Fit
    is_core = category in core_cats

    if is_core and mentioned:
        return FitGapStatus.FIT
    elif is_core and not mentioned:
        # Core function but not explicitly mentioned - partial fit
        return FitGapStatus.PARTIAL_FIT
    elif mentioned:
        return FitGapStatus.FIT
    else:
        # Advanced / specialized function not discussed
        return FitGapStatus.GAP


def _get_gap_reason(func: dict[str, Any], status: FitGapStatus) -> str:
    if status == FitGapStatus.FIT:
        return "Standard function covers the requirement."
    elif status == FitGapStatus.PARTIAL_FIT:
        return f"Standard function available but may need configuration: {func['name']}."
    else:
        return f"Custom development or add-on may be needed for: {func['name']}."


def _get_gap_reason_ja(func: dict[str, Any], status: FitGapStatus) -> str:
    if status == FitGapStatus.FIT:
        return "標準機能で対応可能です。"
    elif status == FitGapStatus.PARTIAL_FIT:
        return f"標準機能がありますが、設定調整が必要な可能性があります: {func['name_ja']}。"
    else:
        return f"アドオン開発またはカスタマイズが必要な可能性があります: {func['name_ja']}。"


def _estimate_effort(status: FitGapStatus) -> str:
    if status == FitGapStatus.FIT:
        return "low"
    elif status == FitGapStatus.PARTIAL_FIT:
        return "medium"
    else:
        return "high"


def build_fitgap_prompt(session: FitGapSession) -> str:
    """Build a prompt for LLM-based Fit/Gap analysis (production use).

    Returns a prompt string that can be sent to Claude for deeper analysis.
    """
    mod = get_module(session.module_id)
    if mod is None:
        return ""

    functions_summary = "\n".join(
        f"- {f['id']}: {f['name_ja']} ({f['name']}): {f['description']}"
        for f in mod["standard_functions"]
    )

    answers_summary = "\n".join(
        f"Q{k}: {v}" for k, v in session.answers.items()
    )

    return f"""あなたはSAP S/4HANA導入のFit/Gap分析の専門家です。

以下の業務ヒアリング結果に基づいて、SAP {mod['name']}({mod['name_ja']})モジュールの
標準機能とのFit/Gapを分析してください。

## SAP {session.module_id} 標準機能一覧
{functions_summary}

## ヒアリング結果
{answers_summary}

## 出力形式
各標準機能について以下をJSON配列で出力してください:
- function_id: 機能ID
- status: "fit" / "partial_fit" / "gap"
- reason_ja: 日本語での理由
- reason_en: 英語での理由
- effort: "low" / "medium" / "high"（カスタマイズ工数）
- priority: "high" / "medium" / "low"

最後に全体のサマリーを日英両方で記載してください。
"""


# ---------------------------------------------------------------------------
# SAP Best Practices-based Fit/Gap Analysis (v2)
# ---------------------------------------------------------------------------

def get_scope_items_for_module(module_id: str) -> list[dict[str, Any]]:
    """Get SAP Best Practices Scope Items for a module as dicts."""
    from app.knowledge.sap_best_practices import get_scope_items_by_module
    items = get_scope_items_by_module(module_id.upper())
    return [item.to_dict() for item in items]


def get_common_gap_patterns(module_id: str) -> list[dict[str, Any]]:
    """Get common gap patterns for a module from SAP Best Practices."""
    from app.knowledge.sap_best_practices import get_common_gaps_for_module
    return get_common_gaps_for_module(module_id.upper())


def match_scope_items(
    module_id: str,
    answers_text: str,
) -> list[dict[str, Any]]:
    """Match business requirements against SAP Best Practices Scope Items.

    Returns a list of scope items with fit/gap status based on keyword matching.
    Enhanced version that uses Scope Item data including common gaps.
    """
    from app.knowledge.sap_best_practices import get_scope_items_by_module

    module_id = module_id.upper()
    scope_items = get_scope_items_by_module(module_id)
    answers_lower = answers_text.lower()
    results: list[dict[str, Any]] = []

    for item in scope_items:
        # Check if scope item keywords are mentioned
        search_terms = [
            item.name_en.lower(),
            item.name_ja,
        ]
        # Add key transaction codes as search terms
        search_terms.extend(t.lower() for t in item.key_transactions)
        # Add words from process steps
        for step in item.process_steps:
            search_terms.append(step.lower())

        mentioned = any(term in answers_lower for term in search_terms if term)

        # Check for common gap pattern matches
        # Use longer keywords (>5 chars) to avoid false positives from common words
        matching_gaps: list[str] = []
        for gap in item.common_gaps:
            gap_keywords = gap.lower().split()
            if any(kw in answers_lower for kw in gap_keywords if len(kw) > 5):
                matching_gaps.append(gap)

        # Determine fit status
        from app.knowledge.fit_to_standard import FitClassification
        if mentioned and not matching_gaps:
            fit_class = FitClassification.STANDARD_FIT
            status = "fit"
        elif mentioned and matching_gaps:
            fit_class = FitClassification.CONFIGURATION_FIT
            status = "partial_fit"
        else:
            fit_class = FitClassification.GAP
            status = "gap"

        results.append({
            "scope_id": item.scope_id,
            "name_en": item.name_en,
            "name_ja": item.name_ja,
            "module": item.module,
            "category": item.category,
            "fit_classification": fit_class.value,
            "status": status,
            "matching_gaps": matching_gaps,
            "key_transactions": item.key_transactions,
            "process_steps": item.process_steps,
            "common_gaps": item.common_gaps,
        })

    return results


def generate_fit_to_standard_report(
    project_id: str,
    module_id: str,
    answers_text: str,
) -> dict[str, Any]:
    """Generate a Fit-to-Standard analysis report.

    Combines Scope Item matching with Fit-to-Standard methodology
    including gap resolution recommendations.
    """
    from app.knowledge.fit_to_standard import (
        FitClassification,
        FitToStandardReport,
        FitToStandardItem,
        recommend_resolution,
    )

    module_id = module_id.upper()
    matched = match_scope_items(module_id, answers_text)

    items: list[FitToStandardItem] = []
    for m in matched:
        gap_resolution = None
        recommendation = ""
        recommendation_ja = ""

        if m["status"] == "gap":
            gap_resolution = recommend_resolution(
                gap_description="; ".join(m["common_gaps"][:2]) if m["common_gaps"] else m["name_en"],
                is_regulatory=False,
                current_process_changeable=True,
            )
            recommendation = (
                f"Consider {gap_resolution.value.replace('_', ' ')} for {m['name_en']}. "
                f"Evaluate SAP standard process first."
            )
            recommendation_ja = (
                f"{m['name_ja']}について、まずSAP標準プロセスの採用を検討してください。"
            )
        elif m["status"] == "partial_fit":
            recommendation = (
                f"Configuration adjustment needed for {m['name_en']}. "
                f"Potential gaps: {'; '.join(m['matching_gaps'][:2])}"
            )
            recommendation_ja = (
                f"{m['name_ja']}の設定調整が必要です。"
            )

        item = FitToStandardItem(
            requirement_id=m["scope_id"],
            requirement_description=m["name_en"],
            requirement_description_ja=m["name_ja"],
            scope_item_id=m["scope_id"],
            scope_item_name=m["name_en"],
            fit_classification=FitClassification(m["fit_classification"]),
            gap_resolution=gap_resolution,
            gap_description="; ".join(m["matching_gaps"]) if m["matching_gaps"] else "",
            gap_description_ja="",
            recommendation=recommendation,
            recommendation_ja=recommendation_ja,
        )
        items.append(item)

    report = FitToStandardReport(
        project_id=project_id,
        module_id=module_id,
        items=items,
    )
    report.calculate_statistics()

    mod = get_module(module_id)
    mod_name = mod["name"] if mod else module_id
    mod_name_ja = mod["name_ja"] if mod else module_id

    report.summary = (
        f"Fit-to-Standard analysis for {mod_name}: "
        f"Standard Fit: {report.standard_fit_count}, "
        f"Configuration Fit: {report.configuration_fit_count}, "
        f"Gap: {report.gap_count}. "
        f"Overall fit rate: {report.overall_fit_rate}%."
    )
    report.summary_ja = (
        f"{mod_name_ja}のFit-to-Standard分析: "
        f"標準Fit: {report.standard_fit_count}件、"
        f"設定Fit: {report.configuration_fit_count}件、"
        f"Gap: {report.gap_count}件。"
        f"総合Fit率: {report.overall_fit_rate}%。"
    )

    return report.model_dump()


def build_fitgap_prompt_v2(session: "FitGapSession") -> str:
    """Build an enhanced prompt for LLM-based Fit/Gap analysis using Best Practices.

    Uses SAP Best Practices Scope Items and Fit-to-Standard methodology.
    """
    from app.knowledge.sap_best_practices import get_scope_items_by_module
    from app.knowledge.fit_to_standard import (
        build_fit_to_standard_prompt,
    )

    mod = get_module(session.module_id)
    if mod is None:
        return ""

    scope_items = get_scope_items_by_module(session.module_id.upper())
    scope_summary = "\n".join(
        f"- [{item.scope_id}] {item.name_ja} ({item.name_en}): {item.description}"
        for item in scope_items
    )

    answers_summary = "\n".join(
        f"Q{k}: {v}" for k, v in session.answers.items()
    )

    return build_fit_to_standard_prompt(
        module_id=session.module_id,
        scope_items_summary=scope_summary,
        business_requirements=answers_summary,
    )

"""Test Case Auto-Generation Service.

Generates SAP test scenarios including:
- T-codes, input values, expected results
- Unit, integration, and UAT test cases
- Based on business requirements and SAP module knowledge
"""

from __future__ import annotations

from typing import Any

from app.knowledge.sap_modules import get_functions_for_module, get_module
from app.models import TestCase, TestStep, TestSuite


# ---------------------------------------------------------------------------
# Standard test scenario templates per module
# ---------------------------------------------------------------------------
_SD_SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "Standard Order to Cash",
        "name_ja": "標準販売プロセス（受注→出荷→請求）",
        "type": "integration",
        "steps": [
            {"action": "Create Sales Order", "action_ja": "販売伝票の登録",
             "t_code": "VA01", "input": "Order type: OR, Sales org, Customer, Material, Qty",
             "expected": "Sales order created", "expected_ja": "販売伝票が登録されること"},
            {"action": "Create Delivery", "action_ja": "出荷伝票の登録",
             "t_code": "VL01N", "input": "Reference: Sales Order number",
             "expected": "Delivery created", "expected_ja": "出荷伝票が登録されること"},
            {"action": "Post Goods Issue", "action_ja": "出庫転記",
             "t_code": "VL02N", "input": "Select delivery, Post GI",
             "expected": "Goods issue posted, stock reduced", "expected_ja": "出庫が転記され在庫が減少すること"},
            {"action": "Create Billing Document", "action_ja": "請求伝票の登録",
             "t_code": "VF01", "input": "Reference: Delivery number",
             "expected": "Invoice created, FI document posted", "expected_ja": "請求伝票が登録されFI伝票が転記されること"},
        ],
    },
    {
        "name": "Returns Processing",
        "name_ja": "返品処理",
        "type": "unit",
        "steps": [
            {"action": "Create Returns Order", "action_ja": "返品伝票の登録",
             "t_code": "VA01", "input": "Order type: RE, Reference original order",
             "expected": "Returns order created", "expected_ja": "返品伝票が登録されること"},
            {"action": "Create Return Delivery", "action_ja": "返品入庫伝票の登録",
             "t_code": "VL01N", "input": "Reference: Returns order",
             "expected": "Return delivery created", "expected_ja": "返品入庫伝票が登録されること"},
            {"action": "Post Goods Receipt", "action_ja": "入庫転記",
             "t_code": "VL02N", "input": "Post goods receipt for return",
             "expected": "Stock increased", "expected_ja": "在庫が増加すること"},
            {"action": "Create Credit Memo", "action_ja": "クレジットメモの登録",
             "t_code": "VF01", "input": "Reference: Returns order",
             "expected": "Credit memo posted", "expected_ja": "クレジットメモが転記されること"},
        ],
    },
]

_MM_SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "Procure to Pay",
        "name_ja": "標準購買プロセス（購買依頼→発注→入庫→請求照合）",
        "type": "integration",
        "steps": [
            {"action": "Create Purchase Requisition", "action_ja": "購買依頼の登録",
             "t_code": "ME51N", "input": "Material, Qty, Delivery date, Plant",
             "expected": "PR created", "expected_ja": "購買依頼が登録されること"},
            {"action": "Create Purchase Order", "action_ja": "発注伝票の登録",
             "t_code": "ME21N", "input": "Reference PR, Vendor, Price",
             "expected": "PO created", "expected_ja": "発注伝票が登録されること"},
            {"action": "Post Goods Receipt", "action_ja": "入庫の転記",
             "t_code": "MIGO", "input": "PO reference, Movement type 101",
             "expected": "GR posted, stock increased", "expected_ja": "入庫が転記され在庫が増加すること"},
            {"action": "Invoice Verification", "action_ja": "請求照合",
             "t_code": "MIRO", "input": "PO reference, Invoice amount",
             "expected": "Invoice posted, 3-way match", "expected_ja": "請求書が転記され3点照合が完了すること"},
        ],
    },
    {
        "name": "Physical Inventory",
        "name_ja": "棚卸プロセス",
        "type": "unit",
        "steps": [
            {"action": "Create Physical Inventory Document", "action_ja": "棚卸伝票の登録",
             "t_code": "MI01", "input": "Plant, Storage location, Materials",
             "expected": "PI doc created", "expected_ja": "棚卸伝票が登録されること"},
            {"action": "Enter Count", "action_ja": "棚卸数量の入力",
             "t_code": "MI04", "input": "Counted quantities",
             "expected": "Counts entered", "expected_ja": "棚卸数量が入力されること"},
            {"action": "Post Differences", "action_ja": "差異の転記",
             "t_code": "MI07", "input": "Approve differences",
             "expected": "Adjustments posted", "expected_ja": "差異が転記され在庫が調整されること"},
        ],
    },
]

_FI_SCENARIOS: list[dict[str, Any]] = [
    {
        "name": "AP Invoice to Payment",
        "name_ja": "買掛金処理（請求書登録→支払）",
        "type": "integration",
        "steps": [
            {"action": "Post Vendor Invoice", "action_ja": "仕入先請求書の転記",
             "t_code": "FB60", "input": "Vendor, Amount, GL account, Tax code",
             "expected": "AP document posted", "expected_ja": "買掛金伝票が転記されること"},
            {"action": "Run Payment Program", "action_ja": "支払プログラムの実行",
             "t_code": "F110", "input": "Run date, Company code, Payment method",
             "expected": "Payment proposal created", "expected_ja": "支払提案が作成されること"},
            {"action": "Execute Payment", "action_ja": "支払の実行",
             "t_code": "F110", "input": "Execute payment run",
             "expected": "Payment posted, AP cleared", "expected_ja": "支払が転記され買掛金が消込されること"},
        ],
    },
    {
        "name": "Month-End Closing",
        "name_ja": "月次決算処理",
        "type": "integration",
        "steps": [
            {"action": "Foreign Currency Valuation", "action_ja": "外貨評価",
             "t_code": "FAGL_FC_VAL", "input": "Valuation date, Exchange rate type",
             "expected": "Valuation documents posted", "expected_ja": "評価伝票が転記されること"},
            {"action": "GR/IR Clearing", "action_ja": "GR/IR消込",
             "t_code": "F.13", "input": "Company code, Posting date",
             "expected": "GR/IR items cleared", "expected_ja": "GR/IR消込が完了すること"},
            {"action": "Depreciation Run", "action_ja": "減価償却実行",
             "t_code": "AFAB", "input": "Company code, Fiscal year, Period",
             "expected": "Depreciation posted", "expected_ja": "減価償却が転記されること"},
        ],
    },
]

_SCENARIO_REGISTRY: dict[str, list[dict[str, Any]]] = {
    "SD": _SD_SCENARIOS,
    "MM": _MM_SCENARIOS,
    "FI": _FI_SCENARIOS,
}


def get_standard_scenarios(module_id: str) -> list[dict[str, Any]]:
    """Get predefined test scenarios for a module."""
    return _SCENARIO_REGISTRY.get(module_id.upper(), [])


def generate_test_suite(
    project_id: str,
    module_id: str,
    requirements: str = "",
    test_type: str = "unit",
) -> TestSuite:
    """Generate a test suite for a module.

    Combines standard scenarios with requirement-specific cases.
    """
    module_id = module_id.upper()
    mod = get_module(module_id)
    module_name = mod["name_ja"] if mod else module_id

    test_cases: list[TestCase] = []

    # Add standard scenarios
    scenarios = get_standard_scenarios(module_id)
    for scenario in scenarios:
        if test_type != "all" and scenario.get("type") != test_type:
            continue
        steps = [
            TestStep(
                step_number=i + 1,
                action=s["action"],
                action_ja=s["action_ja"],
                t_code=s["t_code"],
                input_data=s["input"],
                expected_result=s["expected"],
                expected_result_ja=s["expected_ja"],
            )
            for i, s in enumerate(scenario["steps"])
        ]
        tc = TestCase(
            project_id=project_id,
            module_id=module_id,
            scenario_name=scenario["name"],
            scenario_name_ja=scenario["name_ja"],
            description=f"Standard {module_id} test scenario",
            steps=steps,
            priority="high",
            test_type=scenario.get("type", "unit"),
        )
        test_cases.append(tc)

    # Generate requirement-based test cases if requirements provided
    if requirements:
        req_cases = _generate_from_requirements(project_id, module_id, requirements, test_type)
        test_cases.extend(req_cases)

    return TestSuite(
        project_id=project_id,
        name=f"{module_name} Test Suite",
        name_ja=f"{module_name}テストスイート",
        module_id=module_id,
        test_type=test_type,
        test_cases=test_cases,
    )


def _generate_from_requirements(
    project_id: str,
    module_id: str,
    requirements: str,
    test_type: str,
) -> list[TestCase]:
    """Generate test cases from free-text requirements.

    Prototype uses keyword matching. Production uses LLM.
    """
    functions = get_functions_for_module(module_id)
    req_lower = requirements.lower()
    cases: list[TestCase] = []

    for func in functions:
        # Check if requirement mentions this function
        keywords = [
            func["name"].lower(),
            func["name_ja"],
            func.get("category", ""),
        ]
        if any(kw in req_lower for kw in keywords if kw):
            t_codes = func.get("t_codes", [])
            main_tcode = t_codes[0] if t_codes else ""
            steps = [
                TestStep(
                    step_number=1,
                    action=f"Execute {func['name']}",
                    action_ja=f"{func['name_ja']}を実行",
                    t_code=main_tcode,
                    input_data="Test data per requirement specification",
                    expected_result=f"{func['name']} completes successfully",
                    expected_result_ja=f"{func['name_ja']}が正常に完了すること",
                ),
            ]
            tc = TestCase(
                project_id=project_id,
                module_id=module_id,
                scenario_name=f"{func['name']} Validation",
                scenario_name_ja=f"{func['name_ja']}検証",
                description=f"Validate {func['name']} based on requirements",
                steps=steps,
                priority="medium",
                test_type=test_type,
            )
            cases.append(tc)

    return cases


def generate_uat_scenarios(
    project_id: str,
    module_id: str,
    business_process: str = "",
) -> TestSuite:
    """Generate UAT (User Acceptance Test) scenarios.

    UAT scenarios focus on end-to-end business processes.
    """
    module_id = module_id.upper()
    mod = get_module(module_id)
    module_name = mod["name_ja"] if mod else module_id

    # UAT uses integration scenarios as base
    return generate_test_suite(
        project_id=project_id,
        module_id=module_id,
        requirements=business_process,
        test_type="integration",
    )


def get_scope_item_scenarios(module_id: str) -> list[dict[str, Any]]:
    """Get test scenarios derived from SAP Best Practices Scope Items.

    Returns structured test scenarios with scope_id linkage.
    """
    from app.knowledge.sap_best_practices import get_scope_items_by_module

    scope_items = get_scope_items_by_module(module_id.upper())
    scenarios: list[dict[str, Any]] = []

    for item in scope_items:
        for ts in item.test_scenarios:
            steps = []
            for i, step_data in enumerate(ts.get("steps", [])):
                steps.append({
                    "action": step_data.get("action", ""),
                    "action_ja": step_data.get("action", ""),
                    "t_code": step_data.get("t_code", ""),
                    "input": step_data.get("input", ""),
                    "expected": step_data.get("expected", ""),
                    "expected_ja": step_data.get("expected", ""),
                })
            scenarios.append({
                "scope_id": item.scope_id,
                "name": ts.get("name", item.name_en),
                "name_ja": ts.get("name_ja", item.name_ja),
                "type": "integration",
                "steps": steps,
            })

    return scenarios


def generate_scope_item_test_suite(
    project_id: str,
    module_id: str,
    scope_id: str = "",
    test_type: str = "all",
) -> TestSuite:
    """Generate a test suite based on SAP Best Practices Scope Items.

    If scope_id is provided, generates tests only for that scope item.
    Otherwise, generates tests for all scope items in the module.
    """
    module_id = module_id.upper()
    mod = get_module(module_id)
    module_name = mod["name_ja"] if mod else module_id

    scenarios = get_scope_item_scenarios(module_id)

    if scope_id:
        scenarios = [s for s in scenarios if s.get("scope_id") == scope_id]

    test_cases: list[TestCase] = []
    for scenario in scenarios:
        if test_type != "all" and scenario.get("type") != test_type:
            continue
        steps = [
            TestStep(
                step_number=i + 1,
                action=s["action"],
                action_ja=s["action_ja"],
                t_code=s["t_code"],
                input_data=s["input"],
                expected_result=s["expected"],
                expected_result_ja=s["expected_ja"],
            )
            for i, s in enumerate(scenario["steps"])
        ]
        scope_label = f" [{scenario.get('scope_id', '')}]" if scenario.get("scope_id") else ""
        tc = TestCase(
            project_id=project_id,
            module_id=module_id,
            scenario_name=f"{scenario['name']}{scope_label}",
            scenario_name_ja=f"{scenario['name_ja']}{scope_label}",
            description=f"SAP Best Practices test scenario for {scenario.get('scope_id', module_id)}",
            steps=steps,
            priority="high",
            test_type=scenario.get("type", "integration"),
        )
        test_cases.append(tc)

    return TestSuite(
        project_id=project_id,
        name=f"{module_name} Best Practices Test Suite",
        name_ja=f"{module_name} ベストプラクティス テストスイート",
        module_id=module_id,
        test_type=test_type,
        test_cases=test_cases,
    )


def build_test_generation_prompt(
    module_id: str,
    requirements: str,
    test_type: str = "unit",
) -> str:
    """Build prompt for LLM-based test case generation."""
    mod = get_module(module_id)
    if mod is None:
        return ""

    functions_summary = "\n".join(
        f"- {f['id']}: {f['name_ja']} (T-code: {', '.join(f.get('t_codes', []))})"
        for f in mod["standard_functions"]
    )

    return f"""あなたはSAP S/4HANAのテストエンジニアです。
以下の要件に基づいて、{mod['name_ja']}モジュールのテストケースを生成してください。

## テストタイプ: {test_type}

## SAP {module_id} 標準機能
{functions_summary}

## 業務要件
{requirements}

## 出力形式 (JSON配列)
各テストケースに以下を含めてください:
- scenario_name / scenario_name_ja
- description
- preconditions (前提条件)
- steps: [{{"step_number", "action", "action_ja", "t_code", "input_data", "expected_result", "expected_result_ja"}}]
- priority: "high" / "medium" / "low"

テストケースは以下を網羅してください:
1. 正常系（Happy Path）
2. 異常系（エラーケース）
3. 境界値テスト
4. 権限チェック
"""

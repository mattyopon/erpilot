"""Tests for SAP Best Practices knowledge base and Fit-to-Standard framework."""

from __future__ import annotations

from app.knowledge.sap_best_practices import (
    ALL_SCOPE_ITEMS,
    PROCESS_CATEGORIES,
    get_all_categories,
    get_all_scope_items,
    get_common_gaps_for_module,
    get_scope_item,
    get_scope_item_summary,
    get_scope_items_by_category,
    get_scope_items_by_module,
    get_test_scenarios_for_scope_item,
    search_scope_items,
)
from app.knowledge.fit_to_standard import (
    CHALLENGE_QUESTIONS,
    FitClassification,
    FitToStandardItem,
    FitToStandardReport,
    GapResolutionType,
    build_fit_to_standard_prompt,
    get_challenge_questions,
    get_effort_estimate,
    get_gap_resolution_priority,
    recommend_resolution,
)
from app.services.fitgap import (
    build_fitgap_prompt_v2,
    generate_fit_to_standard_report,
    get_common_gap_patterns,
    get_scope_items_for_module,
    match_scope_items,
    start_session,
)
from app.services.test_generator import (
    generate_scope_item_test_suite,
    get_scope_item_scenarios,
)


# ---------------------------------------------------------------------------
# SAP Best Practices Knowledge Base Tests
# ---------------------------------------------------------------------------
class TestSAPBestPracticesKnowledgeBase:
    """Test the SAP Best Practices Scope Items database."""

    def test_minimum_50_scope_items(self) -> None:
        """Requirement: at least 50 scope items defined."""
        items = get_all_scope_items()
        assert len(items) >= 50, f"Only {len(items)} scope items defined, need >= 50"

    def test_all_scope_items_have_required_fields(self) -> None:
        for item in ALL_SCOPE_ITEMS:
            assert item.scope_id, "Missing scope_id"
            assert item.name_en, f"Missing name_en for {item.scope_id}"
            assert item.name_ja, f"Missing name_ja for {item.scope_id}"
            assert item.module, f"Missing module for {item.scope_id}"
            assert item.category, f"Missing category for {item.scope_id}"
            assert item.description, f"Missing description for {item.scope_id}"
            assert len(item.key_transactions) > 0, (
                f"Missing key_transactions for {item.scope_id}"
            )

    def test_scope_ids_are_unique(self) -> None:
        ids = [item.scope_id for item in ALL_SCOPE_ITEMS]
        assert len(ids) == len(set(ids)), "Duplicate scope IDs found"

    def test_scope_items_have_process_steps(self) -> None:
        for item in ALL_SCOPE_ITEMS:
            assert len(item.process_steps) > 0, (
                f"Missing process_steps for {item.scope_id}"
            )

    def test_scope_items_have_common_gaps(self) -> None:
        for item in ALL_SCOPE_ITEMS:
            assert len(item.common_gaps) > 0, (
                f"Missing common_gaps for {item.scope_id}"
            )

    def test_scope_items_have_test_scenarios(self) -> None:
        for item in ALL_SCOPE_ITEMS:
            assert len(item.test_scenarios) > 0, (
                f"Missing test_scenarios for {item.scope_id}"
            )

    def test_to_dict(self) -> None:
        item = ALL_SCOPE_ITEMS[0]
        d = item.to_dict()
        assert d["scope_id"] == item.scope_id
        assert d["name_en"] == item.name_en
        assert d["name_ja"] == item.name_ja
        assert d["module"] == item.module
        assert "key_transactions" in d
        assert "common_gaps" in d
        assert "test_scenarios" in d


# ---------------------------------------------------------------------------
# Scope Item Lookup Tests
# ---------------------------------------------------------------------------
class TestScopeItemLookup:
    """Test scope item retrieval functions."""

    def test_get_scope_item_by_id(self) -> None:
        item = get_scope_item("BD1")
        assert item is not None
        assert item.name_en == "Sales Order Processing"
        assert item.module == "SD"

    def test_get_scope_item_nonexistent(self) -> None:
        item = get_scope_item("XXXXX")
        assert item is None

    def test_get_scope_items_by_module_sd(self) -> None:
        items = get_scope_items_by_module("SD")
        assert len(items) > 0
        for item in items:
            assert item.module == "SD"

    def test_get_scope_items_by_module_mm(self) -> None:
        items = get_scope_items_by_module("MM")
        assert len(items) > 0

    def test_get_scope_items_by_module_fi(self) -> None:
        items = get_scope_items_by_module("FI")
        assert len(items) > 0

    def test_get_scope_items_by_module_co(self) -> None:
        items = get_scope_items_by_module("CO")
        assert len(items) > 0

    def test_get_scope_items_by_module_pp(self) -> None:
        items = get_scope_items_by_module("PP")
        assert len(items) > 0

    def test_get_scope_items_by_module_wm(self) -> None:
        items = get_scope_items_by_module("WM")
        assert len(items) > 0

    def test_get_scope_items_by_module_qm(self) -> None:
        items = get_scope_items_by_module("QM")
        assert len(items) > 0

    def test_get_scope_items_by_module_pm(self) -> None:
        items = get_scope_items_by_module("PM")
        assert len(items) > 0

    def test_get_scope_items_by_module_hr(self) -> None:
        items = get_scope_items_by_module("HR")
        assert len(items) > 0

    def test_get_scope_items_by_module_case_insensitive(self) -> None:
        items_upper = get_scope_items_by_module("SD")
        items_lower = get_scope_items_by_module("sd")
        assert len(items_upper) == len(items_lower)

    def test_get_scope_items_by_module_nonexistent(self) -> None:
        items = get_scope_items_by_module("XX")
        assert items == []

    def test_get_scope_items_by_category_o2c(self) -> None:
        items = get_scope_items_by_category("O2C")
        assert len(items) > 0
        for item in items:
            assert item.category == "O2C"

    def test_get_scope_items_by_category_p2p(self) -> None:
        items = get_scope_items_by_category("P2P")
        assert len(items) > 0

    def test_get_scope_items_by_category_r2r(self) -> None:
        items = get_scope_items_by_category("R2R")
        assert len(items) > 0

    def test_get_scope_items_by_category_p2m(self) -> None:
        items = get_scope_items_by_category("P2M")
        assert len(items) > 0

    def test_search_scope_items_by_name(self) -> None:
        results = search_scope_items("Sales Order")
        assert len(results) > 0
        assert any("Sales Order" in r.name_en for r in results)

    def test_search_scope_items_japanese(self) -> None:
        results = search_scope_items("受注")
        assert len(results) > 0

    def test_search_scope_items_by_tcode(self) -> None:
        results = search_scope_items("VA01")
        assert len(results) > 0

    def test_get_scope_item_summary(self) -> None:
        summary = get_scope_item_summary()
        assert len(summary) >= 50
        for s in summary:
            assert "scope_id" in s
            assert "name_en" in s
            assert "name_ja" in s
            assert "module" in s
            assert "category" in s

    def test_get_common_gaps_for_module(self) -> None:
        gaps = get_common_gaps_for_module("SD")
        assert len(gaps) > 0
        for g in gaps:
            assert "scope_id" in g
            assert "common_gaps" in g
            assert len(g["common_gaps"]) > 0

    def test_get_test_scenarios_for_scope_item(self) -> None:
        scenarios = get_test_scenarios_for_scope_item("BD1")
        assert len(scenarios) > 0
        for s in scenarios:
            assert "name" in s
            assert "steps" in s

    def test_get_test_scenarios_nonexistent(self) -> None:
        scenarios = get_test_scenarios_for_scope_item("XXXXX")
        assert scenarios == []


# ---------------------------------------------------------------------------
# Process Categories Tests
# ---------------------------------------------------------------------------
class TestProcessCategories:
    """Test process category definitions."""

    def test_all_categories_defined(self) -> None:
        cats = get_all_categories()
        assert "O2C" in cats
        assert "P2P" in cats
        assert "R2R" in cats
        assert "P2M" in cats
        assert "WM" in cats
        assert "QM" in cats
        assert "AM" in cats
        assert "HCM" in cats

    def test_categories_have_bilingual_names(self) -> None:
        for cat_id, cat in PROCESS_CATEGORIES.items():
            assert "name_en" in cat, f"Missing name_en for {cat_id}"
            assert "name_ja" in cat, f"Missing name_ja for {cat_id}"
            assert "description" in cat, f"Missing description for {cat_id}"


# ---------------------------------------------------------------------------
# Fit-to-Standard Framework Tests
# ---------------------------------------------------------------------------
class TestFitToStandardFramework:
    """Test the Fit-to-Standard analysis framework."""

    def test_fit_classifications(self) -> None:
        assert FitClassification.STANDARD_FIT.value == "standard_fit"
        assert FitClassification.CONFIGURATION_FIT.value == "configuration_fit"
        assert FitClassification.GAP.value == "gap"

    def test_gap_resolution_types(self) -> None:
        assert GapResolutionType.PROCESS_CHANGE.value == "process_change"
        assert GapResolutionType.IN_APP_EXTENSION.value == "in_app_extension"
        assert GapResolutionType.SIDE_BY_SIDE_EXTENSION.value == "side_by_side_extension"
        assert GapResolutionType.CUSTOM_DEVELOPMENT.value == "custom_development"

    def test_challenge_questions_count(self) -> None:
        questions = get_challenge_questions()
        assert len(questions) >= 5

    def test_challenge_questions_bilingual(self) -> None:
        for q in CHALLENGE_QUESTIONS:
            assert "ja" in q
            assert "en" in q
            assert "purpose" in q

    def test_effort_estimates(self) -> None:
        for key in ["standard_fit", "configuration_fit", "process_change",
                     "in_app_extension", "side_by_side_extension", "custom_development"]:
            est = get_effort_estimate(key)
            assert est != {}, f"Missing effort estimate for {key}"
            assert "effort_days_range" in est
            assert "risk" in est

    def test_gap_resolution_priority_order(self) -> None:
        priorities = get_gap_resolution_priority()
        assert len(priorities) == 4
        assert priorities[0]["type"] == "process_change"
        assert priorities[3]["type"] == "custom_development"

    def test_recommend_resolution_process_change(self) -> None:
        result = recommend_resolution(
            "Custom pricing logic",
            is_regulatory=False,
            current_process_changeable=True,
        )
        assert result == GapResolutionType.PROCESS_CHANGE

    def test_recommend_resolution_regulatory(self) -> None:
        result = recommend_resolution(
            "Tax compliance requirement",
            is_regulatory=True,
            current_process_changeable=True,
        )
        assert result == GapResolutionType.IN_APP_EXTENSION

    def test_recommend_resolution_not_changeable(self) -> None:
        result = recommend_resolution(
            "Complex integration",
            is_regulatory=False,
            is_industry_standard=False,
            current_process_changeable=False,
        )
        assert result == GapResolutionType.SIDE_BY_SIDE_EXTENSION


# ---------------------------------------------------------------------------
# Fit-to-Standard Report Model Tests
# ---------------------------------------------------------------------------
class TestFitToStandardReport:
    """Test the Fit-to-Standard report model."""

    def test_report_statistics_calculation(self) -> None:
        report = FitToStandardReport(project_id="proj-1", module_id="SD")
        report.items = [
            FitToStandardItem(fit_classification=FitClassification.STANDARD_FIT),
            FitToStandardItem(fit_classification=FitClassification.STANDARD_FIT),
            FitToStandardItem(fit_classification=FitClassification.CONFIGURATION_FIT),
            FitToStandardItem(
                fit_classification=FitClassification.GAP,
                gap_resolution=GapResolutionType.PROCESS_CHANGE,
            ),
            FitToStandardItem(
                fit_classification=FitClassification.GAP,
                gap_resolution=GapResolutionType.CUSTOM_DEVELOPMENT,
            ),
        ]
        report.calculate_statistics()
        assert report.standard_fit_count == 2
        assert report.configuration_fit_count == 1
        assert report.gap_count == 2
        assert report.gap_by_resolution["process_change"] == 1
        assert report.gap_by_resolution["custom_development"] == 1
        assert report.overall_fit_rate > 0

    def test_empty_report(self) -> None:
        report = FitToStandardReport(project_id="proj-1")
        report.calculate_statistics()
        assert report.overall_fit_rate == 0.0
        assert report.standard_fit_count == 0


# ---------------------------------------------------------------------------
# Fit-to-Standard Prompt Builder Tests
# ---------------------------------------------------------------------------
class TestFitToStandardPromptBuilder:
    """Test the Fit-to-Standard prompt builder."""

    def test_build_prompt(self) -> None:
        prompt = build_fit_to_standard_prompt(
            module_id="SD",
            scope_items_summary="BD1: Sales Order Processing",
            business_requirements="受注処理のプロセスについて",
        )
        assert "Fit-to-Standard" in prompt
        assert "SD" in prompt
        assert "BD1" in prompt
        assert "チャレンジ質問" in prompt


# ---------------------------------------------------------------------------
# Fitgap Service v2 Integration Tests
# ---------------------------------------------------------------------------
class TestFitgapServiceV2:
    """Test the enhanced fitgap service with Best Practices integration."""

    def test_get_scope_items_for_module(self) -> None:
        items = get_scope_items_for_module("SD")
        assert len(items) > 0
        for item in items:
            assert "scope_id" in item
            assert "name_en" in item
            assert "module" in item
            assert item["module"] == "SD"

    def test_get_common_gap_patterns(self) -> None:
        gaps = get_common_gap_patterns("SD")
        assert len(gaps) > 0
        for g in gaps:
            assert "common_gaps" in g

    def test_match_scope_items_with_keywords(self) -> None:
        results = match_scope_items("SD", "受注処理 sales order 出荷 delivery 請求 billing")
        assert len(results) > 0
        # At least some should be fit
        fit_items = [r for r in results if r["status"] == "fit"]
        assert len(fit_items) > 0

    def test_match_scope_items_empty_answers(self) -> None:
        results = match_scope_items("SD", "")
        assert len(results) > 0
        # With empty answers, most should be gap
        gap_items = [r for r in results if r["status"] == "gap"]
        assert len(gap_items) > 0

    def test_generate_fit_to_standard_report(self) -> None:
        report = generate_fit_to_standard_report(
            project_id="proj-1",
            module_id="SD",
            answers_text="受注処理 sales order processing 出荷 delivery 請求 billing",
        )
        assert report["project_id"] == "proj-1"
        assert report["module_id"] == "SD"
        assert "items" in report
        assert len(report["items"]) > 0
        assert "overall_fit_rate" in report
        assert "summary" in report
        assert "summary_ja" in report

    def test_generate_fit_to_standard_report_mm(self) -> None:
        report = generate_fit_to_standard_report(
            project_id="proj-1",
            module_id="MM",
            answers_text="購買依頼 発注 入庫 purchase order goods receipt",
        )
        assert report["module_id"] == "MM"
        assert len(report["items"]) > 0

    def test_build_fitgap_prompt_v2(self) -> None:
        session = start_session("proj-1", "SD")
        session.answers = {"q1": "標準受注プロセス", "q2": "見積もあります"}
        prompt = build_fitgap_prompt_v2(session)
        assert "SD" in prompt
        assert "Fit-to-Standard" in prompt
        assert "チャレンジ質問" in prompt

    def test_build_fitgap_prompt_v2_nonexistent(self) -> None:
        from app.models import FitGapSession
        session = FitGapSession(project_id="proj-1", module_id="XX")
        prompt = build_fitgap_prompt_v2(session)
        assert prompt == ""


# ---------------------------------------------------------------------------
# Test Generator v2 Integration Tests
# ---------------------------------------------------------------------------
class TestTestGeneratorV2:
    """Test the enhanced test generator with Scope Item scenarios."""

    def test_get_scope_item_scenarios_sd(self) -> None:
        scenarios = get_scope_item_scenarios("SD")
        assert len(scenarios) > 0
        for s in scenarios:
            assert "scope_id" in s
            assert "name" in s
            assert "steps" in s
            assert len(s["steps"]) > 0

    def test_get_scope_item_scenarios_mm(self) -> None:
        scenarios = get_scope_item_scenarios("MM")
        assert len(scenarios) > 0

    def test_get_scope_item_scenarios_fi(self) -> None:
        scenarios = get_scope_item_scenarios("FI")
        assert len(scenarios) > 0

    def test_get_scope_item_scenarios_pp(self) -> None:
        scenarios = get_scope_item_scenarios("PP")
        assert len(scenarios) > 0

    def test_get_scope_item_scenarios_have_tcodes(self) -> None:
        scenarios = get_scope_item_scenarios("SD")
        for s in scenarios:
            for step in s["steps"]:
                assert step["t_code"] != "", f"Missing t_code in {s['name']}"

    def test_generate_scope_item_test_suite(self) -> None:
        suite = generate_scope_item_test_suite("proj-1", "SD")
        assert suite.project_id == "proj-1"
        assert suite.module_id == "SD"
        assert len(suite.test_cases) > 0
        assert "Best Practices" in suite.name

    def test_generate_scope_item_test_suite_by_scope_id(self) -> None:
        suite = generate_scope_item_test_suite("proj-1", "SD", scope_id="BD1")
        assert len(suite.test_cases) > 0
        for tc in suite.test_cases:
            assert "BD1" in tc.scenario_name

    def test_generate_scope_item_test_suite_nonexistent_scope(self) -> None:
        suite = generate_scope_item_test_suite("proj-1", "SD", scope_id="XXXXX")
        assert len(suite.test_cases) == 0

    def test_scope_item_test_cases_have_steps(self) -> None:
        suite = generate_scope_item_test_suite("proj-1", "MM")
        for tc in suite.test_cases:
            assert len(tc.steps) > 0
            for step in tc.steps:
                assert step.t_code != ""
                assert step.action != ""

    def test_scope_item_scenarios_for_all_modules(self) -> None:
        """Verify that scope item scenarios exist for all covered modules."""
        for module_id in ["SD", "MM", "FI", "PP"]:
            scenarios = get_scope_item_scenarios(module_id)
            assert len(scenarios) > 0, f"No scenarios for {module_id}"


# ---------------------------------------------------------------------------
# Coverage: Scope Items per Category
# ---------------------------------------------------------------------------
class TestScopeItemCoverage:
    """Test that all required business process categories have scope items."""

    def test_o2c_coverage(self) -> None:
        items = get_scope_items_by_category("O2C")
        assert len(items) >= 5, "O2C needs at least 5 scope items"

    def test_p2p_coverage(self) -> None:
        items = get_scope_items_by_category("P2P")
        assert len(items) >= 5, "P2P needs at least 5 scope items"

    def test_r2r_coverage(self) -> None:
        items = get_scope_items_by_category("R2R")
        assert len(items) >= 5, "R2R needs at least 5 scope items"

    def test_p2m_coverage(self) -> None:
        items = get_scope_items_by_category("P2M")
        assert len(items) >= 3, "P2M needs at least 3 scope items"

    def test_wm_coverage(self) -> None:
        items = get_scope_items_by_category("WM")
        assert len(items) >= 3, "WM needs at least 3 scope items"

    def test_qm_coverage(self) -> None:
        items = get_scope_items_by_category("QM")
        assert len(items) >= 2, "QM needs at least 2 scope items"

    def test_hcm_coverage(self) -> None:
        items = get_scope_items_by_category("HCM")
        assert len(items) >= 3, "HCM needs at least 3 scope items"

    def test_all_modules_have_scope_items(self) -> None:
        """Every SAP module in the system should have scope items."""
        for module in ["SD", "MM", "FI", "CO", "PP", "WM", "QM", "PM", "HR"]:
            items = get_scope_items_by_module(module)
            assert len(items) > 0, f"Module {module} has no scope items"

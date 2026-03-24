"""Tests for Test Case Generator and Training/Bridge services."""

from __future__ import annotations


from app.models import Language, TestSuite, TrainingMaterial, TranslationRequest
from app.services.bridge import (
    get_glossary,
    summarize_meeting,
    translate_text,
    translate_with_glossary,
    build_translation_prompt,
    build_meeting_summary_prompt,
)
from app.services.test_generator import (
    build_test_generation_prompt,
    generate_test_suite,
    generate_uat_scenarios,
    get_standard_scenarios,
)
from app.services.training_gen import (
    build_training_prompt,
    generate_training_material,
    get_available_templates,
)


# ---------------------------------------------------------------------------
# Test Case Generation Tests
# ---------------------------------------------------------------------------
class TestTestCaseGeneration:
    """Test the test case generator service."""

    def test_get_standard_scenarios_sd(self) -> None:
        scenarios = get_standard_scenarios("SD")
        assert len(scenarios) > 0
        for s in scenarios:
            assert "name" in s
            assert "name_ja" in s
            assert "steps" in s
            assert len(s["steps"]) > 0

    def test_get_standard_scenarios_mm(self) -> None:
        scenarios = get_standard_scenarios("MM")
        assert len(scenarios) > 0

    def test_get_standard_scenarios_fi(self) -> None:
        scenarios = get_standard_scenarios("FI")
        assert len(scenarios) > 0

    def test_get_standard_scenarios_nonexistent(self) -> None:
        scenarios = get_standard_scenarios("XX")
        assert scenarios == []

    def test_generate_test_suite_unit(self) -> None:
        suite = generate_test_suite("proj-1", "SD", test_type="unit")
        assert isinstance(suite, TestSuite)
        assert suite.module_id == "SD"
        assert suite.project_id == "proj-1"

    def test_generate_test_suite_integration(self) -> None:
        suite = generate_test_suite("proj-1", "SD", test_type="integration")
        assert len(suite.test_cases) > 0
        for tc in suite.test_cases:
            assert tc.test_type == "integration"

    def test_generate_test_suite_all(self) -> None:
        suite = generate_test_suite("proj-1", "SD", test_type="all")
        assert len(suite.test_cases) > 0

    def test_generate_test_suite_with_requirements(self) -> None:
        suite = generate_test_suite(
            "proj-1", "SD",
            requirements="Sales Order Processing and Billing Document Processing",
            test_type="unit",
        )
        # Should have standard scenarios + requirement-matched cases
        assert len(suite.test_cases) > 0

    def test_generate_test_suite_with_japanese_requirements(self) -> None:
        suite = generate_test_suite(
            "proj-1", "MM",
            requirements="購買依頼と請求照合のプロセス",
            test_type="all",
        )
        assert len(suite.test_cases) > 0

    def test_test_steps_have_t_codes(self) -> None:
        suite = generate_test_suite("proj-1", "SD", test_type="integration")
        for tc in suite.test_cases:
            for step in tc.steps:
                assert step.t_code != "", f"Step {step.step_number} missing t_code"
                assert step.action != ""
                assert step.expected_result != ""

    def test_generate_uat_scenarios(self) -> None:
        suite = generate_uat_scenarios("proj-1", "SD")
        assert isinstance(suite, TestSuite)
        assert len(suite.test_cases) > 0

    def test_build_test_generation_prompt(self) -> None:
        prompt = build_test_generation_prompt("SD", "受注処理のテスト", "unit")
        assert "SD" in prompt
        assert "受注処理" in prompt

    def test_build_test_generation_prompt_nonexistent(self) -> None:
        prompt = build_test_generation_prompt("XX", "test", "unit")
        assert prompt == ""


# ---------------------------------------------------------------------------
# Training Material Generation Tests
# ---------------------------------------------------------------------------
class TestTrainingGeneration:
    """Test training material generation service."""

    def test_get_available_templates(self) -> None:
        templates = get_available_templates()
        assert len(templates) > 0
        for t in templates:
            assert "id" in t
            assert "title" in t
            assert "title_ja" in t

    def test_generate_from_template(self) -> None:
        material = generate_training_material(
            project_id="proj-1",
            module_id="SD",
            process_name="ORDER",
        )
        assert isinstance(material, TrainingMaterial)
        assert material.module_id == "SD"
        assert len(material.steps) > 0
        assert "VA01" in material.steps[0].t_code

    def test_generate_mm_po_template(self) -> None:
        material = generate_training_material(
            project_id="proj-1",
            module_id="MM",
            process_name="PO",
        )
        assert len(material.steps) > 0
        assert "ME21N" in material.steps[0].t_code

    def test_generate_fi_posting_template(self) -> None:
        material = generate_training_material(
            project_id="proj-1",
            module_id="FI",
            process_name="POSTING",
        )
        assert len(material.steps) > 0

    def test_generate_basic_material(self) -> None:
        material = generate_training_material(
            project_id="proj-1",
            module_id="CO",
            process_name="cost-center",
        )
        assert isinstance(material, TrainingMaterial)
        assert len(material.steps) > 0

    def test_generate_with_language(self) -> None:
        material_ja = generate_training_material(
            "proj-1", "SD", "ORDER", language=Language.JA
        )
        material_en = generate_training_material(
            "proj-1", "SD", "ORDER", language=Language.EN
        )
        assert material_ja.language == Language.JA
        assert material_en.language == Language.EN

    def test_training_steps_have_content(self) -> None:
        material = generate_training_material("proj-1", "SD", "ORDER")
        for step in material.steps:
            assert step.step_number > 0
            assert step.instruction != ""
            assert step.instruction_ja != ""

    def test_build_training_prompt(self) -> None:
        prompt = build_training_prompt("SD", "受注処理", language=Language.JA)
        assert "SD" in prompt
        assert "受注処理" in prompt

    def test_build_training_prompt_nonexistent(self) -> None:
        prompt = build_training_prompt("XX", "test")
        assert prompt == ""


# ---------------------------------------------------------------------------
# Bridge (日英ブリッジ) Tests
# ---------------------------------------------------------------------------
class TestBridge:
    """Test Japanese-English bridge service."""

    def test_get_glossary_all(self) -> None:
        glossary = get_glossary()
        assert len(glossary) > 40
        for g in glossary:
            assert "ja" in g
            assert "en" in g
            assert "context" in g

    def test_get_glossary_filtered(self) -> None:
        sd_glossary = get_glossary("SD")
        assert len(sd_glossary) > 0
        for g in sd_glossary:
            assert "SD" in g["context"]

    def test_get_glossary_fi(self) -> None:
        fi_glossary = get_glossary("FI")
        assert len(fi_glossary) > 0

    def test_translate_ja_to_en(self) -> None:
        text, used = translate_with_glossary(
            "購買依頼を作成して発注伝票を登録します",
            Language.JA, Language.EN
        )
        assert "Purchase Requisition" in text
        assert "Purchase Order" in text
        assert len(used) > 0

    def test_translate_en_to_ja(self) -> None:
        text, used = translate_with_glossary(
            "Create a Sales Order and post Goods Issue",
            Language.EN, Language.JA
        )
        assert "受注伝票" in text
        assert "出庫" in text

    def test_translate_text_api(self) -> None:
        req = TranslationRequest(
            text="総勘定元帳に仕訳を転記します",
            source_language=Language.JA,
            target_language=Language.EN,
        )
        result = translate_text(req)
        assert result.translated_text != ""
        assert result.source_language == Language.JA
        assert result.target_language == Language.EN

    def test_summarize_meeting_ja(self) -> None:
        minutes = summarize_meeting(
            project_id="proj-1",
            title="SD要件定義会議",
            date="2026-03-24",
            attendees=["田中", "佐藤", "Smith"],
            raw_text="本日の議題はSD受注プロセスです。\nTODO: 田中さんが受注タイプを整理する\nアクション: Smithさんが価格設定を確認",
        )
        assert minutes.summary_ja != ""
        assert minutes.summary_en != ""
        assert len(minutes.action_items_ja) > 0

    def test_summarize_meeting_en(self) -> None:
        minutes = summarize_meeting(
            project_id="proj-1",
            title="MM Workshop",
            date="2026-03-24",
            attendees=["Tanaka", "Smith"],
            raw_text="Discussion about Purchase Order process.\nAction: Smith to review vendor master data",
            original_language=Language.EN,
        )
        assert minutes.summary_en != ""

    def test_build_translation_prompt(self) -> None:
        prompt = build_translation_prompt(
            "受注処理", Language.JA, Language.EN
        )
        assert "翻訳" in prompt
        assert "用語集" in prompt

    def test_build_meeting_summary_prompt(self) -> None:
        prompt = build_meeting_summary_prompt("会議メモ")
        assert "議事録" in prompt
        assert "アクションアイテム" in prompt


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------
class TestModels:
    """Test Pydantic model validation."""

    def test_test_suite_model(self) -> None:
        suite = TestSuite(
            project_id="proj-1", name="Test", module_id="SD",
        )
        assert suite.id != ""
        assert suite.test_cases == []

    def test_training_material_model(self) -> None:
        material = TrainingMaterial(
            project_id="proj-1", module_id="SD",
            title="Test", title_ja="テスト",
        )
        assert material.id != ""
        assert material.steps == []

    def test_translation_request_model(self) -> None:
        req = TranslationRequest(
            text="test", source_language=Language.JA,
            target_language=Language.EN,
        )
        assert req.context == "SAP implementation project"

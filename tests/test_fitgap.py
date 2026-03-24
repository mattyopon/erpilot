"""Tests for Fit/Gap Analysis service."""

from __future__ import annotations


from app.knowledge.sap_modules import (
    get_all_modules,
    get_functions_for_module,
    get_module,
    get_module_summary,
    search_functions,
)
from app.models import FitGapSession, FitGapStatus
from app.services.fitgap import (
    get_questions_for_module,
    process_answer,
    start_session,
    build_fitgap_prompt,
)


# ---------------------------------------------------------------------------
# SAP Knowledge Base Tests
# ---------------------------------------------------------------------------
class TestSAPKnowledgeBase:
    """Test SAP module knowledge base."""

    def test_get_all_modules(self) -> None:
        modules = get_all_modules()
        assert len(modules) == 9
        assert "SD" in modules
        assert "MM" in modules
        assert "FI" in modules
        assert "CO" in modules
        assert "PP" in modules
        assert "WM" in modules
        assert "QM" in modules
        assert "PM" in modules
        assert "HR" in modules

    def test_get_module_by_id(self) -> None:
        sd = get_module("SD")
        assert sd is not None
        assert sd["name"] == "Sales and Distribution"
        assert sd["name_ja"] == "販売管理"
        assert len(sd["standard_functions"]) >= 20

    def test_get_module_case_insensitive(self) -> None:
        sd_lower = get_module("sd")
        sd_upper = get_module("SD")
        assert sd_lower is not None
        assert sd_upper is not None
        assert sd_lower["name"] == sd_upper["name"]

    def test_get_nonexistent_module(self) -> None:
        result = get_module("XX")
        assert result is None

    def test_get_module_summary(self) -> None:
        summary = get_module_summary()
        assert len(summary) == 9
        for item in summary:
            assert "id" in item
            assert "name" in item
            assert "name_ja" in item
            assert "function_count" in item
            assert int(item["function_count"]) >= 20

    def test_get_functions_for_module(self) -> None:
        functions = get_functions_for_module("SD")
        assert len(functions) >= 20
        for func in functions:
            assert "id" in func
            assert "name" in func
            assert "name_ja" in func
            assert "description" in func
            assert "t_codes" in func
            assert "category" in func

    def test_get_functions_for_nonexistent_module(self) -> None:
        functions = get_functions_for_module("XX")
        assert functions == []

    def test_search_functions(self) -> None:
        results = search_functions("invoice")
        assert len(results) > 0
        for r in results:
            assert "module" in r

    def test_search_functions_japanese(self) -> None:
        results = search_functions("請求")
        assert len(results) > 0

    def test_each_module_has_functions(self) -> None:
        for module_id in ["SD", "MM", "FI", "CO", "PP", "WM", "QM", "PM", "HR"]:
            functions = get_functions_for_module(module_id)
            assert len(functions) >= 20, f"{module_id} has less than 20 functions"

    def test_function_ids_are_unique_per_module(self) -> None:
        for module_id in ["SD", "MM", "FI", "CO", "PP", "WM", "QM", "PM", "HR"]:
            functions = get_functions_for_module(module_id)
            ids = [f["id"] for f in functions]
            assert len(ids) == len(set(ids)), f"Duplicate IDs in {module_id}"

    def test_all_functions_have_t_codes(self) -> None:
        for module_id in ["SD", "MM", "FI", "CO", "PP", "WM", "QM", "PM", "HR"]:
            functions = get_functions_for_module(module_id)
            for func in functions:
                assert len(func["t_codes"]) > 0, (
                    f"{func['id']} in {module_id} has no t_codes"
                )


# ---------------------------------------------------------------------------
# Fit/Gap Session Tests
# ---------------------------------------------------------------------------
class TestFitGapSession:
    """Test Fit/Gap analysis session management."""

    def test_start_session(self) -> None:
        session = start_session("proj-1", "SD")
        assert session.project_id == "proj-1"
        assert session.module_id == "SD"
        assert session.current_question_index == 0
        assert not session.is_complete
        assert len(session.messages) == 1
        assert session.messages[0]["role"] == "assistant"

    def test_start_session_case_insensitive(self) -> None:
        session = start_session("proj-1", "sd")
        assert session.module_id == "SD"

    def test_process_single_answer(self) -> None:
        session = start_session("proj-1", "SD")
        session = process_answer(session, "受注から出荷、請求までの標準プロセスです")
        assert session.current_question_index == 1
        assert "q1" in session.answers
        assert not session.is_complete

    def test_complete_session(self) -> None:
        session = start_session("proj-1", "SD")
        questions = get_questions_for_module("SD")
        for _ in range(len(questions)):
            session = process_answer(session, "標準プロセスで対応しています。受注、出荷、請求の基本フローです。")
        assert session.is_complete
        assert session.report is not None

    def test_report_has_items(self) -> None:
        session = start_session("proj-1", "SD")
        questions = get_questions_for_module("SD")
        for _ in range(len(questions)):
            session = process_answer(
                session,
                "受注、見積、価格設定、与信管理、出荷、請求、返品、海外取引すべて対応しています"
            )
        report = session.report
        assert report is not None
        assert len(report.items) > 0
        assert report.fit_rate > 0

    def test_report_fit_rate_calculation(self) -> None:
        session = start_session("proj-1", "MM")
        questions = get_questions_for_module("MM")
        for _ in range(len(questions)):
            session = process_answer(
                session,
                "購買依頼、発注、入庫、請求照合、在庫管理、棚卸、ロット管理、すべて必要です"
            )
        report = session.report
        assert report is not None
        total = report.fit_count + report.gap_count + report.partial_fit_count
        assert total == len(report.items)
        assert 0 <= report.fit_rate <= 100

    def test_report_has_module_info(self) -> None:
        session = start_session("proj-1", "FI")
        questions = get_questions_for_module("FI")
        for _ in range(len(questions)):
            session = process_answer(session, "一般的な会計処理です")
        report = session.report
        assert report is not None
        assert report.module_id == "FI"
        assert report.module_name == "Financial Accounting"
        assert report.module_name_ja == "財務会計"

    def test_fitgap_item_statuses(self) -> None:
        session = start_session("proj-1", "SD")
        questions = get_questions_for_module("SD")
        for _ in range(len(questions)):
            session = process_answer(session, "基本的な受注処理のみです")
        report = session.report
        assert report is not None
        statuses = {item.status for item in report.items}
        assert len(statuses) > 0
        for status in statuses:
            assert status in (FitGapStatus.FIT, FitGapStatus.GAP, FitGapStatus.PARTIAL_FIT)


# ---------------------------------------------------------------------------
# Interview Questions Tests
# ---------------------------------------------------------------------------
class TestInterviewQuestions:
    """Test interview questions for each module."""

    def test_all_modules_have_questions(self) -> None:
        for module_id in ["SD", "MM", "FI", "CO", "PP", "WM", "QM", "PM", "HR"]:
            questions = get_questions_for_module(module_id)
            assert len(questions) >= 10, f"{module_id} has less than 10 questions"

    def test_questions_have_bilingual_text(self) -> None:
        for module_id in ["SD", "MM", "FI"]:
            questions = get_questions_for_module(module_id)
            for q in questions:
                assert "ja" in q, f"Missing Japanese text in {module_id} question"
                assert "en" in q, f"Missing English text in {module_id} question"
                assert len(q["ja"]) > 0
                assert len(q["en"]) > 0


# ---------------------------------------------------------------------------
# Prompt Builder Tests
# ---------------------------------------------------------------------------
class TestPromptBuilder:
    """Test LLM prompt builders."""

    def test_build_fitgap_prompt(self) -> None:
        session = start_session("proj-1", "SD")
        session.answers = {"q1": "標準受注プロセスです", "q2": "見積もあります"}
        prompt = build_fitgap_prompt(session)
        assert "SD" in prompt
        assert "販売管理" in prompt
        assert "標準受注プロセスです" in prompt
        assert "JSON" in prompt

    def test_build_fitgap_prompt_nonexistent_module(self) -> None:
        session = FitGapSession(project_id="proj-1", module_id="XX")
        prompt = build_fitgap_prompt(session)
        assert prompt == ""

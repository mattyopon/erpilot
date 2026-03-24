"""Tests for PMO Dashboard service."""

from __future__ import annotations

import os
import tempfile

import pytest

from app.db.database import (
    count_entities,
    delete_entity,
    get_entity,
    init_db,
    list_entities,
    save_entity,
)
from app.models import (
    Issue,
    PMOTask,
    Project,
    ProjectPhase,
    Risk,
    RiskLevel,
    TaskPriority,
    TaskStatus,
)
from app.services.pmo_dashboard import (
    PHASE_NAMES_JA,
    PHASE_ORDER,
    generate_weekly_report,
    get_dashboard_summary,
    get_issue_summary,
    get_phase_progress,
    get_risk_summary,
    get_task_summary,
    predict_delay_risk,
    build_weekly_report_prompt,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_project() -> Project:
    return Project(
        name="Test SAP Project",
        name_ja="テストSAPプロジェクト",
        client="Test Corp",
        current_phase=ProjectPhase.DESIGN,
        go_live_date="2027-04-01",
        modules=["SD", "MM", "FI"],
    )


@pytest.fixture
def sample_tasks(sample_project: Project) -> list[PMOTask]:
    return [
        PMOTask(project_id=sample_project.id, title="Task 1",
                phase=ProjectPhase.CONCEPT, status=TaskStatus.COMPLETED),
        PMOTask(project_id=sample_project.id, title="Task 2",
                phase=ProjectPhase.REQUIREMENTS, status=TaskStatus.COMPLETED),
        PMOTask(project_id=sample_project.id, title="Task 3",
                phase=ProjectPhase.DESIGN, status=TaskStatus.IN_PROGRESS),
        PMOTask(project_id=sample_project.id, title="Task 4",
                phase=ProjectPhase.DESIGN, status=TaskStatus.NOT_STARTED),
        PMOTask(project_id=sample_project.id, title="Task 5",
                phase=ProjectPhase.DESIGN, status=TaskStatus.BLOCKED,
                due_date="2026-01-01"),  # Overdue
    ]


@pytest.fixture
def sample_issues(sample_project: Project) -> list[Issue]:
    return [
        Issue(project_id=sample_project.id, title="Issue 1",
              priority=TaskPriority.HIGH, status=TaskStatus.IN_PROGRESS),
        Issue(project_id=sample_project.id, title="Issue 2",
              priority=TaskPriority.MEDIUM, status=TaskStatus.NOT_STARTED),
    ]


@pytest.fixture
def sample_risks(sample_project: Project) -> list[Risk]:
    return [
        Risk(project_id=sample_project.id, title="Risk 1",
             level=RiskLevel.HIGH, status="open"),
        Risk(project_id=sample_project.id, title="Risk 2",
             level=RiskLevel.MEDIUM, status="mitigated"),
    ]


@pytest.fixture
def db_path() -> str:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    os.unlink(path)


# ---------------------------------------------------------------------------
# Phase Management Tests
# ---------------------------------------------------------------------------
class TestPhaseManagement:
    def test_phase_order(self) -> None:
        assert len(PHASE_ORDER) == 7
        assert PHASE_ORDER[0] == ProjectPhase.CONCEPT
        assert PHASE_ORDER[-1] == ProjectPhase.SUPPORT

    def test_phase_names_ja(self) -> None:
        assert PHASE_NAMES_JA[ProjectPhase.CONCEPT] == "構想"
        assert PHASE_NAMES_JA[ProjectPhase.GO_LIVE] == "本番稼働"

    def test_get_phase_progress(
        self, sample_project: Project, sample_tasks: list[PMOTask]
    ) -> None:
        progress = get_phase_progress(sample_project, sample_tasks)
        assert "concept" in progress
        assert "design" in progress
        assert progress["concept"]["completion_rate"] == 100.0
        assert progress["design"]["is_current"] is True
        assert progress["concept"]["is_completed"] is True

    def test_get_phase_progress_empty_tasks(self, sample_project: Project) -> None:
        progress = get_phase_progress(sample_project, [])
        for phase_val, info in progress.items():
            assert info["total_tasks"] == 0
            assert info["completion_rate"] == 0.0


# ---------------------------------------------------------------------------
# Task/Issue/Risk Summary Tests
# ---------------------------------------------------------------------------
class TestSummaries:
    def test_task_summary(self, sample_tasks: list[PMOTask]) -> None:
        summary = get_task_summary(sample_tasks)
        assert summary["total"] == 5
        assert summary["completed"] == 2
        assert summary["in_progress"] == 1
        assert summary["blocked"] == 1

    def test_task_summary_empty(self) -> None:
        summary = get_task_summary([])
        assert summary["total"] == 0

    def test_issue_summary(self, sample_issues: list[Issue]) -> None:
        summary = get_issue_summary(sample_issues)
        assert summary["total"] == 2

    def test_risk_summary(self, sample_risks: list[Risk]) -> None:
        summary = get_risk_summary(sample_risks)
        assert summary["total"] == 2
        assert summary["open"] == 1


# ---------------------------------------------------------------------------
# Delay Risk Prediction Tests
# ---------------------------------------------------------------------------
class TestDelayRiskPrediction:
    def test_no_risk_factors(self, sample_project: Project) -> None:
        score, factors = predict_delay_risk(sample_project, [], [], [])
        assert score == 0.0
        assert len(factors) == 1  # Default "no risk" message

    def test_overdue_tasks_increase_risk(
        self, sample_project: Project, sample_tasks: list[PMOTask]
    ) -> None:
        score, factors = predict_delay_risk(sample_project, sample_tasks, [], [])
        assert score > 0

    def test_high_issues_increase_risk(
        self, sample_project: Project, sample_issues: list[Issue]
    ) -> None:
        score, factors = predict_delay_risk(
            sample_project, [], sample_issues, []
        )
        assert score > 0

    def test_high_risks_increase_risk(
        self, sample_project: Project, sample_risks: list[Risk]
    ) -> None:
        score, factors = predict_delay_risk(
            sample_project, [], [], sample_risks
        )
        assert score > 0

    def test_risk_score_capped_at_100(self, sample_project: Project) -> None:
        # Create many risk factors
        tasks = [
            PMOTask(
                project_id=sample_project.id, title=f"Overdue {i}",
                phase=ProjectPhase.DESIGN, status=TaskStatus.BLOCKED,
                due_date="2020-01-01"
            )
            for i in range(50)
        ]
        issues = [
            Issue(
                project_id=sample_project.id, title=f"Critical {i}",
                priority=TaskPriority.HIGH, status=TaskStatus.IN_PROGRESS
            )
            for i in range(20)
        ]
        risks = [
            Risk(
                project_id=sample_project.id, title=f"Risk {i}",
                level=RiskLevel.HIGH, status="open"
            )
            for i in range(20)
        ]
        score, _ = predict_delay_risk(sample_project, tasks, issues, risks)
        assert score <= 100.0


# ---------------------------------------------------------------------------
# Weekly Report Tests
# ---------------------------------------------------------------------------
class TestWeeklyReport:
    def test_generate_weekly_report(
        self,
        sample_project: Project,
        sample_tasks: list[PMOTask],
        sample_issues: list[Issue],
        sample_risks: list[Risk],
    ) -> None:
        report = generate_weekly_report(
            sample_project, sample_tasks, sample_issues, sample_risks
        )
        assert report.project_id == sample_project.id
        assert report.summary_ja != ""
        assert report.summary_en != ""
        assert report.week_start != ""
        assert report.week_end != ""

    def test_weekly_report_bilingual(
        self,
        sample_project: Project,
        sample_tasks: list[PMOTask],
        sample_issues: list[Issue],
        sample_risks: list[Risk],
    ) -> None:
        report = generate_weekly_report(
            sample_project, sample_tasks, sample_issues, sample_risks
        )
        assert "プロジェクト" in report.summary_ja
        assert "Project" in report.summary_en

    def test_weekly_report_has_delay_score(
        self,
        sample_project: Project,
        sample_tasks: list[PMOTask],
        sample_issues: list[Issue],
        sample_risks: list[Risk],
    ) -> None:
        report = generate_weekly_report(
            sample_project, sample_tasks, sample_issues, sample_risks
        )
        assert report.delay_risk_score >= 0
        assert len(report.delay_risk_factors) > 0


# ---------------------------------------------------------------------------
# Dashboard Summary Tests
# ---------------------------------------------------------------------------
class TestDashboardSummary:
    def test_get_dashboard_summary(
        self,
        sample_project: Project,
        sample_tasks: list[PMOTask],
        sample_issues: list[Issue],
        sample_risks: list[Risk],
    ) -> None:
        summary = get_dashboard_summary(
            sample_project, sample_tasks, sample_issues, sample_risks
        )
        assert summary.project.id == sample_project.id
        assert "design" in summary.phase_progress
        assert summary.task_summary["total"] == 5
        assert summary.delay_risk_score >= 0


# ---------------------------------------------------------------------------
# Database Tests
# ---------------------------------------------------------------------------
class TestDatabase:
    def test_save_and_get_entity(self, db_path: str) -> None:
        project = Project(name="Test", client="Corp")
        save_entity("projects", project.id, project, db_path=db_path)
        result = get_entity("projects", project.id, db_path=db_path)
        assert result is not None
        assert result["name"] == "Test"

    def test_list_entities(self, db_path: str) -> None:
        p1 = Project(name="P1")
        p2 = Project(name="P2")
        save_entity("projects", p1.id, p1, db_path=db_path)
        save_entity("projects", p2.id, p2, db_path=db_path)
        results = list_entities("projects", db_path=db_path)
        assert len(results) == 2

    def test_delete_entity(self, db_path: str) -> None:
        project = Project(name="To Delete")
        save_entity("projects", project.id, project, db_path=db_path)
        deleted = delete_entity("projects", project.id, db_path=db_path)
        assert deleted is True
        result = get_entity("projects", project.id, db_path=db_path)
        assert result is None

    def test_count_entities(self, db_path: str) -> None:
        for i in range(3):
            task = PMOTask(project_id="proj-1", title=f"Task {i}")
            save_entity("tasks", task.id, task, project_id="proj-1", db_path=db_path)
        count = count_entities("tasks", project_id="proj-1", db_path=db_path)
        assert count == 3

    def test_list_entities_by_project(self, db_path: str) -> None:
        t1 = PMOTask(project_id="proj-1", title="T1")
        t2 = PMOTask(project_id="proj-2", title="T2")
        save_entity("tasks", t1.id, t1, project_id="proj-1", db_path=db_path)
        save_entity("tasks", t2.id, t2, project_id="proj-2", db_path=db_path)
        results = list_entities("tasks", project_id="proj-1", db_path=db_path)
        assert len(results) == 1
        assert results[0]["title"] == "T1"


# ---------------------------------------------------------------------------
# Prompt Builder Tests
# ---------------------------------------------------------------------------
class TestPromptBuilders:
    def test_build_weekly_report_prompt(
        self,
        sample_project: Project,
        sample_tasks: list[PMOTask],
        sample_issues: list[Issue],
        sample_risks: list[Risk],
    ) -> None:
        prompt = build_weekly_report_prompt(
            sample_project, sample_tasks, sample_issues, sample_risks
        )
        assert "PMO" in prompt
        assert sample_project.name in prompt

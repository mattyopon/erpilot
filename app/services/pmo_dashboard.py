"""PMO Dashboard Service.

Manages SAP implementation project phases, tasks, issues, risks,
and generates weekly status reports with AI-powered delay risk prediction.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.models import (
    DashboardSummary,
    Issue,
    PMOTask,
    Project,
    ProjectPhase,
    Risk,
    RiskLevel,
    TaskPriority,
    TaskStatus,
    WeeklyReport,
)


# ---------------------------------------------------------------------------
# Phase management
# ---------------------------------------------------------------------------
PHASE_ORDER: list[ProjectPhase] = [
    ProjectPhase.CONCEPT,
    ProjectPhase.REQUIREMENTS,
    ProjectPhase.DESIGN,
    ProjectPhase.DEVELOPMENT,
    ProjectPhase.TESTING,
    ProjectPhase.GO_LIVE,
    ProjectPhase.SUPPORT,
]

PHASE_NAMES_JA: dict[ProjectPhase, str] = {
    ProjectPhase.CONCEPT: "構想",
    ProjectPhase.REQUIREMENTS: "要件定義",
    ProjectPhase.DESIGN: "設計",
    ProjectPhase.DEVELOPMENT: "開発",
    ProjectPhase.TESTING: "テスト",
    ProjectPhase.GO_LIVE: "本番稼働",
    ProjectPhase.SUPPORT: "保守",
}

# Typical duration (months) for each phase in SAP projects
PHASE_DURATION_MONTHS: dict[ProjectPhase, int] = {
    ProjectPhase.CONCEPT: 2,
    ProjectPhase.REQUIREMENTS: 3,
    ProjectPhase.DESIGN: 3,
    ProjectPhase.DEVELOPMENT: 4,
    ProjectPhase.TESTING: 3,
    ProjectPhase.GO_LIVE: 1,
    ProjectPhase.SUPPORT: 0,
}


def get_phase_progress(project: Project, tasks: list[PMOTask]) -> dict[str, Any]:
    """Calculate progress per phase."""
    progress: dict[str, Any] = {}
    for phase in PHASE_ORDER:
        phase_tasks = [t for t in tasks if t.phase == phase]
        total = len(phase_tasks)
        completed = sum(1 for t in phase_tasks if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in phase_tasks if t.status == TaskStatus.IN_PROGRESS)

        current = project.current_phase == phase
        past = PHASE_ORDER.index(phase) < PHASE_ORDER.index(project.current_phase)

        progress[phase.value] = {
            "name_ja": PHASE_NAMES_JA[phase],
            "total_tasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0.0,
            "is_current": current,
            "is_completed": past,
        }
    return progress


# ---------------------------------------------------------------------------
# Task summary
# ---------------------------------------------------------------------------
def get_task_summary(tasks: list[PMOTask]) -> dict[str, int]:
    """Summarize tasks by status."""
    summary: dict[str, int] = {s.value: 0 for s in TaskStatus}
    for task in tasks:
        summary[task.status.value] = summary.get(task.status.value, 0) + 1
    summary["total"] = len(tasks)
    return summary


def get_issue_summary(issues: list[Issue]) -> dict[str, int]:
    """Summarize issues by status and priority."""
    status_counts: dict[str, int] = {s.value: 0 for s in TaskStatus}
    priority_counts: dict[str, int] = {p.value: 0 for p in TaskPriority}
    for issue in issues:
        status_counts[issue.status.value] = status_counts.get(issue.status.value, 0) + 1
        priority_counts[issue.priority.value] = priority_counts.get(issue.priority.value, 0) + 1
    return {
        "total": len(issues),
        "by_status": status_counts,
        "by_priority": priority_counts,
    }


def get_risk_summary(risks: list[Risk]) -> dict[str, int]:
    """Summarize risks by level."""
    level_counts: dict[str, int] = {r.value: 0 for r in RiskLevel}
    for risk in risks:
        level_counts[risk.level.value] = level_counts.get(risk.level.value, 0) + 1
    return {
        "total": len(risks),
        "by_level": level_counts,
        "open": sum(1 for r in risks if r.status == "open"),
    }


# ---------------------------------------------------------------------------
# Delay risk prediction (rule-based prototype)
# ---------------------------------------------------------------------------
def predict_delay_risk(
    project: Project,
    tasks: list[PMOTask],
    issues: list[Issue],
    risks: list[Risk],
) -> tuple[float, list[str]]:
    """Predict delay risk score (0-100) and risk factors.

    Rule-based heuristic for prototype. Production version uses ML.
    """
    score = 0.0
    factors: list[str] = []

    # Factor 1: Overdue tasks
    today = datetime.utcnow().strftime("%Y-%m-%d")
    overdue_tasks = [
        t for t in tasks
        if t.due_date and t.due_date < today
        and t.status not in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)
    ]
    if overdue_tasks:
        overdue_pct = len(overdue_tasks) / max(len(tasks), 1) * 100
        score += min(overdue_pct * 2, 30)
        factors.append(
            f"期限超過タスク: {len(overdue_tasks)}件 "
            f"/ Overdue tasks: {len(overdue_tasks)}"
        )

    # Factor 2: Blocked tasks
    blocked = [t for t in tasks if t.status == TaskStatus.BLOCKED]
    if blocked:
        score += min(len(blocked) * 5, 20)
        factors.append(
            f"ブロック中タスク: {len(blocked)}件 "
            f"/ Blocked tasks: {len(blocked)}"
        )

    # Factor 3: High-priority open issues
    high_issues = [
        i for i in issues
        if i.priority == TaskPriority.HIGH
        and i.status != TaskStatus.COMPLETED
    ]
    if high_issues:
        score += min(len(high_issues) * 8, 25)
        factors.append(
            f"優先度高の未解決課題: {len(high_issues)}件 "
            f"/ High-priority open issues: {len(high_issues)}"
        )

    # Factor 4: High risks
    high_risks = [r for r in risks if r.level == RiskLevel.HIGH and r.status == "open"]
    if high_risks:
        score += min(len(high_risks) * 10, 25)
        factors.append(
            f"高リスク(未対応): {len(high_risks)}件 "
            f"/ High risks (open): {len(high_risks)}"
        )

    # Factor 5: Low completion rate in current phase
    current_phase_tasks = [t for t in tasks if t.phase == project.current_phase]
    if current_phase_tasks:
        completed_rate = (
            sum(1 for t in current_phase_tasks if t.status == TaskStatus.COMPLETED)
            / len(current_phase_tasks)
        )
        if completed_rate < 0.3:
            score += 10
            factors.append(
                f"現フェーズの進捗率が低い: {completed_rate*100:.0f}% "
                f"/ Low current phase progress: {completed_rate*100:.0f}%"
            )

    score = min(score, 100.0)

    if not factors:
        factors.append("重大な遅延リスク要因は検出されていません / No significant delay risk factors detected")

    return round(score, 1), factors


# ---------------------------------------------------------------------------
# Weekly report generation
# ---------------------------------------------------------------------------
def generate_weekly_report(
    project: Project,
    tasks: list[PMOTask],
    issues: list[Issue],
    risks: list[Risk],
) -> WeeklyReport:
    """Generate a weekly status report."""
    today = datetime.utcnow()
    week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
    week_end = (today + timedelta(days=6 - today.weekday())).strftime("%Y-%m-%d")

    task_sum = get_task_summary(tasks)
    delay_score, delay_factors = predict_delay_risk(project, tasks, issues, risks)

    open_issues = sum(
        1 for i in issues if i.status != TaskStatus.COMPLETED
    )
    high_risks = sum(
        1 for r in risks if r.level == RiskLevel.HIGH and r.status == "open"
    )

    summary_ja = _build_summary_ja(project, task_sum, open_issues, high_risks, delay_score)
    summary_en = _build_summary_en(project, task_sum, open_issues, high_risks, delay_score)

    return WeeklyReport(
        project_id=project.id,
        week_start=week_start,
        week_end=week_end,
        summary_ja=summary_ja,
        summary_en=summary_en,
        phase=project.current_phase,
        tasks_completed=task_sum.get("completed", 0),
        tasks_in_progress=task_sum.get("in_progress", 0),
        tasks_blocked=task_sum.get("blocked", 0),
        open_issues=open_issues,
        high_risks=high_risks,
        delay_risk_score=delay_score,
        delay_risk_factors=delay_factors,
    )


def _build_summary_ja(
    project: Project,
    task_sum: dict[str, int],
    open_issues: int,
    high_risks: int,
    delay_score: float,
) -> str:
    phase_ja = PHASE_NAMES_JA.get(project.current_phase, project.current_phase.value)
    risk_label = "低" if delay_score < 30 else "中" if delay_score < 60 else "高"
    return (
        f"# 週次ステータスレポート\n\n"
        f"## プロジェクト: {project.name}\n"
        f"### 現在のフェーズ: {phase_ja}\n\n"
        f"## タスク状況\n"
        f"- 完了: {task_sum.get('completed', 0)}件\n"
        f"- 進行中: {task_sum.get('in_progress', 0)}件\n"
        f"- ブロック中: {task_sum.get('blocked', 0)}件\n"
        f"- 未着手: {task_sum.get('not_started', 0)}件\n\n"
        f"## 課題・リスク\n"
        f"- 未解決課題: {open_issues}件\n"
        f"- 高リスク: {high_risks}件\n\n"
        f"## 遅延リスク評価: {delay_score}点 ({risk_label})\n"
    )


def _build_summary_en(
    project: Project,
    task_sum: dict[str, int],
    open_issues: int,
    high_risks: int,
    delay_score: float,
) -> str:
    risk_label = "Low" if delay_score < 30 else "Medium" if delay_score < 60 else "High"
    return (
        f"# Weekly Status Report\n\n"
        f"## Project: {project.name}\n"
        f"### Current Phase: {project.current_phase.value}\n\n"
        f"## Task Summary\n"
        f"- Completed: {task_sum.get('completed', 0)}\n"
        f"- In Progress: {task_sum.get('in_progress', 0)}\n"
        f"- Blocked: {task_sum.get('blocked', 0)}\n"
        f"- Not Started: {task_sum.get('not_started', 0)}\n\n"
        f"## Issues & Risks\n"
        f"- Open Issues: {open_issues}\n"
        f"- High Risks: {high_risks}\n\n"
        f"## Delay Risk Score: {delay_score} ({risk_label})\n"
    )


def get_dashboard_summary(
    project: Project,
    tasks: list[PMOTask],
    issues: list[Issue],
    risks: list[Risk],
) -> DashboardSummary:
    """Build the full dashboard summary."""
    delay_score, delay_factors = predict_delay_risk(project, tasks, issues, risks)
    return DashboardSummary(
        project=project,
        phase_progress=get_phase_progress(project, tasks),
        task_summary=get_task_summary(tasks),
        issue_summary=get_issue_summary(issues),
        risk_summary=get_risk_summary(risks),
        delay_risk_score=delay_score,
        delay_risk_factors=delay_factors,
    )


def build_weekly_report_prompt(
    project: Project,
    tasks: list[PMOTask],
    issues: list[Issue],
    risks: list[Risk],
) -> str:
    """Build a prompt for LLM-enhanced weekly report generation."""
    phase_ja = PHASE_NAMES_JA.get(project.current_phase, project.current_phase.value)
    task_lines = "\n".join(
        f"- [{t.status.value}] {t.title} (期限: {t.due_date}, 担当: {t.assignee})"
        for t in tasks[:50]  # Limit for context
    )
    issue_lines = "\n".join(
        f"- [{i.priority.value}] {i.title}: {i.description[:100]}"
        for i in issues[:20]
    )
    risk_lines = "\n".join(
        f"- [{r.level.value}] {r.title}: {r.description[:100]}"
        for r in risks[:20]
    )

    return f"""あなたはSAP導入プロジェクトのPMOアシスタントです。
以下のプロジェクト情報から、週次ステータスレポートを日本語と英語で作成してください。

## プロジェクト情報
- 名前: {project.name}
- クライアント: {project.client}
- 現在のフェーズ: {phase_ja}
- Go-Live予定: {project.go_live_date}

## タスク一覧
{task_lines}

## 課題一覧
{issue_lines}

## リスク一覧
{risk_lines}

## 出力形式
1. エグゼクティブサマリー（3-5行、日本語）
2. Executive Summary (3-5 lines, English)
3. 今週の主な進捗
4. 課題・リスクの状況
5. 来週のアクションアイテム
6. 遅延リスク評価とその根拠
"""

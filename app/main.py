"""ERPilot FastAPI Application.

SAP Implementation PMO AI - API endpoints for all core services.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import (
    get_entity,
    init_db,
    list_entities,
    save_entity,
)
from app.knowledge.sap_modules import (
    get_module,
    get_module_summary,
    search_functions,
)
from app.models import (
    CreateProjectRequest,
    FitGapAnswerRequest,
    FitGapStartRequest,
    GenerateTestCasesRequest,
    GenerateTrainingRequest,
    GenerateWeeklyReportRequest,
    Issue,
    Language,
    PMOTask,
    Project,
    Risk,
    TranslationRequest,
)
from app.services.bridge import (
    get_glossary,
    summarize_meeting,
    translate_text,
)
from app.services.fitgap import process_answer, start_session
from app.services.pmo_dashboard import (
    generate_weekly_report,
    get_dashboard_summary,
)
from app.services.test_generator import generate_test_suite, generate_uat_scenarios
from app.services.training_gen import (
    generate_training_material,
    get_available_templates,
)

app = FastAPI(
    title="ERPilot",
    description="SAP Implementation PMO AI - SAP導入PMO AIアシスタント",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    """Initialize database on startup."""
    init_db()


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "ERPilot"}


# ---------------------------------------------------------------------------
# SAP Knowledge Base
# ---------------------------------------------------------------------------
@app.get("/api/modules")
def list_modules() -> list[dict[str, str]]:
    """List all SAP modules."""
    return get_module_summary()


@app.get("/api/modules/{module_id}")
def get_module_detail(module_id: str) -> dict[str, Any]:
    """Get detailed module information."""
    mod = get_module(module_id)
    if mod is None:
        raise HTTPException(status_code=404, detail=f"Module {module_id} not found")
    return mod


@app.get("/api/modules/search/{keyword}")
def search_module_functions(keyword: str) -> list[dict[str, Any]]:
    """Search SAP functions across all modules."""
    return search_functions(keyword)


# ---------------------------------------------------------------------------
# Project Management
# ---------------------------------------------------------------------------
@app.post("/api/projects")
def create_project(req: CreateProjectRequest) -> Project:
    """Create a new SAP implementation project."""
    project = Project(
        name=req.name,
        name_ja=req.name_ja,
        client=req.client,
        description=req.description,
        modules=req.modules,
        start_date=req.start_date,
        go_live_date=req.go_live_date,
    )
    save_entity("projects", project.id, project)
    return project


@app.get("/api/projects")
def list_projects() -> list[dict[str, Any]]:
    """List all projects."""
    return list_entities("projects")


@app.get("/api/projects/{project_id}")
def get_project(project_id: str) -> dict[str, Any]:
    """Get project details."""
    project = get_entity("projects", project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ---------------------------------------------------------------------------
# Fit/Gap Analysis
# ---------------------------------------------------------------------------
_sessions: dict[str, Any] = {}  # In-memory session store for prototype


@app.post("/api/fitgap/start")
def start_fitgap(req: FitGapStartRequest) -> dict[str, Any]:
    """Start a Fit/Gap analysis session."""
    session = start_session(req.project_id, req.module_id)
    _sessions[session.id] = session
    return session.model_dump()


@app.post("/api/fitgap/answer")
def answer_fitgap(req: FitGapAnswerRequest) -> dict[str, Any]:
    """Submit an answer in a Fit/Gap session."""
    session = _sessions.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    session = process_answer(session, req.answer)
    _sessions[session.id] = session
    if session.is_complete and session.report:
        save_entity(
            "fitgap_reports",
            session.report.id,
            session.report,
            project_id=session.project_id,
            module_id=session.module_id,
        )
    return session.model_dump()


@app.get("/api/fitgap/sessions/{session_id}")
def get_fitgap_session(session_id: str) -> dict[str, Any]:
    """Get current session state."""
    session = _sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.model_dump()


@app.get("/api/fitgap/reports/{project_id}")
def list_fitgap_reports(project_id: str) -> list[dict[str, Any]]:
    """List Fit/Gap reports for a project."""
    return list_entities("fitgap_reports", project_id=project_id)


# ---------------------------------------------------------------------------
# PMO Dashboard - Tasks
# ---------------------------------------------------------------------------
@app.post("/api/tasks")
def create_task(task: PMOTask) -> PMOTask:
    """Create a project task."""
    save_entity("tasks", task.id, task, project_id=task.project_id)
    return task


@app.get("/api/tasks/{project_id}")
def list_tasks(project_id: str) -> list[dict[str, Any]]:
    """List tasks for a project."""
    return list_entities("tasks", project_id=project_id)


# ---------------------------------------------------------------------------
# PMO Dashboard - Issues
# ---------------------------------------------------------------------------
@app.post("/api/issues")
def create_issue(issue: Issue) -> Issue:
    """Create a project issue."""
    save_entity("issues", issue.id, issue, project_id=issue.project_id)
    return issue


@app.get("/api/issues/{project_id}")
def list_issues(project_id: str) -> list[dict[str, Any]]:
    """List issues for a project."""
    return list_entities("issues", project_id=project_id)


# ---------------------------------------------------------------------------
# PMO Dashboard - Risks
# ---------------------------------------------------------------------------
@app.post("/api/risks")
def create_risk(risk: Risk) -> Risk:
    """Create a project risk."""
    save_entity("risks", risk.id, risk, project_id=risk.project_id)
    return risk


@app.get("/api/risks/{project_id}")
def list_risks(project_id: str) -> list[dict[str, Any]]:
    """List risks for a project."""
    return list_entities("risks", project_id=project_id)


# ---------------------------------------------------------------------------
# PMO Dashboard - Summary & Weekly Report
# ---------------------------------------------------------------------------
@app.get("/api/dashboard/{project_id}")
def get_dashboard(project_id: str) -> dict[str, Any]:
    """Get dashboard summary for a project."""
    project_data = get_entity("projects", project_id)
    if project_data is None:
        raise HTTPException(status_code=404, detail="Project not found")

    project = Project(**project_data)
    tasks = [PMOTask(**t) for t in list_entities("tasks", project_id=project_id)]
    issues = [Issue(**i) for i in list_entities("issues", project_id=project_id)]
    risks = [Risk(**r) for r in list_entities("risks", project_id=project_id)]

    summary = get_dashboard_summary(project, tasks, issues, risks)
    return summary.model_dump()


@app.post("/api/reports/weekly")
def create_weekly_report(req: GenerateWeeklyReportRequest) -> dict[str, Any]:
    """Generate a weekly status report."""
    project_data = get_entity("projects", req.project_id)
    if project_data is None:
        raise HTTPException(status_code=404, detail="Project not found")

    project = Project(**project_data)
    tasks = [PMOTask(**t) for t in list_entities("tasks", project_id=req.project_id)]
    issues = [Issue(**i) for i in list_entities("issues", project_id=req.project_id)]
    risks = [Risk(**r) for r in list_entities("risks", project_id=req.project_id)]

    report = generate_weekly_report(project, tasks, issues, risks)
    save_entity("weekly_reports", report.id, report, project_id=req.project_id)
    return report.model_dump()


# ---------------------------------------------------------------------------
# Test Case Generation
# ---------------------------------------------------------------------------
@app.post("/api/testcases/generate")
def generate_test_cases(req: GenerateTestCasesRequest) -> dict[str, Any]:
    """Generate test cases for a module."""
    suite = generate_test_suite(
        project_id=req.project_id,
        module_id=req.module_id,
        requirements=req.requirements,
        test_type=req.test_type,
    )
    save_entity("test_suites", suite.id, suite, project_id=req.project_id)
    return suite.model_dump()


@app.post("/api/testcases/uat")
def generate_uat(req: GenerateTestCasesRequest) -> dict[str, Any]:
    """Generate UAT test scenarios."""
    suite = generate_uat_scenarios(
        project_id=req.project_id,
        module_id=req.module_id,
        business_process=req.requirements,
    )
    save_entity("test_suites", suite.id, suite, project_id=req.project_id)
    return suite.model_dump()


@app.get("/api/testcases/{project_id}")
def list_test_suites(project_id: str) -> list[dict[str, Any]]:
    """List test suites for a project."""
    return list_entities("test_suites", project_id=project_id)


# ---------------------------------------------------------------------------
# Training Material Generation
# ---------------------------------------------------------------------------
@app.get("/api/training/templates")
def list_training_templates() -> list[dict[str, str]]:
    """List available training templates."""
    return get_available_templates()


@app.post("/api/training/generate")
def generate_training(req: GenerateTrainingRequest) -> dict[str, Any]:
    """Generate training material."""
    material = generate_training_material(
        project_id=req.project_id,
        module_id=req.module_id,
        process_name=req.process_name,
        target_audience=req.target_audience,
        language=req.language,
    )
    save_entity("training_materials", material.id, material, project_id=req.project_id)
    return material.model_dump()


@app.get("/api/training/{project_id}")
def list_training_materials(project_id: str) -> list[dict[str, Any]]:
    """List training materials for a project."""
    return list_entities("training_materials", project_id=project_id)


# ---------------------------------------------------------------------------
# Japanese-English Bridge
# ---------------------------------------------------------------------------
@app.get("/api/bridge/glossary")
def list_glossary(context: str | None = None) -> list[dict[str, str]]:
    """Get SAP bilingual glossary."""
    return get_glossary(context)


@app.post("/api/bridge/translate")
def translate(req: TranslationRequest) -> dict[str, Any]:
    """Translate text between Japanese and English."""
    result = translate_text(req)
    return result.model_dump()


@app.post("/api/bridge/meeting")
def summarize_meeting_minutes(
    project_id: str,
    title: str,
    date: str,
    raw_text: str,
    attendees: list[str] | None = None,
    language: Language = Language.JA,
) -> dict[str, Any]:
    """Summarize meeting minutes."""
    minutes = summarize_meeting(
        project_id=project_id,
        title=title,
        date=date,
        attendees=attendees or [],
        raw_text=raw_text,
        original_language=language,
    )
    save_entity("meeting_minutes", minutes.id, minutes, project_id=project_id)
    return minutes.model_dump()

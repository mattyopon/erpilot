"""ERPilot data models using Pydantic."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class ProjectPhase(str, Enum):
    """SAP implementation project phases."""
    CONCEPT = "concept"           # 構想
    REQUIREMENTS = "requirements" # 要件定義
    DESIGN = "design"             # 設計
    DEVELOPMENT = "development"   # 開発
    TESTING = "testing"           # テスト
    GO_LIVE = "go_live"           # 本番稼働
    SUPPORT = "support"           # 保守


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FitGapStatus(str, Enum):
    FIT = "fit"
    GAP = "gap"
    PARTIAL_FIT = "partial_fit"


class Language(str, Enum):
    JA = "ja"
    EN = "en"


# ---------------------------------------------------------------------------
# Fit/Gap Analysis Models
# ---------------------------------------------------------------------------
class FitGapItem(BaseModel):
    """Single Fit/Gap analysis item."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    module_id: str
    function_id: str
    function_name: str
    function_name_ja: str
    status: FitGapStatus
    gap_description: str = ""
    gap_description_ja: str = ""
    customization_effort: str = ""  # low / medium / high
    priority: str = "medium"
    notes: str = ""


class FitGapReport(BaseModel):
    """Complete Fit/Gap analysis report for a module."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    module_id: str
    module_name: str
    module_name_ja: str
    items: list[FitGapItem] = []
    fit_count: int = 0
    gap_count: int = 0
    partial_fit_count: int = 0
    fit_rate: float = 0.0
    summary: str = ""
    summary_ja: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def calculate_fit_rate(self) -> None:
        """Calculate fit rate from items."""
        self.fit_count = sum(1 for i in self.items if i.status == FitGapStatus.FIT)
        self.gap_count = sum(1 for i in self.items if i.status == FitGapStatus.GAP)
        self.partial_fit_count = sum(
            1 for i in self.items if i.status == FitGapStatus.PARTIAL_FIT
        )
        total = len(self.items)
        if total > 0:
            self.fit_rate = round(
                (self.fit_count + self.partial_fit_count * 0.5) / total * 100, 1
            )


class FitGapSession(BaseModel):
    """Interactive Fit/Gap analysis session state."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    module_id: str
    messages: list[dict[str, str]] = []
    current_question_index: int = 0
    answers: dict[str, str] = {}
    is_complete: bool = False
    report: FitGapReport | None = None


# ---------------------------------------------------------------------------
# PMO Dashboard Models
# ---------------------------------------------------------------------------
class Project(BaseModel):
    """SAP implementation project."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    name_ja: str = ""
    client: str = ""
    description: str = ""
    current_phase: ProjectPhase = ProjectPhase.CONCEPT
    start_date: str = ""
    go_live_date: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modules: list[str] = []  # Module IDs: SD, MM, FI, etc.


class PMOTask(BaseModel):
    """Project task."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    title: str
    title_ja: str = ""
    description: str = ""
    phase: ProjectPhase = ProjectPhase.CONCEPT
    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: str = ""
    due_date: str = ""
    module_id: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class Issue(BaseModel):
    """Project issue."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    title: str
    title_ja: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.NOT_STARTED
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: str = ""
    due_date: str = ""
    module_id: str = ""
    impact: str = ""
    resolution: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Risk(BaseModel):
    """Project risk."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    title: str
    title_ja: str = ""
    description: str = ""
    level: RiskLevel = RiskLevel.MEDIUM
    probability: str = "medium"  # low / medium / high
    impact: str = "medium"       # low / medium / high
    mitigation: str = ""
    status: str = "open"         # open / mitigated / closed
    module_id: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WeeklyReport(BaseModel):
    """Auto-generated weekly status report."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    week_start: str
    week_end: str
    summary_ja: str = ""
    summary_en: str = ""
    phase: ProjectPhase = ProjectPhase.CONCEPT
    tasks_completed: int = 0
    tasks_in_progress: int = 0
    tasks_blocked: int = 0
    open_issues: int = 0
    high_risks: int = 0
    delay_risk_score: float = 0.0
    delay_risk_factors: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Test Case Models
# ---------------------------------------------------------------------------
class TestStep(BaseModel):
    """Single test step."""
    step_number: int
    action: str
    action_ja: str = ""
    t_code: str = ""
    input_data: str = ""
    expected_result: str = ""
    expected_result_ja: str = ""


class TestCase(BaseModel):
    """SAP test case."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    module_id: str
    scenario_name: str
    scenario_name_ja: str = ""
    description: str = ""
    preconditions: str = ""
    steps: list[TestStep] = []
    priority: str = "medium"
    test_type: str = "unit"  # unit / integration / uat
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TestSuite(BaseModel):
    """Collection of test cases."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    name: str
    name_ja: str = ""
    module_id: str = ""
    test_type: str = "unit"
    test_cases: list[TestCase] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Training Material Models
# ---------------------------------------------------------------------------
class TrainingStep(BaseModel):
    """Single step in a training procedure."""
    step_number: int
    instruction: str
    instruction_ja: str = ""
    t_code: str = ""
    screen_area: str = ""
    field_actions: list[str] = []
    tips: str = ""


class TrainingMaterial(BaseModel):
    """Training document for SAP operations."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    module_id: str
    title: str
    title_ja: str = ""
    description: str = ""
    target_audience: str = ""
    prerequisites: str = ""
    steps: list[TrainingStep] = []
    language: Language = Language.JA
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Bridge (日英ブリッジ) Models
# ---------------------------------------------------------------------------
class MeetingMinutes(BaseModel):
    """Meeting minutes with translation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    title: str
    date: str
    attendees: list[str] = []
    original_text: str
    original_language: Language = Language.JA
    summary_ja: str = ""
    summary_en: str = ""
    action_items_ja: list[str] = []
    action_items_en: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TranslationRequest(BaseModel):
    """Translation request."""
    text: str
    source_language: Language
    target_language: Language
    context: str = "SAP implementation project"
    document_type: str = "general"  # general / requirements / meeting / issue


class TranslationResponse(BaseModel):
    """Translation response."""
    original_text: str
    translated_text: str
    source_language: Language
    target_language: Language
    glossary_used: list[dict[str, str]] = []


# ---------------------------------------------------------------------------
# API Request/Response Models
# ---------------------------------------------------------------------------
class CreateProjectRequest(BaseModel):
    name: str
    name_ja: str = ""
    client: str = ""
    description: str = ""
    modules: list[str] = []
    start_date: str = ""
    go_live_date: str = ""


class FitGapStartRequest(BaseModel):
    project_id: str
    module_id: str


class FitGapAnswerRequest(BaseModel):
    session_id: str
    answer: str


class GenerateTestCasesRequest(BaseModel):
    project_id: str
    module_id: str
    requirements: str
    test_type: str = "unit"


class GenerateTrainingRequest(BaseModel):
    project_id: str
    module_id: str
    process_name: str
    target_audience: str = "end_user"
    language: Language = Language.JA


class GenerateWeeklyReportRequest(BaseModel):
    project_id: str


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class DashboardSummary(BaseModel):
    """Dashboard overview data."""
    project: Project
    phase_progress: dict[str, Any] = {}
    task_summary: dict[str, int] = {}
    issue_summary: dict[str, Any] = {}
    risk_summary: dict[str, Any] = {}
    fit_gap_summary: dict[str, Any] = {}
    delay_risk_score: float = 0.0
    delay_risk_factors: list[str] = []

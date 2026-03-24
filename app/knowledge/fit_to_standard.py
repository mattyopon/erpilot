"""Fit-to-Standard Analysis Framework based on SAP Activate Methodology.

SAP Activate promotes a Fit-to-Standard approach where organizations adopt
SAP Best Practices as the baseline and only deviate when there is a clear,
justified business need. This module provides the framework for classifying
fits and gaps, and recommending gap resolution strategies.

Reference: SAP Activate Methodology
Reference: https://help.sap.com/docs/SAP_ACTIVATE
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# Fit Classification
# ============================================================================

class FitClassification(str, Enum):
    """Classification of how well a business requirement fits SAP standard."""

    STANDARD_FIT = "standard_fit"
    """Business requirement is fully met by SAP Best Practices standard process.
    No configuration changes needed beyond basic parameter settings."""

    CONFIGURATION_FIT = "configuration_fit"
    """Business requirement can be met through SAP configuration (IMG/customizing).
    No code changes needed, but configuration effort is required."""

    GAP = "gap"
    """Business requirement cannot be met by SAP standard or configuration.
    Extension or process change is required."""


# ============================================================================
# Gap Resolution Strategy
# ============================================================================

class GapResolutionType(str, Enum):
    """Types of gap resolution, ordered by recommendation priority.

    SAP Activate methodology recommends Process Change first, then In-App,
    then Side-by-Side, and Custom Development as last resort.
    """

    PROCESS_CHANGE = "process_change"
    """Adapt the business process to fit SAP standard.
    HIGHEST PRIORITY: Always evaluate this option first."""

    IN_APP_EXTENSION = "in_app_extension"
    """Extend using SAP's in-app extensibility (Custom Fields, Custom Logic,
    Key User Extensibility). Stays within the SAP clean core."""

    SIDE_BY_SIDE_EXTENSION = "side_by_side_extension"
    """Build on SAP BTP (Business Technology Platform) with APIs connecting
    to S/4HANA. Keeps core clean while adding functionality."""

    CUSTOM_DEVELOPMENT = "custom_development"
    """Traditional ABAP development or modification.
    LOWEST PRIORITY: Only when no other option works. Impacts upgrade path."""


# Recommended evaluation order (highest to lowest priority)
GAP_RESOLUTION_PRIORITY: list[GapResolutionType] = [
    GapResolutionType.PROCESS_CHANGE,
    GapResolutionType.IN_APP_EXTENSION,
    GapResolutionType.SIDE_BY_SIDE_EXTENSION,
    GapResolutionType.CUSTOM_DEVELOPMENT,
]


# ============================================================================
# Fit-to-Standard Question Framework
# ============================================================================

# Questions to challenge whether a gap is truly necessary
CHALLENGE_QUESTIONS: list[dict[str, str]] = [
    {
        "id": "cq01",
        "ja": "SAP標準プロセスをそのまま採用した場合、具体的にどのような業務上の問題が発生しますか？",
        "en": "If you adopt the SAP standard process as-is, what specific business problems would occur?",
        "purpose": "Validate that the gap is genuine and not based on habit",
    },
    {
        "id": "cq02",
        "ja": "現在のプロセスがそのようになっている理由は何ですか？規制要件ですか、過去の慣習ですか？",
        "en": "Why does your current process work this way? Is it a regulatory requirement or historical practice?",
        "purpose": "Distinguish regulatory gaps from preference gaps",
    },
    {
        "id": "cq03",
        "ja": "この要件はSAP標準の設定変更（カスタマイズ）だけで対応できませんか？",
        "en": "Can this requirement be addressed through SAP configuration alone (without code changes)?",
        "purpose": "Explore configuration options before development",
    },
    {
        "id": "cq04",
        "ja": "業務プロセスを変更してSAP標準に合わせることは可能ですか？変更の障壁は何ですか？",
        "en": "Is it possible to change the business process to fit SAP standard? What are the barriers?",
        "purpose": "Evaluate process change as the primary solution",
    },
    {
        "id": "cq05",
        "ja": "このGapを解消しない場合（SAP標準のまま運用した場合）のビジネスインパクトは何ですか？",
        "en": "What is the business impact if this gap is NOT resolved (operating with SAP standard)?",
        "purpose": "Quantify the gap severity",
    },
    {
        "id": "cq06",
        "ja": "同業他社はこのプロセスをどのように処理していますか？業界標準はSAPの標準と一致しませんか？",
        "en": "How do industry peers handle this process? Does the industry standard align with SAP standard?",
        "purpose": "Check if the gap is company-specific or industry-wide",
    },
    {
        "id": "cq07",
        "ja": "開発による対応はアップグレード時にコストが発生します。そのコストを考慮しても開発が必要ですか？",
        "en": "Custom development incurs costs during upgrades. Is development still necessary considering those costs?",
        "purpose": "Evaluate total cost of ownership for custom development",
    },
]


# ============================================================================
# Effort and Impact Estimation
# ============================================================================

EFFORT_ESTIMATES: dict[str, dict[str, Any]] = {
    "standard_fit": {
        "effort_days_range": (0, 2),
        "effort_label": "minimal",
        "effort_label_ja": "最小",
        "risk": "low",
        "upgrade_impact": "none",
        "description": "Standard configuration, no custom work needed",
        "description_ja": "標準設定のみ、カスタマイズ不要",
    },
    "configuration_fit": {
        "effort_days_range": (1, 10),
        "effort_label": "low_to_medium",
        "effort_label_ja": "低〜中",
        "risk": "low",
        "upgrade_impact": "minimal",
        "description": "Configuration changes in IMG, tested and documented",
        "description_ja": "IMG設定変更、テストとドキュメント作成が必要",
    },
    "process_change": {
        "effort_days_range": (5, 20),
        "effort_label": "medium",
        "effort_label_ja": "中",
        "risk": "medium",
        "upgrade_impact": "none",
        "description": "Business process redesign, change management, training",
        "description_ja": "業務プロセス再設計、変更管理、研修が必要",
    },
    "in_app_extension": {
        "effort_days_range": (5, 30),
        "effort_label": "medium",
        "effort_label_ja": "中",
        "risk": "low_to_medium",
        "upgrade_impact": "low",
        "description": "Key User or Developer extensibility within S/4HANA",
        "description_ja": "S/4HANA内のキーユーザー/開発者拡張",
    },
    "side_by_side_extension": {
        "effort_days_range": (10, 60),
        "effort_label": "medium_to_high",
        "effort_label_ja": "中〜高",
        "risk": "medium",
        "upgrade_impact": "low",
        "description": "BTP-based development with API integration",
        "description_ja": "BTP上の開発、API連携",
    },
    "custom_development": {
        "effort_days_range": (20, 100),
        "effort_label": "high",
        "effort_label_ja": "高",
        "risk": "high",
        "upgrade_impact": "high",
        "description": "ABAP development, modification. Full SDLC needed",
        "description_ja": "ABAP開発・修正。フルSDLCが必要",
    },
}


# ============================================================================
# Fit-to-Standard Analysis Result Model
# ============================================================================

class FitToStandardItem(BaseModel):
    """Result of Fit-to-Standard analysis for a single requirement."""

    requirement_id: str = ""
    requirement_description: str = ""
    requirement_description_ja: str = ""
    scope_item_id: str = ""
    scope_item_name: str = ""
    fit_classification: FitClassification = FitClassification.STANDARD_FIT
    gap_resolution: GapResolutionType | None = None
    gap_description: str = ""
    gap_description_ja: str = ""
    challenge_questions_asked: list[str] = Field(default_factory=list)
    effort_estimate: str = "low"
    risk_level: str = "low"
    upgrade_impact: str = "none"
    recommendation: str = ""
    recommendation_ja: str = ""
    priority: str = "medium"


class FitToStandardReport(BaseModel):
    """Complete Fit-to-Standard analysis report."""

    project_id: str
    module_id: str = ""
    items: list[FitToStandardItem] = Field(default_factory=list)
    standard_fit_count: int = 0
    configuration_fit_count: int = 0
    gap_count: int = 0
    gap_by_resolution: dict[str, int] = Field(default_factory=dict)
    overall_fit_rate: float = 0.0
    summary: str = ""
    summary_ja: str = ""

    def calculate_statistics(self) -> None:
        """Calculate fit/gap statistics from items."""
        self.standard_fit_count = sum(
            1 for i in self.items
            if i.fit_classification == FitClassification.STANDARD_FIT
        )
        self.configuration_fit_count = sum(
            1 for i in self.items
            if i.fit_classification == FitClassification.CONFIGURATION_FIT
        )
        self.gap_count = sum(
            1 for i in self.items
            if i.fit_classification == FitClassification.GAP
        )

        # Count gaps by resolution type
        self.gap_by_resolution = {}
        for item in self.items:
            if item.gap_resolution is not None:
                key = item.gap_resolution.value
                self.gap_by_resolution[key] = self.gap_by_resolution.get(key, 0) + 1

        total = len(self.items)
        if total > 0:
            fit_score = (
                self.standard_fit_count * 1.0
                + self.configuration_fit_count * 0.8
            )
            self.overall_fit_rate = round(fit_score / total * 100, 1)


# ============================================================================
# Helper Functions
# ============================================================================

def get_challenge_questions() -> list[dict[str, str]]:
    """Get all Fit-to-Standard challenge questions."""
    return CHALLENGE_QUESTIONS


def get_effort_estimate(classification_or_resolution: str) -> dict[str, Any]:
    """Get effort estimate for a fit classification or gap resolution type."""
    return EFFORT_ESTIMATES.get(classification_or_resolution, {})


def get_gap_resolution_priority() -> list[dict[str, str]]:
    """Get gap resolution types in recommended priority order."""
    descriptions = {
        GapResolutionType.PROCESS_CHANGE: {
            "name_en": "Process Change",
            "name_ja": "業務プロセス変更",
            "description": "Adapt business process to SAP standard",
            "description_ja": "業務プロセスをSAP標準に合わせる",
            "priority": "1 (Highest - Evaluate first)",
        },
        GapResolutionType.IN_APP_EXTENSION: {
            "name_en": "In-App Extension",
            "name_ja": "アプリ内拡張",
            "description": "Use SAP extensibility features (Custom Fields, Custom Logic)",
            "description_ja": "SAP拡張機能を使用（カスタムフィールド、カスタムロジック）",
            "priority": "2",
        },
        GapResolutionType.SIDE_BY_SIDE_EXTENSION: {
            "name_en": "Side-by-Side Extension",
            "name_ja": "サイドバイサイド拡張",
            "description": "Build on SAP BTP with API integration",
            "description_ja": "SAP BTP上で構築、API連携",
            "priority": "3",
        },
        GapResolutionType.CUSTOM_DEVELOPMENT: {
            "name_en": "Custom Development",
            "name_ja": "カスタム開発",
            "description": "Traditional ABAP development (last resort)",
            "description_ja": "従来のABAP開発（最終手段）",
            "priority": "4 (Lowest - Last resort)",
        },
    }
    return [
        {"type": t.value, **descriptions[t]}
        for t in GAP_RESOLUTION_PRIORITY
    ]


def recommend_resolution(
    gap_description: str,
    is_regulatory: bool = False,
    is_industry_standard: bool = False,
    current_process_changeable: bool = True,
) -> GapResolutionType:
    """Recommend a gap resolution type based on gap characteristics.

    This is a rule-based recommendation. In production, this would be
    augmented with LLM analysis.
    """
    # If the current process can be changed and it's not regulatory, prefer process change
    if current_process_changeable and not is_regulatory:
        return GapResolutionType.PROCESS_CHANGE

    # Regulatory or industry-standard gaps likely need technical solutions
    if is_regulatory:
        # Regulatory needs tend to be well-defined, in-app extension often works
        return GapResolutionType.IN_APP_EXTENSION

    if is_industry_standard:
        return GapResolutionType.IN_APP_EXTENSION

    # Default to side-by-side for complex gaps
    return GapResolutionType.SIDE_BY_SIDE_EXTENSION


def build_fit_to_standard_prompt(
    module_id: str,
    scope_items_summary: str,
    business_requirements: str,
) -> str:
    """Build prompt for LLM-based Fit-to-Standard analysis."""
    challenge_q_text = "\n".join(
        f"- {q['ja']}" for q in CHALLENGE_QUESTIONS
    )

    return f"""あなたはSAP S/4HANA Fit-to-Standard分析の専門家です。
SAP Activate方法論に基づいて、業務要件とSAP Best Practicesの適合度を分析してください。

## 分析原則（SAP Activate Fit-to-Standard）
1. SAP標準を「正」とする。標準から外れる理由を説明する責任はユーザー側にある
2. Gap解消の優先順位: 業務プロセス変更 > アプリ内拡張 > サイドバイサイド拡張 > カスタム開発
3. 「なぜ標準ではダメなのか？」を必ず問う

## チャレンジ質問フレームワーク
各Gapに対して以下の質問を適用してください:
{challenge_q_text}

## 対象モジュール: {module_id}

## SAP Best Practices Scope Items
{scope_items_summary}

## 業務要件
{business_requirements}

## 出力形式 (JSON配列)
各要件について:
- requirement_description / requirement_description_ja
- scope_item_id: 対応するScope Item ID
- fit_classification: "standard_fit" / "configuration_fit" / "gap"
- gap_resolution: (gapの場合) "process_change" / "in_app_extension" / "side_by_side_extension" / "custom_development"
- gap_description / gap_description_ja: Gap の詳細
- effort_estimate: "low" / "medium" / "high"
- recommendation / recommendation_ja: 推奨アクション

最後にサマリーを日英両方で記載してください。
"""

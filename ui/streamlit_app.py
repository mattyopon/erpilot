"""ERPilot Streamlit UI.

Provides a web interface for all ERPilot features:
- Fit/Gap Analysis Chat
- PMO Dashboard
- Test Case Generation
- Training Material Generation
- Japanese-English Bridge
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.db.database import (
    init_db,
    list_entities,
    save_entity,
)
from app.knowledge.sap_modules import get_module_summary
from app.models import (
    Issue,
    Language,
    PMOTask,
    Project,
    ProjectPhase,
    Risk,
    RiskLevel,
    TaskPriority,
    TranslationRequest,
)
from app.services.bridge import get_glossary, summarize_meeting, translate_text
from app.services.fitgap import process_answer, start_session
from app.services.pmo_dashboard import (
    generate_weekly_report,
    get_dashboard_summary,
)
from app.services.test_generator import generate_test_suite
from app.services.training_gen import generate_training_material, get_available_templates

# Initialize database
init_db()

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ERPilot - SAP導入PMO AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
st.sidebar.title("ERPilot")
st.sidebar.caption("SAP導入PMO AIアシスタント")

page = st.sidebar.radio(
    "メニュー / Menu",
    [
        "🏠 ホーム / Home",
        "📊 Fit/Gap分析 / Fit-Gap Analysis",
        "📋 PMOダッシュボード / PMO Dashboard",
        "🧪 テストケース生成 / Test Cases",
        "📚 トレーニング資料 / Training",
        "🌏 日英ブリッジ / JA-EN Bridge",
    ],
)


# ---------------------------------------------------------------------------
# Home Page
# ---------------------------------------------------------------------------
def render_home() -> None:
    st.title("ERPilot - SAP導入PMO AI")
    st.markdown("""
    ### SAP導入プロジェクトをAIでサポート

    **ERPilot**は、SAP S/4HANA導入プロジェクトのPMO業務をAIで自動化・効率化するSaaSです。

    ---

    #### 主な機能

    | 機能 | 概要 |
    |------|------|
    | **Fit/Gap分析AI** | チャット形式で業務ヒアリング → SAP標準機能とのマッチング |
    | **PMOダッシュボード** | フェーズ管理、タスク・課題・リスク管理、遅延リスク予測 |
    | **テストケース自動生成** | 業務要件からSAPテストシナリオを自動生成 |
    | **トレーニング資料生成** | SAP画面の操作手順書をAIが生成 |
    | **日英ブリッジ** | 会議議事録の自動要約・翻訳、SAP用語集 |

    ---

    #### 対応SAPモジュール
    """)

    modules = get_module_summary()
    cols = st.columns(3)
    for i, mod in enumerate(modules):
        with cols[i % 3]:
            st.metric(
                label=f"{mod['id']} - {mod['name_ja']}",
                value=f"{mod['function_count']}機能",
            )


# ---------------------------------------------------------------------------
# Fit/Gap Analysis Page
# ---------------------------------------------------------------------------
def render_fitgap() -> None:
    st.title("📊 Fit/Gap分析AI")
    st.markdown("SAP標準機能と御社の業務プロセスのFit/Gap分析をチャット形式で実施します。")

    # Module selection
    modules = get_module_summary()
    module_options = {f"{m['id']} - {m['name_ja']}": m['id'] for m in modules}
    selected = st.selectbox("分析対象モジュール", list(module_options.keys()))
    module_id = module_options[selected] if selected else "SD"

    # Session management
    if "fitgap_session" not in st.session_state:
        st.session_state.fitgap_session = None

    if st.button("分析を開始する / Start Analysis"):
        session = start_session("demo-project", module_id)
        st.session_state.fitgap_session = session
        st.rerun()

    session = st.session_state.fitgap_session
    if session is None:
        st.info("上のボタンをクリックしてFit/Gap分析を開始してください。")
        return

    # Display chat messages
    for msg in session.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input for next answer
    if not session.is_complete:
        answer = st.chat_input("回答を入力してください / Enter your answer")
        if answer:
            session = process_answer(session, answer)
            st.session_state.fitgap_session = session
            st.rerun()
    else:
        # Show report
        if session.report:
            st.divider()
            st.subheader("📑 Fit/Gap分析レポート")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Fit率", f"{session.report.fit_rate}%")
            with col2:
                st.metric("Fit", session.report.fit_count)
            with col3:
                st.metric("Partial Fit", session.report.partial_fit_count)
            with col4:
                st.metric("Gap", session.report.gap_count)

            st.markdown("### 詳細")
            for item in session.report.items:
                icon = "✅" if item.status.value == "fit" else "⚠️" if item.status.value == "partial_fit" else "❌"
                with st.expander(f"{icon} {item.function_name_ja} ({item.function_name})"):
                    st.write(f"**ステータス**: {item.status.value}")
                    st.write(f"**説明**: {item.gap_description_ja}")
                    st.write(f"**カスタマイズ工数**: {item.customization_effort}")


# ---------------------------------------------------------------------------
# PMO Dashboard Page
# ---------------------------------------------------------------------------
def render_pmo_dashboard() -> None:
    st.title("📋 PMOダッシュボード")

    # Project selection/creation
    projects = list_entities("projects")

    if not projects:
        st.info("プロジェクトを作成してください。")
        with st.form("create_project"):
            name = st.text_input("プロジェクト名", "SAP S/4HANA導入プロジェクト")
            client = st.text_input("クライアント名", "サンプル株式会社")
            go_live = st.text_input("Go-Live予定日", "2027-04-01")
            if st.form_submit_button("プロジェクト作成"):
                project = Project(
                    name=name, name_ja=name, client=client,
                    go_live_date=go_live, modules=["SD", "MM", "FI", "CO"],
                )
                save_entity("projects", project.id, project)
                st.success(f"プロジェクト作成完了: {project.id}")
                st.rerun()
        return

    project_data = projects[0]
    project = Project(**project_data)

    # Dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "概要", "タスク", "課題", "リスク", "週次レポート"
    ])

    with tab1:
        tasks = [PMOTask(**t) for t in list_entities("tasks", project_id=project.id)]
        issues = [Issue(**i) for i in list_entities("issues", project_id=project.id)]
        risks = [Risk(**r) for r in list_entities("risks", project_id=project.id)]

        summary = get_dashboard_summary(project, tasks, issues, risks)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("現在のフェーズ", project.current_phase.value)
        with col2:
            risk_label = "低" if summary.delay_risk_score < 30 else "中" if summary.delay_risk_score < 60 else "高"
            st.metric("遅延リスクスコア", f"{summary.delay_risk_score} ({risk_label})")
        with col3:
            st.metric("Go-Live", project.go_live_date or "未設定")

        st.subheader("フェーズ進捗")
        for phase_val, info in summary.phase_progress.items():
            progress = info["completion_rate"] / 100.0
            label = f"{info['name_ja']} ({info['completion_rate']}%)"
            if info["is_current"]:
                label += " ← 現在"
            st.progress(progress, text=label)

    with tab2:
        st.subheader("タスク管理")
        with st.form("add_task"):
            t_title = st.text_input("タスク名")
            t_phase = st.selectbox("フェーズ", [p.value for p in ProjectPhase])
            t_priority = st.selectbox("優先度", [p.value for p in TaskPriority])
            t_due = st.text_input("期限 (YYYY-MM-DD)")
            if st.form_submit_button("タスク追加"):
                task = PMOTask(
                    project_id=project.id, title=t_title,
                    phase=ProjectPhase(t_phase),
                    priority=TaskPriority(t_priority), due_date=t_due,
                )
                save_entity("tasks", task.id, task, project_id=project.id)
                st.success("タスクを追加しました")
                st.rerun()

        tasks_data = list_entities("tasks", project_id=project.id)
        if tasks_data:
            for t in tasks_data:
                st.write(f"- [{t.get('status', 'not_started')}] {t.get('title', '')} "
                        f"(期限: {t.get('due_date', 'N/A')})")

    with tab3:
        st.subheader("課題管理")
        with st.form("add_issue"):
            i_title = st.text_input("課題名")
            i_desc = st.text_area("説明")
            i_priority = st.selectbox("優先度 ", [p.value for p in TaskPriority])
            if st.form_submit_button("課題追加"):
                issue = Issue(
                    project_id=project.id, title=i_title,
                    description=i_desc, priority=TaskPriority(i_priority),
                )
                save_entity("issues", issue.id, issue, project_id=project.id)
                st.success("課題を追加しました")
                st.rerun()

    with tab4:
        st.subheader("リスク管理")
        with st.form("add_risk"):
            r_title = st.text_input("リスク名")
            r_desc = st.text_area("説明 ")
            r_level = st.selectbox("リスクレベル", [r.value for r in RiskLevel])
            r_mitigation = st.text_area("対策")
            if st.form_submit_button("リスク追加"):
                risk = Risk(
                    project_id=project.id, title=r_title,
                    description=r_desc, level=RiskLevel(r_level),
                    mitigation=r_mitigation,
                )
                save_entity("risks", risk.id, risk, project_id=project.id)
                st.success("リスクを追加しました")
                st.rerun()

    with tab5:
        st.subheader("週次レポート生成")
        if st.button("週次レポートを生成"):
            tasks = [PMOTask(**t) for t in list_entities("tasks", project_id=project.id)]
            issues = [Issue(**i) for i in list_entities("issues", project_id=project.id)]
            risks = [Risk(**r) for r in list_entities("risks", project_id=project.id)]
            report = generate_weekly_report(project, tasks, issues, risks)
            save_entity("weekly_reports", report.id, report, project_id=project.id)

            st.markdown("### 日本語")
            st.markdown(report.summary_ja)
            st.markdown("### English")
            st.markdown(report.summary_en)

            if report.delay_risk_factors:
                st.markdown("### 遅延リスク要因")
                for factor in report.delay_risk_factors:
                    st.write(f"- {factor}")


# ---------------------------------------------------------------------------
# Test Case Generation Page
# ---------------------------------------------------------------------------
def render_test_cases() -> None:
    st.title("🧪 テストケース自動生成")

    modules = get_module_summary()
    module_options = {f"{m['id']} - {m['name_ja']}": m['id'] for m in modules}
    selected = st.selectbox("対象モジュール", list(module_options.keys()))
    module_id = module_options[selected] if selected else "SD"

    test_type = st.selectbox("テストタイプ", ["unit", "integration", "uat", "all"])
    requirements = st.text_area("業務要件（オプション）", placeholder="例: 受注から出荷までの標準プロセスのテスト")

    if st.button("テストケースを生成"):
        suite = generate_test_suite(
            project_id="demo-project",
            module_id=module_id,
            requirements=requirements,
            test_type=test_type,
        )

        st.success(f"{len(suite.test_cases)}件のテストケースを生成しました")

        for tc in suite.test_cases:
            with st.expander(f"📝 {tc.scenario_name_ja} ({tc.scenario_name})"):
                st.write(f"**テストタイプ**: {tc.test_type}")
                st.write(f"**優先度**: {tc.priority}")
                st.markdown("| # | アクション | T-code | 入力 | 期待結果 |")
                st.markdown("|---|----------|--------|------|---------|")
                for step in tc.steps:
                    st.markdown(
                        f"| {step.step_number} | {step.action_ja} | "
                        f"`{step.t_code}` | {step.input_data} | {step.expected_result_ja} |"
                    )


# ---------------------------------------------------------------------------
# Training Material Page
# ---------------------------------------------------------------------------
def render_training() -> None:
    st.title("📚 トレーニング資料生成")

    modules = get_module_summary()
    module_options = {f"{m['id']} - {m['name_ja']}": m['id'] for m in modules}
    selected = st.selectbox("対象モジュール ", list(module_options.keys()))
    module_id = module_options[selected] if selected else "SD"

    process_name = st.text_input("プロセス名", placeholder="例: ORDER, PO, POSTING")
    target = st.selectbox("対象者", ["end_user", "key_user", "admin"])
    language = st.selectbox("言語", ["ja", "en"])

    st.markdown("#### 利用可能なテンプレート")
    templates = get_available_templates()
    for t in templates:
        st.write(f"- **{t['id']}**: {t['title_ja']}")

    if st.button("資料を生成"):
        material = generate_training_material(
            project_id="demo-project",
            module_id=module_id,
            process_name=process_name,
            target_audience=target,
            language=Language(language),
        )

        st.success(f"トレーニング資料を生成しました: {material.title_ja}")

        st.markdown(f"### {material.title_ja}")
        st.write(f"**対象**: {material.target_audience}")
        st.write(f"**前提条件**: {material.prerequisites}")

        for step in material.steps:
            st.markdown(f"#### ステップ {step.step_number}: {step.instruction_ja}")
            st.write(f"**T-code**: `{step.t_code}`")
            st.write(f"**画面エリア**: {step.screen_area}")
            if step.field_actions:
                st.write("**操作:**")
                for action in step.field_actions:
                    st.write(f"  - {action}")
            if step.tips:
                st.info(f"💡 {step.tips}")


# ---------------------------------------------------------------------------
# Japanese-English Bridge Page
# ---------------------------------------------------------------------------
def render_bridge() -> None:
    st.title("🌏 日英ブリッジ")

    tab1, tab2, tab3 = st.tabs(["翻訳", "会議議事録", "SAP用語集"])

    with tab1:
        st.subheader("テキスト翻訳")
        direction = st.radio("翻訳方向", ["日本語 → English", "English → 日本語"])
        text = st.text_area("翻訳するテキスト", height=200)
        if st.button("翻訳"):
            if direction == "日本語 → English":
                src, tgt = Language.JA, Language.EN
            else:
                src, tgt = Language.EN, Language.JA

            req = TranslationRequest(
                text=text, source_language=src, target_language=tgt,
            )
            result = translate_text(req)
            st.markdown("### 翻訳結果")
            st.write(result.translated_text)
            if result.glossary_used:
                st.markdown("### 使用した用語集")
                for g in result.glossary_used:
                    st.write(f"- {g['ja']} = {g['en']}")

    with tab2:
        st.subheader("会議議事録の要約・翻訳")
        m_title = st.text_input("会議タイトル", "SAP SD モジュール要件定義会議")
        m_date = st.text_input("日付", "2026-03-24")
        m_attendees = st.text_input("参加者（カンマ区切り）", "田中, 佐藤, Smith")
        m_text = st.text_area("会議メモ", height=300,
                              placeholder="会議の内容をここに入力してください...")
        m_lang = st.radio("原文の言語", ["日本語", "English"], key="meeting_lang")

        if st.button("議事録を生成"):
            lang = Language.JA if m_lang == "日本語" else Language.EN
            minutes = summarize_meeting(
                project_id="demo-project",
                title=m_title, date=m_date,
                attendees=[a.strip() for a in m_attendees.split(",")],
                raw_text=m_text, original_language=lang,
            )
            st.markdown("### 日本語サマリー")
            st.write(minutes.summary_ja)
            st.markdown("### English Summary")
            st.write(minutes.summary_en)
            if minutes.action_items_ja:
                st.markdown("### アクションアイテム")
                for item in minutes.action_items_ja:
                    st.write(f"- {item}")

    with tab3:
        st.subheader("SAP用語集")
        context_filter = st.selectbox(
            "モジュールフィルター",
            ["All"] + ["SD", "MM", "FI", "CO", "PP", "QM", "PM", "HR", "BASIS", "SAP", "Project"],
        )
        ctx = None if context_filter == "All" else context_filter
        glossary = get_glossary(ctx)

        st.markdown("| 日本語 | English | モジュール |")
        st.markdown("|--------|---------|----------|")
        for g in glossary:
            st.markdown(f"| {g['ja']} | {g['en']} | {g['context']} |")


# ---------------------------------------------------------------------------
# Main Router
# ---------------------------------------------------------------------------
if "🏠" in page:
    render_home()
elif "Fit/Gap" in page:
    render_fitgap()
elif "PMO" in page:
    render_pmo_dashboard()
elif "テスト" in page or "Test" in page:
    render_test_cases()
elif "トレーニング" in page or "Training" in page:
    render_training()
elif "ブリッジ" in page or "Bridge" in page:
    render_bridge()

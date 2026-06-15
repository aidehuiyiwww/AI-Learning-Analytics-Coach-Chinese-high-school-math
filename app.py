import os
import time
import threading
from fractions import Fraction
from pathlib import Path

import matplotlib
from matplotlib import font_manager
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import sympy as sp
from dotenv import load_dotenv

from db import init_db, save_attempt, load_attempts_df, load_mastery_df
from llm import diagnose_mistake, has_openai_key, get_openai_model, save_openai_config
from problems import SAMPLE_PROBLEMS, KNOWLEDGE_POINTS
from recommendations import build_dashboard_table, recommend_knowledge_points, generate_practice_problems

load_dotenv()
APP_DIR = Path(__file__).resolve().parent
SHUTDOWN_FLAG = APP_DIR / "shutdown.flag"


def configure_chinese_font():
    """Configure matplotlib so Chinese labels are not rendered as square boxes."""
    preferred_fonts = [
        "Microsoft YaHei", "SimHei", "SimSun", "DengXian",
        "Noto Sans CJK SC", "Source Han Sans SC", "Arial Unicode MS"
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for font in preferred_fonts:
        if font in available:
            matplotlib.rcParams["font.sans-serif"] = [font]
            break
    else:
        # Keep a broad fallback list. Windows normally has Microsoft YaHei.
        matplotlib.rcParams["font.sans-serif"] = preferred_fonts
    matplotlib.rcParams["axes.unicode_minus"] = False


configure_chinese_font()
st.set_page_config(page_title="AI Learning Coach", layout="wide")

st.markdown("""
<style>
    /* V6: make the sidebar wider by default and manually resizable.
       Drag the right edge of the sidebar to adjust its width. */
    [data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 220px !important;
        max-width: 460px !important;
        resize: horizontal;
        overflow: auto;
    }
    [data-testid="stSidebar"] > div:first-child {padding-left: 0.75rem; padding-right: 0.75rem;}
    .block-container {padding-top: 2rem; max-width: 1180px;}
    .problem-card {background: #12324f; padding: 1.1rem; border-radius: 0.6rem; margin: 1rem 0; color: #4bb1ff;}
    .solution-card {background: #20331f; padding: 1rem; border-radius: 0.6rem; border: 1px solid #4d7c4a;}
    .small-muted {color: #999; font-size: 0.9rem;}
    .mode-card {background: #1b3149; border-radius: 0.6rem; padding: 0.85rem; margin: 0.5rem 0;}
    .metric-card {border: 1px solid rgba(150,150,150,.25); border-radius: 0.7rem; padding: 1rem;}
</style>
""", unsafe_allow_html=True)

init_db()


def normalize_answer(ans: str) -> str:
    return (ans or "").strip().replace(" ", "").replace("，", ",").replace("≤", "<=").replace("≥", ">=").replace("∞", "oo").replace("π", "pi").replace("∪", "U")


def is_answer_correct(student_answer: str, correct_answer: str) -> bool:
    s = normalize_answer(student_answer)
    c = normalize_answer(correct_answer)
    if not s:
        return False
    if s.lower() == c.lower():
        return True
    try:
        return Fraction(s) == Fraction(c)
    except Exception:
        pass
    try:
        x, y, a, m, n = sp.symbols("x y a m n")
        return sp.simplify(sp.sympify(s) - sp.sympify(c)) == 0
    except Exception:
        pass
    aliases = {
        "(-oo,2)u(3,oo)": ["x<2orx>3", "(-∞,2)∪(3,∞)", "(-oo,2)U(3,oo)"],
        "a<=1": ["a≤1", "(-oo,1]"],
        "2i": ["0+2i", "2*i", "2I"],
        "10%": ["0.1", "百分之十", "0.10"],
        "{1,2}": ["{2,1}", "1,2"],
    }
    return s.lower() in [v.lower() for v in aliases.get(c.lower(), [])]


def select_problem(kp=None):
    pool = [p for p in SAMPLE_PROBLEMS if (kp in [None, "all"] or p["knowledge_point"] == kp)]
    return __import__("random").choice(pool or SAMPLE_PROBLEMS)


def reset_problem(kp="all"):
    st.session_state.problem = select_problem(kp)
    st.session_state.start_time = time.time()
    st.session_state.last_diagnosis = None
    st.session_state.wrong_count = 0


def shutdown_after_delay(seconds=1.2):
    """Stop the Streamlit server itself. Works whether launched by bat or streamlit run."""
    time.sleep(seconds)
    try:
        SHUTDOWN_FLAG.write_text("shutdown", encoding="utf-8")
    except Exception:
        pass
    os._exit(0)


if "problem" not in st.session_state:
    reset_problem("all")

with st.sidebar:
    st.title("Navigation")
    page = st.radio("", ["Student Practice", "Dashboard", "Recommendations", "About"], label_visibility="collapsed")
    st.divider()

    st.caption("AI Mode")
    if has_openai_key():
        st.success(f"GPT Enhanced\n\nModel: {get_openai_model()}")
    else:
        st.warning("Demo Mode\n\nNo API key required. Mock diagnosis is active.")

    with st.expander("How to enable OpenAI", expanded=False):
        st.markdown(
            """
**OpenAI is optional.** The app works without it, but GPT mode enables stronger mistake diagnosis and AI-generated practice problems.

**Method 1: configure inside this app**

1. Paste your OpenAI API key below.
2. Keep the model as `gpt-4o-mini`, or change it if needed.
3. Click **Save API settings**.
4. Restart the app.

**Method 2: configure manually**

1. Copy `.env.example` and rename the copy to `.env`.
2. Open `.env` and fill in:
            """
        )
        st.code("OPENAI_API_KEY=sk-your-key-here\nOPENAI_MODEL=gpt-4o-mini", language="text")
        st.caption("Do not upload your real .env file to GitHub.")
        api_key_input = st.text_input("OpenAI API key", type="password", placeholder="sk-...")
        model_input = st.text_input("Model", value="gpt-4o-mini")
        if st.button("Save API settings", use_container_width=True):
            try:
                save_openai_config(api_key_input, model_input)
                st.success("Saved. GPT mode will be used from the next diagnosis request. If the status does not update, refresh the page.")
            except Exception as e:
                st.error(f"Could not save settings: {e}")

    st.divider()
    if st.button("关闭程序", use_container_width=True):
        try:
            SHUTDOWN_FLAG.write_text("shutdown", encoding="utf-8")
        except Exception:
            pass
        st.success("正在关闭程序。浏览器标签页可手动关闭。")
        threading.Thread(target=shutdown_after_delay, daemon=True).start()
        st.stop()

st.title("AI Learning Coach")
st.caption("Chinese High School Math · LLM Feedback · Mastery Tracking · Learning Analytics")

if page == "Student Practice":
    st.header("Student Practice")
    selected_kp = st.selectbox(
        "选择练习知识点",
        options=["all"] + list(KNOWLEDGE_POINTS.keys()),
        format_func=lambda k: "全部知识点" if k == "all" else KNOWLEDGE_POINTS[k],
    )
    if st.button("按所选知识点出题"):
        reset_problem(selected_kp)
        st.rerun()

    p = st.session_state.problem
    c1, c2, c3 = st.columns(3)
    c1.metric("Knowledge Point", KNOWLEDGE_POINTS[p["knowledge_point"]])
    c2.metric("Difficulty", p["difficulty"])
    c3.metric("Problem ID", p["problem_id"])

    st.subheader("Question")
    st.markdown(f'<div class="problem-card">{p["question"]}</div>', unsafe_allow_html=True)

    with st.form("answer_form"):
        student_answer = st.text_input("Your answer")
        submitted = st.form_submit_button("Submit Answer")

    if submitted:
        elapsed = round(time.time() - st.session_state.start_time, 2)
        correct = is_answer_correct(student_answer, p["correct_answer"])
        if correct:
            st.success("Correct!")
            st.session_state.wrong_count = 0
            error_type = None
            st.session_state.last_diagnosis = None
        else:
            st.session_state.wrong_count = st.session_state.get("wrong_count", 0) + 1
            st.error("Not correct yet.")
            with st.spinner("AI 正在分析你的解题过程并生成个性化反馈，请稍候（通常 2–10 秒）..."):
                diagnosis = diagnose_mistake(p, student_answer)
            error_type = diagnosis.get("error_type", "unknown")
            st.session_state.last_diagnosis = diagnosis
        save_attempt(p, student_answer, correct, elapsed, error_type)

    if st.session_state.last_diagnosis:
        d = st.session_state.last_diagnosis
        st.subheader("AI Mistake Diagnosis")
        st.write(f"**Error type:** `{d.get('error_type', 'unknown')}`")
        st.write(f"**Explanation:** {d.get('explanation', '')}")
        st.write(f"**Hint:** {d.get('hint', '')}")
        st.write(f"**Recommended next step:** {d.get('recommended_next_step', '')}")

    wrong_count = st.session_state.get("wrong_count", 0)
    if wrong_count == 1:
        st.info("你已经答错 1 次。再答错 1 次后，系统会显示参考答案和完整解题思路。")
    if wrong_count >= 2:
        st.subheader("Correct solution")
        solution = p.get("solution", f"参考答案：{p['correct_answer']}")
        st.markdown(f'<div class="solution-card"><b>Answer:</b> {p["correct_answer"]}<br><br>{solution}</div>', unsafe_allow_html=True)

    if st.button("Next Problem"):
        reset_problem(selected_kp)
        st.rerun()

elif page == "Dashboard":
    st.header("Dashboard")
    attempts = load_attempts_df()
    mastery = load_mastery_df()
    dashboard = build_dashboard_table(mastery, attempts)

    total_attempts = len(attempts) if attempts is not None else 0
    overall_accuracy = float(attempts["is_correct"].mean()) if total_attempts and "is_correct" in attempts.columns else 0.0
    weakest = dashboard.sort_values("adjusted_mastery").iloc[0]["知识点"] if not dashboard.empty else "N/A"
    strongest = dashboard.sort_values("adjusted_mastery", ascending=False).iloc[0]["知识点"] if not dashboard.empty else "N/A"
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Attempts", total_attempts)
    m2.metric("Overall Accuracy", f"{overall_accuracy:.0%}")
    m3.metric("Weakest Topic", weakest)
    m4.metric("Strongest Topic", strongest)

    display_cols = ["知识点", "raw_mastery", "adjusted_mastery", "attempts", "accuracy", "most_common_error_type", "last_practiced"]
    st.dataframe(dashboard[display_cols], use_container_width=True)

    st.subheader("Adjusted Mastery by Knowledge Point")
    if dashboard.empty:
        st.info("No mastery data yet.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        plot_df = dashboard.sort_values("adjusted_mastery")
        ax.barh(plot_df["知识点"], plot_df["adjusted_mastery"])
        ax.set_xlim(0, 1)
        ax.set_xlabel("调整后掌握度")
        ax.set_ylabel("知识点")
        ax.set_title("各知识点调整后掌握度")
        fig.tight_layout()
        st.pyplot(fig)

    st.subheader("Accuracy Over Time")
    if attempts.empty:
        st.info("No attempts yet.")
    else:
        attempts = attempts.copy()
        attempts["timestamp"] = pd.to_datetime(attempts["timestamp"], errors="coerce")
        attempts = attempts.dropna(subset=["timestamp"])
        attempts["date"] = attempts["timestamp"].dt.date
        daily = attempts.groupby("date")["is_correct"].mean().reset_index()
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.plot(daily["date"], daily["is_correct"], marker="o")
        ax2.set_ylim(0, 1)
        ax2.set_ylabel("正确率")
        ax2.set_xlabel("日期")
        ax2.set_title("每日正确率趋势")
        ax2.tick_params(axis="x", rotation=45)
        fig2.tight_layout()
        st.pyplot(fig2)

elif page == "Recommendations":
    st.header("Recommendations")
    attempts = load_attempts_df()
    mastery = load_mastery_df()
    dashboard = build_dashboard_table(mastery, attempts)
    recs = recommend_knowledge_points(dashboard, 3)
    st.subheader("Next 3 knowledge points to practice")
    if recs.empty:
        st.info("No recommendation data yet.")
    else:
        cols = ["知识点", "adjusted_mastery", "attempts", "accuracy", "most_common_error_type", "last_practiced", "priority_score"]
        st.dataframe(recs[cols], use_container_width=True)
        st.markdown("### Why these topics?")
        for _, row in recs.iterrows():
            st.markdown(
                f"- **{row['知识点']}**: adjusted mastery `{row['adjusted_mastery']}`, "
                f"attempts `{row['attempts']}`, common error `{row['most_common_error_type']}`, "
                f"days since practice `{row.get('days_since', 'N/A')}`."
            )
        weakest = recs.iloc[0]["knowledge_point"]
        st.subheader(f"Generated practice problems: {KNOWLEDGE_POINTS.get(weakest, weakest)}")
        for i, item in enumerate(generate_practice_problems(weakest), 1):
            st.markdown(f"**Problem {i}.** {item.get('question')}")
            st.caption(f"Difficulty: {item.get('difficulty')} | Reference answer: {item.get('correct_answer')}")

else:
    st.header("About")
    st.write("This portfolio prototype demonstrates educational technology, learning analytics, a forgetting-curve-inspired mastery model, and AI-assisted personalized feedback.")
    st.write("If OpenAI API key is unavailable, the app automatically falls back to mock diagnosis and template-based recommendation problems.")

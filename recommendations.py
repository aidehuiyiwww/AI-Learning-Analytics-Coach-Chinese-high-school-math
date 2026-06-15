import pandas as pd
from mastery import adjusted_mastery, days_since_practice
from problems import KNOWLEDGE_POINTS, get_problems_by_kp
from llm import generate_problems_with_llm


def build_dashboard_table(mastery_df, attempts_df):
    rows = []
    if mastery_df is None or mastery_df.empty:
        mastery_df = pd.DataFrame(
            [{"knowledge_point": kp, "mastery": 0.5, "last_practiced": None} for kp in KNOWLEDGE_POINTS]
        )
    if attempts_df is None or attempts_df.empty:
        attempts_df = pd.DataFrame(columns=["knowledge_point", "is_correct", "error_type", "timestamp"])

    for _, m in mastery_df.iterrows():
        kp = m.get("knowledge_point")
        if "knowledge_point" in attempts_df.columns:
            kp_attempts = attempts_df[attempts_df["knowledge_point"] == kp].copy()
        else:
            kp_attempts = pd.DataFrame()

        n_attempts = len(kp_attempts)
        accuracy = None
        if n_attempts and "is_correct" in kp_attempts.columns:
            accuracy = float(pd.to_numeric(kp_attempts["is_correct"], errors="coerce").fillna(0).mean())

        common_error = "none"
        if n_attempts and "error_type" in kp_attempts.columns:
            wrong = kp_attempts[pd.to_numeric(kp_attempts.get("is_correct", 0), errors="coerce").fillna(0) == 0]
            if not wrong.empty:
                mode = wrong["error_type"].fillna("unknown").replace("", "unknown").mode()
                common_error = mode.iloc[0] if not mode.empty else "unknown"

        last_practiced = m.get("last_practiced")
        raw = float(m.get("mastery", 0.5) if m.get("mastery", 0.5) is not None else 0.5)
        rows.append({
            "knowledge_point": kp,
            "知识点": KNOWLEDGE_POINTS.get(kp, kp),
            "raw_mastery": round(raw, 3),
            "adjusted_mastery": round(adjusted_mastery(raw, last_practiced), 3),
            "attempts": int(n_attempts),
            "accuracy": round(accuracy, 3) if accuracy is not None else None,
            "most_common_error_type": common_error,
            "last_practiced": last_practiced if last_practiced not in [None, ""] else "never",
        })
    return pd.DataFrame(rows)


def recommend_knowledge_points(dashboard_df, top_n=3):
    df = dashboard_df.copy()
    if df.empty:
        return df
    df["days_since"] = df["last_practiced"].apply(days_since_practice)
    df["error_penalty"] = df["most_common_error_type"].apply(lambda x: 0 if x in ["none", None, ""] else 0.15)
    df["accuracy_penalty"] = (1 - df["accuracy"].fillna(0.5).astype(float)) * 0.25
    df["priority_score"] = (
        (1 - df["adjusted_mastery"].astype(float))
        + df["error_penalty"]
        + df["accuracy_penalty"]
        + df["days_since"].clip(0, 30) / 100
    )
    return df.sort_values("priority_score", ascending=False).head(top_n)


def generate_practice_problems(kp):
    label = KNOWLEDGE_POINTS.get(kp, kp)
    llm_items = generate_problems_with_llm(label)
    if llm_items:
        return llm_items[:3]
    base = get_problems_by_kp(kp)
    if base:
        return [{"question": p["question"], "correct_answer": p["correct_answer"], "difficulty": p["difficulty"]} for p in base[:3]]
    return [
        {"question": f"请完成一道关于{label}的基础概念辨析题。", "correct_answer": "略", "difficulty": 2},
        {"question": f"请完成一道关于{label}的计算题。", "correct_answer": "略", "difficulty": 3},
        {"question": f"请完成一道关于{label}的综合应用题。", "correct_answer": "略", "difficulty": 4},
    ]

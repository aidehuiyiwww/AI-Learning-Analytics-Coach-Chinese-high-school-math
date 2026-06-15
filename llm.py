import json
import os
from pathlib import Path
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
ENV_PATH = APP_DIR / ".env"

VALID_ERROR_TYPES = ["conceptual_error", "calculation_error", "careless_error", "misunderstanding_question", "unknown"]


def refresh_env():
    """Reload local .env so users can enable OpenAI without editing code."""
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    load_dotenv(override=False)


def get_openai_key():
    refresh_env()
    return os.getenv("OPENAI_API_KEY", "").strip()


def get_openai_model():
    refresh_env()
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def has_openai_key():
    return bool(get_openai_key())


def save_openai_config(api_key: str, model: str = "gpt-4o-mini"):
    """Save API settings into .env for local demo use. .env is ignored by Git."""
    api_key = (api_key or "").strip()
    model = (model or "gpt-4o-mini").strip()
    if not api_key:
        raise ValueError("API key cannot be empty.")
    ENV_PATH.write_text(f"OPENAI_API_KEY={api_key}\nOPENAI_MODEL={model}\n", encoding="utf-8")
    refresh_env()


def mock_diagnosis(problem, student_answer):
    """Rule-based diagnosis used as a safe fallback.

    The app should always show a useful explanation even if the OpenAI API
    is missing, temporarily unavailable, or returns malformed JSON.
    """
    answer = str(student_answer or "").strip()
    correct = str(problem.get("correct_answer", "")).strip()
    kp = str(problem.get("knowledge_point", ""))
    if not answer:
        return {
            "error_type": "misunderstanding_question",
            "explanation": "你还没有输入答案。建议先写出题目已知条件，再确定要求的目标量。",
            "hint": "先把题目中的关键词圈出来，例如函数区间、参数范围、向量方向、概率事件等。",
            "recommended_next_step": "先完成一道同知识点的基础题，重点训练审题和条件提取。",
        }
    return {
        "error_type": "unknown",
        "explanation": f"你的答案“{answer}”暂时不能判定为正确。请对照题目条件检查概念选择、公式代入和计算化简过程。",
        "hint": "不要直接改最终答案，先从第一步推导开始检查：条件是否用全、公式是否选对、符号方向是否正确。",
        "recommended_next_step": f"继续练习“{kp}”相关题目，并把错误步骤记录下来。参考答案会在连续两次答错后显示。",
    }


def normalize_diagnosis(data, problem, student_answer):
    """Ensure diagnosis always contains the required JSON fields."""
    fallback = mock_diagnosis(problem, student_answer)
    if not isinstance(data, dict):
        return fallback
    result = {**fallback, **{k: v for k, v in data.items() if v not in [None, ""]}}
    if result.get("error_type") not in VALID_ERROR_TYPES:
        result["error_type"] = "unknown"
    for key in ["explanation", "hint", "recommended_next_step"]:
        if not str(result.get(key, "")).strip():
            result[key] = fallback[key]
    return result


def diagnose_mistake(problem, student_answer):
    api_key = get_openai_key()
    if not api_key:
        return mock_diagnosis(problem, student_answer)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = get_openai_model()
        prompt = f"""
You are an AI math learning coach for Chinese high school students.
Return ONLY valid JSON with these keys:
error_type: one of {VALID_ERROR_TYPES}
explanation: short student-friendly Chinese explanation
hint: a guiding hint without directly giving the answer
recommended_next_step: what the student should practice next

Problem: {problem['question']}
Correct answer: {problem['correct_answer']}
Student answer: {student_answer}
Knowledge point: {problem['knowledge_point']}
Difficulty: {problem['difficulty']}
"""
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content or "{}")
        return normalize_diagnosis(data, problem, student_answer)
    except Exception as e:
        data = mock_diagnosis(problem, student_answer)
        data["error_type"] = data.get("error_type", "unknown")
        data["explanation"] = (
            "GPT 调用没有成功完成，因此系统已自动切换为本地诊断，"
            f"但本次错因提示和两次答错后的正确答案仍会正常显示。错误信息：{str(e)[:120]}"
        )
        return normalize_diagnosis(data, problem, student_answer)


def generate_problems_with_llm(knowledge_point_label):
    api_key = get_openai_key()
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = get_openai_model()
        prompt = f"""
Generate 3 Chinese high-school Gaokao-style math practice problems for: {knowledge_point_label}.
Return ONLY valid JSON object with key "problems".
Each problem has: question, correct_answer, difficulty from 1 to 5.
Avoid primary-school or junior-middle-school style questions.
"""
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role":"user", "content": prompt}],
            temperature=0.4,
            response_format={"type":"json_object"},
        )
        obj = json.loads(resp.choices[0].message.content)
        if isinstance(obj, dict):
            return obj.get("problems") or obj.get("items")
        return obj
    except Exception:
        return None

import sqlite3
from datetime import datetime
from pathlib import Path
from problems import KNOWLEDGE_POINTS
from mastery import update_mastery_score

DB_PATH = Path(__file__).with_name("learning_coach.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            problem_id TEXT NOT NULL,
            student_answer TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            knowledge_point TEXT NOT NULL,
            difficulty INTEGER NOT NULL,
            response_time_seconds REAL NOT NULL,
            error_type TEXT
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS mastery (
            knowledge_point TEXT PRIMARY KEY,
            mastery REAL NOT NULL,
            last_practiced TEXT
        )''')
        for kp in KNOWLEDGE_POINTS:
            conn.execute("INSERT OR IGNORE INTO mastery VALUES (?, ?, ?)", (kp, 0.5, None))


def save_attempt(problem, student_answer, is_correct, response_time_seconds, error_type=None):
    now = datetime.now().isoformat(timespec="seconds")
    with get_conn() as conn:
        conn.execute('''INSERT INTO attempts(timestamp, problem_id, student_answer, correct_answer, is_correct,
            knowledge_point, difficulty, response_time_seconds, error_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (now, problem["problem_id"], student_answer, problem["correct_answer"], int(is_correct),
             problem["knowledge_point"], problem["difficulty"], response_time_seconds, error_type))
        row = conn.execute("SELECT mastery FROM mastery WHERE knowledge_point=?", (problem["knowledge_point"],)).fetchone()
        old = row[0] if row else 0.5
        new = update_mastery_score(old, problem["difficulty"], is_correct)
        conn.execute("INSERT OR REPLACE INTO mastery VALUES (?, ?, ?)", (problem["knowledge_point"], new, now))

def load_attempts_df():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM attempts ORDER BY timestamp", conn)

def load_mastery_df():
    import pandas as pd
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM mastery", conn)

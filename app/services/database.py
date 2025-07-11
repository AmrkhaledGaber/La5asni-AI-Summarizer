import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("la5asni_history.db")

# ✅ Create table if it doesn't exist
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                summary TEXT,
                key_points TEXT,
                training_modules TEXT,
                num_pages INTEGER,
                useful_text_ratio REAL,
                num_key_points INTEGER,
                estimated_minutes TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

# ✅ Save a new analysis result
def save_analysis(filename, summary, key_points, training_modules,
                  num_pages, useful_text_ratio, num_key_points, estimated_minutes):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO analyses (
                filename, summary, key_points, training_modules,
                num_pages, useful_text_ratio, num_key_points, estimated_minutes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename,
            summary,
            "\n".join(key_points),
            "\n".join(training_modules),
            num_pages,
            useful_text_ratio,
            num_key_points,
            ",".join(map(str, estimated_minutes)),
            datetime.now().isoformat()
        ))
        conn.commit()

# ✅ Get all past analyses
def get_all_analyses():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT id, filename, created_at FROM analyses ORDER BY created_at DESC
        """)
        return cursor.fetchall()

# ✅ Get full details for a specific analysis
def get_analysis_by_id(analysis_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT * FROM analyses WHERE id = ?
        """, (analysis_id,))
        return cursor.fetchone()
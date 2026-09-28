import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "omni_sessions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            meta TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT,
            model TEXT,
            tokens_in INTEGER,
            tokens_out INTEGER,
            cost_usd REAL,
            saved_usd REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

class SessionManager:
    """Gerenciador local e persistente de sessões e DRE de economia de tokens."""

    @classmethod
    def list_sessions(cls) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, created_at FROM sessions ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "title": r[1], "created_at": r[2]} for r in rows]

    @classmethod
    def create_session(cls, session_id: str, title: str = "Nova Análise") -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO sessions (id, title, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)", (session_id, title))
        conn.commit()
        conn.close()
        return {"id": session_id, "title": title}

    @classmethod
    def add_message(cls, session_id: str, role: str, content: str, meta: Optional[Dict] = None):
        cls.create_session(session_id)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        meta_json = json.dumps(meta) if meta else None
        cursor.execute("INSERT INTO messages (session_id, role, content, meta) VALUES (?, ?, ?, ?)", (session_id, role, content, meta_json))
        cursor.execute("UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_messages(cls, session_id: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT role, content, meta, created_at FROM messages WHERE session_id = ? ORDER BY id ASC", (session_id,))
        rows = cursor.fetchall()
        conn.close()
        result = []
        for r in rows:
            meta_dict = json.loads(r[2]) if r[2] else None
            result.append({"role": r[0], "content": r[1], "meta": meta_dict, "created_at": r[3]})
        return result

    @classmethod
    def record_savings(cls, provider: str, model: str, tokens_in: int, tokens_out: int, actual_cost: float):
        """Calcula a economia comparando com o GPT-4o ($2.50 in / $10.00 out por 1M)."""
        benchmark_cost = (tokens_in * 2.50 + tokens_out * 10.00) / 1_000_000
        saved = max(0.0, benchmark_cost - actual_cost)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO token_telemetry (provider, model, tokens_in, tokens_out, cost_usd, saved_usd)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (provider, model, tokens_in, tokens_out, actual_cost, saved))
        conn.commit()
        conn.close()

    @classmethod
    def get_savings_summary(cls) -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*),
                COALESCE(SUM(tokens_in), 0),
                COALESCE(SUM(tokens_out), 0),
                COALESCE(SUM(cost_usd), 0.0),
                COALESCE(SUM(saved_usd), 0.0)
            FROM token_telemetry
        """)
        row = cursor.fetchone()
        conn.close()

        req_count, total_in, total_out, cost_usd, saved_usd = row
        return {
            "total_requests": req_count,
            "total_tokens": total_in + total_out,
            "total_cost_usd": round(cost_usd, 4),
            "total_saved_usd": round(saved_usd, 4),
            "total_saved_brl": round(saved_usd * 5.60, 2), # Câmbio estimado R$ 5,60
            "benchmark_model": "OpenAI GPT-4o ($2.50 / $10.00 per 1M)"
        }

init_db()

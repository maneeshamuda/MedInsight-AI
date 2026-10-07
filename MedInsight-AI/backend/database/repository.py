"""Optional persistence (off by default: STORE_RESULTS=false). Source files are never stored."""
import json
import uuid

from backend.database.database import connect


def save(result: dict) -> str:
    aid = uuid.uuid4().hex
    with connect() as c:
        c.execute("INSERT INTO analyses (id, result_json) VALUES (?, ?)", (aid, json.dumps(result, ensure_ascii=False)))
    return aid


def get(aid: str) -> dict | None:
    with connect() as c:
        row = c.execute("SELECT result_json FROM analyses WHERE id = ?", (aid,)).fetchone()
    return json.loads(row[0]) if row else None


def delete(aid: str) -> bool:
    with connect() as c:
        return c.execute("DELETE FROM analyses WHERE id = ?", (aid,)).rowcount > 0

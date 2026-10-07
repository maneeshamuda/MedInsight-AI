SCHEMA = """CREATE TABLE IF NOT EXISTS analyses (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  result_json TEXT NOT NULL
)"""

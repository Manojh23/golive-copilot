"""Small, persistent local review workspace. All source snapshots are immutable."""
import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.now(timezone.utc).isoformat()

@contextmanager
def db():
    path = Path(os.getenv('GOLIVE_DB', str(ROOT / 'data/runtime/workspace.sqlite3')))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sources(
          id TEXT PRIMARY KEY, title TEXT NOT NULL, filename TEXT NOT NULL,
          kind TEXT NOT NULL, origin TEXT NOT NULL, url TEXT, license TEXT,
          sha256 TEXT NOT NULL, created_at TEXT NOT NULL, pages INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS chunks(
          id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id),
          locator TEXT NOT NULL, content TEXT NOT NULL);
        CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(chunk_id UNINDEXED, content, tokenize='porter unicode61');
        CREATE TABLE IF NOT EXISTS impacts(id TEXT PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL,
          text TEXT NOT NULL, origin TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,
          action TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL);
        ''')

def get_setting(key, default=None):
    with db() as c:
        r = c.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
    return json.loads(r['value']) if r else default

def set_setting(key, value):
    with db() as c:
        c.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', (key, json.dumps(value)))

def audit(action, detail):
    with db() as c:
        c.execute('INSERT INTO audit(action,detail,created_at) VALUES (?,?,?)', (action, json.dumps(detail), now()))

def list_sources():
    with db() as c:
        return [dict(r) for r in c.execute('SELECT s.*,count(ch.id) chunk_count FROM sources s LEFT JOIN chunks ch ON ch.source_id=s.id GROUP BY s.id ORDER BY created_at')]

def get_chunks(source_id=None):
    with db() as c:
        rows = c.execute('SELECT ch.*,s.title,s.origin,s.url,s.kind FROM chunks ch JOIN sources s ON s.id=ch.source_id'+(' WHERE source_id=?' if source_id else '')+' ORDER BY ch.id', (source_id,) if source_id else ()).fetchall()
        return [dict(r) for r in rows]

def get_impacts():
    with db() as c:
        return [json.loads(r['body']) for r in c.execute('SELECT body FROM impacts ORDER BY id')]

def save_impacts(items):
    with db() as c:
        c.execute('DELETE FROM impacts')
        c.executemany('INSERT INTO impacts VALUES (?,?)', [(x['id'], json.dumps(x)) for x in items])

def fingerprint():
    payload = {'project':get_setting('project'), 'sources':[(s['id'],s['sha256']) for s in list_sources()]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()

def stale_assessment(reason):
    a = get_setting('assessment')
    if a:
        a['stale'] = True
        a['stale_reason'] = reason
        set_setting('assessment', a)
    audit('inputs_changed', {'reason':reason})

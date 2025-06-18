import os
import sqlite3

_conn = None


def get_db_path():
    """Return path to SQLite DB from env or default."""
    return os.environ.get('DB_PATH', 'inventory.db')


def init_db(db_path: str | None = None):
    """Initialize connection and ensure tables exist."""
    global _conn
    if db_path is None:
        db_path = get_db_path()
    _conn = sqlite3.connect(db_path, check_same_thread=False)
    _conn.row_factory = sqlite3.Row
    cursor = _conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
    )
    _conn.commit()
    return _conn


def get_connection():
    """Return initialized connection, creating one if needed."""
    global _conn
    if _conn is None:
        init_db()
    return _conn


# CRUD helpers

def list_items():
    conn = get_connection()
    cur = conn.execute("SELECT id, name FROM items ORDER BY id")
    rows = cur.fetchall()
    return [{"id": row["id"], "name": row["name"]} for row in rows]


def create_item(name: str):
    conn = get_connection()
    cur = conn.execute("INSERT INTO items (name) VALUES (?)", (name,))
    conn.commit()
    item_id = cur.lastrowid
    return {"id": item_id, "name": name}


def get_item(item_id: int):
    conn = get_connection()
    cur = conn.execute("SELECT id, name FROM items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    if row is None:
        return None
    return {"id": row["id"], "name": row["name"]}


def update_item(item_id: int, name: str):
    conn = get_connection()
    cur = conn.execute("UPDATE items SET name = ? WHERE id = ?", (name, item_id))
    if cur.rowcount == 0:
        return None
    conn.commit()
    return {"id": item_id, "name": name}


def delete_item(item_id: int):
    conn = get_connection()
    cur = conn.execute("SELECT id, name FROM items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    if row is None:
        return None
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    return {"id": row["id"], "name": row["name"]}

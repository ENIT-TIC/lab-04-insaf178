import os
import sqlite3
from fastapi import FastAPI, HTTPException

DB_PATH = os.getenv("DB_PATH", "/data/app.db")

app = FastAPI()

def get_conn():
    # check_same_thread=False si tu as plusieurs threads (uvicorn)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@app.on_event("startup")
def startup():
    # Assure que la table existe même si init.sql n’a pas tourné
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
      );
    """)
    conn.commit()
    conn.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/db")
def health_db():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        conn.close()
        return {"db": "ok", "path": DB_PATH}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/items")
def create_item(payload: dict):
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO items(name) VALUES(?);", (name,))
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return {"id": item_id, "name": name}

@app.get("/items")
def list_items():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items ORDER BY id;")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]

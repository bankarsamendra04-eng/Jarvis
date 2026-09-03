import csv
import sqlite3
import os

DB_PATH = "jarvis.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("CREATE TABLE IF NOT EXISTS sys_command(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(100), path VARCHAR(1000))")
    cursor.execute("CREATE TABLE IF NOT EXISTS web_command(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(100), url VARCHAR(1000))")
    cursor.execute("CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(200), Phone VARCHAR(255), email VARCHAR(255) NULL)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sender VARCHAR(50) NOT NULL,
            transcription TEXT NOT NULL,
            is_priority_memory BOOLEAN DEFAULT 0
        )
    """)

    # Seed default web commands if empty
    cursor.execute("SELECT COUNT(*) FROM web_command")
    if cursor.fetchone()[0] == 0:
        default_websites = [
            ('google', 'https://www.google.com'),
            ('youtube', 'https://www.youtube.com'),
            ('github', 'https://www.github.com'),
            ('gmail', 'https://mail.google.com'),
            ('whatsapp', 'https://web.whatsapp.com'),
            ('chatgpt', 'https://chat.openai.com'),
            ('linkedin', 'https://www.linkedin.com'),
            ('instagram', 'https://www.instagram.com'),
            ('facebook', 'https://www.facebook.com'),
            ('twitter', 'https://www.twitter.com'),
            ('spotify', 'https://open.spotify.com'),
            ('netflix', 'https://www.netflix.com'),
            ('reddit', 'https://www.reddit.com'),
            ('amazon', 'https://www.amazon.com'),
            ('wikipedia', 'https://www.wikipedia.org')
        ]
        cursor.executemany("INSERT INTO web_command (name, url) VALUES (?, ?)", default_websites)

    # Seed default system commands if empty
    cursor.execute("SELECT COUNT(*) FROM sys_command")
    if cursor.fetchone()[0] == 0:
        default_sys_apps = [
            ('notepad', 'notepad.exe'),
            ('calculator', 'calc.exe'),
            ('cmd', 'cmd.exe'),
            ('explorer', 'explorer.exe'),
            ('paint', 'mspaint.exe'),
            ('task manager', 'taskmgr.exe')
        ]
        cursor.executemany("INSERT INTO sys_command (name, path) VALUES (?, ?)", default_sys_apps)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def store_message_log(sender, transcription, is_priority_memory=False):
    """
    Stores a message log in the database with timestamp, sender, transcription, and priority flag.
    Returns a dict with operation status and log details.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO message_logs (sender, transcription, is_priority_memory)
            VALUES (?, ?, ?)
        """, (sender, str(transcription), 1 if is_priority_memory else 0))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        
        priority_label = " [High-Priority Memory]" if is_priority_memory else ""
        print(f"[Memory Log #{inserted_id}]{priority_label} {sender}: {transcription}")
        return {
            "status": "success",
            "id": inserted_id,
            "sender": sender,
            "transcription": transcription,
            "is_priority_memory": bool(is_priority_memory)
        }
    except Exception as e:
        print(f"Error storing message log: {e}")
        return {"status": "error", "message": str(e)}

def get_recent_messages(limit=10):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, sender, transcription, is_priority_memory
            FROM message_logs
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{
            "id": r[0],
            "timestamp": r[1],
            "sender": r[2],
            "transcription": r[3],
            "is_priority_memory": bool(r[4])
        } for r in rows][::-1]
    except Exception as e:
        print(f"Error fetching message logs: {e}")
        return []

def get_priority_memories():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, sender, transcription
            FROM message_logs
            WHERE is_priority_memory = 1
            ORDER BY id ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [{
            "id": r[0],
            "timestamp": r[1],
            "sender": r[2],
            "transcription": r[3]
        } for r in rows]
    except Exception as e:
        print(f"Error fetching priority memories: {e}")
        return []

# Run initialization on import
init_db()

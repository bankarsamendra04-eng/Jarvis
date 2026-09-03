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

# Run initialization on import
init_db()

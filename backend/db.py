import csv
import sqlite3
import os
import uuid
import datetime
import eel

DB_PATH = "jarvis.db"
CURRENT_ACTIVE_CONV_ID = None

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create system and web command tables
    cursor.execute("CREATE TABLE IF NOT EXISTS sys_command(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(100), path VARCHAR(1000))")
    cursor.execute("CREATE TABLE IF NOT EXISTS web_command(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(100), url VARCHAR(1000))")
    cursor.execute("CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(200), Phone VARCHAR(255), email VARCHAR(255) NULL)")
    
    # Message logs table for long-term memory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sender VARCHAR(50) NOT NULL,
            transcription TEXT NOT NULL,
            is_priority_memory BOOLEAN DEFAULT 0
        )
    """)

    # Conversations table for multi-chat history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_pinned INTEGER DEFAULT 0
        )
    """)

    # Conversation messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            transcription TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_priority_memory BOOLEAN DEFAULT 0,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
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

# Run initialization
init_db()


# -------------------------------------------------------------
# Conversation Management & CRUD APIs
# -------------------------------------------------------------

def init_session_new_conversation():
    """
    Always initializes a clean, fresh conversation for a newly started session.
    Reuses an empty 'New Conversation' (0 messages) if present, or creates a fresh one.
    """
    global CURRENT_ACTIVE_CONV_ID
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT c.id FROM conversations c
            WHERE (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) = 0
            ORDER BY c.created_at DESC LIMIT 1
        """)
        row = c.fetchone()
        conn.close()
        if row:
            CURRENT_ACTIVE_CONV_ID = row[0]
            try:
                from backend.context_manager import get_context_manager
                get_context_manager().set_active_conversation(CURRENT_ACTIVE_CONV_ID)
                get_context_manager().reset_context()
            except Exception:
                pass
            return {
                "status": "success",
                "id": CURRENT_ACTIVE_CONV_ID,
                "title": "New Conversation",
                "is_new": True
            }
    except Exception as e:
        print(f"Error checking existing empty conversation: {e}")

    new_conv = create_conversation("New Conversation")
    CURRENT_ACTIVE_CONV_ID = new_conv["id"]
    try:
        from backend.context_manager import get_context_manager
        get_context_manager().set_active_conversation(CURRENT_ACTIVE_CONV_ID)
        get_context_manager().reset_context()
    except Exception:
        pass
    new_conv["is_new"] = True
    return new_conv


@eel.expose
def startNewSessionConversation():
    """Exposed endpoint to ensure the frontend always boots into a brand-new conversation."""
    return init_session_new_conversation()


def get_or_create_active_conversation():
    """
    Returns the currently active conversation ID. If none is set,
    initiates a fresh session conversation.
    """
    global CURRENT_ACTIVE_CONV_ID
    if CURRENT_ACTIVE_CONV_ID:
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id FROM conversations WHERE id = ?", (CURRENT_ACTIVE_CONV_ID,))
            if c.fetchone():
                conn.close()
                return CURRENT_ACTIVE_CONV_ID
            conn.close()
        except Exception:
            pass

    conv = init_session_new_conversation()
    return conv["id"]


@eel.expose
def setActiveConversation(conversation_id):
    global CURRENT_ACTIVE_CONV_ID
    CURRENT_ACTIVE_CONV_ID = str(conversation_id)
    try:
        from backend.context_manager import get_context_manager
        get_context_manager().set_active_conversation(CURRENT_ACTIVE_CONV_ID)
    except Exception:
        pass
    return {"status": "success", "active_id": CURRENT_ACTIVE_CONV_ID}


@eel.expose
def getActiveConversationId():
    return get_or_create_active_conversation()


@eel.expose
def createConversation(title=None):
    return create_conversation(title)


def create_conversation(title=None):
    global CURRENT_ACTIVE_CONV_ID
    conv_id = f"conv_{uuid.uuid4().hex[:12]}"
    if not title or not title.strip():
        title = "New Conversation"
    else:
        title = title.strip()

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO conversations (id, title, created_at, updated_at, is_pinned)
            VALUES (?, ?, ?, ?, 0)
        """, (conv_id, title, now_str, now_str))
        conn.commit()
        conn.close()
        CURRENT_ACTIVE_CONV_ID = conv_id
        try:
            from backend.context_manager import get_context_manager
            get_context_manager().set_active_conversation(CURRENT_ACTIVE_CONV_ID)
        except Exception:
            pass
        return {
            "status": "success",
            "id": conv_id,
            "title": title,
            "created_at": now_str,
            "updated_at": now_str,
            "is_pinned": 0,
            "last_message": "",
            "message_count": 0
        }
    except Exception as e:
        print(f"Error creating conversation: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def getConversations(search_query=None):
    return get_all_conversations(search_query)


def get_all_conversations(search_query=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query = """
                SELECT 
                    c.id, c.title, c.created_at, c.updated_at, c.is_pinned,
                    (SELECT transcription FROM messages WHERE conversation_id = c.id ORDER BY id DESC LIMIT 1) as last_msg,
                    (SELECT timestamp FROM messages WHERE conversation_id = c.id ORDER BY id DESC LIMIT 1) as last_msg_time,
                    (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as msg_count
                FROM conversations c
                WHERE c.title LIKE ? OR EXISTS (
                    SELECT 1 FROM messages m WHERE m.conversation_id = c.id AND m.transcription LIKE ?
                )
                ORDER BY c.is_pinned DESC, c.updated_at DESC
            """
            c.execute(query, (sq, sq))
        else:
            query = """
                SELECT 
                    c.id, c.title, c.created_at, c.updated_at, c.is_pinned,
                    (SELECT transcription FROM messages WHERE conversation_id = c.id ORDER BY id DESC LIMIT 1) as last_msg,
                    (SELECT timestamp FROM messages WHERE conversation_id = c.id ORDER BY id DESC LIMIT 1) as last_msg_time,
                    (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as msg_count
                FROM conversations c
                ORDER BY c.is_pinned DESC, c.updated_at DESC
            """
            c.execute(query)

        rows = c.fetchall()
        conn.close()

        conversations = []
        for r in rows:
            conversations.append({
                "id": r[0],
                "title": r[1],
                "created_at": r[2],
                "updated_at": r[3],
                "is_pinned": bool(r[4]),
                "last_message": r[5] or "No messages yet",
                "last_message_time": r[6] or r[3],
                "message_count": r[7] or 0
            })
        return conversations
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return []


@eel.expose
def getMessages(conversation_id):
    return get_conversation_messages(conversation_id)


def get_conversation_messages(conversation_id):
    if not conversation_id:
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT id, conversation_id, sender, transcription, timestamp, is_priority_memory
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """, (str(conversation_id),))
        rows = c.fetchall()
        conn.close()

        return [{
            "id": r[0],
            "conversation_id": r[1],
            "sender": r[2],
            "transcription": r[3],
            "timestamp": r[4],
            "is_priority_memory": bool(r[5])
        } for r in rows]
    except Exception as e:
        print(f"Error fetching conversation messages: {e}")
        return []


def save_message(sender, transcription, conversation_id=None, is_priority_memory=False):
    """
    Saves a message to both messages table (linked to conversation)
    and message_logs table for long-term memory.
    Auto-generates title if default 'New Conversation' and sender is 'user'.
    """
    if not conversation_id:
        conversation_id = get_or_create_active_conversation()

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    trans_clean = str(transcription).strip()

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Insert message
        c.execute("""
            INSERT INTO messages (conversation_id, sender, transcription, timestamp, is_priority_memory)
            VALUES (?, ?, ?, ?, ?)
        """, (conversation_id, sender, trans_clean, now_str, 1 if is_priority_memory else 0))
        msg_id = c.lastrowid

        # Check if conversation needs title auto-generation
        c.execute("SELECT title, (SELECT COUNT(*) FROM messages WHERE conversation_id = ?) FROM conversations WHERE id = ?", (conversation_id, conversation_id))
        conv_row = c.fetchone()
        
        auto_title = None
        if conv_row:
            current_title = conv_row[0]
            if (current_title == "New Conversation" or not current_title) and sender == "user":
                # Generate clean punchy title from first prompt
                words = trans_clean.split()
                if len(words) > 6:
                    auto_title = " ".join(words[:6]).capitalize() + "..."
                else:
                    auto_title = trans_clean.capitalize()
                if len(auto_title) > 40:
                    auto_title = auto_title[:37] + "..."
                
                c.execute("UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?", (auto_title, now_str, conversation_id))
            else:
                c.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now_str, conversation_id))
        else:
            # If conversation record somehow didn't exist, create it
            c.execute("INSERT OR REPLACE INTO conversations (id, title, created_at, updated_at, is_pinned) VALUES (?, ?, ?, ?, 0)",
                      (conversation_id, "Chat", now_str, now_str))

        # Also store in legacy message_logs for global memory retrieval
        c.execute("""
            INSERT INTO message_logs (timestamp, sender, transcription, is_priority_memory)
            VALUES (?, ?, ?, ?)
        """, (now_str, sender, trans_clean, 1 if is_priority_memory else 0))

        conn.commit()
        conn.close()

        return {
            "status": "success",
            "id": msg_id,
            "conversation_id": conversation_id,
            "sender": sender,
            "transcription": trans_clean,
            "timestamp": now_str,
            "is_priority_memory": bool(is_priority_memory),
            "updated_title": auto_title
        }
    except Exception as e:
        print(f"Error saving message: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def renameConversation(conversation_id, new_title):
    if not conversation_id or not new_title or not new_title.strip():
        return {"status": "error", "message": "Invalid title"}
    title_clean = new_title.strip()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?", (title_clean, now_str, str(conversation_id)))
        conn.commit()
        conn.close()
        return {"status": "success", "id": conversation_id, "title": title_clean}
    except Exception as e:
        print(f"Error renaming conversation: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def deleteConversation(conversation_id):
    global CURRENT_ACTIVE_CONV_ID
    if not conversation_id:
        return {"status": "error", "message": "Invalid conversation ID"}
    conv_id = str(conversation_id)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        c.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        conn.commit()
        conn.close()

        if CURRENT_ACTIVE_CONV_ID == conv_id:
            CURRENT_ACTIVE_CONV_ID = None
            next_active = get_or_create_active_conversation()
        else:
            next_active = CURRENT_ACTIVE_CONV_ID

        return {"status": "success", "deleted_id": conv_id, "active_id": next_active}
    except Exception as e:
        print(f"Error deleting conversation: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def togglePinConversation(conversation_id):
    if not conversation_id:
        return {"status": "error", "message": "Invalid conversation ID"}
    conv_id = str(conversation_id)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT is_pinned FROM conversations WHERE id = ?", (conv_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return {"status": "error", "message": "Conversation not found"}
        
        new_pinned = 0 if row[0] == 1 else 1
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE conversations SET is_pinned = ?, updated_at = ? WHERE id = ?", (new_pinned, now_str, conv_id))
        conn.commit()
        conn.close()
        return {"status": "success", "id": conv_id, "is_pinned": bool(new_pinned)}
    except Exception as e:
        print(f"Error toggling pin: {e}")
        return {"status": "error", "message": str(e)}


def store_message_log(sender, transcription, is_priority_memory=False):
    """
    Backwards-compatible wrapper calling save_message()
    """
    return save_message(sender, transcription, conversation_id=None, is_priority_memory=is_priority_memory)


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

# Snake_case aliases for internal Python calls
toggle_pin_conversation = togglePinConversation
rename_conversation = renameConversation
delete_conversation = deleteConversation
set_active_conversation = setActiveConversation
get_active_conversation_id = getActiveConversationId


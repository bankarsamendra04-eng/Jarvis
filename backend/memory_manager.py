import re
import sqlite3
import datetime
import os
import eel

DB_PATH = "jarvis.db"

# -------------------------------------------------------------
# Security & Sensitive Data Guard
# -------------------------------------------------------------
FORBIDDEN_PATTERNS = [
    # Passwords & PINs
    (r'\b(?:password|passwd|pwd|pin|passcode|secret\s*key)\s*(?:is|:|to|=)?\s*([^\s,;]+)', "Password / PIN"),
    # One Time Passwords (OTPs)
    (r'\b(?:otp|one\s*time\s*password|verification\s*code)\s*(?:is|:|to|=)?\s*(\d{4,8})', "OTP / Verification Code"),
    # Credit/Debit Card numbers (13-19 digits)
    (r'\b(?:\d[ -]*?){13,19}\b', "Payment Card Number"),
    # CVV / Security Codes
    (r'\b(?:cvv|cvc|security\s*code)\s*(?:is|:|to|=)?\s*(\d{3,4})', "Card CVV / CVC"),
    # API Keys / Auth Tokens
    (r'\b(?:ghp_[a-zA-Z0-9]{36}|AIza[0-9A-Za-z-_]{35}|sk-[a-zA-Z0-9]{32,}|bearer\s+[a-zA-Z0-9_\-\.]+)', "API Key / Auth Token")
]

SENSITIVE_PERSONAL_PATTERNS = [
    (r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', "Phone Number"),
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "Email Address"),
    (r'\b(?:address|resident|lives\s*at|ghar\s*ka\s*pata)\s*(?:is|:|at)?\s*([^\n\r,]+)', "Personal Address"),
    (r'\b(?:aadhaar|ssn|social\s*security|pan\s*card)\b', "Government ID")
]


def check_security_guard(text):
    """
    Checks if text contains forbidden credentials (passwords, OTPs, API keys).
    Returns (is_allowed, reason, matched_type).
    """
    text_lower = text.lower()

    # 1. Check strict forbidden credentials
    for pattern, label in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"Security Warning: {label} cannot be stored in long-term memory.", label

    # Check explicit password statements
    if any(w in text_lower for w in ["my password is", "mera password", "save my password", "remember my password", "my otp is", "mera otp"]):
        return False, "Security Warning: Passwords and OTPs are blocked from memory.", "Password/OTP"

    return True, "Safe to store", None


def is_sensitive_info(text):
    """
    Checks if text contains sensitive personal data (phone, email, address).
    """
    for pattern, _ in SENSITIVE_PERSONAL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


# -------------------------------------------------------------
# Database Initialization & Default Memory Seeding
# -------------------------------------------------------------
def init_memory_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category VARCHAR(50) NOT NULL,
            key VARCHAR(100) NULL,
            content TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            is_sensitive INTEGER DEFAULT 0,
            source VARCHAR(50) DEFAULT 'user_explicit',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if empty, seed Samendra Bankar's core memories
    cursor.execute("SELECT COUNT(*) FROM user_memories")
    if cursor.fetchone()[0] == 0:
        default_memories = [
            ("Profile", "name", "User's full name is Samendra Bankar.", 0, "system_seed"),
            ("Education", "education", "BTech 3rd-Year Student with a Diploma in Engineering background.", 0, "system_seed"),
            ("Skills", "technical_skills", "Skilled in Python, Java, JavaScript, PHP, SQL, MySQL, SQLite, FastAPI, Firebase/Firestore, Android Development, Git, GitHub, and VS Code.", 0, "system_seed"),
            ("Projects", "jarvis_project", "Working on Jarvis: AI Desktop Voice Assistant with Eel Web GUI, OpenCV Face Biometrics, and Indian male neural voice.", 0, "system_seed"),
            ("Preferences", "learning_style", "Prefers practical, step-by-step explanations in simple English or Hinglish over abstract theory.", 0, "system_seed"),
            ("Preferences", "language", "Preferred voice assistant language is Hinglish (Hindi + English mix).", 0, "system_seed"),
            ("Goals", "career_aspirations", "Aspirations include Software Development, AI/ML, Cloud/DevOps, Cybersecurity, Embedded Systems, and PSU technical roles.", 0, "system_seed"),
            ("Instructions", "response_format", "Keep verbal spoken responses punchy, concise, and under 2 sentences whenever possible.", 0, "system_seed")
        ]
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for cat, key, content, is_sens, src in default_memories:
            cursor.execute("""
                INSERT INTO user_memories (category, key, content, is_sensitive, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cat, key, content, is_sens, src, now_str, now_str))

    conn.commit()
    conn.close()

init_memory_table()


# -------------------------------------------------------------
# Automatic Intent & Category Detection
# -------------------------------------------------------------
def detect_memory_category(text):
    """
    Classifies memory into appropriate category based on keywords & semantics.
    """
    t = text.lower()
    if any(w in t for w in ["skill", "know", "programming", "python", "java", "coding", "technolog", "framework", "sikha", "aata hai"]):
        return "Skills"
    if any(w in t for w in ["study", "college", "degree", "diploma", "btech", "semester", "year", "education", "school", "university", "padh"]):
        return "Education"
    if any(w in t for w in ["project", "building", "app", "website", "hackathon", "bana raha", "kaam kar"]):
        return "Projects"
    if any(w in t for w in ["prefer", "like", "favorite", "love", "hate", "pasand", "aadat", "mode", "theme", "dark mode"]):
        return "Preferences"
    if any(w in t for w in ["goal", "dream", "career", "aspire", "future", "target", "banna chahta", "placement"]):
        return "Goals"
    if any(w in t for w in ["always", "never", "instruction", "rule", "whenever", "rule", "hamesha", "kabhi mat"]):
        return "Instructions"
    if any(w in t for w in ["name", "live", "city", "born", "age", "profile", "rehta hoon", "naam"]):
        return "Profile"
    return "General"


def auto_detect_worth_remembering(text):
    """
    Detects if an ordinary conversational message contains important facts worth saving.
    Returns (should_remember, extracted_content, category)
    """
    t = text.strip()
    t_lower = t.lower()

    # Explicit memory triggers
    explicit_triggers = ["remember that", "remember this", "save to memory", "save this", "yaad rakhna", "yaad rakho", "note this down", "keep in mind"]
    for trig in explicit_triggers:
        if trig in t_lower:
            cleaned = re.sub(rf'^(?:please\s+)?(?:{trig})\s*(?::|that)?\s*', '', t, flags=re.IGNORECASE).strip()
            if len(cleaned) > 4:
                cat = detect_memory_category(cleaned)
                return True, cleaned, cat

    # Implicit declarative facts
    patterns = [
        (r'\bmy\s+favorite\s+(\w+)\s+is\s+([^,.]+)', "Preferences"),
        (r'\bi\s+(?:prefer|like|love)\s+([^,.]+)', "Preferences"),
        (r'\bi\s+am\s+(?:currently\s+)?working\s+on\s+([^,.]+)', "Projects"),
        (r'\bmy\s+(?:final\s+year\s+)?project\s+is\s+([^,.]+)', "Projects"),
        (r'\bmy\s+goal\s+is\s+to\s+([^,.]+)', "Goals"),
        (r'\bi\s+want\s+to\s+become\s+(?:a|an)?\s*([^,.]+)', "Goals"),
        (r'\bmujhe\s+([^,.]+)\s+pasand\s+hai', "Preferences"),
        (r'\bmera\s+project\s+([^,.]+)\s+hai', "Projects")
    ]

    for p, cat in patterns:
        m = re.search(p, t_lower)
        if m:
            return True, t, cat

    return False, None, None


# -------------------------------------------------------------
# Memory CRUD Backend APIs
# -------------------------------------------------------------
@eel.expose
def getAllMemories(search_query=None, category_filter=None):
    return get_all_memories(search_query, category_filter)


def get_all_memories(search_query=None, category_filter=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        query = "SELECT id, category, key, content, is_sensitive, source, created_at, updated_at FROM user_memories WHERE 1=1"
        params = []

        if category_filter and category_filter != "All":
            query += " AND category = ?"
            params.append(category_filter)

        if search_query and search_query.strip():
            query += " AND (content LIKE ? OR category LIKE ? OR key LIKE ?)"
            sq = f"%{search_query.strip()}%"
            params.extend([sq, sq, sq])

        query += " ORDER BY category ASC, updated_at DESC"
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        return [{
            "id": r[0],
            "category": r[1],
            "key": r[2] or "",
            "content": r[3],
            "is_sensitive": bool(r[4]),
            "source": r[5],
            "created_at": r[6],
            "updated_at": r[7]
        } for r in rows]
    except Exception as e:
        print(f"Error fetching memories: {e}")
        return []


@eel.expose
def addMemory(category, content, is_sensitive=False, key=None):
    return add_user_memory(category, content, is_sensitive=is_sensitive, key=key)


def add_user_memory(category, content, is_sensitive=None, key=None, source="user_explicit"):
    if not content or not content.strip():
        return {"status": "error", "message": "Memory content cannot be empty."}

    content_clean = content.strip()
    
    # 1. Security Check
    allowed, reason, threat = check_security_guard(content_clean)
    if not allowed:
        return {"status": "blocked", "message": reason, "threat_type": threat}

    if is_sensitive is None:
        is_sensitive = is_sensitive_info(content_clean)

    if not category or category.strip() == "":
        category = detect_memory_category(content_clean)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO user_memories (category, key, content, is_sensitive, source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (category, key or "", content_clean, 1 if is_sensitive else 0, source, now_str, now_str))
        mem_id = c.lastrowid
        conn.commit()
        conn.close()

        print(f"[Memory System] Saved #{mem_id} [{category}]: {content_clean}")
        return {
            "status": "success",
            "id": mem_id,
            "category": category,
            "content": content_clean,
            "is_sensitive": bool(is_sensitive),
            "updated_at": now_str
        }
    except Exception as e:
        print(f"Error adding memory: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def updateMemory(memory_id, category, content, is_sensitive=None):
    if not memory_id or not content or not content.strip():
        return {"status": "error", "message": "Invalid memory update payload."}

    content_clean = content.strip()
    allowed, reason, threat = check_security_guard(content_clean)
    if not allowed:
        return {"status": "blocked", "message": reason}

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if is_sensitive is not None:
            c.execute("""
                UPDATE user_memories
                SET category = ?, content = ?, is_sensitive = ?, updated_at = ?
                WHERE id = ?
            """, (category, content_clean, 1 if is_sensitive else 0, now_str, int(memory_id)))
        else:
            c.execute("""
                UPDATE user_memories
                SET category = ?, content = ?, updated_at = ?
                WHERE id = ?
            """, (category, content_clean, now_str, int(memory_id)))
        conn.commit()
        conn.close()

        return {"status": "success", "id": memory_id, "category": category, "content": content_clean}
    except Exception as e:
        print(f"Error updating memory: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def deleteMemory(memory_id):
    if not memory_id:
        return {"status": "error", "message": "Invalid memory ID."}

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM user_memories WHERE id = ?", (int(memory_id),))
        conn.commit()
        conn.close()

        return {"status": "success", "deleted_id": memory_id}
    except Exception as e:
        print(f"Error deleting memory: {e}")
        return {"status": "error", "message": str(e)}


def forget_memory_by_topic(topic):
    """
    Deletes memories matching a given topic phrase (e.g. 'meeting', 'project', 'password').
    """
    if not topic or not topic.strip():
        return False, "Topic is empty"
    t_clean = topic.strip()
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            DELETE FROM user_memories
            WHERE content LIKE ? OR key LIKE ? OR category LIKE ?
        """, (f"%{t_clean}%", f"%{t_clean}%", f"%{t_clean}%"))
        deleted_count = c.rowcount
        conn.commit()
        conn.close()
        return deleted_count > 0, deleted_count
    except Exception as e:
        print(f"Error forgetting memory: {e}")
        return False, str(e)


# -------------------------------------------------------------
# Context-Aware Relevant Memory Retrieval (Smart Search)
# -------------------------------------------------------------
def get_relevant_memories(query, limit=4):
    """
    Scores and retrieves only the most relevant memories for the active query
    instead of feeding the entire memory database to the AI.
    """
    if not query or not query.strip():
        return []

    q_words = [w.lower() for w in re.findall(r'\b\w+\b', query) if len(w) > 2 and w.lower() not in (
        'what', 'when', 'where', 'tell', 'about', 'your', 'this', 'that', 'with', 'from', 'have',
        'does', 'mera', 'meri', 'karo', 'batao', 'kya', 'hai', 'hain', 'the', 'and', 'for'
    )]

    all_memories = get_all_memories()
    scored = []

    for m in all_memories:
        text_lower = (m["content"] + " " + m["category"] + " " + (m["key"] or "")).lower()
        score = 0
        for w in q_words:
            if w in text_lower:
                score += 2
        # Exact substring boost
        if query.lower().strip() in text_lower:
            score += 5
        
        if score > 0:
            scored.append((score, m))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:limit]]


@eel.expose
def getMemoryStats():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*), COUNT(DISTINCT category) FROM user_memories")
        total, cats = c.fetchone()
        conn.close()
        return {"total_memories": total or 0, "categories_count": cats or 0}
    except Exception:
        return {"total_memories": 0, "categories_count": 0}


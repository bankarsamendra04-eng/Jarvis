import json
import sqlite3
import datetime
import re
import os
import eel

DB_PATH = "jarvis.db"

# -------------------------------------------------------------
# Database Table Initialization & Seed Goals
# -------------------------------------------------------------
def init_goals_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            category VARCHAR(50) DEFAULT 'General',
            description TEXT NULL,
            deadline DATE NULL,
            priority VARCHAR(20) DEFAULT 'Medium',
            milestones TEXT DEFAULT '[]',
            progress INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'Active',
            notes TEXT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if empty, seed initial goals for Samendra Bankar
    cursor.execute("SELECT COUNT(*) FROM goals")
    if cursor.fetchone()[0] == 0:
        default_goals = [
            (
                "Complete Jarvis Voice Assistant Project",
                "Project",
                "Build full-stack AI desktop assistant with Eel GUI, Face Biometrics, Indian Male Voice, Memory Vault, and Goal Tracker.",
                "2026-10-30",
                "High",
                json.dumps([
                    {"id": 1, "title": "Face Biometrics & Authentication", "completed": True},
                    {"id": 2, "title": "Indian Tone Neural Voice Engine", "completed": True},
                    {"id": 3, "title": "Conversation History Sidebar & SQLite Memory", "completed": True},
                    {"id": 4, "title": "Personal Goal & Progress Tracking System", "completed": True},
                    {"id": 5, "title": "Final Performance Testing & Documentation", "completed": False}
                ]),
                80,
                "Active",
                "Flagship engineering capstone project."
            ),
            (
                "Master Advanced AI/ML & Deep Learning",
                "Learning",
                "Deep dive into Neural Networks, PyTorch, Model Fine-tuning, and LLM Agents.",
                "2026-11-15",
                "High",
                json.dumps([
                    {"id": 1, "title": "Master NumPy, Pandas & Data Preprocessing", "completed": True},
                    {"id": 2, "title": "Build CNNs & Computer Vision models with OpenCV", "completed": True},
                    {"id": 3, "title": "NLP, Transformers & Speech Recognition pipelines", "completed": True},
                    {"id": 4, "title": "Deploy FastAPI AI microservices", "completed": False}
                ]),
                75,
                "Active",
                "Core domain for career placement."
            ),
            (
                "Technical Interview & Placement Preparation",
                "Interview",
                "Prepare Data Structures & Algorithms in Java/Python, System Design, and Core CS Fundamentals.",
                "2026-12-01",
                "High",
                json.dumps([
                    {"id": 1, "title": "Arrays, Strings, HashMaps, and Two Pointers", "completed": True},
                    {"id": 2, "title": "Trees, Graphs, and Dynamic Programming", "completed": False},
                    {"id": 3, "title": "OOPs, DBMS, OS, and Computer Networks Revision", "completed": True},
                    {"id": 4, "title": "Mock Technical Interviews & Resume Polish", "completed": False}
                ]),
                50,
                "Active",
                "Daily 1.5 hours problem solving."
            ),
            (
                "Build Developer Portfolio Website",
                "Portfolio",
                "Design and deploy an interactive modern portfolio showcasing all software & AI projects.",
                "2026-10-20",
                "Medium",
                json.dumps([
                    {"id": 1, "title": "Design responsive UI layout with Tailwind/Bootstrap", "completed": True},
                    {"id": 2, "title": "Integrate GitHub projects showcase & live demos", "completed": True},
                    {"id": 3, "title": "Deploy to Vercel/GitHub Pages with custom domain", "completed": False}
                ]),
                65,
                "Active",
                "Include Jarvis live demo link and credentials."
            )
        ]

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for name, cat, desc, dline, prio, mls, prog, stat, notes in default_goals:
            cursor.execute("""
                INSERT INTO goals (name, category, description, deadline, priority, milestones, progress, status, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, cat, desc, dline, prio, mls, prog, stat, notes, now_str, now_str))

    conn.commit()
    conn.close()

init_goals_table()


# -------------------------------------------------------------
# Goals CRUD APIs
# -------------------------------------------------------------
@eel.expose
def getAllGoals(search_query=None, status_filter=None, category_filter=None):
    return get_all_goals(search_query, status_filter, category_filter)


def get_all_goals(search_query=None, status_filter=None, category_filter=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        query = "SELECT id, name, category, description, deadline, priority, milestones, progress, status, notes, created_at, updated_at FROM goals WHERE 1=1"
        params = []

        if status_filter and status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)

        if category_filter and category_filter != "All":
            query += " AND category = ?"
            params.append(category_filter)

        if search_query and search_query.strip():
            sq = f"%{search_query.strip()}%"
            query += " AND (name LIKE ? OR description LIKE ? OR notes LIKE ? OR category LIKE ?)"
            params.extend([sq, sq, sq, sq])

        # Priority ordering: High > Medium > Low, then deadline ASC
        query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 ELSE 4 END, deadline ASC"
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        goals = []
        for r in rows:
            try:
                mls = json.loads(r[6]) if r[6] else []
            except Exception:
                mls = []
            
            goals.append({
                "id": r[0],
                "name": r[1],
                "category": r[2] or "General",
                "description": r[3] or "",
                "deadline": r[4] or "",
                "priority": r[5] or "Medium",
                "milestones": mls,
                "progress": r[7] if r[7] is not None else 0,
                "status": r[8] or "Active",
                "notes": r[9] or "",
                "created_at": r[10],
                "updated_at": r[11]
            })
        return goals
    except Exception as e:
        print(f"Error fetching goals: {e}")
        return []


@eel.expose
def createGoal(name, category="General", description="", deadline="", priority="Medium", milestones=None, progress=0, status="Active", notes=""):
    return create_user_goal(name, category, description, deadline, priority, milestones, progress, status, notes)


def create_user_goal(name, category="General", description="", deadline="", priority="Medium", milestones=None, progress=0, status="Active", notes=""):
    if not name or not name.strip():
        return {"status": "error", "message": "Goal name cannot be empty."}

    name_clean = name.strip()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if milestones is None:
        milestones = []
    elif isinstance(milestones, str):
        try:
            milestones = json.loads(milestones)
        except Exception:
            milestones = []

    # Auto-calculate progress if milestones provided
    if milestones and len(milestones) > 0:
        completed_count = sum(1 for m in milestones if m.get("completed"))
        progress = int((completed_count / len(milestones)) * 100)
    else:
        try:
            progress = max(0, min(100, int(progress)))
        except Exception:
            progress = 0

    if progress >= 100 and (not status or status == "Active"):
        status = "Completed"
    elif not status:
        status = "Active"

    mls_json = json.dumps(milestones)

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO goals (name, category, description, deadline, priority, milestones, progress, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name_clean, category or "General", description or "", deadline or "", priority or "Medium", mls_json, progress, status, notes or "", now_str, now_str))
        goal_id = c.lastrowid
        conn.commit()
        conn.close()

        print(f"[Goals System] Created Goal #{goal_id}: {name_clean} ({progress}%)")
        return {
            "status": "success",
            "id": goal_id,
            "name": name_clean,
            "category": category,
            "progress": progress,
            "status_label": status
        }
    except Exception as e:
        print(f"Error creating goal: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def updateGoal(goal_id, name, category, description, deadline, priority, milestones, progress, status, notes):
    if not goal_id or not name or not name.strip():
        return {"status": "error", "message": "Invalid goal parameters."}

    name_clean = name.strip()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(milestones, str):
        try:
            milestones = json.loads(milestones)
        except Exception:
            milestones = []

    if milestones and len(milestones) > 0:
        completed_count = sum(1 for m in milestones if m.get("completed"))
        progress = int((completed_count / len(milestones)) * 100)
    else:
        try:
            progress = max(0, min(100, int(progress)))
        except Exception:
            progress = 0

    if progress >= 100 and status == "Active":
        status = "Completed"
    elif progress < 100 and status == "Completed":
        status = "Active"

    mls_json = json.dumps(milestones or [])

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            UPDATE goals
            SET name = ?, category = ?, description = ?, deadline = ?, priority = ?, milestones = ?, progress = ?, status = ?, notes = ?, updated_at = ?
            WHERE id = ?
        """, (name_clean, category or "General", description or "", deadline or "", priority or "Medium", mls_json, progress, status or "Active", notes or "", now_str, int(goal_id)))
        conn.commit()
        conn.close()

        return {"status": "success", "id": goal_id, "name": name_clean, "progress": progress, "status_label": status}
    except Exception as e:
        print(f"Error updating goal: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def updateGoalProgress(goal_id, new_progress):
    try:
        prog = max(0, min(100, int(new_progress)))
    except Exception:
        return {"status": "error", "message": "Invalid progress value"}

    status = "Completed" if prog >= 100 else "Active"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            UPDATE goals
            SET progress = ?, status = ?, updated_at = ?
            WHERE id = ?
        """, (prog, status, now_str, int(goal_id)))
        conn.commit()
        conn.close()
        return {"status": "success", "id": goal_id, "progress": prog, "status": status}
    except Exception as e:
        print(f"Error updating progress: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def toggleMilestone(goal_id, milestone_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT milestones FROM goals WHERE id = ?", (int(goal_id),))
        row = c.fetchone()
        if not row:
            conn.close()
            return {"status": "error", "message": "Goal not found"}

        try:
            milestones = json.loads(row[0]) if row[0] else []
        except Exception:
            milestones = []

        found = False
        for m in milestones:
            if str(m.get("id")) == str(milestone_id):
                m["completed"] = not m.get("completed", False)
                found = True
                break

        if not found:
            conn.close()
            return {"status": "error", "message": "Milestone not found"}

        completed_count = sum(1 for m in milestones if m.get("completed"))
        new_progress = int((completed_count / len(milestones)) * 100) if len(milestones) > 0 else 0
        status = "Completed" if new_progress >= 100 else "Active"
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute("""
            UPDATE goals
            SET milestones = ?, progress = ?, status = ?, updated_at = ?
            WHERE id = ?
        """, (json.dumps(milestones), new_progress, status, now_str, int(goal_id)))
        conn.commit()
        conn.close()

        return {"status": "success", "id": goal_id, "milestones": milestones, "progress": new_progress, "status": status}
    except Exception as e:
        print(f"Error toggling milestone: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def deleteGoal(goal_id):
    if not goal_id:
        return {"status": "error", "message": "Invalid goal ID."}
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM goals WHERE id = ?", (int(goal_id),))
        conn.commit()
        conn.close()
        return {"status": "success", "deleted_id": goal_id}
    except Exception as e:
        print(f"Error deleting goal: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def getGoalsStats():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*), AVG(progress) FROM goals WHERE status = 'Active'")
        active_count, avg_progress = c.fetchone()
        
        c.execute("SELECT COUNT(*) FROM goals WHERE status = 'Completed'")
        completed_count = c.fetchone()[0]

        # Find closest to completion goal (< 100%)
        c.execute("SELECT id, name, progress FROM goals WHERE status = 'Active' AND progress < 100 ORDER BY progress DESC LIMIT 1")
        closest_row = c.fetchone()
        closest = {"id": closest_row[0], "name": closest_row[1], "progress": closest_row[2]} if closest_row else None

        conn.close()
        return {
            "active_goals": active_count or 0,
            "completed_goals": completed_count or 0,
            "avg_progress": int(avg_progress or 0),
            "closest_goal": closest
        }
    except Exception as e:
        print(f"Error getting goals stats: {e}")
        return {"active_goals": 0, "completed_goals": 0, "avg_progress": 0, "closest_goal": None}


# -------------------------------------------------------------
# Daily Action Plan Generator
# -------------------------------------------------------------
@eel.expose
def generateDailyActionPlan(available_hours=4):
    """
    Generates a personalized daily action plan based on active goals,
    priority rankings, upcoming deadlines, and incomplete milestones.
    """
    goals = get_all_goals(status_filter="Active")
    if not goals:
        return {
            "status": "empty",
            "summary": "Currently there are no active goals. Create a new goal to generate your daily action plan!",
            "tasks": []
        }

    tasks = []
    # 1. Gather incomplete milestones from High Priority goals first
    for g in goals:
        incomplete_mls = [m["title"] for m in g["milestones"] if not m.get("completed")]
        deadline_text = f"Due: {g['deadline']}" if g['deadline'] else ""
        
        if incomplete_mls:
            for m_title in incomplete_mls[:2]:  # Top 2 milestones per goal
                tasks.append({
                    "goal_id": g["id"],
                    "goal_name": g["name"],
                    "task": m_title,
                    "category": g["category"],
                    "priority": g["priority"],
                    "deadline": deadline_text,
                    "est_time": "45 mins" if g["priority"] == "High" else "30 mins"
                })
        else:
            # If no explicit milestones, add direct action item
            tasks.append({
                "goal_id": g["id"],
                "goal_name": g["name"],
                "task": f"Advance progress on {g['name']} (Current: {g['progress']}%)",
                "category": g["category"],
                "priority": g["priority"],
                "deadline": deadline_text,
                "est_time": "1 hour"
            })

    # Sort tasks by Priority: High first
    tasks.sort(key=lambda x: 0 if x["priority"] == "High" else (1 if x["priority"] == "Medium" else 2))
    selected_tasks = tasks[:4]  # Curate top 3-4 tasks for the day

    summary = f"Today's Plan focuses on {len(selected_tasks)} key tasks across your high-priority goals."
    return {
        "status": "success",
        "date": datetime.datetime.now().strftime("%A, %B %d"),
        "summary": summary,
        "tasks": selected_tasks
    }


# -------------------------------------------------------------
# Natural Voice Command Handlers
# -------------------------------------------------------------
def get_closest_to_completion_goal():
    """
    Finds the active goal with the highest progress percentage under 100%.
    """
    goals = get_all_goals(status_filter="Active")
    candidates = [g for g in goals if g["progress"] < 100]
    if candidates:
        candidates.sort(key=lambda x: x["progress"], reverse=True)
        top = candidates[0]
        return f"Aapka goal '{top['name']}' completion ke sabse kareeb hai, jo abhi {top['progress']}% complete ho chuka hai."
    return "Abhi aapke sabhi active goals ya toh 100% complete hain ya naye shuru hue hain."


def get_goals_voice_summary():
    """
    Generates spoken overview of active goals in Hinglish.
    """
    goals = get_all_goals(status_filter="Active")
    if not goals:
        return "Samendra, abhi aapke paas koi active goals nahi hain. Aap 'Create a new goal' bol kar goal bana sakte hain."

    summaries = []
    for g in goals[:3]:
        summaries.append(f"{g['name']} ({g['progress']}% complete)")

    return f"Aapke paas {len(goals)} active goals hain: " + ", aur ".join(summaries) + "."


def get_daily_action_plan_voice():
    """
    Generates spoken response for 'What should I work on today?'.
    """
    plan = generateDailyActionPlan()
    if plan["status"] == "empty":
        return "Aaj ke liye koi active goal nahi mila. Aap naya goal create kar sakte hain."

    tasks = plan["tasks"]
    task_points = []
    for i, t in enumerate(tasks[:3], 1):
        task_points.append(f"{t['task']} ({t['goal_name']})")

    return f"Aaj aapko in main tasks par focus karna chahiye: " + ", aur ".join(task_points) + "."


def update_goal_progress_voice(query):
    """
    Parses voice commands like 'Update progress of Jarvis project to 85%' or 'Update progress to 90%'.
    """
    match_prog = re.search(r'(?:to|at|by|ko)?\s*(\d{1,3})\s*%', query)
    if not match_prog:
        match_prog = re.search(r'(\d{1,3})\s*percent', query, re.IGNORECASE)

    if not match_prog:
        return False, "Kripya progress percentage specify karein, jaise 'Update progress of Jarvis project to 85%'."

    new_val = int(match_prog.group(1))
    new_val = max(0, min(100, new_val))

    goals = get_all_goals(status_filter="Active")
    if not goals:
        return False, "Abhi koi active goal nahi mila jiska progress update kiya ja sake."

    # Try matching goal name in query
    matched_goal = None
    for g in goals:
        g_words = [w.lower() for w in re.findall(r'\b\w+\b', g['name']) if len(w) > 3]
        if any(w in query.lower() for w in g_words):
            matched_goal = g
            break

    if not matched_goal:
        # Default to highest priority active goal
        matched_goal = goals[0]

    updateGoalProgress(matched_goal["id"], new_val)
    return True, f"Maine '{matched_goal['name']}' ka progress update karke {new_val}% kar diya hai."

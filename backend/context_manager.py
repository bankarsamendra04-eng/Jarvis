import re
import time
import json
from typing import Dict, Any, List, Optional, Tuple

class ConversationContextManager:
    def __init__(self):
        # Global store of conversation contexts indexed by conversation_id (or 'default')
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.active_conv_id: str = "default"

    def _get_empty_context(self) -> Dict[str, Any]:
        return {
            "current_project": None,        # dict: {name, type, description, files}
            "previous_project": None,       # dict or str
            "current_task": None,           # str: e.g. "Create JavaScript file for Quiz App"
            "current_topic": None,          # str: e.g. "Quiz App", "OSI Model"
            "recent_files": [],             # list of dicts: [{name, path, type, timestamp}]
            "recent_commands": [],          # list of dicts: [{query, timestamp}]
            "recent_errors": [],            # list of dicts: [{error, context, timestamp}]
            "last_code_snippet": None,      # dict: {code, language, description}
            "pending_clarification": None,  # dict: {original_query, candidate_options, type}
            "last_updated": time.time()
        }

    def get_context(self, conv_id: Optional[str] = None) -> Dict[str, Any]:
        cid = conv_id or self.active_conv_id or "default"
        if cid not in self.contexts:
            self.contexts[cid] = self._get_empty_context()
        return self.contexts[cid]

    def set_active_conversation(self, conv_id: str):
        if conv_id:
            self.active_conv_id = conv_id
            if conv_id not in self.contexts:
                self.contexts[conv_id] = self._get_empty_context()

    def reset_context(self, conv_id: Optional[str] = None):
        cid = conv_id or self.active_conv_id or "default"
        self.contexts[cid] = self._get_empty_context()

    # -------------------------------------------------------------------------
    # Entity Extraction & Updates
    # -------------------------------------------------------------------------
    def update_from_user_query(self, query: str, conv_id: Optional[str] = None) -> Dict[str, Any]:
        ctx = self.get_context(conv_id)
        q = query.strip()
        q_lower = q.lower()
        now = time.time()

        # 1. Record in recent commands (keep max 15)
        ctx["recent_commands"].insert(0, {"query": q, "timestamp": now})
        ctx["recent_commands"] = ctx["recent_commands"][:15]

        # 2. Extract Project mentions
        # E.g. "I'm building a quiz app", "I am making a portfolio website", "working on Jarvis project", "my project is..."
        proj_match = re.search(
            r'(?:i am|i\'m|working on|building|creating|developing|starting|making|my project is|project:?)\s+(?:a|an|the)?\s*([a-zA-Z0-9_\-\s]+?)(?:\s+app|\s+application|\s+website|\s+project|\s+system|\s+service|\.|\,|$)',
            q, re.IGNORECASE
        )
        if proj_match:
            raw_proj = proj_match.group(1).strip()
            # Clean common filler words
            raw_proj = re.sub(r'^(?:a|an|the)\s+', '', raw_proj, flags=re.IGNORECASE)
            # Reconstruct full meaningful title
            full_match = proj_match.group(0).strip()
            if any(w in full_match.lower() for w in ["app", "website", "project", "system"]):
                project_name = full_match.split("building")[-1].split("making")[-1].split("creating")[-1].split("working on")[-1].strip(" .:,")
                project_name = re.sub(r'^(?:a|an|the)\s+', '', project_name, flags=re.IGNORECASE).title()
            else:
                project_name = f"{raw_proj.title()} Project"

            if len(project_name) >= 3 and not any(project_name.lower().startswith(x) for x in ["this", "that", "it", "code", "file", "error"]):
                if ctx["current_project"] and ctx["current_project"].get("name") != project_name:
                    ctx["previous_project"] = ctx["current_project"]
                ctx["current_project"] = {
                    "name": project_name,
                    "type": "Application/Project",
                    "description": f"User project: {project_name}",
                    "files": ctx["current_project"].get("files", []) if ctx["current_project"] and ctx["current_project"].get("name") == project_name else [],
                    "updated_at": now
                }
                ctx["current_topic"] = project_name
                ctx["current_task"] = f"Working on {project_name}"

        # 3. Extract Error mentions
        # E.g., "IndexError: list index out of range", "getting 404 error", "SyntaxError in script.py"
        error_match = re.search(
            r'([A-Za-z0-9_]+Error(?::[^\n\r]+)?|\b(?:404|500|502|403)\s*(?:error|exception)?|error:\s*[^\n\r]+|uncaught\s+[A-Za-z0-9_]+)',
            q, re.IGNORECASE
        )
        if error_match:
            err_text = error_match.group(1).strip()
            ctx["recent_errors"].insert(0, {
                "error": err_text,
                "raw_query": q,
                "timestamp": now
            })
            ctx["recent_errors"] = ctx["recent_errors"][:10]
            ctx["current_topic"] = f"Debugging {err_text.split(':')[0]}"
            ctx["current_task"] = f"Fixing {err_text}"

        # 4. Extract File mentions
        # E.g. "Create the JavaScript file", "open index.html", "check script.js", "edit styles.css"
        file_match = re.search(
            r'\b([a-zA-Z0-9_\-]+\.(?:js|py|html|css|json|java|cpp|c|ts|jsx|tsx|sql|txt|md))\b',
            q, re.IGNORECASE
        )
        if file_match:
            fname = file_match.group(1)
            self.record_file(fname, conv_id=conv_id)
        elif "javascript file" in q_lower or "js file" in q_lower:
            self.record_file("script.js", file_type="javascript", conv_id=conv_id)
        elif "css file" in q_lower or "style file" in q_lower or "stylesheet" in q_lower:
            self.record_file("style.css", file_type="css", conv_id=conv_id)
        elif "html file" in q_lower or "html page" in q_lower:
            self.record_file("index.html", file_type="html", conv_id=conv_id)
        elif "python file" in q_lower or "python script" in q_lower:
            self.record_file("main.py", file_type="python", conv_id=conv_id)

        ctx["last_updated"] = now
        return ctx

    def record_file(self, file_name: str, file_type: Optional[str] = None, conv_id: Optional[str] = None):
        ctx = self.get_context(conv_id)
        now = time.time()
        ext = file_name.split('.')[-1].lower() if '.' in file_name else (file_type or "text")
        # Avoid duplicate top entry
        ctx["recent_files"] = [f for f in ctx["recent_files"] if f["name"] != file_name]
        ctx["recent_files"].insert(0, {
            "name": file_name,
            "type": ext,
            "timestamp": now
        })
        ctx["recent_files"] = ctx["recent_files"][:10]
        if ctx["current_project"]:
            if file_name not in ctx["current_project"]["files"]:
                ctx["current_project"]["files"].append(file_name)

    def record_code(self, code_text: str, language: str = "python", description: str = "", conv_id: Optional[str] = None):
        ctx = self.get_context(conv_id)
        ctx["last_code_snippet"] = {
            "code": code_text,
            "language": language,
            "description": description,
            "timestamp": time.time()
        }

    # -------------------------------------------------------------------------
    # Ambiguity Checking & Clarifications
    # -------------------------------------------------------------------------
    def check_ambiguity(self, query: str, conv_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Detects if a query contains genuinely ambiguous references where multiple candidates
        exist with equal likelihood, and returns a concise clarifying question if needed.
        """
        ctx = self.get_context(conv_id)
        q_lower = query.lower().strip()

        # Check for clarification answer if pending
        if ctx.get("pending_clarification"):
            pending = ctx["pending_clarification"]
            # Clear pending after answering
            ctx["pending_clarification"] = None
            return False, None

        # Case 1: "open that file" or "show the file" when there are multiple recent files and no specific recency dominant
        if re.search(r'\b(open|show|display|edit|delete)\s+(?:that|the|this)\s+file\b', q_lower):
            files = ctx.get("recent_files", [])
            if len(files) >= 2:
                # If the top 2 files were recorded within 3 seconds of each other (batch created)
                f0, f1 = files[0]["name"], files[1]["name"]
                if abs(files[0]["timestamp"] - files[1]["timestamp"]) < 5 and f0 != f1:
                    ctx["pending_clarification"] = {
                        "original_query": query,
                        "type": "file",
                        "options": [f0, f1]
                    }
                    return True, f"Are you referring to {f0} or {f1}?"

        # Case 2: "switch to that project" or "the previous project" when multiple prior projects exist or none exist
        if re.search(r'\b(?:switch to|open|show)\s+(?:the\s+previous\s+project|that\s+project)\b', q_lower):
            if not ctx.get("previous_project") and not ctx.get("current_project"):
                return True, "Which project are you referring to? You haven't mentioned a project yet."

        return False, None

    # -------------------------------------------------------------------------
    # Context-Aware Reference Resolution
    # -------------------------------------------------------------------------
    def resolve_references(self, query: str, conv_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Resolves relative pronouns and references:
        - "this", "that", "it"
        - "the previous project", "my previous project"
        - "the last file", "that file", "this file"
        - "that code", "this code", "the code"
        - "the above error", "this error", "that error"
        - "my current project", "this project", "current project"
        """
        ctx = self.get_context(conv_id)
        resolved = query.strip()
        q_lower = resolved.lower()
        applied_resolutions = {}

        cur_proj = ctx.get("current_project")
        prev_proj = ctx.get("previous_project")
        cur_proj_name = cur_proj["name"] if cur_proj else None
        prev_proj_name = prev_proj["name"] if isinstance(prev_proj, dict) else prev_proj
        last_file = ctx["recent_files"][0]["name"] if ctx.get("recent_files") else None
        last_error = ctx["recent_errors"][0]["error"] if ctx.get("recent_errors") else None
        last_code = ctx.get("last_code_snippet")

        # 1. "my current project" / "the current project" / "this project"
        if re.search(r'\b(my current project|the current project|this project|our project)\b', q_lower):
            if cur_proj_name:
                resolved = re.sub(r'\b(my current project|the current project|this project|our project)\b', cur_proj_name, resolved, flags=re.IGNORECASE)
                applied_resolutions["project"] = cur_proj_name

        # 2. "the previous project" / "my previous project" / "that other project"
        if re.search(r'\b(the previous project|my previous project|that other project|prior project)\b', q_lower):
            if prev_proj_name:
                resolved = re.sub(r'\b(the previous project|my previous project|that other project|prior project)\b', prev_proj_name, resolved, flags=re.IGNORECASE)
                applied_resolutions["previous_project"] = prev_proj_name

        # 3. "the last file" / "that file" / "this file"
        if re.search(r'\b(the last file|that file|this file)\b', q_lower):
            if last_file:
                resolved = re.sub(r'\b(the last file|that file|this file)\b', last_file, resolved, flags=re.IGNORECASE)
                applied_resolutions["file"] = last_file

        # 4. "the above error" / "this error" / "that error"
        if re.search(r'\b(the above error|this error|that error|the error)\b', q_lower):
            if last_error:
                resolved = re.sub(r'\b(the above error|this error|that error|the error)\b', f"the error '{last_error}'", resolved, flags=re.IGNORECASE)
                applied_resolutions["error"] = last_error

        # 5. "that code" / "this code" / "the code"
        if re.search(r'\b(that code|this code|the code)\b', q_lower):
            if last_code:
                lang = last_code.get("language", "code")
                resolved = re.sub(r'\b(that code|this code|the code)\b', f"the {lang} code", resolved, flags=re.IGNORECASE)
                applied_resolutions["code"] = last_code

        # 6. Context synthesis for implicit file creation/handling
        # Example: User: "Create the JavaScript file" when current_project is "Quiz App"
        if cur_proj_name:
            if re.search(r'\b(?:create|write|make|generate)\s+(?:the\s+)?(?:javascript|js)\s+file\b', q_lower):
                resolved = f"Write JavaScript code (script.js) for {cur_proj_name}"
                applied_resolutions["synthesized_task"] = resolved
            elif re.search(r'\b(?:create|write|make|generate)\s+(?:the\s+)?(?:css|style|stylesheet)\s+file\b', q_lower):
                resolved = f"Write CSS styling (style.css) for {cur_proj_name}"
                applied_resolutions["synthesized_task"] = resolved
            elif re.search(r'\b(?:create|write|make|generate)\s+(?:the\s+)?(?:html|index)\s+file\b', q_lower):
                resolved = f"Write HTML structure (index.html) for {cur_proj_name}"
                applied_resolutions["synthesized_task"] = resolved
            elif re.search(r'\b(?:add|write)\s+(?:css|styling|styles)\s+for\s+(?:that|this|it)\b', q_lower):
                resolved = f"Write CSS styling for {cur_proj_name}"
                applied_resolutions["synthesized_task"] = resolved
            elif re.search(r'\b(?:add|write)\s+(?:javascript|logic|js)\s+for\s+(?:that|this|it)\b', q_lower):
                resolved = f"Write JavaScript code for {cur_proj_name}"
                applied_resolutions["synthesized_task"] = resolved

        # 7. Pronouns "this", "that", "it" in standalone action
        # E.g. "explain that", "debug this", "fix it"
        if re.search(r'\b(explain|debug|fix|solve|run)\s+(?:this|that|it)\b', q_lower):
            if last_error and any(w in q_lower for w in ["debug", "fix", "solve", "explain"]):
                resolved = re.sub(r'\b(?:this|that|it)\b', f"error: {last_error}", resolved, flags=re.IGNORECASE)
                applied_resolutions["it_resolved"] = last_error
            elif last_code:
                resolved = re.sub(r'\b(?:this|that|it)\b', f"the {last_code.get('language', 'code')}", resolved, flags=re.IGNORECASE)
                applied_resolutions["it_resolved"] = last_code
            elif cur_proj_name:
                resolved = re.sub(r'\b(?:this|that|it)\b', cur_proj_name, resolved, flags=re.IGNORECASE)
                applied_resolutions["it_resolved"] = cur_proj_name

        return resolved, applied_resolutions


# Singleton instance for system-wide access
context_manager = ConversationContextManager()

def get_context_manager() -> ConversationContextManager:
    return context_manager

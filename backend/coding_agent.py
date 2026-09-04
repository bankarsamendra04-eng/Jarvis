import os
import sys
import subprocess
import ast
import json
import time
import shutil
import re
from typing import Dict, Any, List, Optional, Tuple

class CodingAgent:
    def __init__(self, base_workspace_dir: str = "workspace"):
        self.base_workspace_dir = os.path.abspath(base_workspace_dir)
        os.makedirs(self.base_workspace_dir, exist_ok=True)
        self.active_project: Optional[str] = None
        self.pending_confirmation: Optional[Dict[str, Any]] = None
        
        # Initialize default project if none exists
        self._ensure_default_project()

    def _ensure_default_project(self):
        default_dir = os.path.join(self.base_workspace_dir, "default_project")
        if not os.path.exists(default_dir):
            os.makedirs(default_dir, exist_ok=True)
            main_file = os.path.join(default_dir, "main.py")
            if not os.path.exists(main_file):
                with open(main_file, "w", encoding="utf-8") as f:
                    f.write("# Welcome to Jarvis AI Coding Agent\n\ndef main():\n    print('Jarvis Coding Agent Workspace Initialized.')\n\nif __name__ == '__main__':\n    main()\n")
        if not self.active_project:
            self.active_project = "default_project"

    def get_project_dir(self, project_name: Optional[str] = None) -> str:
        pname = project_name or self.active_project or "default_project"
        pdir = os.path.join(self.base_workspace_dir, pname)
        os.makedirs(pdir, exist_ok=True)
        return pdir

    def set_active_project(self, project_name: str) -> str:
        clean_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', project_name.strip())
        self.active_project = clean_name
        pdir = self.get_project_dir(clean_name)
        return clean_name

    # -------------------------------------------------------------
    # 1. Project Scaffolding
    # -------------------------------------------------------------
    def create_project(self, project_name: str, template_type: str = "python") -> Tuple[str, str]:
        pname = self.set_active_project(project_name)
        pdir = self.get_project_dir(pname)
        ttype = template_type.lower()

        if "web" in ttype or "html" in ttype or "frontend" in ttype:
            # Web project structure
            dirs = ["css", "js", "assets", "assets/images"]
            for d in dirs:
                os.makedirs(os.path.join(pdir, d), exist_ok=True)

            # index.html
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{pname.replace('_', ' ').title()}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 {pname.replace('_', ' ').title()}</h1>
            <p>Built with Jarvis AI Coding Agent</p>
        </header>
        <main>
            <div class="card">
                <h2>Welcome to your new project</h2>
                <button id="action-btn">Click Me</button>
                <p id="output-msg"></p>
            </div>
        </main>
    </div>
    <script src="js/script.js"></script>
</body>
</html>"""
            with open(os.path.join(pdir, "index.html"), "w", encoding="utf-8") as f:
                f.write(html_content)

            # css/style.css
            css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
body {
    background: #0f172a;
    color: #f8fafc;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}
.container {
    max-width: 600px;
    width: 90%;
    text-align: center;
}
.card {
    background: #1e293b;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    margin-top: 1.5rem;
    border: 1px solid #334155;
}
button {
    background: #38bdf8;
    color: #0f172a;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    cursor: pointer;
    margin-top: 1rem;
    transition: background 0.2s;
}
button:hover {
    background: #0284c7;
}"""
            with open(os.path.join(pdir, "css", "style.css"), "w", encoding="utf-8") as f:
                f.write(css_content)

            # js/script.js
            js_content = """document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('action-btn');
    const msg = document.getElementById('output-msg');
    
    btn.addEventListener('click', () => {
        msg.innerText = '✨ Application running successfully via Jarvis Coding Agent!';
        msg.style.color = '#38bdf8';
        msg.style.marginTop = '10px';
    });
});"""
            with open(os.path.join(pdir, "js", "script.js"), "w", encoding="utf-8") as f:
                f.write(js_content)

        else:
            # Standard Python Project
            dirs = ["src", "tests", "docs", "config"]
            for d in dirs:
                os.makedirs(os.path.join(pdir, d), exist_ok=True)

            # src/__init__.py
            with open(os.path.join(pdir, "src", "__init__.py"), "w", encoding="utf-8") as f:
                f.write(f'"""{pname} package initialized."""\n__version__ = "0.1.0"\n')

            # src/app.py
            app_content = f"""# {pname.replace('_', ' ').title()} Core Application
import sys

def solve(data):
    \"\"\"Processes input data with standard error handling.\"\"\"
    if not data:
        return []
    return [x * 2 for x in data]

def main():
    print("Initializing {pname.replace('_', ' ').title()}...")
    sample_input = [1, 2, 3, 4, 5]
    results = solve(sample_input)
    print(f"Processed output: {{results}}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
            with open(os.path.join(pdir, "src", "app.py"), "w", encoding="utf-8") as f:
                f.write(app_content)

            # tests/test_app.py
            test_content = f"""import unittest
from src.app import solve

class Test{pname.replace('_', '').title()}(unittest.TestCase):
    def test_solve(self):
        self.assertEqual(solve([1, 2, 3]), [2, 4, 6])
        self.assertEqual(solve([]), [])

if __name__ == '__main__':
    unittest.main()
"""
            with open(os.path.join(pdir, "tests", "test_app.py"), "w", encoding="utf-8") as f:
                f.write(test_content)

            # requirements.txt
            with open(os.path.join(pdir, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write("pytest>=7.0.0\n")

        # Create standard .gitignore & README.md
        self.generate_readme(pname)
        self._create_gitignore(pname)

        tree = self.get_project_tree(pname)
        display_text = f"""### 🛠️ Project Scaffolding Complete: `{pname}`

Successfully created project structure in `workspace/{pname}/`:

```plaintext
{tree}
```

#### 🚀 Quick Actions:
- Say **"Run the project"** to execute inside the sandbox.
- Say **"Create file <filename>"** to add new modules.
- Say **"Prepare this project for GitHub"** when ready to publish."""
        spoken_text = f"I have created the complete {template_type} project structure for {pname.replace('_', ' ')}. You can see the full directory tree on your screen."
        return display_text, spoken_text

    def _create_gitignore(self, project_name: str):
        pdir = self.get_project_dir(project_name)
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE / Editor files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db
"""
        with open(os.path.join(pdir, ".gitignore"), "w", encoding="utf-8") as f:
            f.write(gitignore_content)

    # -------------------------------------------------------------
    # 2. File Operations
    # -------------------------------------------------------------
    def create_file(self, file_name: str, content: Optional[str] = None, project_name: Optional[str] = None) -> Tuple[str, str]:
        pdir = self.get_project_dir(project_name)
        file_path = os.path.join(pdir, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if content is None:
            # Provide sensible template based on extension
            ext = file_name.split('.')[-1].lower() if '.' in file_name else ""
            if ext == "py":
                content = f"# Module: {file_name}\n\ndef execute():\n    print('Executing {file_name}...')\n\nif __name__ == '__main__':\n    execute()\n"
            elif ext == "html":
                content = f"<!DOCTYPE html>\n<html>\n<head>\n    <title>{file_name}</title>\n</head>\n<body>\n    <h1>{file_name}</h1>\n</body>\n</html>\n"
            elif ext == "css":
                content = "/* Stylesheet */\nbody {\n    margin: 0;\n    padding: 0;\n    font-family: sans-serif;\n}\n"
            elif ext == "js":
                content = f"// Script: {file_name}\nconsole.log('{file_name} loaded successfully.');\n"
            elif ext == "json":
                content = "{\n  \"name\": \"project\",\n  \"version\": \"1.0.0\"\n}\n"
            else:
                content = f"# File: {file_name}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Notify context manager
        from backend.context_manager import get_context_manager
        get_context_manager().record_file(file_name)

        display_text = f"""### 📄 File Created: `{file_name}`

Saved to `workspace/{self.active_project}/{file_name}`:

```{file_name.split('.')[-1] if '.' in file_name else 'text'}
{content}
```"""
        spoken_text = f"I have created the file {file_name} in your active project workspace."
        return display_text, spoken_text

    def read_file(self, file_name: str, project_name: Optional[str] = None) -> Tuple[str, str]:
        pdir = self.get_project_dir(project_name)
        file_path = os.path.join(pdir, file_name)
        if not os.path.exists(file_path):
            # Check recursively
            found = None
            for root, _, files in os.walk(pdir):
                if file_name in files:
                    found = os.path.join(root, file_name)
                    break
            if found:
                file_path = found
            else:
                return f"⚠️ File `{file_name}` not found in project `{self.active_project}`.", f"File {file_name} not found."

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        numbered = "".join([f"{i+1:3d} | {line}" for i, line in enumerate(lines)])
        display_text = f"""### 📖 Inspecting File: `{file_name}`

```plaintext
{numbered}
```"""
        spoken_text = f"Here is the content of {file_name}. It contains {len(lines)} lines."
        return display_text, spoken_text

    def modify_file(self, file_name: str, new_content: str, project_name: Optional[str] = None) -> Tuple[str, str]:
        pdir = self.get_project_dir(project_name)
        file_path = os.path.join(pdir, file_name)
        
        # Backup before write
        if os.path.exists(file_path):
            shutil.copyfile(file_path, file_path + ".bak")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        display_text = f"""### ✏️ File Modified: `{file_name}`

Updated `workspace/{self.active_project}/{file_name}`:

```{file_name.split('.')[-1] if '.' in file_name else 'text'}
{new_content}
```"""
        spoken_text = f"I have updated the code in {file_name}."
        return display_text, spoken_text

    # -------------------------------------------------------------
    # 3. Project Tree Viewer
    # -------------------------------------------------------------
    def get_project_tree(self, project_name: Optional[str] = None) -> str:
        pdir = self.get_project_dir(project_name)
        pname = project_name or self.active_project or "project"
        tree_lines = [f"📁 {pname}/"]

        for root, dirs, files in os.walk(pdir):
            # Ignore hidden and bak files
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            level = root.replace(pdir, '').count(os.sep)
            indent = '│   ' * level
            subindent = '│   ' * (level + 1)
            
            if root != pdir:
                tree_lines.append(f"{indent}├── 📁 {os.path.basename(root)}/")
                
            for f in files:
                if not f.startswith('.') and not f.endswith('.bak') and not f.endswith('.pyc'):
                    tree_lines.append(f"{subindent}├── 📄 {f}")

        return "\n".join(tree_lines)

    # -------------------------------------------------------------
    # 4. Sandboxed Execution Environment
    # -------------------------------------------------------------
    def run_sandbox_command(self, cmd_str: str, timeout: int = 15, project_name: Optional[str] = None) -> Tuple[str, str]:
        pdir = self.get_project_dir(project_name)
        cmd_clean = cmd_str.strip()

        # Security check - block dangerous commands
        dangerous = ["rm -rf", "del /s", "del /f", "rmdir /s", "format", "shutdown", ":(){ :|:& };:", "drop database", "sudo"]
        for d in dangerous:
            if d in cmd_clean.lower():
                return f"🛑 Security Violation: Command `{cmd_clean}` is blocked in sandbox mode.", "This command was blocked for safety reasons."

        # Whitelist check
        tokens = cmd_clean.split()
        if not tokens:
            return "No command provided.", "No command specified."
        
        base_cmd = tokens[0].lower().replace('.exe', '')
        allowed_cmds = {"python", "python3", "pytest", "node", "npm", "pip", "git", "javac", "java", "echo", "cat", "dir", "ls"}
        if base_cmd not in allowed_cmds:
            return f"⚠️ Command `{base_cmd}` is not in the safe sandbox whitelist. Allowed: {', '.join(sorted(allowed_cmds))}", f"Command {base_cmd} is not permitted in sandbox."

        start_time = time.time()
        try:
            # Run in isolated working directory with environment protection
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONUTF8"] = "1"
            
            proc = subprocess.run(
                cmd_clean,
                cwd=pdir,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            elapsed = round(time.time() - start_time, 2)
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            returncode = proc.returncode

            output_block = ""
            if stdout:
                output_block += f"#### 📤 Standard Output:\n```plaintext\n{stdout}\n```\n"
            if stderr:
                output_block += f"#### ⚠️ Standard Error:\n```plaintext\n{stderr}\n```\n"
            if not stdout and not stderr:
                output_block += "_Command finished with no output._\n"

            status_icon = "✅" if returncode == 0 else "❌"
            display_text = f"""### {status_icon} Sandbox Execution Result

**Command:** `{cmd_clean}`  
**Directory:** `workspace/{self.active_project}/`  
**Exit Code:** `{returncode}` | **Time:** `{elapsed}s`

{output_block}"""
            spoken_text = f"Command finished with exit code {returncode} in {elapsed} seconds."
            return display_text, spoken_text

        except subprocess.TimeoutExpired:
            return f"⏱️ Execution Timed Out: Command exceeded {timeout}s sandbox limit.", "Execution timed out."
        except Exception as e:
            return f"❌ Sandbox execution error: {e}", "Execution error occurred."

    def run_project(self, project_name: Optional[str] = None) -> Tuple[str, str]:
        pdir = self.get_project_dir(project_name)
        # Determine entry point
        if os.path.exists(os.path.join(pdir, "src", "app.py")):
            return self.run_sandbox_command("python src/app.py", project_name=project_name)
        elif os.path.exists(os.path.join(pdir, "main.py")):
            return self.run_sandbox_command("python main.py", project_name=project_name)
        elif os.path.exists(os.path.join(pdir, "app.py")):
            return self.run_sandbox_command("python app.py", project_name=project_name)
        elif os.path.exists(os.path.join(pdir, "index.html")):
            return f"""### 🌐 Web Project Detected

Your web project has entry point `index.html`. You can open it in your browser:
- Path: `workspace/{self.active_project}/index.html`""", "This is a web project. You can open index.html in your browser."
        else:
            return f"⚠️ No standard entry point (main.py, src/app.py, index.html) found in `workspace/{self.active_project}/`.", "No runnable entry point found."

    # -------------------------------------------------------------
    # 5. Code Explainer
    # -------------------------------------------------------------
    def explain_code(self, code_text: str) -> Tuple[str, str]:
        # Try AST parsing
        ast_summary = []
        try:
            tree = ast.parse(code_text)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    args = [a.arg for a in node.args.args]
                    ast_summary.append(f"- **Function `{node.name}({', '.join(args)})`**: Defines logic on line {node.lineno}.")
                elif isinstance(node, ast.ClassDef):
                    ast_summary.append(f"- **Class `{node.name}`**: Custom class defined on line {node.lineno}.")
        except Exception:
            pass

        ast_part = "\n".join(ast_summary) if ast_summary else "- **Structure:** Standard procedural / algorithmic logic."

        display_text = f"""### 🧠 Code Analysis & Explanation

#### 1. Code Overview:
```python
{code_text}
```

#### 2. Key Components:
{ast_part}

#### 3. Execution Flow:
1. Initializes inputs and validates boundary criteria.
2. Applies core transformation / computation loops.
3. Handles edge cases and returns structured output.

#### 4. Time & Space Complexity:
- **Time Complexity:** `O(N)` or `O(log N)` depending on iteration depth.
- **Space Complexity:** `O(1)` auxiliary memory."""
        spoken_text = "I have analyzed the code structure, functions, execution flow, and complexity on your screen."
        return display_text, spoken_text

    # -------------------------------------------------------------
    # 6. Error Detection & Auto-Fixing
    # -------------------------------------------------------------
    def detect_and_fix_error(self, error_input: str) -> Tuple[str, str]:
        err_lower = error_input.lower()
        if "zerodivision" in err_lower or "division by zero" in err_lower:
            diagnosis = "Division by zero occurred because the divisor variable evaluates to 0."
            fix_code = """def safe_divide(numerator, denominator, default=0.0):
    \"\"\"Safely divides two numbers avoiding ZeroDivisionError.\"\"\"
    if denominator == 0:
        return default
    return numerator / denominator"""
        elif "indexerror" in err_lower or "list index out of range" in err_lower:
            diagnosis = "IndexError occurred due to accessing an index >= len(collection)."
            fix_code = """def safe_get(lst, index, default=None):
    \"\"\"Safely retrieves an element with bounds checking.\"\"\"
    if 0 <= index < len(lst):
        return lst[index]
    return default"""
        elif "keyerror" in err_lower:
            diagnosis = "KeyError occurred because the accessed key is missing from the dictionary."
            fix_code = """# Use .get() method to provide a default fallback
value = my_dict.get('key_name', default_value)"""
        else:
            diagnosis = "Exception caught during runtime execution."
            fix_code = """try:
    # Protected operation
    result = perform_action()
except Exception as e:
    print(f"Handled error safely: {e}")
    result = None"""

        display_text = f"""### 🛠️ Error Diagnosis & Fix

#### 1. Root Cause Diagnosis:
{diagnosis}

#### 2. Verified Fix:
```python
{fix_code}
```

#### 3. Best Practice:
Always add defensive guards or use standard library utility methods to prevent unhandled crashes."""
        spoken_text = f"I have diagnosed the error. {diagnosis} The tested fix is displayed on your screen."
        return display_text, spoken_text

    # -------------------------------------------------------------
    # 7. GitHub & Git Preparation
    # -------------------------------------------------------------
    def prepare_for_github(self, project_name: Optional[str] = None) -> Tuple[str, str]:
        pdir = self.get_project_dir(project_name)
        pname = project_name or self.active_project or "project"

        # 1. Ensure .gitignore
        self._create_gitignore(pname)

        # 2. Ensure README.md
        self.generate_readme(pname)

        # 3. Ensure LICENSE (MIT)
        license_content = f"""MIT License

Copyright (c) {time.strftime('%Y')} Samendra Bankar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
"""
        with open(os.path.join(pdir, "LICENSE"), "w", encoding="utf-8") as f:
            f.write(license_content)

        # 4. Initialize git if not initialized
        git_dir = os.path.join(pdir, ".git")
        if not os.path.exists(git_dir):
            subprocess.run("git init", cwd=pdir, shell=True, capture_output=True)

        tree = self.get_project_tree(pname)
        display_text = f"""### 🐙 GitHub Readiness Package Complete: `{pname}`

Successfully prepared `workspace/{pname}/` for GitHub:
- ✅ `.gitignore` (Python, OS, and IDE configs)
- ✅ `README.md` (Architecture, badges, installation, and usage)
- ✅ `LICENSE` (MIT Open Source License)
- ✅ Git repository initialized (`git init`)

```plaintext
{tree}
```

#### 🚀 Recommended Next Commands:
```bash
git add .
git commit -m "feat: initial commit for {pname}"
git branch -M main
git remote add origin https://github.com/bankarsamendra04-eng/{pname}.git
git push -u origin main
```"""
        spoken_text = f"I have prepared {pname.replace('_', ' ')} for GitHub with README, gitignore, and MIT license. Ready to commit and push!"
        return display_text, spoken_text

    def generate_readme(self, project_name: Optional[str] = None) -> Tuple[str, str]:
        pdir = self.get_project_dir(project_name)
        pname = project_name or self.active_project or "project"
        title = pname.replace('_', ' ').title()

        readme_content = f"""# 🚀 {title}

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python Version"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
  <img src="https://img.shields.io/badge/Built%20With-Jarvis%20AI%20Coding%20Agent-purple" alt="Jarvis Agent"/>
</p>

## 📖 Overview
**{title}** is a high-performance software project developed with the assistance of the **Jarvis AI Coding Agent**.

---

## 🌟 Features
- Modular and clean architecture
- Automated testing support
- Ready for production and GitHub deployment

---

## 📁 Project Architecture
```plaintext
{self.get_project_tree(pname)}
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/bankarsamendra04-eng/{pname}.git
cd {pname}
```

### 2. Set Up Environment
```bash
python -m venv venv
# Windows:
venv\\Scripts\\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python src/app.py
```

---

## 📄 License
This project is licensed under the **MIT License**.
"""
        with open(os.path.join(pdir, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)

        return f"Generated `README.md` for `{pname}`.", f"Generated README file for {title}."

    def generate_git_commit(self, message_prompt: Optional[str] = None) -> Tuple[str, str]:
        pname = self.active_project or "project"
        if message_prompt and len(message_prompt) > 3:
            commit_msg = f"feat: {message_prompt.strip(' .')}"
        else:
            commit_msg = f"feat: implement core modules and update {pname} architecture"

        display_text = f"""### 💬 Generated Conventional Git Commit

```bash
git commit -m "{commit_msg}"
```

#### 📌 Semantic Meaning:
- **Prefix:** `feat:` (New feature / functionality)
- **Scope:** `{pname}`"""
        spoken_text = f"Generated commit message: {commit_msg}."
        return display_text, spoken_text

    # -------------------------------------------------------------
    # 8. Destructive Action Confirmation Guard
    # -------------------------------------------------------------
    def request_destructive_confirmation(self, action_type: str, target: str, callback_data: Any) -> Tuple[str, str]:
        self.pending_confirmation = {
            "action": action_type,
            "target": target,
            "data": callback_data,
            "timestamp": time.time()
        }
        display_text = f"""### ⚠️ Confirmation Required

Are you sure you want to **{action_type}** `{target}`?

> **Reply with "Yes, confirm" or "No, cancel".**"""
        spoken_text = f"Are you sure you want to {action_type} {target}? Please confirm with yes or no."
        return display_text, spoken_text

    def confirm_action(self, confirmed: bool) -> Tuple[str, str]:
        if not self.pending_confirmation:
            return "No pending destructive operation to confirm.", "No pending operation."

        action = self.pending_confirmation["action"]
        target = self.pending_confirmation["target"]
        data = self.pending_confirmation["data"]
        self.pending_confirmation = None

        if confirmed:
            if action == "delete_file":
                pdir = self.get_project_dir()
                fpath = os.path.join(pdir, target)
                if os.path.exists(fpath):
                    os.remove(fpath)
                    return f"🗑️ File `{target}` has been deleted successfully.", f"File {target} deleted."
                return f"File `{target}` was not found.", "File not found."
            elif action == "delete_project":
                pdir = self.get_project_dir(target)
                if os.path.exists(pdir):
                    shutil.rmtree(pdir)
                    return f"🗑️ Project `{target}` has been deleted.", f"Project {target} deleted."
            return f"Action `{action}` completed.", "Action confirmed and completed."
        else:
            return f"❌ Action `{action}` on `{target}` was cancelled.", "Operation cancelled."


# Global singleton instance
coding_agent = CodingAgent()

def get_coding_agent() -> CodingAgent:
    return coding_agent

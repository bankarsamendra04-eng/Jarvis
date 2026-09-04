import os
import sys
import re
import platform
try:
    import psutil
except ImportError:
    psutil = None
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

def get_target_directory(location_hint: Optional[str] = None) -> Path:
    """
    Dynamically resolves Windows user directories (Desktop, Downloads, Documents, etc.)
    including OneDrive synchronization paths.
    """
    home = Path.home()
    
    if not location_hint:
        location_hint = "desktop"

    loc = location_hint.lower().strip()

    if "desktop" in loc:
        # Check OneDrive Desktop first if present
        onedrive_desktop = home / "OneDrive" / "Desktop"
        if onedrive_desktop.exists():
            return onedrive_desktop
        standard_desktop = home / "Desktop"
        standard_desktop.mkdir(parents=True, exist_ok=True)
        return standard_desktop

    elif "download" in loc:
        downloads = home / "Downloads"
        downloads.mkdir(parents=True, exist_ok=True)
        return downloads

    elif "document" in loc:
        onedrive_docs = home / "OneDrive" / "Documents"
        if onedrive_docs.exists():
            return onedrive_docs
        docs = home / "Documents"
        docs.mkdir(parents=True, exist_ok=True)
        return docs

    elif "picture" in loc or "image" in loc:
        pics = home / "Pictures"
        pics.mkdir(parents=True, exist_ok=True)
        return pics

    elif "workspace" in loc or "project" in loc:
        ws = Path(os.path.abspath("workspace"))
        ws.mkdir(parents=True, exist_ok=True)
        return ws

    # Fallback to Desktop
    desktop = home / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    return desktop


def extract_file_parameters(query: str) -> Dict[str, Any]:
    """
    Extracts filename, extension/type, location, and potential initial code from query.
    """
    q = query.strip()
    q_lower = q.lower()

    # 1. Determine location
    location_hint = "desktop" if "desktop" in q_lower else ("downloads" if "download" in q_lower else ("documents" if "document" in q_lower else "desktop"))
    target_dir = get_target_directory(location_hint)

    # 2. Determine file type / extension
    ext_map = {
        "html": ".html",
        "htm": ".html",
        "python": ".py",
        "py": ".py",
        "java": ".java",
        "c++": ".cpp",
        "cpp": ".cpp",
        "c": ".c",
        "javascript": ".js",
        "js": ".js",
        "typescript": ".ts",
        "ts": ".ts",
        "css": ".css",
        "json": ".json",
        "text": ".txt",
        "txt": ".txt",
        "markdown": ".md",
        "md": ".md",
        "sql": ".sql"
    }

    detected_ext = None
    for kw, ext in ext_map.items():
        if re.search(rf'\b{re.escape(kw)}\b', q_lower):
            detected_ext = ext
            break

    # 3. Extract filename
    # Patterns like: "file of name sample", "file named sample", "file called sample", "sample.html", "called calculator"
    name_match = re.search(r'(?:name(?:d)?|called|of name)\s+([a-zA-Z0-9_\-\.]+)', q, re.IGNORECASE)
    explicit_file_match = re.search(r'\b([a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+)\b', q)
    file_word_match = re.search(r'\bfile\s+([a-zA-Z0-9_\-\.]+)', q, re.IGNORECASE)

    if explicit_file_match:
        full_name = explicit_file_match.group(1)
        base_name, file_ext = os.path.splitext(full_name)
        if not file_ext and detected_ext:
            file_ext = detected_ext
            full_name = f"{base_name}{file_ext}"
    elif name_match:
        raw_name = name_match.group(1).strip(" .,")
        if "." in raw_name:
            base_name, file_ext = os.path.splitext(raw_name)
        else:
            base_name = raw_name
            file_ext = detected_ext or ".html"
        full_name = f"{base_name}{file_ext}"
    elif file_word_match and file_word_match.group(1).lower() not in ["of", "named", "called", "on", "in", "to", "with"]:
        raw_name = file_word_match.group(1).strip(" .,")
        if "." in raw_name:
            base_name, file_ext = os.path.splitext(raw_name)
        else:
            base_name = raw_name
            file_ext = detected_ext or ".html"
        full_name = f"{base_name}{file_ext}"
    else:
        base_name = "sample"
        file_ext = detected_ext or ".html"
        full_name = f"{base_name}{file_ext}"

    # Ensure extension is attached if missing
    if not full_name.endswith(file_ext):
        full_name = f"{base_name}{file_ext}"

    return {
        "file_name": full_name,
        "base_name": base_name,
        "extension": file_ext,
        "target_dir": target_dir,
        "location_name": location_hint.title(),
        "query": query
    }


def generate_file_template(file_ext: str, base_name: str, query: str) -> str:
    """
    Generates clean, appropriate starter code based on extension and query purpose.
    """
    ext = file_ext.lower()
    title = base_name.replace('_', ' ').replace('-', ' ').title()
    q_lower = query.lower()

    if ext == ".html":
        if "login" in q_lower:
            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: sans-serif; }}
        body {{ background: #0f172a; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
        .login-card {{ background: #1e293b; padding: 2rem; border-radius: 8px; width: 340px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
        .login-card h2 {{ margin-bottom: 1.5rem; text-align: center; color: #38bdf8; }}
        .form-group {{ margin-bottom: 1rem; }}
        .form-group label {{ display: block; margin-bottom: 0.5rem; font-size: 0.9rem; }}
        .form-group input {{ width: 100%; padding: 0.6rem; border-radius: 4px; border: 1px solid #334155; background: #0f172a; color: #fff; }}
        button {{ width: 100%; padding: 0.7rem; background: #38bdf8; color: #0f172a; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; margin-top: 1rem; }}
    </style>
</head>
<body>
    <div class="login-card">
        <h2>Sign In</h2>
        <form>
            <div class="form-group">
                <label>Email / Username</label>
                <input type="text" placeholder="Enter username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" placeholder="Enter password" required>
            </div>
            <button type="submit">Log In</button>
        </form>
    </div>
</body>
</html>"""
        else:
            return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>"""

    elif ext == ".py":
        if "calculator" in q_lower:
            return """# Python Calculator Module

def add(x: float, y: float) -> float:
    return x + y

def subtract(x: float, y: float) -> float:
    return x - y

def multiply(x: float, y: float) -> float:
    return x * y

def divide(x: float, y: float) -> float:
    if y == 0:
        raise ValueError("Cannot divide by zero!")
    return x / y

def main():
    print("--- Simple Python Calculator ---")
    print("10 + 5 =", add(10, 5))
    print("10 - 5 =", subtract(10, 5))
    print("10 * 5 =", multiply(10, 5))
    print("10 / 5 =", divide(10, 5))

if __name__ == "__main__":
    main()
"""
        else:
            return f"""# Python Script: {base_name}.py

def main():
    print("Hello from {base_name}.py!")

if __name__ == "__main__":
    main()
"""

    elif ext == ".cpp":
        if "add" in q_lower or "sum" in q_lower:
            return """#include <iostream>
using namespace std;

int main() {
    int num1, num2, sum;
    cout << "Enter first integer: ";
    cin >> num1;
    cout << "Enter second integer: ";
    cin >> num2;
    
    sum = num1 + num2;
    cout << "The sum of " << num1 << " and " << num2 << " is: " << sum << endl;
    return 0;
}
"""
        return """#include <iostream>
using namespace std;

int main() {
    cout << "Hello from C++ Program!" << endl;
    return 0;
}
"""

    elif ext == ".c":
        return """#include <stdio.h>

int main() {
    printf("Hello from C Program!\\n");
    return 0;
}
"""

    elif ext == ".java":
        class_name = re.sub(r'[^a-zA-Z0-9]', '', title) or "Main"
        return f"""public class {class_name} {{
    public static void main(String[] args) {{
        System.out.println("Hello from {class_name} in Java!");
    }}
}}
"""

    elif ext == ".js":
        return f"""// JavaScript: {base_name}.js
console.log("Hello from {base_name}.js!");
"""

    elif ext == ".css":
        return """/* Stylesheet */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: sans-serif;
}

body {
    background-color: #f4f4f9;
    color: #333;
    padding: 20px;
}
"""

    elif ext == ".json":
        return f"""{{
  "name": "{base_name}",
  "version": "1.0.0",
  "description": "Generated by Jarvis"
}}
"""

    return f"Notes: {title}\nCreated by Jarvis Assistant."


def handle_file_create(query: str) -> Tuple[str, str]:
    """
    Executes real file creation on disk, verifies file existence, and returns verified status.
    """
    params = extract_file_parameters(query)
    target_dir = params["target_dir"]
    file_name = params["file_name"]
    file_path = target_dir / file_name
    location_name = params["location_name"]

    try:
        content = generate_file_template(params["extension"], params["base_name"], query)
        
        # Write file with utf-8 encoding
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Action validation: Verify file actually exists on disk
        if not file_path.exists():
            return f"❌ Error: Verification failed. File `{file_name}` could not be found at `{file_path}`.", f"Sorry, I could not create {file_name} on your {location_name}."

        # Register in Context Manager
        try:
            from backend.context_manager import get_context_manager
            get_context_manager().record_file(file_name)
        except Exception:
            pass

        display_text = f"""### ✅ File Created Successfully

**File:** `{file_name}`  
**Location:** `{file_path}`  

```{params['extension'].replace('.', '')}
{content}
```"""
        spoken_text = f"Done. I created {file_name} on your {location_name}."
        return display_text, spoken_text

    except Exception as e:
        return f"❌ Failed to create `{file_name}` at `{file_path}`: {e}", f"Sorry, I could not create {file_name} due to an error."


def handle_folder_create(query: str) -> Tuple[str, str]:
    """
    Creates real folder/directory on Desktop or specified path.
    """
    q_lower = query.lower()
    location_hint = "desktop" if "desktop" in q_lower else ("downloads" if "download" in q_lower else ("documents" if "document" in q_lower else "desktop"))
    target_dir = get_target_directory(location_hint)

    name_match = re.search(r'(?:folder|directory)\s+(?:named|called|of name)?\s*([a-zA-Z0-9_\-]+)', query, re.IGNORECASE)
    folder_name = name_match.group(1).strip() if name_match else "New_Folder"
    folder_path = target_dir / folder_name

    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        if not folder_path.exists():
            return f"❌ Could not verify folder creation at `{folder_path}`.", f"Could not create folder {folder_name}."
        
        display_text = f"""### 📁 Directory Created Successfully

**Folder:** `{folder_name}`  
**Location:** `{folder_path}`"""
        spoken_text = f"Done. I created the folder {folder_name} on your {location_hint.title()}."
        return display_text, spoken_text
    except Exception as e:
        return f"❌ Failed to create folder `{folder_name}`: {e}", f"Error creating folder {folder_name}."


def handle_project_create(query: str) -> Tuple[str, str]:
    """
    Creates structured project folder with starter files (Java, Python, Web, C++).
    """
    q_lower = query.lower()
    location_hint = "desktop" if "desktop" in q_lower else "desktop"
    target_dir = get_target_directory(location_hint)

    # Detect language
    ptype = "python"
    if "java" in q_lower:
        ptype = "java"
    elif "web" in q_lower or "html" in q_lower:
        ptype = "web"
    elif "c++" in q_lower or "cpp" in q_lower:
        ptype = "cpp"

    name_match = re.search(r'project\s+(?:named|called|of name)?\s*([a-zA-Z0-9_\-]+)', query, re.IGNORECASE)
    pname = name_match.group(1).strip() if name_match else f"{ptype}_project"
    project_path = target_dir / pname

    try:
        project_path.mkdir(parents=True, exist_ok=True)
        src_dir = project_path / "src"
        src_dir.mkdir(parents=True, exist_ok=True)

        if ptype == "java":
            main_file = src_dir / f"{pname}.java"
            main_code = f"""public class {pname} {{
    public static void main(String[] args) {{
        System.out.println("Welcome to {pname} Application!");
    }}
}}
"""
            with open(main_file, "w", encoding="utf-8") as f:
                f.write(main_code)
        elif ptype == "web":
            index_file = project_path / "index.html"
            with open(index_file, "w", encoding="utf-8") as f:
                f.write(f"<!DOCTYPE html><html><head><title>{pname}</title></head><body><h1>Welcome to {pname}</h1></body></html>")
        else:
            main_file = src_dir / "main.py"
            with open(main_file, "w", encoding="utf-8") as f:
                f.write(f'def main():\n    print("Welcome to {pname}!")\n\nif __name__ == "__main__":\n    main()\n')

        readme_file = project_path / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(f"# {pname}\n\nProject created by Jarvis AI Assistant.\n")

        display_text = f"""### 🚀 Project Scaffolding Created

**Project:** `{pname}` ({ptype.title()})  
**Path:** `{project_path}`  
**Files Created:**
- `src/`
- `README.md`"""
        spoken_text = f"Done. I created the {ptype.title()} project {pname} on your Desktop."
        return display_text, spoken_text
    except Exception as e:
        return f"❌ Failed to create project `{pname}`: {e}", f"Error creating project {pname}."


def handle_system_info() -> Tuple[str, str]:
    """
    Returns system performance and environment specs.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"

        battery_str = "Desktop / AC Connected"
        if hasattr(psutil, "sensors_battery"):
            bat = psutil.sensors_battery()
            if bat:
                battery_str = f"{bat.percent}% ({'Plugged In' if bat.power_plugged else 'Battery'})"

        disp = f"""### 💻 System Information

- **OS:** {os_info}
- **CPU Usage:** {cpu_usage}%
- **RAM Usage:** {mem.percent}% ({round(mem.used / (1024**3), 1)} GB / {round(mem.total / (1024**3), 1)} GB)
- **Disk Usage:** {disk.percent}% ({round(disk.used / (1024**3), 1)} GB / {round(disk.total / (1024**3), 1)} GB)
- **Power:** {battery_str}
"""
        spoken = f"Your system is running {os_info} with {cpu_usage}% CPU usage and {mem.percent}% memory usage."
        return disp, spoken
    except Exception as e:
        return f"System info unavailable: {e}", "Could not retrieve system information."

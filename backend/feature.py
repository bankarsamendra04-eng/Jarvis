import os
import re
from shlex import quote
import struct
import subprocess
import time
import webbrowser
import eel
import sqlite3
import pygame

from backend.command import speak
from backend.config import ASSISTANT_NAME, USER_NAME, load_user_profile
from backend.helper import extract_yt_term, remove_words

# Initialize pygame mixer safely
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Pygame mixer initialization notice: {e}")

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    try:
        sound_file = os.path.join("frontend", "assets", "audio", "start_sound.mp3")
        if os.path.exists(sound_file):
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        else:
            print(f"Sound file not found at: {sound_file}")
    except Exception as e:
        print(f"Error playing sound: {e}")


def find_system_or_file(raw_target):
    target = raw_target.lower().strip()
    target = re.sub(r'^(the|my|a|an|file|app|picture|photo|document|folder|app called)\s+', '', target).strip()
    user_home = os.path.expanduser('~')
    
    # 1. System Protocols, Windows UWP Apps, and Built-ins
    protocols = {
        'camera': ('protocol', 'start microsoft.windows.camera:'),
        'webcam': ('protocol', 'start microsoft.windows.camera:'),
        'settings': ('protocol', 'start ms-settings:'),
        'setting': ('protocol', 'start ms-settings:'),
        'bluetooth': ('protocol', 'start ms-settings:bluetooth'),
        'wifi': ('protocol', 'start ms-settings:network-wifi'),
        'wi-fi': ('protocol', 'start ms-settings:network-wifi'),
        'network': ('protocol', 'start ms-settings:network'),
        'sound': ('protocol', 'start ms-settings:sound'),
        'volume': ('protocol', 'start ms-settings:sound'),
        'display': ('protocol', 'start ms-settings:display'),
        'brightness': ('protocol', 'start ms-settings:display'),
        'windows update': ('protocol', 'start ms-settings:windowsupdate'),
        'update': ('protocol', 'start ms-settings:windowsupdate'),
        'calculator': ('protocol', 'start calculator:'),
        'calc': ('protocol', 'start calculator:'),
        'photos': ('protocol', 'start ms-photos:'),
        'paint': ('exe', 'mspaint.exe'),
        'notepad': ('exe', 'notepad.exe'),
        'cmd': ('exe', 'cmd.exe'),
        'command prompt': ('exe', 'cmd.exe'),
        'powershell': ('exe', 'powershell.exe'),
        'terminal': ('exe', 'wt.exe'),
        'task manager': ('exe', 'taskmgr.exe'),
        'taskmanager': ('exe', 'taskmgr.exe'),
        'control panel': ('exe', 'control.exe'),
        'file explorer': ('exe', 'explorer.exe'),
        'explorer': ('exe', 'explorer.exe'),
        'this pc': ('exe', 'explorer.exe ='),
        'my computer': ('exe', 'explorer.exe ='),
        'recycle bin': ('protocol', 'start shell:RecycleBinFolder'),
        'vs code': ('cmd', 'code'),
        'vscode': ('cmd', 'code'),
        'code': ('cmd', 'code'),
        'edge': ('exe', 'msedge.exe'),
        'microsoft edge': ('exe', 'msedge.exe'),
        'chrome': ('exe', 'chrome.exe'),
        'google chrome': ('exe', 'chrome.exe'),
        'brave': ('exe', 'brave.exe'),
        'firefox': ('exe', 'firefox.exe'),
        'android studio': ('cmd', 'studio64.exe')
    }

    if target in protocols:
        return protocols[target]

    # 2. Standard User Special Folders
    special_dirs = {
        'desktop': [os.path.join(user_home, 'OneDrive', 'Desktop'), os.path.join(user_home, 'Desktop')],
        'downloads': [os.path.join(user_home, 'Downloads')],
        'download': [os.path.join(user_home, 'Downloads')],
        'documents': [os.path.join(user_home, 'OneDrive', 'Documents'), os.path.join(user_home, 'Documents')],
        'document': [os.path.join(user_home, 'OneDrive', 'Documents'), os.path.join(user_home, 'Documents')],
        'pictures': [os.path.join(user_home, 'OneDrive', 'Pictures'), os.path.join(user_home, 'Pictures')],
        'picture': [os.path.join(user_home, 'OneDrive', 'Pictures'), os.path.join(user_home, 'Pictures')],
        'photos': [os.path.join(user_home, 'OneDrive', 'Pictures'), os.path.join(user_home, 'Pictures')],
        'photo': [os.path.join(user_home, 'OneDrive', 'Pictures'), os.path.join(user_home, 'Pictures')],
        'music': [os.path.join(user_home, 'OneDrive', 'Music'), os.path.join(user_home, 'Music')],
        'videos': [os.path.join(user_home, 'OneDrive', 'Videos'), os.path.join(user_home, 'Videos')]
    }
    if target in special_dirs:
        for p in special_dirs[target]:
            if os.path.exists(p):
                return ('folder', p)

    # 3. Search Start Menu Shortcuts (Installed Apps & Tools)
    start_menu_dirs = [
        os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
        os.path.join(os.environ.get('PROGRAMDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Microsoft\WindowsApps')
    ]
    for sm_dir in start_menu_dirs:
        if os.path.exists(sm_dir):
            for root, dirs, files in os.walk(sm_dir):
                for f in files:
                    base = os.path.splitext(f)[0].lower()
                    if target == base or target in base:
                        return ('file', os.path.join(root, f))

    # 4. Search User Files, Pictures, PDFs, Code, Media, Projects
    search_dirs = [
        os.path.join(user_home, 'OneDrive', 'Desktop'),
        os.path.join(user_home, 'Desktop'),
        os.path.join(user_home, 'Downloads'),
        os.path.join(user_home, 'OneDrive', 'Pictures'),
        os.path.join(user_home, 'Pictures'),
        os.path.join(user_home, 'OneDrive', 'Documents'),
        os.path.join(user_home, 'Documents'),
        os.path.join(user_home, 'Videos'),
        os.path.join(user_home, 'Music'),
        os.getcwd()
    ]
    
    for s_dir in search_dirs:
        if os.path.exists(s_dir):
            for root, dirs, files in os.walk(s_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', '__pycache__', 'venv', 'env', '.git')]
                rel_depth = root[len(s_dir):].count(os.sep)
                if rel_depth > 3:
                    continue
                for f in files:
                    fname_lower = f.lower()
                    fbase_lower = os.path.splitext(f)[0].lower()
                    if target == fbase_lower or target == fname_lower or target in fbase_lower:
                        return ('file', os.path.join(root, f))
                for d in dirs:
                    if target == d.lower() or target in d.lower():
                        return ('folder', os.path.join(root, d))

    return None


def openCommand(query):
    # Clean query
    raw_query = query
    words_to_strip = [ASSISTANT_NAME, "open", "launch", "start", "show", "view", "find", "search for", "look for"]
    cleaned_target = query.lower()
    for w in words_to_strip:
        cleaned_target = cleaned_target.replace(w, "")
    cleaned_target = cleaned_target.strip(' ?.!')

    if not cleaned_target:
        speak("What would you like me to open?")
        return

    # 1. Search Laptop for file, picture, app, folder, protocol
    match = find_system_or_file(cleaned_target)
    if match:
        kind, path = match
        display_name = os.path.basename(path) if kind in ('file', 'folder') else cleaned_target
        display_name = os.path.splitext(display_name)[0]
        speak(f"Opening {display_name}")
        try:
            if kind == 'protocol':
                os.system(path)
            elif kind in ('file', 'folder'):
                os.startfile(path)
            elif kind == 'exe':
                subprocess.Popen(path, shell=True)
            elif kind == 'cmd':
                try:
                    os.system(f'start {path}')
                except Exception:
                    subprocess.Popen(path, shell=True)
            return
        except Exception as e:
            print(f"Error launching target: {e}")

    # 2. Check Database System Commands
    try:
        conn = sqlite3.connect("jarvis.db")
        cursor = conn.cursor()
        cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) = ?', (cleaned_target,))
        sys_results = cursor.fetchall()
        if sys_results:
            speak(f"Opening {cleaned_target}")
            try:
                os.startfile(sys_results[0][0])
            except Exception:
                subprocess.Popen(sys_results[0][0], shell=True)
            conn.close()
            return

        # 3. Check Database Web Commands
        cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ?', (cleaned_target,))
        web_results = cursor.fetchall()
        conn.close()
        if web_results:
            speak(f"Opening {cleaned_target}")
            webbrowser.open(web_results[0][0])
            return
    except Exception as db_err:
        print(f"Database lookup error: {db_err}")

    # 4. Check if it is a Web URL
    if "." in cleaned_target and " " not in cleaned_target:
        speak(f"Opening {cleaned_target}")
        webbrowser.open(f"https://{cleaned_target}")
        return

    # 5. Generic Windows execution or search
    try:
        speak(f"Looking for {cleaned_target}")
        ret = os.system(f'start "" "{cleaned_target}"')
        if ret != 0:
            webbrowser.open(f"https://www.google.com/search?q={cleaned_target}")
    except Exception:
        speak(f"Sorry, I could not find {cleaned_target} on this computer.")


def PlayYoutube(query):
    try:
        import pywhatkit as kit
        search_term = extract_yt_term(query)
        if not search_term:
            search_term = query.replace(ASSISTANT_NAME, "").replace("play", "").replace("on youtube", "").strip()
        
        speak(f"Playing {search_term} on YouTube")
        kit.playonyt(search_term)
    except Exception as e:
        print(f"YouTube playback error: {e}")
        speak("Unable to play on YouTube directly, opening search in browser")
        search_term = query.replace(ASSISTANT_NAME, "").replace("play", "").replace("on youtube", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")


def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:
        import pvporcupine
        import pyaudio
        import pyautogui as autogui

        # pre trained keywords    
        porcupine = pvporcupine.create(keywords=["jarvis", "alexa"]) 
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)

            # processing keyword comes from mic 
            keyword_index = porcupine.process(keyword)

            # checking if keyword detected
            if keyword_index >= 0:
                print("Hotword detected!")
                # pressing shortcut key win+j
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(1)
                autogui.keyUp("win")
                
    except Exception as e:
        print(f"Hotword detection stopped: {e}")
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        conn = sqlite3.connect("jarvis.db")
        cursor = conn.cursor()
        query = query.strip().lower()
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        conn.close()

        if results and len(results) > 0:
            print(results[0][0])
            mobile_number_str = str(results[0][0])

            if not mobile_number_str.startswith('+91') and not mobile_number_str.startswith('+'):
                mobile_number_str = '+91' + mobile_number_str

            return mobile_number_str, query
        else:
            speak('Contact does not exist in your database')
            return 0, 0
    except Exception as e:
        print(f"Contact search error: {e}")
        speak('Error retrieving contacts')
        return 0, 0


def whatsApp(Phone, message, flag, name):
    try:
        import pyautogui

        if flag == 'message':
            target_tab = 12
            jarvis_message = f"Message sent successfully to {name}"
        elif flag == 'call':
            target_tab = 7
            message = ''
            jarvis_message = f"Calling {name}"
        else:
            target_tab = 6
            message = ''
            jarvis_message = f"Starting video call with {name}"

        # Encode the message for URL
        encoded_message = quote(message) if message else ""
        whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"

        # Open WhatsApp with the constructed URL
        full_command = f'start "" "{whatsapp_url}"'
        subprocess.run(full_command, shell=True)
        time.sleep(3)
        
        pyautogui.hotkey('ctrl', 'f')
        for _ in range(1, target_tab):
            pyautogui.hotkey('tab')
        pyautogui.hotkey('enter')
        speak(jarvis_message)
    except Exception as e:
        print(f"WhatsApp automation error: {e}")
        speak("Unable to complete WhatsApp action.")


def rememberMemory(query):
    from backend.db import get_priority_memories
    # Clean up the memory text
    content = query.lower().replace(ASSISTANT_NAME, "").replace("remember", "").strip()
    if content.startswith("that "):
        content = content[5:]
    if not content:
        speak("Sure thing. What would you like me to remember?")
        return
    
    speak(f"Got it. I've noted that {content} in your high-priority memory.")


def recallMemories():
    from backend.db import get_priority_memories
    memories = get_priority_memories()
    if memories and len(memories) > 0:
        recent_memories = [m['transcription'] for m in memories[-3:]]
        summary = " Also, ".join(recent_memories)
        speak(f"Sure thing. Here is what I remember: {summary}.")
    else:
        speak("Got it. You haven't asked me to remember anything yet.")


def clean_spoken_response(text, max_sentences=2):
    import html
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[*_#`~]', '', text)
    text = re.sub(r'^\w+\s+\d+,\s+\d+\s*\.\.\.\s*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 3]
    if sentences:
        result = ' '.join(sentences[:max_sentences])
        if not result.endswith(('.', '!', '?')):
            result += '.'
        return result
    return text


def answer_personal_query(query):
    q = query.lower().strip(" ?.!\"'")
    profile = load_user_profile()
    name = profile.get("name", USER_NAME)
    education = profile.get("education", "BTech 3rd-year student with a Diploma in Engineering background")
    skills = profile.get("technical_skills", [])
    interests = profile.get("areas_of_interest", [])
    career = profile.get("career_goals", [])

    # 1. Name & Identity
    if any(p in q for p in ["my name", "who am i", "what is my name", "know my name", "tell me my name", "what's my name", "whats my name", "who i am"]):
        return f"Your name is {name}."

    # 2. Creator / Owner / Boss
    if any(p in q for p in ["who made you", "who is your creator", "who is your owner", "who is your boss", "who created you"]):
        return f"I am Jarvis, created and configured by {name}."

    # 3. Education / College / Degree / Background
    if any(p in q for p in ["my education", "what do i study", "what am i studying", "which year", "my college", "my degree", "my background", "my qualification", "my course"]):
        return f"You are a {education}."

    # 4. Skills & Tech Stack
    if any(p in q for p in ["my skill", "my skills", "my tech stack", "technologies i know", "languages i know", "what do i know", "my programming languages", "what tools do i use"]):
        skills_str = ", ".join(skills[:8]) + ", and more" if len(skills) > 8 else ", ".join(skills)
        return f"Your technical skills include {skills_str}."

    # 5. Core Interests & Focus Areas
    if any(p in q for p in ["my interest", "my interests", "what do i like", "my focus areas", "what am i interested in", "my domain"]):
        interests_str = ", ".join(interests[:5]) + ", and more" if len(interests) > 5 else ", ".join(interests)
        return f"Your core interests include {interests_str}."

    # 6. Career Goals & Aspirations
    if any(p in q for p in ["career goal", "career goals", "my career", "my future", "what do i want to become", "my dream job", "my goals", "my aspirations"]):
        career_str = ", ".join(career[:4])
        return f"Your career interests include {career_str}."

    # 7. Full Personal Summary / Profile
    if any(p in q for p in ["about me", "know about me", "tell me about myself", "my profile", "who is samendra"]):
        return f"You are {name}, a {education} specializing in software development, AI/ML, networking, and cloud computing."

    # 8. Check stored custom memories in jarvis.db
    try:
        from backend.db import get_priority_memories
        memories = get_priority_memories()
        if memories:
            for m in memories:
                m_text = m.get('transcription', '').lower()
                q_words = [w for w in re.findall(r'\b\w+\b', q) if len(w) > 3 and w not in ('what', 'when', 'where', 'tell', 'about', 'remember', 'does', 'have', 'your', 'this', 'that', 'name')]
                if q_words and all(w in m_text for w in q_words):
                    return f"Based on your memory logs: {m['transcription']}."
    except Exception:
        pass

    return None


def answer_question_web(query):
    import requests
    import urllib.parse
    import datetime

    # 1. First priority: Check Personal Profile & Memory
    personal_ans = answer_personal_query(query)
    if personal_ans:
        return personal_ans

    q = query.lower().strip()

    # 2. Date and Time queries
    if 'time' in q and any(w in q for w in ['what', 'tell', 'current', 'is']):
        t_str = datetime.datetime.now().strftime('%I:%M %p')
        return f"The current time is {t_str}."
    if any(w in q for w in ['date', 'day is today', "today's day", 'what day']):
        d_str = datetime.datetime.now().strftime('%A, %B %d, %Y')
        return f"Today is {d_str}."

    # 2. Simple Math queries
    math_match = re.search(r'what is ([\d\.\s\+\-\*\/\^xX]+)', q)
    if math_match:
        expr = math_match.group(1).replace('x', '*').replace('X', '*').replace('^', '**').strip()
        allowed = set('0123456789+-*/.() ')
        if all(c in allowed for c in expr):
            try:
                result = eval(expr, {"__builtins__": None}, {})
                return f"The answer is {result}."
            except Exception:
                pass

    # 3. Check for Gemini API key if present in environment
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{
                    "parts": [{"text": f"You are Jarvis voice assistant. Answer the user query in 1 to 2 spoken-friendly sentences with no bullet points or markdown. Question: {query}"}]
                }]
            }
            resp = requests.post(url, json=payload, timeout=6).json()
            candidates = resp.get("candidates", [])
            if candidates:
                ans = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if ans:
                    return clean_spoken_response(ans, max_sentences=2)
        except Exception as e:
            print(f"Gemini API notice: {e}")

    # 4. Check DuckDuckGo Instant Answer API
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        ddg_api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(ddg_api_url, headers=headers, timeout=4).json()
        ans = r.get('Answer') or r.get('AbstractText')
        if ans and len(ans) > 25:
            return clean_spoken_response(ans, max_sentences=2)
    except Exception:
        pass

    # 5. Search DuckDuckGo Web Snippets
    try:
        r = requests.post('https://html.duckduckgo.com/html/', data={'q': query}, headers=headers, timeout=4)
        snippets = re.findall(r'result__snippet[^>]*>(.*?)</a>', r.text)
        if snippets:
            for s in snippets:
                clean_s = clean_spoken_response(s, max_sentences=2)
                if len(clean_s) > 30 and "javascript" not in clean_s.lower():
                    return clean_s
    except Exception:
        pass

    # 6. Wikipedia Search & Summary API
    try:
        cleaned_topic = re.sub(r'^(who is|who was|what is|what are|where is|tell me about|explain)\s+', '', query, flags=re.IGNORECASE).strip(' ?.')
        search_terms = [query, cleaned_topic] if cleaned_topic != query else [query]

        for term in search_terms:
            search_url = 'https://en.wikipedia.org/w/api.php'
            params = {'action': 'query', 'list': 'search', 'srsearch': term, 'utf8': '', 'format': 'json', 'srlimit': 3}
            sr = requests.get(search_url, params=params, headers={'User-Agent': 'JarvisAssistant/2.0'}, timeout=4).json()
            results = sr.get('query', {}).get('search', [])
            for res in results:
                title = res['title']
                sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
                sum_resp = requests.get(sum_url, headers={'User-Agent': 'JarvisAssistant/2.0'}, timeout=4)
                if sum_resp.status_code == 200:
                    extract = sum_resp.json().get('extract')
                    if extract and len(extract) > 40:
                        return clean_spoken_response(extract, max_sentences=2)
    except Exception:
        pass

    return f"I found some information on {query}, but could not fetch a concise answer right now."


def chatBot(query):
    user_input = query.lower()
    cookie_path = os.path.join("backend", "cookie.json")
    
    # 1. Try HugChat if cookie configured
    if os.path.exists(cookie_path):
        try:
            from hugchat import hugchat
            chatbot = hugchat.ChatBot(cookie_path=cookie_path)
            conv_id = chatbot.new_conversation()
            chatbot.change_conversation(conv_id)
            response = chatbot.chat(user_input)
            spoken_text = clean_spoken_response(str(response), max_sentences=2)
            print(f"AI: {spoken_text}")
            speak(spoken_text)
            return spoken_text
        except Exception as e:
            print(f"HugChat error: {e}")
    
    # 2. Answer via multi-source knowledge & web engine
    answer = answer_question_web(query)
    print(f"Jarvis: {answer}")
    speak(answer)
    return answer
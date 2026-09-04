# 🤖 JARVIS - Next-Gen AI Desktop Voice Assistant

<p align="center">
  <img src="frontend/assets/img/logo.ico" alt="Jarvis Logo" width="100"/>
</p>

<p align="center">
  <b>An intelligent, context-aware desktop voice assistant with authentic Indian male neural voice, Hinglish NLP, Google Library search, facial biometrics, universal file/app launcher, and long-term memory.</b>
</p>

<p align="center">
  <a href="https://github.com/bankarsamendra04-eng/Jarvis"><img src="https://img.shields.io/badge/GitHub-Repository-blue?logo=github" alt="Repo"/></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python Version"/>
  <img src="https://img.shields.io/badge/Language-Hinglish%20%7C%20English-green" alt="Language"/>
  <img src="https://img.shields.io/badge/Biometrics-OpenCV%20LBPH-orange" alt="Biometrics"/>
  <img src="https://img.shields.io/badge/Voice-Indian%20Male%20Neural-purple" alt="Voice Engine"/>
  <img src="https://img.shields.io/badge/License-MIT-brightgreen" alt="License"/>
</p>

---

## 🌟 Key Features & Capabilities

### 🎙️ 1. Authentic Indian Male Voice & Hinglish Assistant
- **"Hey Jarvis" Hands-Free Wake Word**: Say *"Hey Jarvis"* (or *"Hello Jarvis"*, *"Jarvis"*) to instantly activate the voice command mic, trigger the waveform UI, and give your instruction.
- **Human-Grade Neural Voice Engine**: Powered by `edge-tts` (`en-IN-PrabhatNeural`) tuned with deeper baritone resonance, crisp pacing, and commanding volume for a realistic Indian male persona.
- **Hinglish (Hindi + English) NLP**: Speaks and understands natural conversational Hinglish (e.g., *"Hey Jarvis, mera naam kya hai?"*, *"VS Code kholo"*, *"Google pe search karo"*, *"Abhi time kitna hua hai?"*).
- **Speech Recognition (STT)**: Multi-dialect Indian English & Hindi voice recognition via Google Speech API.

### 🧠 2. Secure Categorized Long-Term Memory System & Memory Vault
- **Persistent Local Database**: Categorized SQLite memory bank (`user_memories`) covering Profile, Education, Skills, Projects, Preferences, Goals, and Behavioral Instructions.
- **Security & Sensitive Data Guard**: Automatically blocks passwords, OTPs, CVVs, private keys, and payment credentials with immediate voice safety warnings.
- **Context-Aware Smart Retrieval**: Intelligently scores and injects only the most relevant memories into conversations rather than sending the entire database.
- **Automatic & Explicit Memory**: Automatically detects declarative user facts or records explicit voice triggers (*"Remember this..."*, *"Save to memory..."*, *"Forget this..."*, *"What do you remember about me?"*, *"Update my profile..."*).
- **UI Memory Management Vault**: Full memory management screen with category tabs, search filter, inline editing, privacy tags, and single-click deletion.

### 🔍 3. Google Library Search & Real-Time Q&A
- **Multi-Source Knowledge Engine**: Real-time integration with Google Search, Wikipedia summaries, and DuckDuckGo Instant Answers.
- **Instant Answers**: Factual definitions, live date/time, math calculations, and technical queries articulated in 1–2 punchy spoken sentences.

### 📂 4. Universal File, App, Picture & System Opener
- **Installed Applications & Start Menu Discovery**: Seamlessly launches any installed software (Android Studio, VS Code, Chrome, Edge, Brave, PyCharm, etc.).
- **Local Files, Pictures & Documents**: Automatically searches and opens PDFs, images (`.png`, `.jpg`), archives (`.zip`, `.tar.gz`), code files, and user directories (`Desktop`, `Downloads`, `Documents`, `Pictures`, `Videos`).
- **Windows System Settings & Protocols**: Direct access to Camera, Bluetooth, Wi-Fi, Sound, Calculator, Task Manager, Control Panel, and File Explorer.

### 🔐 5. Facial Biometric Authentication
- Multi-frame face detection and recognition using OpenCV Haar Cascades and Local Binary Pattern Histograms (LBPH).
- Securely authorizes user access upon webcam verification before unlocking the assistant.

### 💬 6. WhatsApp & YouTube Automation
- Automated WhatsApp voice calls, video calls, and instant message delivery linked with an SQLite contacts database.
- Direct voice-controlled YouTube music and video streaming.

### 🎨 7. Futuristic Cyberpunk UI & Visualizations
- Built with Python **Eel**, featuring 3D rotating canvas particle globe, Siri audio waveform visualization, and dynamic real-time chat UI.

### 🗂️ 8. Persistent Conversation History Sidebar
- **Modern Two-Panel Architecture**: Fixed left sidebar on desktop (280–320px) with responsive slide-out drawer on tablets/mobile.
- **Persistent Multi-Chat History**: Stores conversation threads in SQLite (`conversations` and `messages` tables).
- **Rich Management**: "+ New Chat" button (`Ctrl+N`), instant search filter, pin/unpin conversations, inline renaming, and safe deletion with confirmation modal.
- **Auto-Titling**: Automatically generates clean, context-aware titles from the user's first prompt.

### 🎯 9. Personal Goal & Progress Tracking System
- **Comprehensive Goal Categories**: Track career & learning goals across *Learning a technology, Completing projects, Preparing for exams, Internship tasks, Building portfolio, Technical interview preparation, and General goals*.
- **Rich Goal Attributes**: Goal Name, Description, Target Deadline (with days remaining countdown), Priority levels (*High, Medium, Low*), Milestones Checklist, Auto-Calculated Progress Percentage (0–100%), Status (*Active, Completed, On Hold*), and Strategy Notes.
- **AI Daily Action Planner**: Generates a tailored daily action plan with estimated time blocks (30–45 mins each) prioritized from active goals and upcoming deadlines.
- **Milestone-Driven Progress Engine**: Interactive milestone checkboxes automatically update progress percentage and flip status to Completed upon reaching 100%.

### 🎓 10. AI Study Mode & Academic Coach
- **Multi-Subject Curriculum Bank**: Pre-loaded with high-yield concepts across *Computer Networks, Operating Systems, Database Management Systems (DBMS), Data Structures & Algorithms (DSA), AI & Machine Learning, and Python OOPs*.
- **Multi-Format Concept Explainer**: Switch instantly between *Simple Explanations, Hinglish, Step-by-Step Breakdowns, Real-World Analogies, and Key Takeaways*.
- **Interactive MCQ & Mini-Quiz Engine**: Real-time option evaluation (A/B/C/D), instantaneous answer validation, detailed explanations, automatic scoring, and weak-topic logging.
- **Viva Voce Oral Examiner**: Real-time interview and oral viva practice with question prompts, listen audio, model answer inspection, and performance self-evaluations.
- **University & Placement Exam Master**: Structured Short-Answer (2–3 marks) and Long-Answer (5–10 marks) questions with comprehensive marking schemes.
- **3D Interactive Flashcards**: Rapid revision flashcard decks with smooth 3D flip card animations.
- **Automatic Scoring & Weak-Topic Detection**: Automatically analyzes quiz accuracy, logs incorrect questions into SQLite (`weak_topics`), and prioritizes weak topics for personalized revision sessions (*"Revise today's topics"*).
- **Study Voice Commands**:
  - *"Start study mode."* / *"Study mode on"* &rarr; Activates study mode and opens dashboard.
  - *"Explain this simply."* / *"Explain Deadlocks simply"* &rarr; Spoken simple explanation with real-world analogy.
  - *"Give me 10 MCQs."* / *"Test me on networking"* &rarr; Loads MCQs and reads first practice question.
  - *"Take my viva."* &rarr; Initiates oral viva session and asks interview question.
  - *"Show my weak topics."* &rarr; Spoken summary of flagged topics needing revision.
  - *"Revise today's topics."* &rarr; Initiates personalized revision on highest-error weak topic.

### ⚡ 11. Master Intent Engine & Direct Output Generation
- **Zero Meta Phrasing**: Completely eliminates meta responses (*"Search results ke anusaar..."*, *"According to the search results..."*, *"Based on the available results..."*). Delivers exact requested content directly.
- **Intelligent Intent Classification**: Seamlessly classifies requests internally into `MCQ_GENERATION`, `EXPLANATION`, `CODING`, `DEBUGGING`, `VIVA`, `CALCULATION`, `STUDY`, and `QUESTION_ANSWER`.
- **Exact Count MCQ Delivery**: When asked for MCQs (e.g. *"Give me 10 MCQs on OSI model"*), generates the exact requested count with 4 structured options, Answer Key, and pedagogical explanations.
- **6-Part Pedagogical Explanations**: Structured format providing (1) Definition, (2) Purpose, (3) Step-by-Step Breakdown, (4) Real-World Analogy, (5) Mnemonic / Memory trick, and (6) Exam & Viva Voce key points.
- **Complete Tested Code & Complexity Analysis**: Generates complete runnable code with time/space complexity analysis and execution commands.
- **Dual Screen & Voice Delivery**: Decouples rich full-text markdown output on the GUI chat display from concise, punchy natural voice summaries spoken over TTS.

### 🧠 12. Context-Aware Conversation Management & Reference Resolution
- **Short-Term Context Memory**: Maintains active state for Current Project, Previous Project, Current Task, Current Topic, Recent Files, Recent Commands, Recent Errors, and Last Generated Code Snippets.
- **Implicit Context Understanding**: E.g., *"I'm building a quiz app"* &rarr; *"Create the JavaScript file"* &rarr; Jarvis automatically synthesizes the task and generates complete `script.js` with question bank, scoring, and UI listeners.
- **Deictic & Anaphoric Pronoun Resolution**: Intelligently resolves references (*"this"*, *"that"*, *"it"*, *"the previous project"*, *"the last file"*, *"that code"*, *"the above error"*, *"my current project"*).
- **Ambiguity Detection & Targeted Clarifications**: Asks concise, targeted clarifying questions when multiple candidates exist.

### 🛠️ 13. AI Coding Agent Mode & Sandboxed Execution
- **12 Developer Capabilities**:
  1. **Scaffold Project Structures**: Automatic modular architecture for Python and Web/Frontend apps.
  2. **Create Files**: Automatic file generation (`app.py`, `index.html`, `style.css`, `script.js`).
  3. **Read Project Files**: Formatted code viewer with line numbers.
  4. **Modify Code**: Safe file updates with automated backup (`.bak`).
  5. **Explain Code & AST**: Detailed breakdown of functions, classes, and Big-O complexity.
  6. **Detect Errors**: Static and runtime traceback analysis.
  7. **Suggest Fixes**: Verified defensive patches for `ZeroDivisionError`, `IndexError`, `KeyError`, etc.
  8. **Generate Commands**: Safe development command suggestions.
  9. **Sandboxed Command Execution**: Subprocess runner with working directory isolation, output capture, and timeout caps.
  10. **Application Debugging**: Runs code in sandbox, catches exceptions, and auto-proposes fixes.
  11. **Generate Professional READMEs**: Auto-generates GitHub-ready documentation with architecture trees.
  12. **Git & GitHub Readiness**: Prepares `.gitignore`, `LICENSE`, `git init`, and semantic commit messages.
- **Destructive Confirmation Guard**: Prompts for explicit user confirmation before any destructive delete action.
- **Coding Voice Commands**:
  - *"Create a new Python project."* / *"Create a new web project."*
  - *"Create the HTML file."*
  - *"Show me the project structure."*
  - *"Explain this function."*
  - *"Fix this error."*
  - *"Run the project."*
  - *"Prepare this project for GitHub."*

---

## 📁 Project Structure

```plaintext
Jarvis/
├── backend/
│   ├── auth/
│   │   ├── haarcascade_frontalface_default.xml   # OpenCV face detection model
│   │   ├── recoganize.py                         # Real-time face authentication
│   │   ├── sample.py                             # Face sample dataset generator
│   │   ├── trainer.py                            # LBPH model trainer
│   │   └── trainer/
│   │       └── trainer.yml                       # Trained biometric weights
│   ├── coding_agent.py                           # AI Coding Agent & Sandboxed Execution Engine
│   ├── command.py                                # TTS (Indian Voice), STT & command routing
│   ├── config.py                                 # Voice, user profile & assistant configuration
│   ├── context_manager.py                        # Context-Aware Conversation & Reference Engine
│   ├── db.py                                     # SQLite DB (conversations, messages, logs, commands)
│   ├── feature.py                                # Universal file opener, Q&A, WhatsApp & YouTube features
│   ├── goals_manager.py                          # Personal Goal & Progress Tracking + Daily Action Planner
│   ├── helper.py                                 # String processing and regex helpers
│   ├── intent_engine.py                          # Master Intent Engine, Direct Output & Meta-Phrase Filter
│   ├── memory_manager.py                         # Secure Categorized Long-Term Memory Vault
│   ├── study_manager.py                          # AI Study Mode, MCQs, Viva, Exam Q&A & Weak-Topic Detector
│   └── user_profile.json                         # Permanent user profile data
├── frontend/
│   ├── assets/
│   │   ├── audio/start_sound.wav                 # Modern assistant startup chime
│   │   ├── img/logo.ico                          # UI icon
│   │   └── vendore/                              # Textillate & animation plugins
│   ├── index.html                                # Cyberpunk Web GUI Interface
│   ├── main.js                                   # Eel bridge & interaction logic
│   ├── controller.js                             # UI event dispatcher
│   ├── script.js                                 # 3D Particle Canvas engine
│   └── style.css                                 # Cyberpunk styling & layouts
├── jarvis.db                                     # SQLite Database file
├── main.py                                       # Primary Jarvis GUI runner
├── run.py                                        # Multi-process runner (GUI + Hotword)
├── USER_PROFILE.md                               # Profile documentation for Samendra Bankar
├── requirements.txt                              # Python dependencies
├── .gitignore                                    # Git ignore rules
└── README.md                                     # Project documentation
```

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/bankarsamendra04-eng/Jarvis.git
cd Jarvis
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 👤 Face Authentication Setup

To train or update Jarvis with your face:

1. **Capture Face Samples**:
   ```bash
   python backend/auth/sample.py
   ```
   *Enter User ID `1` and look into the camera.*

2. **Train Biometric Model**:
   ```bash
   python backend/auth/trainer.py
   ```
   *Trains LBPH model and saves to `backend/auth/trainer/trainer.yml`.*

---

## ⚡ Running Jarvis

### Option A: Complete System (GUI + Background Hotword)
```bash
python run.py
```

### Option B: GUI & Assistant Engine Only
```bash
python main.py
```

---

## 🗣️ Example Voice Commands

| Category | Example Commands | Action |
| :--- | :--- | :--- |
| **Wake Word Activation** | *"Hey Jarvis"* / *"Hello Jarvis"* | Opens voice command mic and asks: *"Ji Samendra, boliye?"* |
| **Direct Wake Commands** | *"Hey Jarvis VS Code kholo"* | Strips wake word and launches VS Code immediately |
| **Self-Introduction** | *"Tell me about yourself"* / *"Who are you?"* | Speaks dynamic self-introduction & displays full capability overview |
| **Capabilities & Features**| *"What can you do?"* / *"What are your features?"* | Details AI Study Mode, coding, memory, goals, and automation |
| **Assistant Purpose** | *"What is your purpose?"* | Explains core purpose as personal AI assistant |
| **Contextual Code/File** | *"Create the JavaScript file"* (in project) | Context-aware synthesis: generates full quiz logic/script.js |
| **Context Reference** | *"Add CSS for that"* / *"Show the last file"* | Resolves pronouns (*"that"*, *"it"*, *"last file"*) to active project |
| **Daily Action Plan** | *"What should I work on today?"* / *"Aaj kya karna hai?"* | Generates and speaks tailored daily action plan |
| **Goal Summary** | *"Show my goals"* / *"Active goals dikhao"* | Speaks active goals summary and opens Goals Dashboard |
| **Goal Progress** | *"Which goal is closest to completion?"* | Identifies closest goal and current progress % |
| **Update Progress** | *"Update progress of Jarvis project to 85%"* | Updates goal progress percentage via voice |
| **Create New Goal** | *"Create a new goal"* / *"Naya goal banao"* | Opens Goal Creation modal in UI |
| **Study Mode Toggle** | *"Start study mode"* / *"Study mode on"* | Activates AI Study Mode and launches academic coach |
| **Simple Explanations**| *"Explain Deadlocks simply"* | Explains complex concept with simple real-world analogy |
| **MCQ Practice** | *"Give me 10 MCQs"* / *"Test me on networking"* | Loads interactive MCQs and reads first practice question |
| **Oral Viva Examination**| *"Take my viva"* / *"Viva question"* | Conducts interactive interview & reveals model response |
| **Weak-Topic Analytics**| *"Show my weak topics"* | Summarizes flagged weak topics from quizzes |
| **Personalized Revision**| *"Revise today's topics"* | Starts targeted revision on highest-error weak topic |
| **Personal Profile** | *"Mera naam kya hai?"* / *"Who am I?"* | Answers: *"Aapka naam Samendra Bankar hai."* |
| **Profile & Tech** | *"Meri education kya hai?"* / *"Mere skills batao"* | Details BTech background, Python, Java, AI/ML, etc. |
| **Knowledge & Search**| *"Who is the Prime Minister of India?"* | Searches Google & speaks verified answer |
| **Calculations & Time** | *"Calculate 250 * 4"* / *"Abhi time kya hua hai?"* | Computes math and announces current time/date |
| **File & App Launcher** | *"VS Code kholo"* / *"Android Studio open karo"* | Launches application immediately |
| **Local File & Pictures**| *"Open 100 Final Year Projects"* / *"Show picture img3"* | Opens PDF document or image viewer |
| **System Settings** | *"Open Bluetooth"* / *"Open Camera"* / *"Open Settings"* | Opens Windows UWP tools & Settings |
| **Memory & Notes** | *"Remember that my meeting is at 3 PM"* | Saves High-Priority Memory to database |
| **Memory Recall** | *"Kya yaad hai?"* / *"What do you remember?"* | Recalls recent stored memory items |
| **WhatsApp Automation**| *"Send message to Rahul"* / *"Call Rahul"* | Automates WhatsApp message/call |
| **YouTube Streaming** | *"Play Interstellar theme on YouTube"* | Streams video directly on YouTube |

---

## 🛠️ Built With

- **Python 3.10+** - Core intelligence & system automation
- **Eel** - Python desktop GUI framework with Chrome/Edge App mode
- **Edge-TTS & gTTS** - Authentic Indian Male Neural Voice Synthesis
- **OpenCV** - Computer vision & facial biometric authentication
- **SpeechRecognition & PyAudio** - Indian English/Hinglish speech-to-text
- **SQLite3** - Persistent memory logs, contacts, and command indexing
- **Pygame & PyAutoGUI** - Low-latency audio playback & desktop automation

---

## 👨‍💻 Developer & Owner

- **Developer**: Samendra Bankar
- **GitHub**: [@bankarsamendra04-eng](https://github.com/bankarsamendra04-eng)
- **Repository**: [bankarsamendra04-eng/Jarvis](https://github.com/bankarsamendra04-eng/Jarvis)

---

## 📄 License

This project is licensed under the **MIT License**. Feel free to use, modify, and contribute!

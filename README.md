# 🤖 JARVIS - Next-Gen AI Desktop Voice Assistant

<p align="center">
  <img src="frontend/assets/img/logo.ico" alt="Jarvis Logo" width="100"/>
</p>

<p align="center">
  <b>An intelligent, context-aware desktop voice assistant with authentic Indian male neural voice, Hinglish NLP, facial biometrics, persistent multi-conversation management, AI Study Mode, Personal Goals Tracker, universal file/app launcher, and long-term memory vault.</b>
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

### 🔐 1. Startup Authentication & Fresh Session Initialization
- **Automatic New Conversation on Every Run**:
  - Every time you launch JARVIS, the assistant starts with a brand-new, clean conversation thread.
  - Automatically resets conversation context while preserving full multi-chat history in the sidebar.
- **Live Facial Biometric Greeting Sequence**:
  - Automatically triggers the webcam scanner and displays the live prompt in the assistant's chat UI:
    > *"Welcome Samendra! Face authentication ke liye camera ki taraf dekhein."*
  - Upon successful facial recognition via OpenCV LBPH:
    > *"Face recognize ho gaya hai. Welcome Samendra, main aapki kya madad kar sakta hoon?"*
  - Both messages are rendered directly as chat bubbles and recorded into the new conversation history.

### 🎙️ 2. Two-Stage Continuous Wake-Word Engine & Indian Neural Voice
- **Continuous Background Wake-Word Engine (`backend/wake_word.py`)**:
  - Monitors continuously for *"Hey Jarvis"* and *"Hello Jarvis"* without freezing the UI.
  - **Stage 1 (Background Wake Listener)**: Lightweight listening loop with energy threshold calibration.
  - **Stage 2 (Command Listener & Execution Pipeline)**: Upon wake detection, plays an activation chime, animates the `SiriWave` waveform, captures the user's instruction, and routes it to the AI intent engine.
  - **Single & Multi-Utterance Support**: Handles wake phrase alone (*"Hey Jarvis"* &rarr; opens mic and waits) or unified single-sentence commands (*"Hey Jarvis, explain binary search"* &rarr; executes immediately).
  - **Thread-Safe Anti-Conflict Guard**: Automatically pauses background listening during manual mic clicks (`#MicBtn`), shortcut triggers (`Win+J`), active speech recognition, or TTS speech output.
- **Human-Grade Neural Voice Engine**: Powered by `edge-tts` (`en-IN-PrabhatNeural`) tuned with deeper baritone resonance, crisp pacing, and natural cadence.
- **Hinglish (Hindi + English) NLP**: Native understanding and speech synthesis for natural conversational Hinglish (*"Hey Jarvis, mera naam kya hai?"*, *"VS Code kholo"*, *"Google pe search karo"*).

### 🧠 3. Secure Categorized Long-Term Memory System & Memory Vault
- **Persistent Local SQLite Vault**: Categorized memory tables (`user_memories`) covering Profile, Education, Skills, Projects, Preferences, Goals, and Behavioral Instructions.
- **Sensitive Data Security Guard**: Automatically blocks passwords, OTPs, CVVs, private keys, and credit cards with voice warnings.
- **Contextual Retrieval**: Scores and injects only the relevant memory items per prompt.
- **UI Memory Vault**: Dedicated modal with category filters, search bar, inline editing, and privacy tags.

### 🗂️ 4. Persistent Conversation History Sidebar
- **Modern Two-Panel Desktop & Drawer UI**: Responsive left sidebar with searchable conversation cards.
- **SQLite Multi-Chat Persistence**: Stores conversations and messages in `conversations` and `messages` tables.
- **Management Features**: "+ New Chat" button (`Ctrl+N`), pin/unpin chats, inline rename, and deletion with confirmation.
- **Auto-Titling**: Automatically generates concise titles from the user's first query.

### 🎯 5. Personal Goal & Progress Tracking System
- **Comprehensive Goal Categories**: Track learning technologies, projects, exam preparation, internship tasks, and portfolio development.
- **Milestone-Driven Tracking**: Target deadlines, priority tags (*High, Medium, Low*), auto-calculated progress percentage (0–100%), and interactive milestone checklists.
- **AI Daily Action Planner**: Tailored daily schedule with estimated time blocks (30–45 mins each) prioritized from active goals and deadlines.

### 🎓 6. AI Study Mode & Academic Coach
- **Multi-Subject Curriculum**: Computer Networks, Operating Systems, DBMS, DSA, AI/ML, and Python OOPs.
- **Multi-Format Concept Explainer**: Simple explanations, Hinglish breakdowns, step-by-step guides, analogies, and mnemonics.
- **Interactive MCQs & Viva Voce**: Practice quizzes with instant scoring, oral viva voce simulations with model answers, and weak-topic analytics for personalized revision.

### 🛠️ 7. AI Coding Agent & Real System Action Handlers
- **Language-Agnostic Code Synthesis**: Authentic, runnable code in **C++**, **C**, **Java**, **Python**, **JavaScript**, **HTML/CSS**, and **SQL** with build and run commands.
- **Real Windows Filesystem Operations**: Creates, reads, edits, and deletes files and folders on Windows Desktop and local paths.
- **App & File Opener**: Direct launch for VS Code, Android Studio, Chrome, Edge, PDF documents, pictures, and Windows settings.
- **WhatsApp & YouTube Automation**: Automated WhatsApp messaging/calling and YouTube video streaming.

---

## 📁 Project Structure

```plaintext
Jarvis/
├── backend/
│   ├── action_handler.py                         # Windows filesystem & system action handlers
│   ├── auth/
│   │   ├── haarcascade_frontalface_default.xml   # OpenCV face detection cascade
│   │   ├── recoganize.py                         # Real-time face authentication
│   │   ├── sample.py                             # Face dataset generator
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
│   ├── memory_manager.py                         # SQLite categorized memory vault & privacy filter
│   ├── study_manager.py                          # AI Study Mode, MCQs, Viva Voce & Quiz engine
│   ├── wake_word.py                              # Two-Stage Background Wake-Word Engine ("Hey Jarvis")
│   └── user_profile.json                         # Permanent user profile data
├── frontend/
│   ├── assets/
│   │   ├── audio/start_sound.wav                 # Modern assistant startup chime
│   │   ├── img/logo.ico                          # UI icon
│   │   └── vendore/                              # Textillate & animation plugins
│   ├── index.html                                # Cyberpunk Web GUI Interface
│   ├── main.js                                   # Eel bridge & conversation lifecycle logic
│   ├── controller.js                             # UI event dispatcher & message renderer
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
- **SQLite3** - Persistent memory logs, contacts, and conversation database
- **Pygame & PyAutoGUI** - Low-latency audio playback & desktop automation

---

## 👨‍💻 Developer & Owner

- **Developer**: Samendra Bankar
- **GitHub**: [@bankarsamendra04-eng](https://github.com/bankarsamendra04-eng)
- **Repository**: [bankarsamendra04-eng/Jarvis](https://github.com/bankarsamendra04-eng/Jarvis)

---

## 📄 License

This project is licensed under the **MIT License**. Feel free to use, modify, and contribute!

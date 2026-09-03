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

### 🧠 2. Personal Profile & Long-Term Memory
- **Personalized Context**: Pre-configured for **Samendra Bankar** (BTech 3rd-Year Student specializing in Software Development, AI/ML, Networking, Cloud/DevOps, and Embedded Systems).
- **Persistent SQLite Database Memory**: All meaningful interactions and custom *"remember"* requests are stored permanently in `jarvis.db` (`message_logs` table).
- **Personal Identity Q&A**: Instant answers about education, skills, interests, career goals, and saved memories.

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

### 🎨 7. Futuristic Cyberpunk UI
- Built with Python **Eel**, featuring 3D rotating canvas particle globe, Siri audio waveform visualization, and dynamic real-time chat UI.

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
│   ├── command.py                                # TTS (Indian Voice), STT & command routing
│   ├── config.py                                 # Voice, user profile & assistant configuration
│   ├── db.py                                     # SQLite DB (message_logs, web/sys commands, contacts)
│   ├── feature.py                                # Universal file opener, Q&A, WhatsApp & YouTube features
│   ├── helper.py                                 # String processing and regex helpers
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

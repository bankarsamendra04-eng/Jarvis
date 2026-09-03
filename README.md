# 🤖 JARVIS - Next-Gen AI Desktop Voice Assistant

<p align="center">
  <img src="frontend/assets/img/logo.ico" alt="Jarvis Logo" width="100"/>
</p>

<p align="center">
  <b>An intelligent, responsive desktop voice assistant equipped with facial biometric authentication, modern Eel web GUI, hotword detection, and desktop/web automation.</b>
</p>

---

## 🌟 Key Features

- 🎙️ **Interactive Voice Control & TTS**: Real-time voice command processing powered by Google Speech Recognition and high-fidelity speech synthesis (`pyttsx3`).
- 🔐 **Facial Biometric Authentication**: Multi-frame face detection and recognition using OpenCV Haar Cascades and Local Binary Pattern Histograms (LBPH).
- 🌐 **Web & Application Automation**: Effortlessly launch favorite websites (YouTube, GitHub, ChatGPT, Google, Spotify) or local system applications (Notepad, Calculator, Terminal, File Explorer).
- 💬 **WhatsApp & Communications Hub**: Automated WhatsApp messaging and calling integration linked with an SQLite contacts database.
- 🎵 **YouTube Integration**: Instant query search and video playback hands-free.
- ⚡ **Background Hotword Listener**: Lightweight multi-processed background wake-word engine.
- 🎨 **Futuristic UI / UX**: Built with Python Eel, 3D rotating canvas particle globe, Siri audio waveform visualization, and dynamic chat messaging canvas.

---

## 📁 Project Architecture

```plaintext
Jarvis-2025-master/
├── backend/
│   ├── auth/
│   │   ├── haarcascade_frontalface_default.xml   # OpenCV face detection model
│   │   ├── recoganize.py                         # Real-time face authentication
│   │   ├── sample.py                             # Dataset generator for face training
│   │   ├── trainer.py                            # LBPH model trainer
│   │   └── samples/                              # Face capture dataset directory
│   ├── command.py                                # TTS & speech command handler
│   ├── config.py                                 # Assistant configuration & constants
│   ├── db.py                                     # SQLite DB manager (web & sys commands, contacts)
│   ├── feature.py                                # Core feature modules (WhatsApp, YouTube, etc.)
│   └── helper.py                                 # Text parsing and regex utilities
├── frontend/
│   ├── assets/
│   │   ├── audio/start_sound.mp3                 # Startup chime
│   │   ├── img/logo.ico                          # UI icon
│   │   └── vendore/                              # Textillate & animation plugins
│   ├── index.html                                # Jarvis Web GUI Interface
│   ├── main.js                                   # Eel bridge & interaction logic
│   ├── controller.js                             # UI event dispatcher
│   ├── script.js                                 # 3D Particle Canvas engine
│   └── style.css                                 # Cyberpunk styling & layouts
├── main.py                                       # Primary Jarvis GUI runner
├── run.py                                        # Multi-process runner (GUI + Hotword)
├── requirements.txt                              # Python package dependencies
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

### 2. Create and Activate a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 👤 Face Authentication Setup (Optional)

To train Jarvis to recognize your face:

1. **Capture Face Samples**:
   ```bash
   python backend/auth/sample.py
   ```
   *Enter a numeric User ID (e.g. `1`) and look into your webcam.*

2. **Train the Face Recognizer**:
   ```bash
   python backend/auth/trainer.py
   ```
   *This generates `backend/auth/trainer/trainer.yml`.*

---

## ⚡ Running Jarvis

### Full Assistant with Background Hotword Listener:
```bash
python run.py
```

### GUI Mode Only:
```bash
python main.py
```

---

## 🗣️ Supported Commands Examples

| Command | Action |
| :--- | :--- |
| `"Open Google"` / `"Open YouTube"` | Launches websites in default browser |
| `"Open Notepad"` / `"Open Calculator"` | Launches Windows system desktop applications |
| `"Play Interstellar Theme on YouTube"` | Searches and plays music directly on YouTube |
| `"Send message to [Contact Name]"` | Opens WhatsApp and automates message dispatch |
| `"Call [Contact Name]"` | Initiates WhatsApp voice call |
| `"What is artificial intelligence?"` | Triggers intelligent chat / assistant query fallback |

---

## 🌐 Live Web Showcase & Deployment

- **GitHub Repository**: [bankarsamendra04-eng/Jarvis](https://github.com/bankarsamendra04-eng/Jarvis)
- **Deployment Status**: 
  - Desktop Client: Fully functional locally via Python Eel & Chromium/Edge App mode.
  - Web Showcase: Can be deployed to **Vercel** / **GitHub Pages** for visual frontend demonstration.

---

## 🛠️ Built With

- **Python 3.10+** - Core logic and system automation
- **Eel** - Python desktop GUI library with HTML/JS integration
- **OpenCV** - Computer vision & face biometrics
- **SQLite3** - Local database for commands and contacts
- **HTML5 / CSS3 / JavaScript** - Interactive user interface and 3D animations

---

## 📄 License

This project is licensed under the MIT License. Feel free to use and contribute!

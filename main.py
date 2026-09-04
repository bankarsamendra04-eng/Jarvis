import os
import sys
import webbrowser
import eel
from backend.auth import recoganize
from backend.feature import *
from backend.command import *
import backend.db  # Ensures database tables are initialized
import backend.goals_manager  # Ensures goals table and eel endpoints are initialized
import backend.study_manager  # Ensures study mode tables and eel endpoints are initialized
import backend.wake_word  # Two-stage background wake-word engine

def start():
    eel.init("frontend") 
    
    # Start continuous background wake-word listener ("Hey Jarvis" / "Hello Jarvis")
    try:
        backend.wake_word.start_wake_word_service()
    except Exception as wake_err:
        print(f"Wake word startup notice: {wake_err}")
    
    try:
        play_assistant_sound()
    except Exception as e:
        print(f"Assistant startup sound notice: {e}")

    @eel.expose
    def init():
        try:
            eel.hideLoader()
            speak("Welcome Samendra! Face authentication ke liye camera ki taraf dekhein.")
            flag = recoganize.AuthenticateFace()
            if flag == 1:
                speak("Face recognize ho gaya hai. Welcome Samendra, main aapki kya madad kar sakta hoon?")
                eel.hideFaceAuth()
                eel.hideFaceAuthSuccess()
                eel.hideStart()
                play_assistant_sound()
            else:
                speak("Face match nahi hua. Proceeding with default access. Welcome!")
                eel.hideFaceAuth()
                eel.hideFaceAuthSuccess()
                eel.hideStart()
        except Exception as e:
            print(f"Face auth error: {e}")
            try:
                eel.hideLoader()
                eel.hideFaceAuth()
                eel.hideFaceAuthSuccess()
                eel.hideStart()
            except Exception:
                pass

    try:
        # Try launching Edge app mode, else fallback to standard browser
        os.system('start msedge.exe --app="http://localhost:8000/index.html"')
    except Exception:
        webbrowser.open("http://localhost:8000/index.html")
    
    eel.start("index.html", mode=None, host="localhost", port=8000, block=True)

if __name__ == "__main__":
    start()
    
import os
import sys
import webbrowser
import eel
from backend.auth import recoganize
from backend.feature import *
from backend.command import *
import backend.db  # Ensures database tables are initialized

def start():
    eel.init("frontend") 
    
    try:
        play_assistant_sound()
    except Exception as e:
        print(f"Assistant startup sound notice: {e}")

    @eel.expose
    def init():
        try:
            eel.hideLoader()
            speak("Welcome to Jarvis")
            speak("Ready for Face Authentication")
            flag = recoganize.AuthenticateFace()
            if flag == 1:
                speak("Face recognized successfully")
                eel.hideFaceAuth()
                eel.hideFaceAuthSuccess()
                speak("Welcome to Your Assistant")
                eel.hideStart()
                play_assistant_sound()
            else:
                speak("Face not recognized or bypassed. Welcome.")
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

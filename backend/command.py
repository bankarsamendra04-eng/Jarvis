import time
import pyttsx3
import speech_recognition as sr
import eel

def speak(text):
    text = str(text)
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        if voices and len(voices) > 1:
            # Pick a female or natural voice if available, else fallback
            engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
        elif voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 174)
        
        try:
            eel.DisplayMessage(text)
            eel.receiverText(text)
        except Exception:
            pass
            
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Speech error: {e}")
        try:
            eel.DisplayMessage(text)
            eel.receiverText(text)
        except Exception:
            pass


def takecommand():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("I'm listening...")
            try:
                eel.DisplayMessage("I'm listening...")
            except Exception:
                pass
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, 10, 8)
    except Exception as mic_err:
        print(f"Microphone input error: {mic_err}")
        return None

    try:
        print("Recognizing...")
        try:
            eel.DisplayMessage("Recognizing...")
        except Exception:
            pass
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")
        try:
            eel.DisplayMessage(query)
        except Exception:
            pass
        return query.lower()
    except Exception as e:
        print(f"Recognition Error: {str(e)}\n")
        return None


@eel.expose
def takeAllCommands(message=None):
    if message is None or message == "":
        query = takecommand()  # Voice input
        if not query:
            try:
                eel.ShowHood()
            except Exception:
                pass
            return
        print(f"Voice Command: {query}")
        try:
            eel.senderText(query)
        except Exception:
            pass
    else:
        query = message  # Text input from chatbox
        print(f"Text Command: {query}")
        try:
            eel.senderText(query)
        except Exception:
            pass
    
    try:
        if query:
            query_lower = query.lower()
            if "open" in query_lower:
                from backend.feature import openCommand
                openCommand(query)
            elif "send message" in query_lower or "call" in query_lower or "video call" in query_lower:
                from backend.feature import findContact, whatsApp
                flag = ""
                Phone, name = findContact(query)
                if Phone != 0:
                    if "send message" in query_lower:
                        flag = 'message'
                        speak("What message would you like to send?")
                        msg_query = takecommand()
                        if msg_query:
                            whatsApp(Phone, msg_query, flag, name)
                    elif "call" in query_lower:
                        flag = 'call'
                        whatsApp(Phone, "", flag, name)
                    else:
                        flag = 'video call'
                        whatsApp(Phone, "", flag, name)
            elif "on youtube" in query_lower or query_lower.startswith("play "):
                from backend.feature import PlayYoutube
                PlayYoutube(query)
            else:
                from backend.feature import chatBot
                chatBot(query)
        else:
            speak("No command was given.")
    except Exception as e:
        print(f"An error occurred while executing command: {e}")
        speak("Sorry, something went wrong.")
    
    try:
        eel.ShowHood()
    except Exception:
        pass

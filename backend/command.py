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
            
        from backend.db import store_message_log
        store_message_log("assistant", text)
            
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Speech error: {e}")
        try:
            eel.DisplayMessage(text)
            eel.receiverText(text)
        except Exception:
            pass
        try:
            from backend.db import store_message_log
            store_message_log("assistant", text)
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
        # en-IN recognizes English and Hinglish phrases with Indian dialect naturally
        try:
            query = r.recognize_google(audio, language='en-IN')
        except Exception:
            query = r.recognize_google(audio, language='hi-IN')
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
            from backend.db import store_message_log
            query_lower = query.lower()
            is_priority = any(w in query_lower for w in ["remember", "yaad rakh", "yaad karo"])
            store_message_log("user", query, is_priority_memory=is_priority)

            if any(w in query_lower for w in ["remember", "yaad rakh", "yaad karo"]):
                from backend.feature import rememberMemory
                rememberMemory(query)
            elif any(w in query_lower for w in ["what do you remember", "recall", "my memories", "kya yaad hai", "memories batao"]):
                from backend.feature import recallMemories
                recallMemories()
            elif any(w in query_lower for w in ["open", "launch", "show picture", "show photo", "show file", "show document", "start app", "kholo", "open karo", "chalu karo", "dikhao"]):
                from backend.feature import openCommand
                openCommand(query)
            elif "send message" in query_lower or "call" in query_lower or "video call" in query_lower or "message bhejo" in query_lower:
                from backend.feature import findContact, whatsApp
                flag = ""
                Phone, name = findContact(query)
                if Phone != 0:
                    if "send message" in query_lower or "message bhejo" in query_lower:
                        flag = 'message'
                        speak("Aap kya message bhejna chahte hain?")
                        msg_query = takecommand()
                        if msg_query:
                            whatsApp(Phone, msg_query, flag, name)
                    elif "call" in query_lower:
                        flag = 'call'
                        whatsApp(Phone, "", flag, name)
                    else:
                        flag = 'video call'
                        whatsApp(Phone, "", flag, name)
            elif "on youtube" in query_lower or query_lower.startswith("play ") or "play karo" in query_lower or "chalao" in query_lower:
                from backend.feature import PlayYoutube
                PlayYoutube(query)
            else:
                from backend.feature import chatBot
                chatBot(query)
        else:
            speak("Koi command nahi mila.")
    except Exception as e:
        print(f"An error occurred while executing command: {e}")
        speak("Sorry, command execute karte waqt kuch gadbad hui.")
    
    try:
        eel.ShowHood()
    except Exception:
        pass

import asyncio
import os
import time
import pyttsx3
import pygame
import speech_recognition as sr
import eel

# Ensure pygame mixer is initialized
try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
except Exception as e:
    print(f"Mixer notice: {e}")

def play_indian_tts(text):
    """
    Generates and plays natural Indian male accent voice using edge-tts (Neural Indian accent)
    or gTTS (Google India), with pyttsx3 as local fallback.
    """
    from backend.config import ASSISTANT_VOICE, VOICE_PITCH, VOICE_RATE, VOICE_VOLUME
    audio_dir = os.path.join("frontend", "assets", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    temp_audio = os.path.join(audio_dir, f"tts_{int(time.time() * 1000)}.mp3")

    # 1. Primary Engine: Edge Neural Indian Male Accent Voice (en-IN-PrabhatNeural)
    try:
        import edge_tts
        async def _generate():
            # en-IN-PrabhatNeural provides an authentic, natural Indian Male tone for Hinglish and English
            voice = ASSISTANT_VOICE if ASSISTANT_VOICE else "en-IN-PrabhatNeural"
            com = edge_tts.Communicate(text, voice, rate=VOICE_RATE, pitch=VOICE_PITCH, volume=VOICE_VOLUME)
            await com.save(temp_audio)

        asyncio.run(_generate())
        if os.path.exists(temp_audio) and os.path.getsize(temp_audio) > 100:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(temp_audio)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.04)
            pygame.mixer.music.unload()
            try:
                os.remove(temp_audio)
            except Exception:
                pass
            return True
    except Exception as edge_err:
        print(f"Edge TTS notice: {edge_err}")

    # 2. Secondary Engine: Google TTS (Indian domain .co.in)
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en", tld="co.in", slow=False)
        tts.save(temp_audio)
        if os.path.exists(temp_audio):
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(temp_audio)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.04)
            pygame.mixer.music.unload()
            try:
                os.remove(temp_audio)
            except Exception:
                pass
            return True
    except Exception as gtts_err:
        print(f"Google TTS notice: {gtts_err}")

    # 3. Offline Fallback: pyttsx3 SAPI5 (Male Voice)
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        if voices:
            # Set to male voice (David)
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 165)
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as sapi_err:
        print(f"SAPI5 fallback error: {sapi_err}")
        return False

def speak(text):
    text = str(text).strip()
    if not text:
        return
        
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

    play_indian_tts(text)


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
            query_lower = query.lower().strip()

            # Handle 'Hey Jarvis' / 'Jarvis' wake phrases
            wake_words = ["hey jarvis", "hello jarvis", "ok jarvis", "sun jarvis", "jarvis"]
            for ww in wake_words:
                if query_lower == ww:
                    # User only said 'Hey Jarvis' -> Prompt and open mic for instruction
                    speak("Ji Samendra, boliye?")
                    sub_query = takecommand()
                    if not sub_query:
                        try:
                            eel.ShowHood()
                        except Exception:
                            pass
                        return
                    query = sub_query
                    query_lower = query.lower().strip()
                    break
                elif query_lower.startswith(ww + " ") or query_lower.startswith(ww + ","):
                    # User said 'Hey Jarvis <instruction>' -> Strip wake word and execute
                    query = query_lower[len(ww):].strip(" ,.-")
                    query_lower = query.lower().strip()
                    break

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

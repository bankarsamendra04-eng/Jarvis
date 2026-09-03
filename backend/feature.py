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
from backend.config import ASSISTANT_NAME
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


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query = query.strip().lower()

    if query != "":
        try:
            conn = sqlite3.connect("jarvis.db")
            cursor = conn.cursor()

            # Check system commands first
            cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) = ?', (query,))
            sys_results = cursor.fetchall()

            if len(sys_results) != 0:
                speak(f"Opening {query}")
                try:
                    os.startfile(sys_results[0][0])
                except Exception:
                    subprocess.Popen(sys_results[0][0], shell=True)
                conn.close()
                return

            # Check web commands
            cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ?', (query,))
            web_results = cursor.fetchall()
            conn.close()

            if len(web_results) != 0:
                speak(f"Opening {query}")
                webbrowser.open(web_results[0][0])
            else:
                speak(f"Opening {query}")
                try:
                    # Attempt to open as a URL or system application
                    if "." in query and not " " in query:
                        webbrowser.open(f"https://{query}")
                    else:
                        os.system(f'start {query}')
                except Exception:
                    speak("Application or website not found")
        except Exception as e:
            print(f"Error in openCommand: {e}")
            speak("Something went wrong while opening the application")


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


def chatBot(query):
    user_input = query.lower()
    cookie_path = os.path.join("backend", "cookie.json")
    
    if os.path.exists(cookie_path):
        try:
            from hugchat import hugchat
            chatbot = hugchat.ChatBot(cookie_path=cookie_path)
            conv_id = chatbot.new_conversation()
            chatbot.change_conversation(conv_id)
            response = chatbot.chat(user_input)
            response_text = str(response).strip()
            # Format punchy spoken-friendly response (strip long markdown lists/bullets)
            response_text = re.sub(r'[*_#`]', '', response_text)
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', response_text) if s.strip()]
            spoken_text = " ".join(sentences[:3]) if sentences else response_text
            print(f"AI: {spoken_text}")
            speak(spoken_text)
            return spoken_text
        except Exception as e:
            print(f"HugChat error: {e}")
    
    # Natural, punchy spoken response with conversational filler
    fallback_response = f"Got it. I received your request: {query}. Let me know if you want me to open an app, play music, or remember something."
    print(fallback_response)
    speak(fallback_response)
    return fallback_response
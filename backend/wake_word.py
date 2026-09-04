import os
import re
import time
import threading
import speech_recognition as sr
import eel
from typing import Tuple, Optional

# Global wake phrases
WAKE_PHRASES = [
    "hey jarvis",
    "hello jarvis",
    "ok jarvis",
    "okay jarvis",
    "hi jarvis",
    "sun jarvis",
    "jarvis"
]

def separate_wake_phrase(text: str) -> Tuple[bool, Optional[str], str]:
    """
    Case-insensitive, punctuation-tolerant wake phrase detector and command stripper.
    Returns: (is_wake_detected, detected_wake_phrase, remaining_command)
    """
    if not text:
        return False, None, ""

    raw = text.strip()
    # Normalize punctuation and extra spaces
    cleaned = re.sub(r'[!?,.:;]+', ' ', raw).strip().lower()

    for phrase in WAKE_PHRASES:
        # Check if text starts with wake phrase
        pattern_start = rf'^{re.escape(phrase)}(?:\s+|$)'
        match = re.search(pattern_start, cleaned)
        if match:
            # Wake phrase at beginning
            wake_len = len(phrase)
            # Find in original text preserving case for command
            rem_match = re.search(rf'^{re.escape(phrase)}[\s,!?:;]*(.*)', raw, re.IGNORECASE)
            cmd = rem_match.group(1).strip(" ,!?:;.-") if rem_match else ""
            return True, phrase, cmd

        # Check if text ends with wake phrase or contains it
        pattern_contains = rf'\b{re.escape(phrase)}\b'
        if re.search(pattern_contains, cleaned):
            # Strip the wake phrase from the query
            cmd = re.sub(rf'\b{re.escape(phrase)}\b[\s,!?:;]*', '', raw, flags=re.IGNORECASE).strip(" ,!?:;.-")
            return True, phrase, cmd

    return False, None, raw


class WakeWordListener:
    """
    Two-Stage Background Wake-Word Engine for JARVIS.
    Continuously listens for 'Hey Jarvis' / 'Hello Jarvis' without blocking UI,
    preventing duplicate microphone access, and reusing the main command pipeline.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(WakeWordListener, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._running = False
        self._paused = False
        self._thread = None
        self._pause_lock = threading.Lock()
        self._state = "IDLE"
        self._mic_error_count = 0
        self._initialized = True

    def get_state(self) -> str:
        return self._state

    def set_ui_state(self, state: str, message: Optional[str] = None):
        self._state = state
        try:
            if state in ["WAKE_WORD_DETECTED", "COMMAND_LISTENING", "LISTENING"]:
                eel.openMicUI()
                display_msg = message or "🎤 Listening..."
                eel.DisplayMessage(display_msg)
            elif state in ["PROCESSING", "THINKING"]:
                display_msg = message or "⚡ Thinking..."
                eel.DisplayMessage(display_msg)
            elif state in ["SPEAKING"]:
                display_msg = message or "🔊 Speaking..."
                eel.DisplayMessage(display_msg)
            elif state in ["ERROR"]:
                display_msg = message or "❌ Microphone Error"
                eel.DisplayMessage(display_msg)
            else:  # IDLE / WAKE_LISTENING
                eel.ShowHood()
                display_msg = message or "Say 'Hey Jarvis' or 'Hello Jarvis'"
                eel.DisplayMessage(display_msg)
        except Exception:
            pass

    def pause(self):
        """Temporarily pauses the background wake-word listener (e.g. during manual command or TTS)"""
        with self._pause_lock:
            self._paused = True
            print("[WAKE] Wake-word listener paused")

    def resume(self):
        """Resumes background wake-word listening"""
        with self._pause_lock:
            self._paused = False
            print("[WAKE] Wake-word listener resumed")

    def is_paused(self) -> bool:
        with self._pause_lock:
            return self._paused

    def start(self):
        """Starts the background wake-word listening thread"""
        if self._running:
            return
        self._running = True
        self._paused = False
        self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="JarvisWakeWordThread")
        self._thread.start()
        print("[WAKE] Wake-word listener started")

    def stop(self):
        """Stops the background listener"""
        self._running = False
        print("[WAKE] Wake-word listener stopped")

    def _listen_loop(self):
        r = sr.Recognizer()
        r.pause_threshold = 0.8
        r.non_speaking_duration = 0.5
        r.dynamic_energy_threshold = True

        print("[WAKE] Listening loop initialized. Waiting for 'Hey Jarvis' / 'Hello Jarvis'...")

        while self._running:
            if self._paused:
                time.sleep(0.15)
                continue

            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=0.4)
                    self._mic_error_count = 0

                    while self._running and not self._paused:
                        try:
                            # Lightweight audio listen chunk
                            audio = r.listen(source, timeout=3.0, phrase_time_limit=4.5)
                        except sr.WaitTimeoutError:
                            continue
                        except Exception as e:
                            # Break inner loop if microphone error
                            break

                        if self._paused:
                            break

                        # Transcribe audio chunk
                        try:
                            recognized_text = r.recognize_google(audio, language='en-IN')
                        except (sr.UnknownValueError, sr.RequestError):
                            try:
                                recognized_text = r.recognize_google(audio, language='en-US')
                            except Exception:
                                continue

                        if not recognized_text:
                            continue

                        print(f'[WAKE] Detected speech: "{recognized_text}"')
                        is_wake, wake_phrase, cmd = separate_wake_phrase(recognized_text)

                        if is_wake:
                            print(f'[WAKE] Wake phrase detected: "{wake_phrase}"')
                            # Pause wake-word listener to prevent duplicate microphone conflicts
                            self.pause()

                            # Trigger activation sound & UI
                            from backend.feature import play_assistant_sound
                            try:
                                play_assistant_sound()
                            except Exception:
                                pass

                            # If user provided trailing command in the same sentence
                            if cmd and len(cmd.strip()) > 1:
                                print(f'[VOICE] Extracted command from wake phrase: "{cmd}"')
                                self.set_ui_state("COMMAND_LISTENING", f'🎤 "{cmd}"')
                                self._dispatch_command(cmd)
                            else:
                                # User only said 'Hey Jarvis' -> Open command microphone
                                print("[VOICE] Activating command microphone")
                                self.set_ui_state("COMMAND_LISTENING", "🎤 Listening for your command...")
                                
                                from backend.command import takecommand
                                command_query = takecommand()

                                if command_query and len(command_query.strip()) > 0:
                                    print(f'[VOICE] Command received: "{command_query}"')
                                    print("[VOICE] Processing command")
                                    self._dispatch_command(command_query)
                                else:
                                    print("[VOICE] No command detected (timeout / silence)")
                                    from backend.command import speak
                                    speak("Okay, I'm waiting.")
                                    self.set_ui_state("IDLE")

                            # Command lifecycle complete -> Resume wake-word mode
                            self.set_ui_state("IDLE")
                            self.resume()
                            print("[WAKE] Returning to wake-word mode")

            except Exception as mic_err:
                self._mic_error_count += 1
                print(f"[WAKE] Recognition error: {mic_err}")
                if self._mic_error_count == 1:
                    self.set_ui_state("ERROR", "Microphone unavailable. Please check your microphone connection.")
                time.sleep(2.0)

    def _dispatch_command(self, query: str):
        """Executes the captured voice command through the unified command pipeline"""
        try:
            self.set_ui_state("PROCESSING", "⚡ Thinking...")
            from backend.command import execute_command
            execute_command(query, is_voice=True)
        except Exception as e:
            print(f"[VOICE] Execution error: {e}")
            from backend.command import speak
            speak("Sorry, command execute karte waqt kuch gadbad hui.")


# Singleton helper
_global_wake_listener: Optional[WakeWordListener] = None

def get_wake_word_listener() -> WakeWordListener:
    global _global_wake_listener
    if _global_wake_listener is None:
        _global_wake_listener = WakeWordListener()
    return _global_wake_listener

def start_wake_word_service():
    listener = get_wake_word_listener()
    listener.start()
    return listener

def pause_wake_word():
    get_wake_word_listener().pause()

def resume_wake_word():
    get_wake_word_listener().resume()

@eel.expose
def startWakeWordListener():
    start_wake_word_service()
    return {"status": "started"}

@eel.expose
def stopWakeWordListener():
    get_wake_word_listener().stop()
    return {"status": "stopped"}

@eel.expose
def getWakeWordStatus():
    listener = get_wake_word_listener()
    return {
        "running": listener._running,
        "paused": listener.is_paused(),
        "state": listener.get_state()
    }


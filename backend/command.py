import asyncio
import os
import re
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
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 165)
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as sapi_err:
        print(f"SAPI5 fallback error: {sapi_err}")
        return False


def speak(text, display_text=None):
    """
    Sends response to UI display and speaks aloud using Indian Neural TTS.
    Pauses wake listener during speech output.
    """
    text = str(text).strip()
    if not text:
        return
        
    to_display = display_text if display_text else text

    # Update UI to Speaking state
    try:
        eel.DisplayMessage("🔊 Speaking...")
        eel.receiverText(to_display)
    except Exception:
        pass

    try:
        from backend.db import store_message_log
        store_message_log("assistant", to_display)
        try:
            eel.refreshConversations()
        except Exception:
            pass
    except Exception:
        pass

    # Pause wake listener during speech playback to avoid feedback
    try:
        from backend.wake_word import pause_wake_word, resume_wake_word
        pause_wake_word()
        play_indian_tts(text)
    finally:
        try:
            eel.ShowHood()
            eel.DisplayMessage("Say 'Hey Jarvis' or 'Hello Jarvis'")
        except Exception:
            pass
        try:
            from backend.wake_word import resume_wake_word
            resume_wake_word()
        except Exception:
            pass


def takecommand(timeout=8, phrase_time_limit=10):
    """
    Captures command speech from microphone and transcribes to text.
    """
    r = sr.Recognizer()
    r.pause_threshold = 1.0
    r.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            print("[VOICE] Listening for command...")
            try:
                eel.openMicUI()
                eel.DisplayMessage("🎤 Listening...")
            except Exception:
                pass
            r.adjust_for_ambient_noise(source, duration=0.4)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        print("[VOICE] Command listening timed out.")
        return None
    except Exception as mic_err:
        print(f"[VOICE] Microphone input error: {mic_err}")
        try:
            eel.DisplayMessage("Microphone unavailable. Please check your connection.")
            eel.ShowHood()
        except Exception:
            pass
        return None

    try:
        print("[VOICE] Recognizing speech...")
        try:
            eel.DisplayMessage("⚡ Thinking...")
        except Exception:
            pass
        # en-IN recognizes English and Hinglish phrases with Indian dialect naturally
        try:
            query = r.recognize_google(audio, language='en-IN')
        except Exception:
            query = r.recognize_google(audio, language='hi-IN')
        
        print(f'[VOICE] User said: "{query}"')
        return query
    except sr.UnknownValueError:
        print("[VOICE] Could not understand audio")
        return None
    except Exception as e:
        print(f"[VOICE] Recognition Error: {str(e)}")
        return None


def execute_command(raw_query: str, is_voice: bool = False):
    """
    Unified Command Execution Pipeline for Voice, Wake-Word, and Text inputs.
    """
    if not raw_query or not raw_query.strip():
        try:
            eel.ShowHood()
        except Exception:
            pass
        return

    # 1. Clean wake words if present
    from backend.wake_word import separate_wake_phrase
    is_wake, wake_phrase, clean_cmd = separate_wake_phrase(raw_query)
    query = clean_cmd if (is_wake and clean_cmd) else raw_query
    query = query.strip(" ,.!?:;\"'")
    query_lower = query.lower()

    if not query:
        speak("Ji Samendra, main aapki kya madad kar sakta hoon?")
        return

    print(f'[PIPELINE] Executing Command: "{query}" (Source: {"Voice" if is_voice else "Text"})')

    # Display user text in UI
    try:
        eel.senderText(query)
    except Exception:
        pass

    try:
        from backend.db import store_message_log
        is_priority = any(w in query_lower for w in ["remember", "yaad rakh", "yaad karo", "save to memory", "save this to my memory"])
        store_message_log("user", query, is_priority_memory=is_priority)

        # Update Context & Check Ambiguity
        from backend.context_manager import get_context_manager
        cm = get_context_manager()
        cm.update_from_user_query(query)

        is_ambiguous, clarif_text = cm.check_ambiguity(query)
        if is_ambiguous and clarif_text:
            speak(clarif_text)
            return

        resolved_query, applied = cm.resolve_references(query)
        if applied:
            print(f"[Context Engine] Resolved '{query}' -> '{resolved_query}' (Context: {applied})")
        
        exec_query = resolved_query
        query_lower = exec_query.lower().strip()

        # 1. Memory Commands
        if any(w in query_lower for w in ["remember", "save to memory", "save this to my memory", "yaad rakh", "yaad karo"]):
            from backend.feature import rememberMemory
            rememberMemory(exec_query)
        elif any(w in query_lower for w in ["forget this", "forget memory", "forget about", "delete memory", "bhool jao"]):
            from backend.feature import forgetMemory
            forgetMemory(exec_query)
        elif any(w in query_lower for w in ["what do you remember", "recall", "my memories", "kya yaad hai", "memories batao", "mere baare mein kya yaad", "show my memories"]):
            from backend.feature import recallMemories
            recallMemories(exec_query)
        elif any(w in query_lower for w in ["update my profile", "update my skills", "update my details", "profile update"]):
            from backend.feature import updateProfileMemory
            updateProfileMemory(exec_query)

        # 2. Goal & Progress Tracking Commands
        elif any(w in query_lower for w in ["what should i work on today", "what to do today", "aaj kya karu", "aaj kya karna hai", "action plan", "daily action plan", "today plan"]):
            from backend.goals_manager import get_daily_action_plan_voice
            res = get_daily_action_plan_voice()
            speak(res)
        elif any(w in query_lower for w in ["closest to completion", "closest goal", "kaun sa goal complete hone wala hai", "which goal is closest"]):
            from backend.goals_manager import get_closest_to_completion_goal
            res = get_closest_to_completion_goal()
            speak(res)
        elif any(w in query_lower for w in ["create a new goal", "create new goal", "add a new goal", "add new goal", "naya goal banao", "new goal"]):
            try:
                eel.openGoalModal()
            except Exception:
                pass
            speak("Goal create karne ke liye dashboard open kar diya hai. Aap details enter kar sakte hain.")
        elif any(w in query_lower for w in ["update my progress", "update progress", "progress update", "goal progress"]):
            from backend.goals_manager import update_goal_progress_voice
            success, res = update_goal_progress_voice(exec_query)
            speak(res)
        elif any(w in query_lower for w in ["show my goals", "show goals", "my goals", "goals dikhao", "active goals", "kya goals hain", "goals batao"]):
            from backend.goals_manager import get_goals_voice_summary
            res = get_goals_voice_summary()
            try:
                eel.openGoalsDashboard()
            except Exception:
                pass
            speak(res)

        # 3. AI Study Mode Commands
        elif any(w in query_lower for w in ["start study mode", "enable study mode", "study mode on", "padhai shuru karo", "study mode start"]):
            from backend.study_manager import start_study_mode_voice
            res = start_study_mode_voice(exec_query)
            speak(res)
        elif any(w in query_lower for w in ["stop study mode", "exit study mode", "study mode off", "padhai band karo"]):
            from backend.study_manager import stopStudyMode
            stopStudyMode()
            speak("AI Study Mode band kar diya gaya hai. Shabash Samendra!")
        elif any(w in query_lower for w in ["take my viva", "viva question", "viva lo", "take viva"]):
            from backend.study_manager import get_viva_voice
            res = get_viva_voice(exec_query)
            speak(res)
        elif any(w in query_lower for w in ["show my weak topics", "weak topics", "mere weak topics", "weak areas"]):
            from backend.study_manager import get_weak_topics_voice
            res = get_weak_topics_voice()
            speak(res)
        elif any(w in query_lower for w in ["revise today's topics", "revise today", "revision session", "revise weak topics", "revision karo"]):
            from backend.study_manager import get_revision_voice
            res = get_revision_voice()
            speak(res)

        # 4. Applications, Files, WhatsApp & YouTube
        elif any(w in query_lower for w in ["open", "launch", "show picture", "show photo", "show file", "show document", "start app", "kholo", "open karo", "chalu karo", "dikhao"]) and not any(k in query_lower for k in ["create", "make", "project", "code"]):
            from backend.feature import openCommand
            openCommand(exec_query)
        elif "send message" in query_lower or "call" in query_lower or "video call" in query_lower or "message bhejo" in query_lower:
            from backend.feature import findContact, whatsApp
            flag = ""
            Phone, name = findContact(exec_query)
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
            PlayYoutube(exec_query)

        # 5. Master Intent Router & Knowledge / Coding Engine
        else:
            try:
                from backend.memory_manager import auto_detect_worth_remembering, add_user_memory
                should_rem, rem_content, rem_cat = auto_detect_worth_remembering(exec_query)
                if should_rem and rem_content:
                    add_user_memory(rem_cat, rem_content, source="auto_extracted")
            except Exception:
                pass

            from backend.intent_engine import process_user_query_with_intent
            display_content, spoken_text = process_user_query_with_intent(exec_query)
            print(f"[PIPELINE] Jarvis Spoken: {spoken_text}")
            speak(spoken_text, display_text=display_content)

    except Exception as e:
        print(f"[PIPELINE] Error during execution: {e}")
        speak("Sorry, command execute karte waqt kuch gadbad hui.")


@eel.expose
def takeAllCommands(message=None):
    """
    Exposed Eel endpoint triggered by Voice Mic button (#MicBtn), Win+J shortcut, or chatbox text input.
    """
    from backend.wake_word import pause_wake_word, resume_wake_word
    
    # Temporarily pause background wake-word listener to avoid microphone conflict
    pause_wake_word()

    try:
        if message is None or message == "":
            query = takecommand()  # Voice input from button / Win+J
            if query:
                execute_command(query, is_voice=True)
            else:
                try:
                    eel.ShowHood()
                    eel.DisplayMessage("Say 'Hey Jarvis' or 'Hello Jarvis'")
                except Exception:
                    pass
        else:
            execute_command(message, is_voice=False)  # Text input
    finally:
        resume_wake_word()


@eel.expose
def getActiveConversationContext():
    from backend.context_manager import get_context_manager
    return get_context_manager().get_context()


@eel.expose
def resetConversationContext():
    from backend.context_manager import get_context_manager
    get_context_manager().reset_context()
    return {"status": "success"}


@eel.expose
def getCodingAgentProjectTree(project_name=None):
    from backend.coding_agent import get_coding_agent
    return get_coding_agent().get_project_tree(project_name)


@eel.expose
def runSandboxCommand(command):
    from backend.coding_agent import get_coding_agent
    disp, spoken = get_coding_agent().run_sandbox_command(command)
    return {"display": disp, "spoken": spoken}


@eel.expose
def prepareProjectForGitHub(project_name=None):
    from backend.coding_agent import get_coding_agent
    disp, spoken = get_coding_agent().prepare_for_github(project_name)
    return {"display": disp, "spoken": spoken}

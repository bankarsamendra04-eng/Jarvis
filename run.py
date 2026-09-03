import multiprocessing
import sys

def startJarvis():
    print("Process 1: Starting Jarvis Eel GUI & Assistant Engine...")
    from main import start
    start()
    
def listenHotword():
    print("Process 2: Starting Background Hotword Listener...")
    try:
        from backend.feature import hotword
        hotword()
    except Exception as e:
        print(f"Hotword process notice: {e}")
    
if __name__ == "__main__":
    multiprocessing.freeze_support()
    process1 = multiprocessing.Process(target=startJarvis)
    process2 = multiprocessing.Process(target=listenHotword)
    
    process1.start()
    process2.start()
    
    process1.join()
    
    if process2.is_alive():
        process2.terminate()
        print("Hotword listener terminated.")
        process2.join()
        
    print("Jarvis System terminated.")
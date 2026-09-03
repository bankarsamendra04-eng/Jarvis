import os
import json

ASSISTANT_NAME = "jarvis"
USER_NAME = "Samendra Bankar"

def load_user_profile():
    profile_path = os.path.join(os.path.dirname(__file__), "user_profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}
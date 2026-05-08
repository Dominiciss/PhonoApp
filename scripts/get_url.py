import sys
import os
import json

settings_file = None

def resource_path(relative_path):
    """Get absolute path to resource"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_base_dir():
    """
    Safely get the directory where the .exe or .py file is located.
    This prevents saving data in PyInstaller's temporary MEIPASS folder.
    """
    if getattr(sys, 'frozen', False):
        # We are running as a PyInstaller compiled executable
        return os.path.dirname(sys.executable)
    else:
        # We are running as a normal Python script
        return os.path.dirname(os.path.abspath("main.py"))

def load_variables():
    """Load variables from the JSON file, or return defaults if it doesn't exist."""
    from main import settings_file

    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            return json.load(file)
    else:
        # Default variables if the file hasn't been created yet
        return {
            "show_overlay": 1,
            "overlay_position": 0,
        }

def save_variables(data):
    """Save the dictionary of variables back to the JSON file."""
    from main import settings_file

    with open(settings_file, 'w') as file:
        json.dump(data, file, indent=4)
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If we are just running the normal .py script, use the current folder
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
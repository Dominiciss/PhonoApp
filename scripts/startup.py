import sys
import os
import winreg

APP_NAME = "PhonoScribe"  # Change this to your app's name

def get_app_path():
    # This gets the exact path to your script (or .exe if you compile it later)
    script_path = os.path.abspath(sys.argv[0])
    
    # If running as a Python script, we need to tell Windows to use Python to open it
    if script_path.endswith('.py') or script_path.endswith('.pyw'):
        python_exe = sys.executable
        return f'"{python_exe}" "{script_path}"'
    
    # If it's a compiled .exe, just return the path
    return f'"{script_path}"'

def check_startup_status():
    # Checks if the app is currently set to run at startup
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False

def toggle_startup(enable):
    # Adds or removes the app from the registry based on the checkbox
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
    
    if enable:
        app_path = get_app_path()
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, app_path)
        print("Startup enabled!")
    else:
        try:
            winreg.DeleteValue(key, APP_NAME)
            print("Startup disabled!")
        except FileNotFoundError:
            pass # It was already disabled
            
    winreg.CloseKey(key)
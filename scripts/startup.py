import sys
import os
import winreg

APP_NAME = "PhonoScribe"

def get_app_path():
    script_path = os.path.abspath(sys.argv[0])
    
    if script_path.endswith('.py') or script_path.endswith('.pyw'):
        python_exe = sys.executable
        return f'"{python_exe}" "{script_path}"'
    
    return f'"{script_path}"'

def check_startup_status():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False

def toggle_startup(enable):
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
            pass
            
    winreg.CloseKey(key)
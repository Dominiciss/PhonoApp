# create .exe: pyinstaller --onefile --icon=logo.png --add-data="logo.png;." --name=PhonoScribe --windowed main.py

# Dependency imports
from PIL import Image
from tkinter import messagebox
from keyboard import KeyboardEvent
import keyboard
import pystray
import threading
import ctypes
import webbrowser
import pyperclip
import time

# Own scripts
import scripts.get_url as get_url
import scripts.toast as toast
import scripts.menu as menu
import scripts.toggle_keyboard as toggle_keyboard
import scripts.cycle_map as cycle_map
import scripts.transcriptor as transcriptor
import scripts.github

VERSION = 'v1.2.2'
APP_NAME = 'PhonoScribe'
APP_ID = 'phonoscribe.transcription.utility'
ICON = Image.open(get_url.resource_path('logo.png'))
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

last_key = None
toggle_phonemes = True
first_check = True
listeners = []

def transcribe_popup():
    """Shortcut for transcribing and pasting the text in the user's clipboard"""
    start_time = time.perf_counter()
    print("Transcription started")
    clipboard = pyperclip.paste()

    if clipboard is not None:
        toast.show_toast("Making transcription. Please wait...")
        try:
            transcription = transcriptor.get_ipa(clipboard)
            pyperclip.copy(transcription)
            toast.show_toast("Transcription copied to the clipboard!")
            print(f"Transcription copied. Time ellapsed: {time.perf_counter() - start_time}")
        except:
            toast.show_toast("Transcription failed. Do you have internet connection?")
            print(f"Transcription failed. Couldn't connect to the server. Time ellapsed: {time.perf_counter() - start_time}")
    else:
        toast.show_toast("Clipboard did not have information")
        print(f"Transcription failed. Clipboard did not have information. Time ellapsed: {time.perf_counter() - start_time}")

def toggle_window(event: KeyboardEvent):
    menu.root.withdraw() if menu.root.winfo_viewable() else menu.root.deiconify()

def start_transcription(event: KeyboardEvent):
    menu.root.after(0, transcribe_popup)

def on_alt(event: KeyboardEvent):
    global listeners
    global first_check

    if event.event_type == keyboard.KEY_DOWN:
        listeners.append(keyboard.on_press_key(59, toggle_window, suppress=True))
        listeners.append(keyboard.on_press_key(60, start_transcription, suppress=True))
        for data in cycle_map.cycle_map.values():
            listeners.append(keyboard.on_press_key(data['scan_code'], write_symbol, suppress=True))
    elif event.event_type == keyboard.KEY_UP:
        first_check = True
        for data in cycle_map.cycle_map.values():
            data['symbol_state'] = 0
        for item in listeners:
            keyboard.unhook(item)
        listeners = []

def write_symbol(event: KeyboardEvent):
    """Writes the assigned symbol for a specific letter as shown in cycle_map.py"""
    global first_check
    global last_key

    for data in cycle_map.cycle_map.values():
        if data['scan_code'] == event.scan_code:
            letter = data

    start_time = time.perf_counter()
    print("Symbol writing started")

    try:
        if last_key is not None:
            if last_key != letter['scan_code']:
                first_check = True
                for key, data in cycle_map.cycle_map.items():
                    if data['scan_code'] != letter['scan_code']:
                        data['symbol_state'] = 0

        if not first_check:
            keyboard.send('backspace')

        keyboard.write(letter['symbols'][letter['symbol_state']])

        if letter['symbol_state'] >= len(letter['symbols']) - 1:
            letter['symbol_state'] = 0
        else:
            letter['symbol_state'] += 1
        
        print(f"Symbol was written. Time ellapsed: {time.perf_counter() - start_time}")
    except Exception as e:
        print(f"Couldn't write symbol due to {e}. Time ellapsed: {time.perf_counter() - start_time}")

    last_key = letter['scan_code']
    first_check = False

def call_toggle():
    """Changes the state of toggle_phonemes and enables/disables the phonetic keyboard"""
    global ICON
    global toggle_phonemes
    global system_tray

    start_time = time.perf_counter()
    print("Toggle process started...")

    toggle_phonemes = toggle_keyboard.toggle_phonetic_keyboard(toggle_phonemes, ICON, system_tray)

def update_checker():
    """Checks for new updates in the github repository"""
    start_time = time.perf_counter()
    print("Checking for updates...")

    repo = scripts.github.get_repo()

    if (repo is not None):
        github_version = scripts.github.get_latest(repo)

        if (VERSION != github_version):
            print(f"Version {github_version} found. Time ellapsed: {time.perf_counter() - start_time}")

            user_answer = messagebox.askyesno("Confirm Action", f"Do you want to download the version {github_version}?")
            
            if (user_answer):
                webbrowser.open(f"https://github.com/Dominiciss/PhonoScribe/releases/tag/{github_version}")
        else:
            print(f"Version {github_version} found was not newer than client version {VERSION}. Time ellapsed: {time.perf_counter() - start_time}")
            toast.show_toast("You have the latest version available!")
    else:
        print(f"Couldn't connect with GitHub's api. Time ellapsed: {time.perf_counter() - start_time}")
        toast.show_toast("Error produced when looking for updates. Do you have internet connection?")

if __name__ == '__main__':
    menu.create_tk()
    toast.popup_start()
    toast.show_toast("Welcome to PhonoScribe, your Phonetic Keyboard!\nIf you have any doubts, press Alt gr + F1 to open the main menu!", 6)
    system_tray = pystray.Icon('PhonoScribe', ICON, 'PhonoScribe')

    print("App started")

    # keyboard.add_hotkey("alt gr + enter", call_toggle, suppress=True)
    keyboard.hook_key("alt gr", on_alt, suppress=True) 

    system_tray.menu = pystray.Menu(
        pystray.MenuItem('Info', lambda: menu.root.deiconify()),
        pystray.MenuItem('Toggle', lambda: call_toggle()),
        pystray.MenuItem('Check for updates', lambda: update_checker()),
        pystray.MenuItem('Exit', lambda: menu.root.destroy())
    )
    
    threading.Thread(target=system_tray.run, daemon=True).start()

    menu.root.mainloop()
# create .exe: pyinstaller --onefile --icon=logo.png --add-data="logo.png;." --name=PhonoScribe --windowed main.py

# Dependency imports
from PIL import Image
from tkinter import messagebox
import keyboard
import pystray
import threading
import ctypes
import webbrowser
import pyperclip
import time
import logging

# Own scripts
import scripts.get_url as get_url
import scripts.toast as toast
import scripts.menu as menu
import scripts.toggle_keyboard as toggle_keyboard
import scripts.cycle_map as cycle_map
import scripts.transcriptor as transcriptor
import scripts.github

VERSION = 'v1.2.0'
APP_NAME = 'PhonoScribe'
APP_ID = 'phonoscribe.transcription.utility'
ICON = Image.open(get_url.resource_path('logo.png'))
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

last_key = None
toggle_phonemes = True
first_check = True

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

def write_symbol(letter):
    """Writes the assigned symbol for a specific letter as shown in cycle_map.py"""
    global first_check
    global last_key

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

def on_alt_released(event: keyboard.KeyboardEvent) -> None:
    """On alt release, resets symbols state and its bools"""
    global first_check
    global last_key

    first_check = True
    last_key = None
    for letter, data in cycle_map.cycle_map.items():
        data['symbol_state'] = 0

def call_toggle():
    """Changes the state of toggle_phonemes and enables/disables the phonetic keyboard"""
    global ICON
    global toggle_phonemes
    global system_tray

    start_time = time.perf_counter()
    print("Toggle process started...")

    if toggle_phonemes:
        keyboard.remove_hotkey("alt gr + f1")
        keyboard.remove_hotkey("alt gr + f2")
        for letter, data in cycle_map.cycle_map.items():
            data['symbol_state'] = 0
            hotkey_str = f"alt gr + {data['letter']}"
            keyboard.remove_hotkey(hotkey_str)
        print(f"Symbols disabled. Time ellapsed: {time.perf_counter() - start_time}")
    else:
        keyboard.add_hotkey("alt gr + f1", lambda: menu.root.withdraw() if menu.root.winfo_viewable() else menu.root.deiconify(), suppress=True)
        keyboard.add_hotkey("alt gr + f2", lambda: menu.root.after(0, transcribe_popup), suppress=True)
        for letter, data in cycle_map.cycle_map.items():
            hotkey_str = f"alt gr + {data['letter']}"
            keyboard.add_hotkey(hotkey_str, write_symbol, args=[data], suppress=True)
        print(f"Symbols enabled. Time ellapsed: {time.perf_counter() - start_time}")

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

    keyboard.on_release_key("alt gr", on_alt_released, suppress=False)
    keyboard.add_hotkey("alt gr + enter", call_toggle, suppress=True)
    keyboard.add_hotkey("alt gr + f1", lambda: menu.root.withdraw() if menu.root.winfo_viewable() else menu.root.deiconify(), suppress=True)
    keyboard.add_hotkey("alt gr + f2", lambda: menu.root.after(0, transcribe_popup), suppress=True)
    for letter, data in cycle_map.cycle_map.items():
        hotkey_str = f"alt gr + {data['letter']}"
        keyboard.add_hotkey(hotkey_str, write_symbol, args=[data], suppress=True)

    system_tray.menu = pystray.Menu(
        pystray.MenuItem('Info', lambda: menu.root.deiconify()),
        pystray.MenuItem('Toggle', lambda: call_toggle()),
        pystray.MenuItem('Check for updates', lambda: update_checker()),
        pystray.MenuItem('Exit', lambda: menu.root.destroy())
    )
    
    threading.Thread(target=system_tray.run, daemon=True).start()

    menu.root.mainloop()
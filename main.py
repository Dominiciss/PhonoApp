# create .exe: pyinstaller --onefile --icon=logo.png --add-data="logo.png;." --name=PhonoScribe --windowed main.py

# Dependency imports
from PIL import Image
from tkinter import messagebox
import keyboard
import pystray
import threading
import ctypes
import webbrowser
import time
import logging

# Own scripts
import scripts.get_url as get_url
import scripts.toast as toast
import scripts.menu as menu
import scripts.toggle_keyboard as toggle_keyboard
import scripts.cycle_map as cycle_map
import scripts.github


#logging.basicConfig(filename="app.log", level=logging.INFO)
#logging.info("App started")

VERSION = 'v1.0.1'
APP_NAME = 'PhonoScribe'
APP_ID = 'phonoscribe.transcription.utility'
ICON = Image.open(get_url.resource_path('logo.png'))
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

repo = scripts.github.get_repo()
alt_pressed = False
last_key = None
toggle_phonemes = True
first_check = True

def is_altgr_pressed() -> bool:
    return keyboard.is_pressed(514) or (
        keyboard.is_pressed(29) and keyboard.is_pressed(56)
    ) or keyboard.is_pressed('alt gr')

def on_key(event: keyboard.KeyboardEvent) -> bool:
    global last_key
    global alt_pressed
    global toggle_phonemes

    last_key = event.scan_code

    if is_altgr_pressed():
        alt_pressed = True

        if toggle_phonemes and not keyboard._hotkeys:
            for letter, data in cycle_map.cycle_map.items():
                hotkey_str = f"alt gr + {data['letter']}"
                keyboard.add_hotkey(hotkey_str, write_symbol, args=[data], suppress=True)

        if event.scan_code == 28:
            call_toggle()       

        if event.scan_code == 59:
            if menu.root.winfo_viewable():
                menu.root.withdraw()
            else:
                menu.root.deiconify() 
    else:
        for key, data in cycle_map.cycle_map.items():
            data['symbol_state'] = 0

    return alt_pressed

def write_symbol(letter):
    global first_check

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

    first_check = False

def on_alt_released(event: keyboard.KeyboardEvent) -> None:
    global alt_pressed

    if event.event_type == keyboard.KEY_UP and (event.scan_code == 514 or (event.scan_code == 29 and event.scan_code == 56) or event.name in ('alt gr', 'right alt', 'alt')):
        alt_pressed = False

        if keyboard._hotkeys:
            for letter, data in cycle_map.cycle_map.items():
                data['symbol_state'] = 0
                hotkey_str = f"alt gr + {data['letter']}"
                keyboard.remove_hotkey(hotkey_str)

def call_toggle():
    global ICON
    global toggle_phonemes
    global system_tray

    if keyboard._hotkeys:
            for letter, data in cycle_map.cycle_map.items():
                data['symbol_state'] = 0
                hotkey_str = f"alt gr + {data['letter']}"
                keyboard.remove_hotkey(hotkey_str)

    toggle_phonemes = toggle_keyboard.toggle_phonetic_keyboard(toggle_phonemes, ICON, system_tray)

def update_checker():
    global repo

    if (repo is not None):
        github_version = scripts.github.get_latest(repo)
        if (VERSION != github_version):
            user_answer = messagebox.askyesno("Confirm Action", f"Do you want to download the version {github_version}?")
            
            if (user_answer):
                webbrowser.open(f"https://github.com/Dominiciss/PhonoScribe/releases/tag/{github_version}")
        else:
            toast.show_toast("You have the latest version available!")
    else:
        repo = scripts.github.get_repo()
        toast.show_toast("Error produced when looking for updates. Do you have internet connection?")

if __name__ == '__main__': 
    menu.create_tk()
    toast.show_toast("Welcome to PhonoScribe, your Phonetic Keyboard!\nIf you have any doubts, press Alt gr + F1 to open the main menu!", 6)
    system_tray = pystray.Icon('PhonoScribe', ICON, 'PhonoScribe')

    keyboard.on_press(on_key)
    keyboard.on_release_key("alt gr", on_alt_released, suppress=False)

    system_tray.menu = pystray.Menu(
        pystray.MenuItem('Info', lambda: menu.root.deiconify()),
        pystray.MenuItem('Toggle', lambda: call_toggle()),
        pystray.MenuItem('Check for updates', lambda: update_checker()),
        pystray.MenuItem('Exit', lambda: menu.root.destroy())
    )
    
    threading.Thread(target=system_tray.run, daemon=True).start()

    menu.root.mainloop()
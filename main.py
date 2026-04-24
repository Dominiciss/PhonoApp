# create .exe: pyinstaller --onefile --icon=logo.png --add-data="logo.png;." --name=PhonoScribe --windowed main.py

# Dependency imports
from PIL import Image
import keyboard
import pystray
import threading
import ctypes
import time
import logging

# Own scripts
import scripts.get_url as get_url
import scripts.toast as toast
import scripts.menu as menu
import scripts.toggle_keyboard as toggle_keyboard

#logging.basicConfig(filename="app.log", level=logging.INFO)
#logging.info("App started")

cycle_map = {
    # --- ALT + [KEY] (Base Phonetics) ---
    30: ['ɑ', 'æ', 'ʌ'],
    48: ['β'],
    32: ['ð'],
    18: ['ə', 'ᵊ', 'ɛ', 'ɜ'],
    33: ['‿'],
    34: ['ɣ'],
    35: ['ʰ'],
    23: ['ɪ'],
    36: ['ʲ'],
    38: ['ɫ'],
    50: ['ɱ'],
    49: ['ñ', 'ŋ', 'ɲ'],
    24: ['ɔ', 'ɒ'],
    19: ['ɾ'],
    31: ['ʃ'],
    20: ['θ', 'ʔ'],
    22: ['ʊ'],
    47: ['ʌ'],
    44: ['ʒ'],
    17: ['ʷ'],

    52: ['ː'],

    2: ['|', '‖'],
    3: ['ˈ', 'ˌ'],
    4: ['̥', '̊'],
    5: ['̪'],
    6: ['̩'],
    7: ['̚'],
    8: ['↗', '↘', 'ꜜ', 'ꜛ'],
    9: ['ˊ', 'ˋ', 'ˏ', 'ˎ'],
    10: ['ˇ', 'ˆ'],
    11: ['<', '>'],

    77: ['→'],
}

APP_NAME = 'PhonoScribe'
APP_ID = 'phonoscribe.transcription.utility'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

cycle_index = {key: 0 for key in cycle_map}
toggle_phonemes = True
first_check = False
previous_letter = -1
icon = Image.open(get_url.resource_path('logo.png'))

def is_altgr_pressed() -> bool:
    return keyboard.is_pressed(514) or (
        keyboard.is_pressed(29) and keyboard.is_pressed(56)
    ) or keyboard.is_pressed('alt gr')

def reset_cycle_states() -> None:
    for key in cycle_index:
        cycle_index[key] = 0

def on_key(event: keyboard.KeyboardEvent) -> bool:
    global previous_letter
    global first_check
    global toggle_phonemes
    global system_tray

    if event.event_type != keyboard.KEY_DOWN or "Unknown" in event.__str__():
        return True

    altgr_pressed = is_altgr_pressed()
    if altgr_pressed and event.scan_code != 28 and event.scan_code != 25:
        for letter in cycle_map:
            if (letter == event.scan_code and toggle_phonemes):
                symbol = cycle_map[letter][cycle_index[letter]]

                if (first_check and previous_letter == event.scan_code):
                    keyboard.send('backspace')
                first_check = True

                keyboard.write(symbol, delay=0)

                if (cycle_index[letter] >= len(cycle_map[letter]) - 1):
                    cycle_index[letter] = 0
                else:
                    cycle_index[letter] = cycle_index[letter] + 1

                previous_letter = event.scan_code
                return False
    elif altgr_pressed and event.scan_code == 28 and event.scan_code != 25:
        call_toggle()
    elif altgr_pressed and event.scan_code == 25:
        if menu.root.winfo_viewable():
            menu.root.withdraw()
        else:
            menu.root.deiconify()

    return True

def on_key_release(event: keyboard.KeyboardEvent) -> None:
    if event.event_type == keyboard.KEY_UP and (event.scan_code == 514 or (event.scan_code == 29 and event.scan_code == 56) or event.name in ('alt gr', 'right alt', 'alt')):
        global first_check
        
        first_check = False
        reset_cycle_states()

def call_toggle():
    global toggle_phonemes
    global icon
    global system_tray

    toggle_phonemes = toggle_keyboard.toggle_phonetic_keyboard(toggle_phonemes, icon, system_tray)

if __name__ == '__main__': 
    menu.create_tk()
    toast.show_toast("Welcome to PhonoApp, your Phonetic Keyboard!\nIf you have any doubts, press Alt gr + P to open the main menu!", 6)
    system_tray = pystray.Icon('TypeIt', icon, 'Phonetic Keyboard')

    keyboard.hook(on_key, suppress=True)
    keyboard.on_release(on_key_release)

    system_tray.menu = pystray.Menu(
        pystray.MenuItem('Info', lambda: menu.root.deiconify()),
        pystray.MenuItem('Toggle', lambda: call_toggle()),
        pystray.MenuItem('Exit', lambda: menu.root.destroy())
    )
    
    threading.Thread(target=system_tray.run, daemon=True).start()

    menu.root.mainloop()
    
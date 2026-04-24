# create .exe: pyinstaller --onefile --icon=icon.ico --windowed main.py

from PIL import Image, ImageTk
import tkinter as tk
import keyboard
import pystray
import threading
import time
import logging

#logging.basicConfig(filename="app.log", level=logging.INFO)
#logging.info("App started")

cycle_map = {
    # --- ALT + [KEY] (Base Phonetics) ---
    30: ['ɑ', 'æ', 'ʌ'],
    48: ['β'],
    32: ['ð'],
    18 : ['ə', 'ᵊ', 'ɛ', 'ɜ'],
    33: ['‿'],
    34: ['ɣ'],
    35: ['ʰ'],
    23: ['ɪ'],
    36: ['ʲ'],
    37: ['|', '‖'],
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
    8: ['↗', '↘'],
    9: ['→'],
    11: ['ꜜ', 'ꜛ'],

    77: ['→'],
}

cycle_index = {key: 0 for key in cycle_map}
toggle_phonemes = True
first_check = False
previous_letter = -1
icon = Image.open('icon.ico')

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

    if event.event_type != keyboard.KEY_DOWN or "Unknown" in event.__str__():
        return True

    altgr_pressed = is_altgr_pressed()
    if altgr_pressed and event.scan_code != 28:
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
    elif altgr_pressed and event.scan_code == 28:
        toggle_phonemes = not toggle_phonemes

        if (toggle_phonemes):
            show_toast("Phonetic keyboard enabled.")
        else:
            show_toast("Phonetic keyboard disabled.")

    return True

def on_key_release(event: keyboard.KeyboardEvent) -> None:
    if event.event_type == keyboard.KEY_UP and (event.scan_code == 514 or (event.scan_code == 29 and event.scan_code == 56) or event.name in ('alt gr', 'right alt', 'alt')):
        global first_check
        
        first_check = False
        reset_cycle_states()

def toggle_phonetic_keyboard() -> None:
    global toggle_phonemes
    toggle_phonemes = not toggle_phonemes
    if (toggle_phonemes):
        show_toast("Phonetic keyboard enabled.")
    else:
        show_toast("Phonetic keyboard disabled.")

# Display a small, non-intrusive popup message.
def show_toast(message, duration=3):
    def _popup():
        root = tk.Tk()
        root.overrideredirect(True)  # Remove window borders
        root.attributes("-topmost", True)  # Keep on top
        root.attributes("-alpha", 0.9)  # Slight transparency

        # Create label with message
        label = tk.Label(root, text=message, bg="#333", fg="white",
                         font=("Segoe UI", 10), padx=10, pady=5)
        label.pack()

        # Position bottom-right corner of the screen
        root.update_idletasks()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = root.winfo_width()
        window_height = root.winfo_height()
        x = screen_width - window_width - 20
        y = screen_height - window_height - 50
        root.geometry(f"+{x}+{y}")

        # Auto-close after duration
        root.after(duration * 1000, root.destroy)
        root.mainloop()

    # Run popup in a separate thread so it doesn't block the main process
    threading.Thread(target=_popup, daemon=True).start()

def create_tk():
    global root
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", root.withdraw)  # Hide window instead of closing
    root.withdraw()  # Hide the main window
    root.configure(bg="white")
    root.geometry("400x300")

    info_text = ("Phonetic Keyboard\n\n"
                 "Hold ALT GR and press the following keys to cycle through phonetic symbols:\n\n")
    
    image = Image.open('./shortcuts.png')
    shortcuts = ImageTk.PhotoImage(image)

    label = tk.Label(root, text=info_text, bg="white", fg="black", font=("Segoe UI", 10), padx=10, pady=5)
    label.pack()

    image_label = tk.Label(root, image=shortcuts, bg="white")
    image_label.image = shortcuts  # Keep a reference to prevent garbage collection
    image_label.pack()

if __name__ == '__main__': 
    create_tk()
    show_toast("Welcome to PhonoApp, your Phonetic Keyboard!")
    system_tray = pystray.Icon('TypeIt', icon, 'Phonetic Keyboard')

    keyboard.hook(on_key, suppress=True)
    keyboard.on_release(on_key_release)

    system_tray.menu = pystray.Menu(
        pystray.MenuItem('Info', lambda: root.deiconify()),
        pystray.MenuItem('Toggle', lambda: toggle_phonetic_keyboard()),
        pystray.MenuItem('Exit', lambda: system_tray.stop())
    )
    
    threading.Thread(target=system_tray.run, daemon=True).start()

    root.mainloop()

    
# create .exe: pyinstaller --onefile --icon=logo.png --add-data="logo.png;." --name=PhonoScribe --windowed main.py

# Dependency imports
from tkinter import messagebox
from PIL import Image, ImageOps, ImageTk
import tkinter as tk
from tkinter import ttk
import keyboard
import pystray
import threading
import ctypes
import time
import logging

# Own scripts
import scripts.startup as startup
import scripts.get_url as get_url

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
            system_tray.icon = icon
        else:
            show_toast("Phonetic keyboard disabled.")
            system_tray.icon = get_disabled_icon(icon)

    return True

def on_key_release(event: keyboard.KeyboardEvent) -> None:
    if event.event_type == keyboard.KEY_UP and (event.scan_code == 514 or (event.scan_code == 29 and event.scan_code == 56) or event.name in ('alt gr', 'right alt', 'alt')):
        global first_check
        
        first_check = False
        reset_cycle_states()

def get_disabled_icon(icon):
    img = icon.convert("RGBA")
    
    r, g, b, a = img.split()
    
    grayscale = ImageOps.grayscale(img)
    
    disabled_img = Image.merge("RGBA", (grayscale, grayscale, grayscale, a))
    
    return disabled_img

def toggle_phonetic_keyboard() -> None:
    global toggle_phonemes
    global system_tray
    toggle_phonemes = not toggle_phonemes
    if (toggle_phonemes):
        show_toast("Phonetic keyboard enabled.")
        system_tray.icon = icon
    else:
        show_toast("Phonetic keyboard disabled.")
        system_tray.icon = get_disabled_icon(icon)

# Display a small, non-intrusive popup message.
def show_toast(message, duration=3):
    def _popup():
        popup = tk.Tk()
        popup.attributes("-alpha", 0.9)
        popup.overrideredirect(True)  # Remove window borders
        popup.attributes("-topmost", True)  # Keep on top
        popup.configure(bg="white")

        header_frame = tk.Frame(popup, bg="white")
        header_frame.pack(pady=(5, 0), padx=(10, 0), anchor="w")

        raw_image = Image.open(get_url.resource_path("logo.png"))
        app_logo = ImageTk.PhotoImage(raw_image.resize((20, 20), Image.Resampling.LANCZOS), master=header_frame)
        image_label = tk.Label(header_frame, image=app_logo, bg="white")
        image_label.image = app_logo
        image_label.pack(side="left", padx=(0, 5))

        title_label = tk.Label(header_frame, text="PhonoScribe", font=("Segoe UI", 12, "bold italic"), bg="white", foreground="#612b6e")
        title_label.pack(side="left")

        custom_line = tk.Frame(popup, bg="#612b6e", height=1)
        custom_line.pack(fill="x", padx=10, pady=0)

        label = tk.Label(popup, text=message, bg="white", fg="black",
                         font=("Segoe UI", 10), padx=10, pady=5)
        label.pack()

        # Position bottom-right corner of the screen
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        window_width = popup.winfo_width()
        window_height = popup.winfo_height()
        x = screen_width - window_width - 20
        y = screen_height - window_height - 50
        popup.geometry(f"+{x}+{y}")

        # Auto-close after duration
        popup.after(duration * 1000, popup.destroy)
        popup.mainloop()

    # Run popup in a separate thread so it doesn't block the main process
    threading.Thread(target=_popup, daemon=True).start()

def create_tk():
    global root
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", root.withdraw)  # Hide window instead of closing
    root.withdraw()  # Hide the main window
    root.attributes("-topmost", True)  # Keep on top
    root.configure(bg="white")
    root.title("Phonetic Shortcuts")
    root.geometry("350x600")

    app_icon = tk.PhotoImage(file=get_url.resource_path('logo.png'))
    root.iconphoto(True, app_icon)

    # Startup script
    startup_var = tk.BooleanVar(value=startup.check_startup_status())

    def on_checkbox_click():
        is_checked = startup_var.get()
        message = "This will make PhonoScribe run automatically every time you start your computer. Do you want to proceed?" if is_checked else "This will stop PhonoScribe from running automatically at startup. Do you want to proceed?"

        user_answer = messagebox.askyesno("Confirm Action", message)

        if user_answer:
            startup.toggle_startup(is_checked)
        else:
            startup_var.set(not startup_var.get())

    startup_checkbox = tk.Checkbutton(
        root, 
        text="Run PhonoScribe when Windows starts", 
        variable=startup_var,      # Links the visual check to the True/False variable
        command=on_checkbox_click, # Runs this function every time it is clicked
        bg="white", 
        activebackground="white",  # Stops the background from turning grey when clicked
        font=("Segoe UI", 10)
    )
    startup_checkbox.pack(side="top", anchor="w", padx=20, pady=(20, 0))

    author = tk.Label(root, text="Made by Manuel Dominich Martinez", bg="white", fg="black",
                         font=("Segoe UI", 12), padx=10, pady=5)
    author.pack(side="bottom")
    
    divider = tk.Frame(root, height=1, bg="#612b6e")
    divider.pack(side="bottom", fill="x", padx=20)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview",
        background="white",
        foreground="black",
        rowheight=50,
        fieldbackground="white",
        font=("Segoe UI", 15)
    )
    style.configure("Treeview.Heading", font=("Segoe UI", 15, "bold"))

    style.map("Treeview", background=[("selected", "#612b6e")]) # Purple highlight when clicked

    table_frame = tk.Frame(root, bg="white")
    table_frame.pack(pady=20, padx=20, fill="both", expand=True)

    table_scroll = tk.Scrollbar(table_frame)
    table_scroll.pack(side="right", fill="y")

    columns = ("shortcut", "symbols")

    my_table = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=table_scroll.set)
    my_table.pack(side="left", fill="both", expand=True)

    table_scroll.config(command=my_table.yview)

    # --- 5. Format Columns and Headings ---
    my_table.column("shortcut", width=120, anchor="center")
    my_table.column("symbols", width=150, anchor="center")

    my_table.heading("shortcut", text="Keys")
    my_table.heading("symbols", text="Symbols")

    # Define a tag for alternating row colors
    my_table.tag_configure('oddrow', background="#f0f0f0")
    my_table.tag_configure('evenrow', background="white")

    # --- 6. Insert the Data ---
    shortcut_data = [
    ("Alt gr + A", "ɑ æ ʌ"),
    ("Alt gr + B", "β"),
    ("Alt gr + D", "ð"),
    ("Alt gr + E", "ə ᵊ ɛ ɜ"),
    ("Alt gr + F", "‿"),
    ("Alt gr + G", "ɣ"),
    ("Alt gr + H", "ʰ"),
    ("Alt gr + I", "ɪ"),
    ("Alt gr + J", "ʲ"),
    ("Alt gr + L", "ɫ"),
    ("Alt gr + M", "ɱ"),
    ("Alt gr + N", "ñ ŋ ɲ"),
    ("Alt gr + O", "ɔ, ɒ"),
    ("Alt gr + R", "ɾ"),
    ("Alt gr + S", "ʃ"),
    ("Alt gr + T", "θ ʔ"),
    ("Alt gr + U", "ʊ"),
    ("Alt gr + V", "ʌ"),
    ("Alt gr + Z", "ʒ"),
    ("Alt gr + W", "ʷ"),
    ("Alt gr + .", "ː"),
    ("Alt gr + 1", "| ‖"),
    ("Alt gr + 2", " ˈ ˌ "),
    ("Alt gr + 3", " ̥  ̊ "),
    ("Alt gr + 4", " ̪  "),
    ("Alt gr + 5", " ̩ "),
    ("Alt gr + 6", " ̚  "),
    ("Alt gr + 7", "↗ ↘ ꜜ ꜛ"),
    ("Alt gr + 8", " ˊ  ˋ  ˏ  ˎ "),
    ("Alt gr + 9", " ˇ  ˆ "),
    ("Alt gr + 0", "< >"),
    ("Alt gr + →", "→")
    ]

    # Loop through the data and insert it row by row
    for index, (key, symbols) in enumerate(shortcut_data):
        if index % 2 == 0:
            my_table.insert(parent="", index="end", iid=index, values=(key, symbols), tags=('evenrow',))
        else:
            my_table.insert(parent="", index="end", iid=index, values=(key, symbols), tags=('oddrow',))

def stop_app():
    global root
    root.destroy()

if __name__ == '__main__': 
    create_tk()
    show_toast("Welcome to PhonoApp, your Phonetic Keyboard!")
    system_tray = pystray.Icon('TypeIt', icon, 'Phonetic Keyboard')

    keyboard.hook(on_key, suppress=True)
    keyboard.on_release(on_key_release)

    system_tray.menu = pystray.Menu(
        pystray.MenuItem('Info', lambda: root.deiconify()),
        pystray.MenuItem('Toggle', lambda: toggle_phonetic_keyboard()),
        pystray.MenuItem('Exit', lambda: stop_app())
    )
    
    threading.Thread(target=system_tray.run, daemon=True).start()

    root.mainloop()

    
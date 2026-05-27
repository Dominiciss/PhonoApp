# create .exe: pyinstaller --onefile --icon=logo.png --add-data="logo.png;." --add-data="shortcuts-hor.png;." --add-data="shortcuts-vert.png;." --add-data="github.png;." --add-data="linkedin.png;." --add-data="logo.ico;." --name=PhonoScribe --windowed main.py

# Dependency imports
from PIL import Image, ImageOps
from tkinter import messagebox
from keyboard import KeyboardEvent
from PIL import ImageTk
import tkinter as tk
import customtkinter as ctk
import urllib.request
import keyboard
import pystray
import threading
import ctypes
import pyperclip
import time
import psutil
import logging
import os

# Own scripts
import scripts.get_url as get_url
import scripts.toast as toast
import scripts.menu as menu
import scripts.toggle_keyboard as toggle_keyboard
import scripts.cycle_map as cycle_map
import scripts.transcriptor as transcriptor
import scripts.github

VERSION = 'v1.4.0'
APP_NAME = 'PhonoScribe'
APP_ID = 'phonoscribe.transcription.utility'
ICON = Image.open(get_url.resource_path('logo.png'))
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)

app_data = os.getenv('APPDATA') 
appdata_dir = os.path.join(app_data, 'PhonoScribe')

os.makedirs(appdata_dir, exist_ok=True)

log_file = os.path.join(appdata_dir, 'info.log')
settings_file = os.path.join(appdata_dir, 'settings.json')

logging.basicConfig(
    filename=log_file, 
    level=logging.INFO, 
    format='%(asctime)s | %(levelname)s | %(message)s'
)

last_key = None
toggle_phonemes = True
first_check = True
enter_listener = None
listeners = []
overlay = None
alt_pressed = 0
persistent_overlay = False
alt_time = 0
overlay_image = None

def transcribe_popup():
    """Shortcut for transcribing and pasting the text in the user's clipboard"""
    
    start_time = time.perf_counter()
    logging.info("Transcription started")
    print("Transcription started")
    clipboard = pyperclip.paste()

    if clipboard is not None:
        try:
            transcription = transcriptor.get_ipa(clipboard)
            pyperclip.copy(transcription)
            toast.show_toast("Transcription copied to the clipboard!")
            logging.info(f"Transcription copied. Time ellapsed: {time.perf_counter() - start_time}")
            print(f"Transcription copied. Time ellapsed: {time.perf_counter() - start_time}")
        except:
            toast.show_toast("Transcription failed. Do you have internet connection?")
            logging.error(f"Transcription failed. Couldn't connect to the server. Time ellapsed: {time.perf_counter() - start_time}")
            print(f"Transcription failed. Couldn't connect to the server. Time ellapsed: {time.perf_counter() - start_time}")
    else:
        toast.show_toast("Clipboard did not have information")
        logging.info(f"Transcription failed. Clipboard did not have information. Time ellapsed: {time.perf_counter() - start_time}")
        print(f"Transcription failed. Clipboard did not have information. Time ellapsed: {time.perf_counter() - start_time}")

def toggle_window(event: KeyboardEvent):
    global last_key

    last_key = 59

    if menu.root.winfo_viewable():
        menu.root.withdraw()
    else:
        menu.root.deiconify()

def start_transcription(event: KeyboardEvent):
    global last_key

    last_key = 60

    menu.root.after(0, transcribe_popup)

def safe_unhook(hook):
    """Unhooks a keyboard hook, ignoring errors if already removed"""
    try:
        keyboard.unhook(hook)
    except Exception:
        pass

def clear_listeners():
    """Force-clears all active listeners and resets state"""
    global listeners, first_check

    for item in listeners:
        safe_unhook(item)
    listeners = []
    first_check = True
    for data in cycle_map.cycle_map.values():
        data['symbol_state'] = 0

def on_key(event: KeyboardEvent):
    global last_key

    last_key = event.scan_code

def on_alt(event: KeyboardEvent):
    global listeners, enter_listener, overlay, toggle_phonemes, last_key, alt_pressed, persistent_overlay, alt_time

    if event.event_type == keyboard.KEY_DOWN:
        if alt_pressed == 1:
            return

        alt_pressed = 1

        clear_listeners()

        last_key = event.scan_code

        enter_listener = keyboard.on_press_key(28, lambda e: call_toggle(), suppress=True)
        if toggle_phonemes:
            if get_url.load_variables()['show_overlay'] == 1 and not overlay.winfo_viewable():
                toggle_overlay()
            if get_url.load_variables()['show_overlay'] == 1 and persistent_overlay == True:
                listeners.append(keyboard.on_press_key(1, hide_overlay, suppress=True))
            else:
                listeners.append(keyboard.on_press_key(1, lambda _: None, suppress=True))
            listeners.append(keyboard.hook(on_key))
            listeners.append(keyboard.on_press_key(29, lambda _: None, suppress=True))
            listeners.append(keyboard.on_press_key(56, lambda _: None, suppress=True))
            listeners.append(keyboard.on_press_key(59, toggle_window, suppress=True))
            listeners.append(keyboard.on_press_key(60, start_transcription, suppress=True))
            listeners.append(keyboard.on_press_key(72, lambda e: overlay_position(0, key=72), suppress=True))
            listeners.append(keyboard.on_press_key(80, lambda e: overlay_position(1, key=80), suppress=True))
            listeners.append(keyboard.on_press_key(75, lambda e: overlay_position(2, key=75), suppress=True))
            listeners.append(keyboard.on_press_key(77, lambda e: overlay_position(3, key=77), suppress=True))
            for data in cycle_map.cycle_map.values():
                listeners.append(keyboard.on_press_key(data['scan_code'], write_symbol, suppress=True))
        alt_time = time.perf_counter()
    elif event.event_type == keyboard.KEY_UP:
        if toggle_phonemes:
            keyboard.send('ctrl')
            keyboard.send('alt')

        safe_unhook(enter_listener)

        clear_listeners()
        duration = round(time.perf_counter() - alt_time, 2)

        if get_url.load_variables()['show_overlay'] == 1 and duration < 0.2 and last_key == event.scan_code and toggle_phonemes:
            alt_pressed = 0
            if persistent_overlay == True:
                toast.show_toast("Persistent mode already activated!\nIf you want to hide the overlay press 'alt gr + esc'")
            else:
                toast.show_toast("Persistent mode activated!\nIf you want to hide the overlay press 'alt gr + esc'")
            persistent_overlay = True
            return

        if get_url.load_variables()['show_overlay'] == 1 and persistent_overlay == True:
            alt_pressed = 0
            return

        if get_url.load_variables()['show_overlay'] == 1 and overlay.winfo_viewable():
            toggle_overlay()

        alt_pressed = 0

def hide_overlay(event: KeyboardEvent):
    """Hides overlay when esc is pressed"""
    global overlay, persistent_overlay, last_key

    last_key = event.scan_code

    persistent_overlay = False
    menu.root.after(0, overlay.withdraw)

def _hide_overlay():
    """Hides overlay when enter is pressed"""
    global overlay, persistent_overlay

    persistent_overlay = False
    menu.root.after(0, overlay.withdraw)

def write_symbol(event: KeyboardEvent):
    """Writes the assigned symbol for a specific letter as shown in cycle_map.py"""
    global first_check, last_key

    for data in cycle_map.cycle_map.values():
        if data['scan_code'] == event.scan_code:
            letter = data

    start_time = time.perf_counter()
    logging.info("Symbol writing started")
    print("Symbol writing started")

    try:
        if last_key is not None:
            if last_key != letter['scan_code']:
                first_check = True
                for key, data in cycle_map.cycle_map.items():
                    if data['scan_code'] != last_key:
                        data['symbol_state'] = 0

        if not first_check:
            keyboard.send('backspace')

        keyboard.write(letter['symbols'][letter['symbol_state']])

        if letter['symbol_state'] >= len(letter['symbols']) - 1:
            letter['symbol_state'] = 0
        else:
            letter['symbol_state'] += 1
        
        logging.info(f"Symbol was written. Time ellapsed: {time.perf_counter() - start_time}")
        print(f"Symbol was written. Time ellapsed: {time.perf_counter() - start_time}")
    except Exception as e:
        logging.error(f"Couldn't write symbol due to {e}. Time ellapsed: {time.perf_counter() - start_time}")
        print(f"Couldn't write symbol due to {e}. Time ellapsed: {time.perf_counter() - start_time}")

    last_key = letter['scan_code']
    first_check = False

def overlay_position(pos, first_time=False, key=0):
    """Changes the overlay position
    
    :param pos: new position 0 = UP, 1 = DOWN, 2 = LEFT, 3 = RIGHT
    :param first_time: used to check if the window has to be created or modified"""
    global overlay, overlay_image, last_key

    screen_width = menu.root.winfo_screenwidth()
    screen_height = menu.root.winfo_screenheight()

    if key != 0:
        last_key = key

    if pos == 0 or pos == 1:
        if (ctk.get_appearance_mode() == "Dark"):
            original_image = ImageOps.invert(Image.open(get_url.resource_path('shortcuts-hor.png')))
        else:
            original_image = Image.open(get_url.resource_path('shortcuts-hor.png'))

        img_w, img_h = original_image.size

        if img_w > (screen_width * 0.9):
            ratio = (screen_width / img_w) * 0.9
            
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)
            
            display_image = original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            display_image = original_image
            new_w, new_h = img_w, img_h
    elif pos == 2 or pos == 3:
        if (ctk.get_appearance_mode() == "Dark"):
            original_image = ImageOps.invert(Image.open(get_url.resource_path('shortcuts-vert.png')))
        else:
            original_image = Image.open(get_url.resource_path('shortcuts-vert.png'))
    
        img_w, img_h = original_image.size

        if img_h > (screen_height * 0.9):
            ratio = (screen_height / img_h) * 0.9
            
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)
            
            display_image = original_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            display_image = original_image
            new_w, new_h = img_w, img_h

    tk_image = ImageTk.PhotoImage(display_image)

    if overlay_image is None:
        overlay_image = tk.Label(overlay, image=tk_image)
        overlay_image.pack(expand=True)
    else:
        overlay_image.config(image=tk_image)
    overlay_image.image = tk_image

    overlay.overrideredirect(True)
    x_position = (screen_width - new_w) // 2
    y_position = (screen_height - new_h) // 2

    if pos == 0:
        overlay.geometry(f"{new_w}x{new_h}+{x_position}+10")
    elif pos == 1:
        overlay.geometry(f"{new_w}x{new_h}+{x_position}+{screen_height - new_h - 10}")
    elif pos == 2:
        overlay.geometry(f"{new_w}x{new_h}+10+{y_position}")
    elif pos == 3:
        overlay.geometry(f"{new_w}x{new_h}+{screen_width - new_w - 10}+{y_position}")

def create_overlay():
    """Creates the shortcuts overlay when the user presses the key alt gr"""
    global overlay

    overlay = tk.Toplevel(menu.root)
    overlay.withdraw()
    
    overlay.attributes('-topmost', True)
    overlay.attributes('-alpha', 0.8) 

def toggle_overlay():
    """Disables or enables the overlay"""
    global overlay

    saved_pos = get_url.load_variables()['overlay_position']

    if overlay.winfo_viewable() and (not keyboard.is_pressed('alt gr') or not toggle_phonemes):
        overlay.after(0, overlay.withdraw)
        overlay_position(saved_pos, first_time=True)
    else: 
        overlay_position(saved_pos, first_time=True)
        overlay.after(0, overlay.deiconify)

def supress_alt(event: KeyboardEvent):
    global alt_listener, alt_pressed, alt_released, enter_listener

    clear_listeners()
    _hide_overlay()
    safe_unhook(alt_listener)
    safe_unhook(enter_listener)
    alt_pressed = 0
    alt_listener = keyboard.hook_key("alt gr", on_alt, suppress=True)

def call_toggle():
    """Changes the state of toggle_phonemes and enables/disables the phonetic keyboard"""
    global ICON, toggle_phonemes, system_tray, alt_listener, alt_released, persistent_overlay, last_key, alt_pressed

    last_key = 28

    if toggle_phonemes:
        _hide_overlay()
        safe_unhook(alt_listener)
        alt_listener = keyboard.hook_key("alt gr", on_alt, suppress=False)
        clear_listeners()
    else:
        if keyboard.is_pressed("alt gr"):
            keyboard.send('ctrl')
            keyboard.send('alt')

            if get_url.load_variables()['show_overlay'] == 1 and not overlay.winfo_viewable():
                toggle_overlay()
            if get_url.load_variables()['show_overlay'] == 1 and persistent_overlay == True:
                listeners.append(keyboard.on_press_key(1, hide_overlay, suppress=True))
            listeners.append(keyboard.hook(on_key))
            listeners.append(keyboard.on_press_key(29, lambda _: None, suppress=True))
            listeners.append(keyboard.on_press_key(56, lambda _: None, suppress=True))
            listeners.append(keyboard.on_press_key(59, toggle_window, suppress=True))
            listeners.append(keyboard.on_press_key(60, start_transcription, suppress=True))
            listeners.append(keyboard.on_press_key(72, lambda e: overlay_position(0, key=72), suppress=True))
            listeners.append(keyboard.on_press_key(80, lambda e: overlay_position(1, key=80), suppress=True))
            listeners.append(keyboard.on_press_key(75, lambda e: overlay_position(2, key=75), suppress=True))
            listeners.append(keyboard.on_press_key(77, lambda e: overlay_position(3, key=77), suppress=True))
            for data in cycle_map.cycle_map.values():
                listeners.append(keyboard.on_press_key(data['scan_code'], write_symbol, suppress=True))

            alt_listener = keyboard.on_release_key("alt gr", supress_alt, suppress=True)
        else:
            safe_unhook(alt_listener)
            alt_pressed = 0
            alt_listener = keyboard.hook_key("alt gr", on_alt, suppress=True)

    toggle_phonemes = toggle_keyboard.toggle_phonetic_keyboard(toggle_phonemes, ICON, system_tray)

def download_and_install(github_version):
    """Downloads the setup wizard in the background and runs it."""
    
    download_window = tk.Toplevel(menu.root)
    download_window.title("Updating PhonoScribe")
    
    screen_width = menu.root.winfo_screenwidth()
    screen_height = menu.root.winfo_screenheight()

    x = (screen_width // 2) - (300 // 2)
    y = (screen_height // 2) - (100 // 2)

    download_window.geometry(f"300x100+{x}+{y}")
    download_window.attributes('-topmost', True)
    tk.Label(download_window, text=f"Downloading version {github_version}...\nPlease wait.", pady=20).pack()
    download_window.update()

    try:
        asset_name = "PhonoScribe-Setup.exe"
        
        download_url = f"https://github.com/Dominiciss/PhonoScribe/releases/download/{github_version}/{asset_name}"
        
        temp_dir = os.environ.get('TEMP')
        installer_path = os.path.join(temp_dir, asset_name)
        
        urllib.request.urlretrieve(download_url, installer_path)
        
        logging.info("Update downloaded. Launching setup and killing app.")
        print("Update downloaded. Launching setup and killing app.")
        
        os.startfile(installer_path)
        
        system_tray.stop()
        os._exit(0) 
        
    except Exception as e:
        download_window.destroy()
        logging.error(f"Failed to download update: {e}")
        toast.show_toast("Failed to download the update. Check your internet connection.")

def update_checker():
    """Checks for new updates in the github repository"""
    start_time = time.perf_counter()
    logging.info("Checking for updates...")
    print("Checking for updates...")

    repo = scripts.github.get_repo()

    if (repo is not None):
        github_version = scripts.github.get_latest(repo)

        if (VERSION != github_version):
            logging.info(f"Version {github_version} found. Time ellapsed: {time.perf_counter() - start_time}")
            print(f"Version {github_version} found. Time ellapsed: {time.perf_counter() - start_time}")

            user_answer = messagebox.askyesno("Confirm Action", f"Version {github_version} is available!\n\nDo you want to download and install it now?")
            
            if (user_answer):
                threading.Thread(target=download_and_install, args=(github_version,), daemon=True).start()
        else:
            logging.info(f"Version {github_version} found was not newer than client version {VERSION}. Time ellapsed: {time.perf_counter() - start_time}")
            print(f"Version {github_version} found was not newer than client version {VERSION}. Time ellapsed: {time.perf_counter() - start_time}")
            toast.show_toast("You have the latest version available!")
    else:
        logging.info(f"Couldn't connect with GitHub's api. Time ellapsed: {time.perf_counter() - start_time}")
        print(f"Couldn't connect with GitHub's api. Time ellapsed: {time.perf_counter() - start_time}")
        toast.show_toast("Error produced when looking for updates. Do you have internet connection?")

def kill_previous_instances():
    """Kills previous instances of the app to avoid multiple instances running at the same time"""
    current_pid = os.getpid()
    
    try:
        current_process = psutil.Process(current_pid)
        current_exe = current_process.exe()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return

    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['exe'] == current_exe and proc.info['pid'] != current_pid:
                logging.info(f"Found older instance (PID: {proc.info['pid']}). Terminating...")
                print(f"Found older instance (PID: {proc.info['pid']}). Terminating...")
                
                proc.terminate()
                proc.wait(timeout=3)  
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        except psutil.TimeoutExpired:
            logging.info("Process did not terminate cleanly. Forcing kill...")
            print("Process did not terminate cleanly. Forcing kill...")
            proc.kill()

def on_closing():
    """Closes the app when the user clicks the 'X' button in the menu window"""
    global system_tray

    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        system_tray.stop()
        menu.root.withdraw()
        menu.root.quit()
        os._exit(0)

if __name__ == '__main__':
    global alt_listener
    global alt_released
    alt_listener = None
    alt_released = None

    kill_previous_instances()

    menu.create_tk()
    create_overlay()
    toast.popup_start()
    toast.show_toast("Welcome to PhonoScribe, your Phonetic Keyboard!\nIf you have any doubts, press Alt gr + F1 to open the main menu!", 6)
    system_tray = pystray.Icon('PhonoScribe', ICON, 'PhonoScribe')

    logging.info("App started")
    print("App started")

    alt_listener = keyboard.hook_key("alt gr", on_alt, suppress=True)

    system_tray.menu = pystray.Menu(
        pystray.MenuItem('Menu', lambda: menu.root.deiconify()),
        pystray.MenuItem('Toggle', lambda: call_toggle()),
        pystray.MenuItem('Check for updates', lambda: update_checker()),
        pystray.MenuItem('Exit', lambda: on_closing())
    )
    
    threading.Thread(target=system_tray.run, daemon=True).start()

    menu.root.mainloop()
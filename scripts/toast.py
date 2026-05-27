import customtkinter as ctk
from PIL import Image
import logging

import scripts.get_url as get_url
import scripts.menu as menu

# Globals
popup = None
label = None
hide_job = None
is_visible = False

def popup_start():
    global popup, label

    popup = ctk.CTkToplevel(menu.root, fg_color="#000001")
    popup.withdraw()
    popup.transient(menu.root)
    popup.overrideredirect(True)
    popup.attributes("-transparentcolor", "#000001")
    popup.attributes("-toolwindow", True)
    popup.attributes("-topmost", True)
    popup.attributes("-alpha", 0)

    main_frame = ctk.CTkFrame(popup, border_width=2, border_color="#612b6e", corner_radius=6)
    main_frame.pack(fill="both", expand=True)

    header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(pady=(10, 0), padx=(10, 10), fill="x")

    try:
        raw_image = Image.open(get_url.resource_path("logo.png"))
        app_logo = ctk.CTkImage(light_image=raw_image, dark_image=raw_image, size=(20, 20))
        image_label = ctk.CTkLabel(header_frame, image=app_logo, text="")
        image_label.pack(side="left", padx=(0, 5))
    except Exception as e:
        logging.error(f"Could not load toast icon: {e}")

    title_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold", slant="italic")
    title_label = ctk.CTkLabel(header_frame, text="PhonoScribe", font=title_font, text_color="#612b6e")
    title_label.pack(side="left")

    custom_line = ctk.CTkFrame(main_frame, fg_color="#612b6e", height=2)
    custom_line.pack(fill="x", padx=10, pady=(5, 0))

    label = ctk.CTkLabel(
        main_frame, 
        text="Waiting...", 
        font=ctk.CTkFont(family="Segoe UI", size=12), 
        justify="left",
        wraplength=350,
        height=0
    )
    label.pack(padx=15, pady=10, anchor="w")

def _slide_in(current_y, target_y, current_alpha, x):
    """Recursively moves the window up and fades it in"""
    global popup
    
    if current_y > target_y:
        current_y -= 4
        current_alpha += 0.05
        
        if current_alpha > 1.0: 
            current_alpha = 1.0
            
        popup.geometry(f"+{x}+{current_y}")
        popup.attributes("-alpha", current_alpha)
        
        popup.after(10, _slide_in, current_y, target_y, current_alpha, x)
    else:
        popup.geometry(f"+{x}+{target_y}")
        popup.attributes("-alpha", 1.0)


def _slide_out(current_y, target_y, current_alpha, x):
    """Recursively moves the window down and fades it out"""
    global popup, is_visible
    
    if current_alpha > 0:
        current_y += 4
        current_alpha -= 0.08
        
        popup.geometry(f"+{x}+{current_y}")
        popup.attributes("-alpha", current_alpha)
        
        popup.after(10, _slide_out, current_y, target_y, current_alpha, x)
    else:
        popup.withdraw()
        is_visible = False


def trigger_hide(target_y, start_y, x):
    """Helper function triggered by the duration timer to start the slide out"""
    _slide_out(target_y, start_y, 1.0, x)


def show_toast(message, duration=3):
    global popup, label, hide_job, is_visible

    if hide_job is not None:
        popup.after_cancel(hide_job)

    label.configure(text=message)
    popup.update_idletasks()
    
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    window_width = popup.winfo_reqwidth()
    window_height = popup.winfo_reqheight()

    x = screen_width - window_width - 20
    target_y = screen_height - window_height - 55
    start_y = target_y + 40
    
    if not is_visible:
        popup.wm_geometry(f"{window_width}x{window_height}+{x}+{start_y}")
        popup.attributes("-alpha", 0)
        popup.deiconify()
        is_visible = True
        
        _slide_in(start_y, target_y, 0.0, x)
    else:
        popup.wm_geometry(f"{window_width}x{window_height}+{x}+{target_y}")

    hide_job = popup.after(int(duration * 1000), trigger_hide, target_y, start_y, x)
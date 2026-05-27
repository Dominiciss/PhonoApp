import tkinter as tk
import webbrowser
import logging
from PIL import Image, ImageOps
import customtkinter as ctk
import CTkMessagebox

import scripts.startup as startup
import scripts.get_url as get_url

def on_select(pos, saved_vars):
    if pos == "Up":
        saved_vars['overlay_position'] = 0
    elif pos == "Down":
        saved_vars['overlay_position'] = 1
    elif pos == "Left":
        saved_vars['overlay_position'] = 2
    elif pos == "Right":
        saved_vars['overlay_position'] = 3
    get_url.save_variables(saved_vars)

def create_tk():
    """Creates the main GUI where you can find basic information about shortcuts, author and startup"""
    global root

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    root.withdraw()
    root.title("PhonoScribe")
    root.geometry("625x500") 

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=2) # Left side
    root.grid_columnconfigure(1, weight=1) # Right side

    try:
        app_png = tk.PhotoImage(file=get_url.resource_path('logo.png'))
        root.iconphoto(True, app_png)
        root.iconbitmap(get_url.resource_path('logo.ico'))
    except Exception as e:
        print(f"Could not load app icon: {e}")
        logging.error(f"Could not load app icon: {e}")

    # ==========================================
    # LEFT COLUMN: INFO & SETTINGS
    # ==========================================
    info_frame = ctk.CTkFrame(root)
    info_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

    info_title = ctk.CTkLabel(info_frame, text="Settings & Information", font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"))
    info_title.pack(anchor="w", padx=20, pady=(15, 10))

    startup_var = ctk.BooleanVar(value=startup.check_startup_status())

    def on_startup_checkbox_click():
        is_checked = startup_var.get()
        message = "This will make PhonoScribe run automatically every time you start your computer. Do you want to proceed?" if is_checked else "This will stop PhonoScribe from running automatically at startup. Do you want to proceed?"
        
        user_answer = CTkMessagebox.CTkMessagebox(
            title="Confirm Action", 
            message=message,
            icon="question", 
            option_1="No", 
            option_2="Yes",
            button_color="#612b6e",
            button_hover_color="#823894"
        )

        if user_answer.get() == "Yes":
            startup.toggle_startup(is_checked)
        else:
            startup_var.set(not is_checked) 

    startup_switch = ctk.CTkSwitch(
        info_frame, 
        text="Run PhonoScribe on startup", 
        variable=startup_var,
        command=on_startup_checkbox_click,
        font=ctk.CTkFont(family="Segoe UI", size=12),
        progress_color="#612b6e"
    )
    startup_switch.pack(anchor="w", padx=20, pady=(0, 15))

    saved_vars = get_url.load_variables()
    show_overlay_var = ctk.BooleanVar(value=bool(saved_vars['show_overlay']))

    def on_show_overlay_checkbox_click():
        is_checked = show_overlay_var.get()
        message = "This will make an overlay of the shortcuts show everytime you press alt gr. Do you want to proceed?" if is_checked else "This will stop the overlay from appearing everytime you press alt gr. Do you want to proceed?"
        
        user_answer = CTkMessagebox.CTkMessagebox(
            title="Confirm Action", 
            message=message,
            icon="question", 
            option_1="No", 
            option_2="Yes",
            button_color="#612b6e",
            button_hover_color="#823894"
        )
        
        if user_answer.get() == "Yes":
            saved_vars['show_overlay'] = 1 if is_checked else 0
            get_url.save_variables(saved_vars)
        else:
            show_overlay_var.set(not is_checked) 

    show_overlay_switch = ctk.CTkSwitch(
        info_frame, 
        text="Show shortcut overlay when pressing Alt Gr", 
        variable=show_overlay_var,
        command=on_show_overlay_checkbox_click,
        font=ctk.CTkFont(family="Segoe UI", size=12),
        progress_color="#612b6e"
    )
    show_overlay_switch.pack(anchor="w", padx=20, pady=(0, 10))

    selector_var = saved_vars.get('overlay_position', 0)
    options = ["Up", "Down", "Left", "Right"]
    
    selector_text = ctk.CTkLabel(info_frame, text="Overlay Position:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
    selector_text.pack(anchor="w", padx=20, pady=(0, 5))

    dropdown = ctk.CTkOptionMenu(
        info_frame, 
        values=options, 
        command=lambda val: on_select(val, saved_vars),
        fg_color="#823894",
        button_color="#612b6e",
        button_hover_color="#823894"
    )
    dropdown.set(options[selector_var])
    dropdown.pack(anchor="w", padx=20)

    shortcut_text = ctk.CTkLabel(info_frame, text="Information about shortcuts:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
    shortcut_text.pack(anchor="w", padx=20, pady=(10, 5))

    description = ctk.CTkLabel(info_frame, justify="left", wraplength=250, text="● 'Alt gr + enter' lets you toggle the phonetic keyboard.\n\n● 'Alt gr + F1' opens the main menu.\n\n● 'Alt gr + F2' lets you transcribe the information in your clipboard (the transcription is stored there).\n\n● A quick press of 'alt gr' pins the overlay to the screen.", font=ctk.CTkFont(family="Segoe UI", size=14, weight="normal"))
    description.pack(padx=30, pady=(2, 2), anchor="w")

    # ==========================================
    # RIGHT COLUMN: TABLE & CREDITS CONTAINER
    # ==========================================
    right_frame = ctk.CTkFrame(root, fg_color="transparent")
    right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
    
    right_frame.grid_rowconfigure(0, weight=1)
    right_frame.grid_rowconfigure(1, weight=0)
    right_frame.grid_columnconfigure(0, weight=1)

    table_frame = ctk.CTkScrollableFrame(right_frame, label_text="PhonoScribe Shortcuts", label_font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
    table_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

    table_frame.grid_columnconfigure(0, weight=1)
    table_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(table_frame, text="Keys", font=ctk.CTkFont(weight="bold", size=16)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    ctk.CTkLabel(table_frame, text="Symbols", font=ctk.CTkFont(weight="bold", size=16)).grid(row=0, column=1, sticky="w", padx=10, pady=5)

    shortcut_data = [
        ("Alt Gr + A", "ɑ æ ʌ ɐ"), ("Alt Gr + B", "β ɓ ʙ"),
        ("Alt Gr + C", "ɔ ç ɕ"), ("Alt Gr + D", "ð ɖ ɗ"), ("Alt Gr + E", "ə ɜ ᵊ ɘ ɛ ɝ"),
        ("Alt Gr + F", "‿  ͡   ͜  "), ("Alt Gr + G", "ɣ ɠ ɢ ʛ ɡ"), ("Alt Gr + H", "ʰ ʱ ħ ɦ ɥ ɧ ʜ"),
        ("Alt Gr + I", "ɪ ɨ"), ("Alt Gr + J", "ʲ ʝ ɟ ʄ"), ("Alt Gr + K", "ǀ ǁ ǂ ǃ ʘ"),
        ("Alt Gr + L", "ɫ ɭ ɬ ʟ ɮ"), ("Alt Gr + M", "ɱ"), ("Alt Gr + N", "ŋ ñ ɲ ɳ ɴ"),
        ("Alt Gr + O", "ɒ ɔ œ ɶ"), ("Alt Gr + P", "ɸ"), ("Alt Gr + Q", "ˈ ˌ"),
        ("Alt Gr + R", "ɾ ɹ ʁ ʀ ɻ ɽ ɺ"), ("Alt Gr + S", "ʃ ʂ"), ("Alt Gr + T", "θ ʔ ʈ ʕ ʡ ʢ"),
        ("Alt Gr + U", "ʊ ʉ ü"), ("Alt Gr + V", "ʌ ʋ ⱱ"), ("Alt Gr + W", "ʷ ɯ ʍ ɰ"),
        ("Alt Gr + X", "æ χ"), ("Alt Gr + Y", "ɣ ʎ ʏ ɤ"), ("Alt Gr + Z", "ʒ ʐ ʑ"),
        ("Alt Gr + ,", " ́  ̀  "), ("Alt Gr + .", "ː"), ("Alt Gr + 1", "| ‖"),
        ("Alt Gr + 2", "< > [ ]"), ("Alt Gr + 3", " ̥  ̊ "), ("Alt Gr + 4", " ̪  "),
        ("Alt Gr + 5", " ̩ "), ("Alt Gr + 6", " ̚  "), ("Alt Gr + 7", "↗ ↘ ꜜ ꜛ"),
        ("Alt Gr + 8", " ˊ ˋ ˏ ˎ "), ("Alt Gr + 9", " ˇ ˆ "), ("Alt Gr + 0", "˭ ø"),
        ("Alt Gr + -", "→"),
    ]

    row_font = ctk.CTkFont(size=15, family="Segoe UI")

    for index, (key, symbols) in enumerate(shortcut_data, start=1):
        ctk.CTkLabel(table_frame, text=key, font=row_font).grid(row=index, column=0, sticky="w", padx=10, pady=2)
        ctk.CTkLabel(table_frame, text=symbols, font=row_font).grid(row=index, column=1, sticky="w", padx=10, pady=2)

    credits_frame = ctk.CTkFrame(right_frame)
    credits_frame.grid(row=1, column=0, sticky="ew")

    author = ctk.CTkLabel(credits_frame, text="Made by Manuel Dominich", font=ctk.CTkFont(family="Segoe UI", size=11))
    author.pack(side="left", padx=(15, 5), pady=10)

    def open_url(url):
        try:
            webbrowser.open(url, new=2)
        except Exception as e:
            logging.error(f"Error opening URL: {e}")
            print(f"Error opening URL: {e}")

    def get_inverted_image(img):
        """Inverts the image colours
    
        :param icon: app icon"""

        r, g, b, a = img.split()
        
        rgb_image = Image.merge('RGB', (r, g, b))
        
        inverted_rgb = ImageOps.invert(rgb_image)
        
        r2, g2, b2 = inverted_rgb.split()
        
        return Image.merge('RGBA', (r2, g2, b2, a))

    try:
        github_logo = ctk.CTkImage(light_image=Image.open(get_url.resource_path('github.png')), dark_image=get_inverted_image(Image.open(get_url.resource_path('github.png'))), size=(16, 16))
        github_btn = ctk.CTkButton(credits_frame, image=github_logo, text="", border_spacing=0, corner_radius=3, border_width=0, width=18, height=18, fg_color="transparent", hover_color="#823894", command=lambda: open_url("https://github.com/Dominiciss"))
        github_btn.pack(side="right", padx=(5, 15), pady=0)
    except Exception as e:
        print(e)
        logging.error

    try:
        linkedin_logo = ctk.CTkImage(light_image=Image.open(get_url.resource_path('linkedin.png')), dark_image=get_inverted_image(Image.open(get_url.resource_path('linkedin.png'))), size=(16, 16))
        linkedin_btn = ctk.CTkButton(credits_frame, image=linkedin_logo, text="", border_spacing=0, corner_radius=3, border_width=0, width=18, height=18, fg_color="transparent", hover_color="#823894", command=lambda: open_url("https://www.linkedin.com/in/manuel-dominich-martinez/"))
        linkedin_btn.pack(side="right", padx=5, pady=0)
    except Exception as e:
        logging.error
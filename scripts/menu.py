import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import scripts.startup as startup
import scripts.get_url as get_url

def create_tk():
    global root
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", root.withdraw)  # Hide window instead of closing
    root.withdraw()  # Hide the main window
    root.attributes("-topmost", True)  # Keep on top
    root.configure(bg="white")
    root.title("PhonoScribe")
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
        variable=startup_var,
        command=on_checkbox_click,
        bg="white", 
        activebackground="white",
        font=("Segoe UI", 10)
    )
    startup_checkbox.pack(side="top", anchor="w", padx=20, pady=(20, 0))

    author = tk.Label(root, text="Made by Manuel Dominich Martinez", bg="white", fg="black",
                         font=("Segoe UI", 8), padx=10, pady=5)
    author.pack(side="bottom")

    divider = tk.Frame(root, height=1, bg="#612b6e")
    divider.pack(side="bottom", fill="x", padx=40)

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

    my_table.column("shortcut", width=120, anchor="center")
    my_table.column("symbols", width=150, anchor="center")

    my_table.heading("shortcut", text="Keys")
    my_table.heading("symbols", text="Symbols")

    # Define a tag for alternating row colors
    my_table.tag_configure('oddrow', background="#f0f0f0")
    my_table.tag_configure('evenrow', background="white")

    # --- 6. Insert the Data ---
    shortcut_data = [
    ("Alt gr + A", "ɑ æ ʌ ɐ"),
    ("Alt gr + B", "β ɓ ʙ"),
    ("Alt gr + C", "ç ɕ"),
    ("Alt gr + D", "ð ɖ ɗ"),
    ("Alt gr + E", "ə ɜ ᵊ ɘ ɛ ɝ"),
    ("Alt gr + F", "‿  ͡   ͜  "),
    ("Alt gr + G", "ɣ ɠ ɢ ʛ ɡ"),
    ("Alt gr + H", "ʰ ʱ ħ ɦ ɥ ɧ ʜ"),
    ("Alt gr + I", "ɪ ɨ ɪ̈"),
    ("Alt gr + J", "ʲ ʝ ɟ ʄ"),
    ("Alt gr + K", "ǀ ǁ ǂ ǃ ʘ"),
    ("Alt gr + L", "ɫ ɭ ɬ ʟ ɮ"),
    ("Alt gr + M", "ɱ"),
    ("Alt gr + N", "ñ ŋ ɲ ɳ ɴ"),
    ("Alt gr + O", "ɔ ɒ œ ɶ"),
    ("Alt gr + P", "ɸ"),
    ("Alt gr + Q", "ˈ ˌ"),
    ("Alt gr + R", "ɾ ɹ ʁ ʀ ɻ ɽ ɺ"),
    ("Alt gr + S", "ʃ ʂ"),
    ("Alt gr + T", "θ ʔ ʈ ʕ ʡ ʢ"),
    ("Alt gr + U", "ʊ ʉ ü"),
    ("Alt gr + V", "ʌ ʋ ⱱ"),
    ("Alt gr + W", "ʷ ɯ ʍ ɰ"),
    ("Alt gr + X", "χ"),
    ("Alt gr + Y", "ɣ ʎ ʏ ɤ"),
    ("Alt gr + Z", "ʒ ʐ ʑ"),
    ("Alt gr + ,", " ́   ̀  "),
    ("Alt gr + .", "ː"),
    ("Alt gr + 1", "| ‖"),
    ("Alt gr + 2", "< >"),
    ("Alt gr + 3", " ̥  ̊ "),
    ("Alt gr + 4", " ̪  "),
    ("Alt gr + 5", " ̩ "),
    ("Alt gr + 6", " ̚  "),
    ("Alt gr + 7", "↗ ↘ ꜜ ꜛ"),
    ("Alt gr + 8", " ˊ  ˋ  ˏ  ˎ "),
    ("Alt gr + 9", " ˇ  ˆ "),
    ("Alt gr + 0", "ø"),
    ("Alt gr + →", "→")
    ]

    # Loop through the data and insert it row by row
    for index, (key, symbols) in enumerate(shortcut_data):
        if index % 2 == 0:
            my_table.insert(parent="", index="end", iid=index, values=(key, symbols), tags=('evenrow',))
        else:
            my_table.insert(parent="", index="end", iid=index, values=(key, symbols), tags=('oddrow',))
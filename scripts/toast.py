from PIL import Image, ImageTk
import tkinter as tk
import threading

import scripts.get_url as get_url

# Display a small, non-intrusive popup message.
def show_toast(message, duration=3):
    def _popup():
        popup = tk.Tk()
        popup.attributes("-alpha", 1)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
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
                         font=("Segoe UI", 10), padx=10, pady=5, anchor="w", justify="left")
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
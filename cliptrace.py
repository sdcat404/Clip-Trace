import customtkinter as ctk
import pyperclip
import time
import threading
from datetime import datetime
import os

LOG_FILE = "clipboard_log.txt"
CHECK_INTERVAL = 1 
MAX_ENTRIES = 100 

# More pretty things
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ClipboardWatcher(threading.Thread):
    def __init__(self, callback):
        super().__init__(daemon=True)
        self.callback = callback
        self.last_text = ""

    def run(self):
        while True:
            try:
                text = pyperclip.paste()
                if text != self.last_text and text.strip() != "":
                    self.last_text = text
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.callback(text, timestamp)
            except Exception as e:
                print("Clipboard error:", e)
            time.sleep(CHECK_INTERVAL)

# Main ze app
class ClipTraceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ClipTrace")
        self.geometry("600x500")

        self.entries = []

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.update_display)

        # Pretty things
        ctk.CTkLabel(self, text="ClipTrace Clipboard Logger", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkEntry(self, textvariable=self.search_var, placeholder_text="Search clipboard...").pack(padx=10, fill="x")

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.load_log()

        ClipboardWatcher(self.add_entry).start()

    def load_log(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                raw = f.read().split("\n--- ")
                for block in raw:
                    if block.strip():
                        lines = block.strip().split("\n", 1)
                        if len(lines) == 2:
                            timestamp, text = lines
                            self.entries.append((text.strip(), timestamp.strip()))
        self.update_display()

    def add_entry(self, text, timestamp):
        self.entries.insert(0, (text, timestamp))
        self.entries = self.entries[:MAX_ENTRIES]

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- {timestamp}\n{text}\n")

        self.update_display()

    def update_display(self, *args):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        query = self.search_var.get().lower()
        for text, timestamp in self.entries:
            if query in text.lower():
                frame = ctk.CTkFrame(self.scroll_frame)
                frame.pack(fill="x", padx=5, pady=4)

                label = ctk.CTkLabel(frame, text=f"[{timestamp}]  {text[:80]}{'...' if len(text) > 80 else ''}", anchor="w")
                label.pack(side="left", fill="x", expand=True, padx=6)

                copy_btn = ctk.CTkButton(frame, text="Copy", width=50, command=lambda t=text: pyperclip.copy(t))
                copy_btn.pack(side="right", padx=6)

if __name__ == "__main__":
    app = ClipTraceApp()
    app.mainloop()

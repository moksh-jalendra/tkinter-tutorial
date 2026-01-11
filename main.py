import tkinter as tk
from tkinter import scrolledtext, filedialog, simpledialog
import pygame
import os
import glob
import time
import psutil # NEW: System Monitoring
from datetime import datetime
from PIL import Image, ImageTk, ImageSequence 

# ================= SETUP =================
MUSIC_FILE = "music.mp3"
pygame.mixer.init()
music_playing = False
EDIT_MODE = False

# ================= WINDOW CONFIG =================
root = tk.Tk()
root.configure(bg="#0b0f1a")
root.overrideredirect(True)
SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()
root.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")

# Exit keys
root.bind("<Escape>", lambda e: root.destroy())

# ================= CANVAS =================
canvas = tk.Canvas(root, bg="#0b0f1a", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Placeholder for Wallpaper
wallpaper_id = None
wallpaper_img = None 

# ================= OBJECT ENGINE (THE BRAIN) =================
class SmartObject:
    def __init__(self, canvas, x, y, size=50):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.ids = [] 
        self.drag_data = {"x": 0, "y": 0}
        self.frames = [] # For GIFs
        self.anim_job = None
        self.update_job = None # For Widgets

    def bind_events(self):
        for item in self.ids:
            self.canvas.tag_bind(item, "<Button-1>", self.on_click)
            self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(item, "<ButtonRelease-1>", self.on_drop)

    def on_click(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        if EDIT_MODE: select_object(self)
        else: self.on_action()

    def on_drag(self, event):
        if not EDIT_MODE: return
        resize_frame.place_forget()
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        for item in self.ids:
            self.canvas.move(item, dx, dy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        # Update internal coords
        c = self.canvas.coords(self.ids[0])
        self.x, self.y = c[0], c[1]

    def on_drop(self, event):
        if EDIT_MODE: select_object(self)

    def resize(self, delta):
        self.size += delta
        if self.size < 30: self.size = 30
        self.redraw()
        select_object(self)

    def delete(self):
        self.stop_animation()
        if self.update_job: root.after_cancel(self.update_job)
        for item in self.ids: self.canvas.delete(item)
        resize_frame.place_forget()

    # --- IMAGE & GIF LOGIC ---
    def set_image(self, path):
        self.stop_animation()
        try:
            pil_img = Image.open(path)
            if path.lower().endswith(".gif") and getattr(pil_img, "is_animated", False):
                self.original_gif_path = path 
                self.reload_gif()
            else:
                pil_img = pil_img.resize((self.size, self.size), Image.Resampling.LANCZOS)
                self.image_ref = ImageTk.PhotoImage(pil_img)
                self.redraw(use_image_ref=True)
        except Exception as e:
            print(f"Error: {e}")

    def reload_gif(self):
        try:
            pil_img = Image.open(self.original_gif_path)
            self.frames = [ImageTk.PhotoImage(f.resize((self.size, self.size))) for f in ImageSequence.Iterator(pil_img)]
            self.frame_index = 0
            self.animate()
        except: pass

    def animate(self):
        if not self.frames: return
        self.canvas.itemconfig(self.main_id, image=self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.anim_job = root.after(100, self.animate)

    def stop_animation(self):
        if self.anim_job: root.after_cancel(self.anim_job)
        self.frames = []

    def redraw(self, use_image_ref=False): pass
    def on_action(self): pass

# ================= WIDGET: APP ICON =================
class AppIcon(SmartObject):
    def __init__(self, canvas, name, path, x, y):
        super().__init__(canvas, x, y, size=45)
        self.name = name
        self.file_path = path
        self.redraw()

    def redraw(self, use_image_ref=False):
        for item in self.ids: self.canvas.delete(item)
        
        if use_image_ref:
            self.main_id = self.canvas.create_image(self.x, self.y, image=self.image_ref)
        else:
            self.main_id = self.canvas.create_text(self.x, self.y, text="🚀", font=("Segoe UI", int(self.size/1.5)), fill="white")

        self.text_id = self.canvas.create_text(self.x, self.y + 35, text=self.name, font=("Segoe UI", 9), fill="#ccc")
        self.ids = [self.main_id, self.text_id]
        self.bind_events()

    def on_action(self):
        try: os.startfile(self.file_path)
        except: pass

# ================= WIDGET: CLOCK =================
class ClockWidget(SmartObject):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, size=30) # Size here controls font size
        self.redraw()
        self.update_time()

    def redraw(self, use_image_ref=False):
        for item in self.ids: self.canvas.delete(item)
        
        # Background Box
        self.box_id = self.canvas.create_rectangle(
            self.x, self.y, self.x+200, self.y+80, fill="#111", outline="#00ff9d", width=2
        )
        # Time Text
        self.text_id = self.canvas.create_text(
            self.x+100, self.y+25, text="00:00", font=("Consolas", self.size, "bold"), fill="white"
        )
        # Date Text
        self.date_id = self.canvas.create_text(
            self.x+100, self.y+60, text="...", font=("Segoe UI", 10), fill="#aaa"
        )
        
        self.ids = [self.box_id, self.text_id, self.date_id]
        self.bind_events()

    def update_time(self):
        now = datetime.now()
        t = now.strftime("%H:%M:%S")
        d = now.strftime("%A, %d %b %Y")
        self.canvas.itemconfig(self.text_id, text=t)
        self.canvas.itemconfig(self.date_id, text=d)
        self.update_job = root.after(1000, self.update_time)

# ================= WIDGET: CPU/RAM STATS =================
class SysStatsWidget(SmartObject):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y, size=14)
        self.redraw()
        self.update_stats()

    def redraw(self, use_image_ref=False):
        for item in self.ids: self.canvas.delete(item)
        
        # Background
        self.box_id = self.canvas.create_rectangle(
            self.x, self.y, self.x+160, self.y+90, fill="#1a0b0b", outline="#ff006e", width=2
        )
        # Labels
        self.cpu_id = self.canvas.create_text(self.x+80, self.y+25, text="CPU: 0%", font=("Consolas", 14), fill="#ff006e")
        self.ram_id = self.canvas.create_text(self.x+80, self.y+55, text="RAM: 0%", font=("Consolas", 14), fill="#00d4ff")
        
        self.ids = [self.box_id, self.cpu_id, self.ram_id]
        self.bind_events()

    def update_stats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.canvas.itemconfig(self.cpu_id, text=f"CPU: {cpu}%")
        self.canvas.itemconfig(self.ram_id, text=f"RAM: {ram}%")
        self.update_job = root.after(2000, self.update_stats)

# ================= WIDGET: PHOTO/ASSISTANT =================
class PhotoWidget(SmartObject):
    def __init__(self, canvas, x, y, is_assistant=False):
        super().__init__(canvas, x, y, size=100 if not is_assistant else 60)
        self.is_assistant = is_assistant
        self.redraw()

    def redraw(self, use_image_ref=False):
        if not hasattr(self, 'main_id'): pass
        else:
            for item in self.ids: self.canvas.delete(item)

        if use_image_ref:
            self.main_id = self.canvas.create_image(self.x, self.y, image=self.image_ref)
        elif self.frames:
            self.main_id = self.canvas.create_image(self.x, self.y, image=self.frames[0])
        else:
            if self.is_assistant:
                self.main_id = self.canvas.create_oval(self.x-30, self.y-30, self.x+30, self.y+30, fill="#ff006e")
            else:
                self.main_id = self.canvas.create_rectangle(self.x-50, self.y-50, self.x+50, self.y+50, fill="#222", outline="white", dash=(2,2))
        
        self.ids = [self.main_id]
        self.bind_events()
        if self.frames: self.animate()

    def on_action(self):
        if self.is_assistant: bot_msg("Listening...")

# ================= UI CONTROLS =================
current_selection = None
resize_frame = tk.Frame(root, bg="#00ff9d", padx=5, pady=5)

def select_object(obj):
    global current_selection
    current_selection = obj
    c = canvas.coords(obj.ids[0])
    if not c: return
    # If shape (4 coords) vs image (2 coords)
    y_off = -60 if len(c) == 2 else -20
    resize_frame.place(x=c[0], y=c[1] + y_off)
    resize_frame.lift()

def set_wallpaper():
    global wallpaper_img, wallpaper_id
    path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.png;*.jpeg")])
    if path:
        img = Image.open(path)
        img = img.resize((SCREEN_W, SCREEN_H), Image.Resampling.LANCZOS)
        wallpaper_img = ImageTk.PhotoImage(img)
        
        if wallpaper_id: canvas.delete(wallpaper_id)
        wallpaper_id = canvas.create_image(0, 0, image=wallpaper_img, anchor="nw")
        canvas.tag_lower(wallpaper_id) # Send to back

def add_new_app():
    path = filedialog.askopenfilename(title="Select .exe or Shortcut", filetypes=[("Executables", "*.exe;*.lnk;*.url")])
    if path:
        name = os.path.splitext(os.path.basename(path))[0]
        AppIcon(canvas, name, path, SCREEN_W//2, SCREEN_H//2)

def delete_current():
    global current_selection
    if current_selection:
        current_selection.delete()
        current_selection = None

# Edit Toolbar
tk.Button(resize_frame, text="IMG", command=lambda: current_selection.set_image(filedialog.askopenfilename()), bg="white").pack(side="left", padx=2)
tk.Button(resize_frame, text="+", command=lambda: current_selection.resize(10), bg="white").pack(side="left")
tk.Button(resize_frame, text="-", command=lambda: current_selection.resize(-10), bg="white").pack(side="left")
tk.Button(resize_frame, text="DEL", command=delete_current, bg="#ff4444", fg="white").pack(side="left", padx=5)

def toggle_edit():
    global EDIT_MODE
    EDIT_MODE = not EDIT_MODE
    
    if EDIT_MODE:
        top_bar.place(x=0, y=0, relwidth=1, height=40)
        bot_msg("EDIT MODE: Add apps, widgets, or change wallpaper.")
    else:
        top_bar.place_forget()
        resize_frame.place_forget()
        bot_msg("Desktop Locked.")

# Top Control Bar (Visible only in Edit Mode)
top_bar = tk.Frame(root, bg="#333")
tk.Button(top_bar, text="DONE", command=toggle_edit, bg="#00ff9d", font=("bold")).pack(side="left", padx=10, pady=5)
tk.Button(top_bar, text="Set Wallpaper", command=set_wallpaper, bg="white").pack(side="left", padx=5)
tk.Button(top_bar, text="+ App", command=add_new_app, bg="white").pack(side="left", padx=5)
tk.Button(top_bar, text="+ Photo", command=lambda: PhotoWidget(canvas, 300, 300), bg="white").pack(side="left", padx=5)
tk.Button(top_bar, text="+ Clock", command=lambda: ClockWidget(canvas, 400, 300), bg="white").pack(side="left", padx=5)
tk.Button(top_bar, text="+ Sys Stats", command=lambda: SysStatsWidget(canvas, 500, 300), bg="white").pack(side="left", padx=5)

# Main "Start" Button (Always visible)
start_btn = tk.Button(root, text="⚙ Settings", command=toggle_edit, bg="#222", fg="white")
start_btn.place(x=10, y=10)

# ================= CHAT =================
chat_frame = tk.Frame(root, bg="#14182b", relief="solid", bd=1)
chat_frame.place(relx=0.75, rely=0.6, relwidth=0.24, relheight=0.35)
chat_log = scrolledtext.ScrolledText(chat_frame, bg="#14182b", fg="white", height=10)
chat_log.pack(fill="both", expand=True)
entry = tk.Entry(chat_frame, bg="#222", fg="white")
entry.pack(fill="x")

def bot_msg(txt):
    chat_log.insert("end", f"Bot: {txt}\n")
    chat_log.see("end")

def send(e):
    msg = entry.get()
    entry.delete(0, "end")
    if msg == "exit": root.destroy()
    elif "play" in msg:
         if os.path.exists(MUSIC_FILE) and not music_playing:
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.play()
    else: bot_msg(f"Echo: {msg}")
entry.bind("<Return>", send)

# ================= RUN =================
asst = PhotoWidget(canvas, 100, SCREEN_H-150, is_assistant=True)
bot_msg("Welcome. Click 'Settings' to customize.")
root.mainloop()
import tkinter as tk
from tkinter import scrolledtext, filedialog
import pygame
import os
import glob
from PIL import Image, ImageTk

# ================= SETUP =================
MUSIC_FILE = "music.mp3"
pygame.mixer.init()
music_playing = False
EDIT_MODE = False

# ================= WINDOW =================
root = tk.Tk()
root.configure(bg="#0b0f1a")
root.overrideredirect(True)
SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()
root.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")
root.bind("<Escape>", lambda e: root.destroy())

canvas = tk.Canvas(root, bg="#0b0f1a", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# ================= ANIMATION ENGINE =================
class AnimatedAssistant:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = 80
        
        # Sprite Storage
        # Format: {"idle": [img1, img2], "left": [img1, img2]...}
        self.sprites = {
            "idle": [], "left": [], "right": [], "jump": [], "wave": []
        }
        self.current_action = "idle"
        self.frame_index = 0
        self.is_moving = False
        
        # Initial Draw
        self.main_id = canvas.create_oval(x, y, x+50, y+50, fill="#ff006e", outline="")
        self.ids = [self.main_id]
        self.bind_events()
        
        # Start Animation Loop
        self.animate()

    def load_sprites_from_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Sprite Images")
        if not folder: return
        
        # Helper to load a sequence
        def load_seq(action_name):
            frames = []
            # Look for file_1.png, file_2.png, etc.
            files = sorted(glob.glob(os.path.join(folder, f"{action_name}_*.png")))
            if not files: 
                # Try simple format: action1.png, action2.png
                files = sorted(glob.glob(os.path.join(folder, f"{action_name}*.png")))
            
            for f in files:
                try:
                    img = Image.open(f).resize((self.size, self.size), Image.Resampling.NEAREST)
                    frames.append(ImageTk.PhotoImage(img))
                except: pass
            
            if frames: 
                self.sprites[action_name] = frames
                print(f"Loaded {len(frames)} frames for {action_name}")

        # Load all states
        load_seq("idle")
        load_seq("left")
        load_seq("right")
        load_seq("jump")
        load_seq("wave")
        
        # Switch to image mode if we found sprites
        if self.sprites["idle"]:
            self.canvas.delete(self.main_id)
            self.main_id = self.canvas.create_image(self.x, self.y, image=self.sprites["idle"][0])
            self.ids = [self.main_id]
            self.bind_events()

    def bind_events(self):
        self.canvas.tag_bind(self.main_id, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.main_id, "<B1-Motion>", self.on_drag)

    def animate(self):
        # 1. Get frames for current action
        frames = self.sprites.get(self.current_action)
        
        # 2. Update Image if frames exist
        if frames:
            self.frame_index = (self.frame_index + 1) % len(frames)
            current_img = frames[self.frame_index]
            self.canvas.itemconfig(self.main_id, image=current_img)
        
        # 3. Loop (Speed: 100ms)
        root.after(100, self.animate)

    def walk_to(self, tx, ty, callback=None):
        if self.is_moving: return
        self.is_moving = True
        
        def step():
            dx, dy = 0, 0
            moved = False
            speed = 8
            
            # Determine Direction
            if tx > self.x + speed:
                dx = speed
                self.current_action = "right" if self.sprites["right"] else "idle"
                moved = True
            elif tx < self.x - speed:
                dx = -speed
                self.current_action = "left" if self.sprites["left"] else "idle"
                moved = True
            else:
                # X alignment done, move Y
                if ty > self.y + speed:
                    dy = speed
                    moved = True
                elif ty < self.y - speed:
                    dy = -speed
                    moved = True
            
            if moved:
                self.x += dx
                self.y += dy
                self.canvas.move(self.main_id, dx, dy)
                root.after(20, step)
            else:
                self.is_moving = False
                self.current_action = "idle"
                if callback: callback()

        step()

    def do_action(self, action_name):
        # Temporarily switch action then go back to idle
        if action_name in self.sprites and self.sprites[action_name]:
            self.current_action = action_name
            # Calculate duration: frames * speed
            duration = len(self.sprites[action_name]) * 100
            root.after(duration + 200, lambda: setattr(self, 'current_action', 'idle'))
        else:
            bot_msg(f"I don't have images for {action_name}!")

    # Standard Dragging
    def on_click(self, e):
        if EDIT_MODE:
            self.drag_start = (e.x, e.y)
        else:
            self.do_action("wave") # Wave when clicked!

    def on_drag(self, e):
        if not EDIT_MODE: return
        dx = e.x - self.drag_start[0]
        dy = e.y - self.drag_start[1]
        self.canvas.move(self.main_id, dx, dy)
        self.x += dx
        self.y += dy
        self.drag_start = (e.x, e.y)

# ================= OBJECTS (Apps) =================
class SimpleApp:
    def __init__(self, name, path, x, y):
        self.path = path
        self.id = canvas.create_text(x, y, text="📂\n"+name, fill="white", font=("Segoe UI", 10), justify="center")
        canvas.tag_bind(self.id, "<Button-1>", lambda e: self.open_app())
        
        # Keep reference to enable drag later if needed
        self.drag_data = {"x":0, "y":0}
        canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
        canvas.tag_bind(self.id, "<Button-1>", self.on_click)

    def open_app(self):
        if not EDIT_MODE:
            try: os.startfile(self.path)
            except: pass
    
    def on_click(self, e):
        self.drag_data["x"] = e.x
        self.drag_data["y"] = e.y

    def on_drag(self, e):
        if EDIT_MODE:
            dx = e.x - self.drag_data["x"]
            dy = e.y - self.drag_data["y"]
            canvas.move(self.id, dx, dy)
            self.drag_data["x"] = e.x
            self.drag_data["y"] = e.y

def load_apps():
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    cx, cy = 50, 50
    if os.path.exists(desktop):
        for f in glob.glob(os.path.join(desktop, "*.lnk"))[:12]:
            name = os.path.splitext(os.path.basename(f))[0]
            SimpleApp(name, f, cx, cy)
            cy += 80
            if cy > SCREEN_H - 100:
                cy = 50
                cx += 80

# ================= CHAT UI (TOGGLEABLE) =================
chat_visible = True

def toggle_chat():
    global chat_visible
    if chat_visible:
        chat_frame.place_forget()
        toggle_btn.config(text="💬") # Show bubble icon
        chat_visible = False
    else:
        chat_frame.place(relx=0.75, rely=0.6, relwidth=0.24, relheight=0.35)
        toggle_btn.config(text="➖") # Show minimize icon
        chat_visible = True

# Chat Frame
chat_frame = tk.Frame(root, bg="#14182b", relief="solid", bd=1)
chat_frame.place(relx=0.75, rely=0.6, relwidth=0.24, relheight=0.35)

chat_log = scrolledtext.ScrolledText(chat_frame, bg="#14182b", fg="white", height=10)
chat_log.pack(fill="both", expand=True)
entry = tk.Entry(chat_frame, bg="#222", fg="white")
entry.pack(fill="x")

# Toggle Button (Floating outside frame)
toggle_btn = tk.Button(root, text="➖", command=toggle_chat, bg="#ff006e", fg="white", font=("bold"))
toggle_btn.place(relx=0.96, rely=0.56, width=30, height=30)

def bot_msg(txt):
    if not chat_visible: return # Don't print if hidden (or you could force open)
    chat_log.insert("end", f"Bot: {txt}\n")
    chat_log.see("end")

def send(e):
    msg = entry.get().lower()
    entry.delete(0, "end")
    
    if "exit" in msg: root.destroy()
    elif "jump" in msg: 
        bot_msg("Jumping!")
        assistant.do_action("jump")
    elif "come here" in msg:
        bot_msg("Coming...")
        assistant.walk_to(SCREEN_W//2, SCREEN_H//2)
    elif "load sprites" in msg:
        bot_msg("Select your folder...")
        assistant.load_sprites_from_folder()
    else: 
        bot_msg(f"Echo: {msg}")

entry.bind("<Return>", send)

# ================= EDIT MODE TOGGLE =================
def toggle_edit_mode():
    global EDIT_MODE
    EDIT_MODE = not EDIT_MODE
    mode_btn.config(bg="#00ff9d" if EDIT_MODE else "#333", text="DONE" if EDIT_MODE else "Customize")
    bot_msg("Edit Mode " + ("ON" if EDIT_MODE else "OFF"))

mode_btn = tk.Button(root, text="Customize", command=toggle_edit_mode, bg="#333", fg="white")
mode_btn.place(x=20, y=20)

# ================= RUN =================
load_apps()
assistant = AnimatedAssistant(canvas, SCREEN_W//2, SCREEN_H//2)
bot_msg("Type 'load sprites' to load images!")
bot_msg("Type 'jump' or 'come here' to test.")

root.mainloop()
import tkinter as tk
from tkinter import scrolledtext
import pygame
import os
import glob

# ================= SETUP =================
MUSIC_FILE = "music.mp3"
pygame.mixer.init()
music_playing = False
is_moving = False

# ================= WINDOW =================
root = tk.Tk()
root.configure(bg="#0b0f1a")
root.overrideredirect(True) # Borderless

SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()
root.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")

# Exit keys
root.bind("<Escape>", lambda e: root.destroy())

# ================= CANVAS =================
canvas = tk.Canvas(root, bg="#0b0f1a", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# ================= ASSETS =================
# Character
CHAR_SIZE = 45
char_x = 100
char_y = SCREEN_H - 200
char = canvas.create_oval(
    char_x, char_y, char_x + CHAR_SIZE, char_y + CHAR_SIZE,
    fill="#ff006e", outline=""
)

# Music Station
player_x = SCREEN_W // 2 - 90
player_y = SCREEN_H - 120
canvas.create_rectangle(
    player_x, player_y, player_x + 180, player_y + 60,
    fill="#14182b", outline=""
)
canvas.create_text(
    player_x + 90, player_y + 30,
    text="🎵 Music Player", fill="white", font=("Segoe UI", 11, "bold")
)

# ================= LOGIC & ANIMATION =================
def bot_msg(text):
    chat_log.config(state="normal")
    chat_log.insert("end", f"Bot: {text}\n")
    chat_log.config(state="disabled")
    chat_log.see("end")

def user_msg(text):
    chat_log.config(state="normal")
    chat_log.insert("end", f"You: {text}\n")
    chat_log.config(state="disabled")
    chat_log.see("end")

def play_music():
    global music_playing
    if not os.path.exists(MUSIC_FILE):
        bot_msg(f"Missing {MUSIC_FILE}")
        return
    if not music_playing:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.play(-1)
        music_playing = True
        bot_msg("Playing music 🎶")

def pause_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
        bot_msg("Music paused ⏸")

def move_character(tx, ty, action=None):
    global char_x, char_y, is_moving
    if is_moving:
        bot_msg("Wait, I'm moving!")
        return

    is_moving = True
    step = 8

    def animate():
        global char_x, char_y, is_moving
        moved = False
        diff_x = tx - char_x
        diff_y = ty - char_y

        if abs(diff_x) > step:
            dx = step if diff_x > 0 else -step
            char_x += dx
            canvas.move(char, dx, 0)
            moved = True
        
        if abs(diff_y) > step:
            dy = step if diff_y > 0 else -step
            char_y += dy
            canvas.move(char, 0, dy)
            moved = True

        if moved:
            root.after(10, animate)
        else:
            is_moving = False
            if action: action()

    animate()

# ================= DRAGGABLE APP ICONS =================
class DesktopIcon:
    def __init__(self, canvas, name, path, x, y):
        self.canvas = canvas
        self.path = path
        self.name = name
        self.font_size = 14
        
        # Create visual elements
        # 1. The Icon (Emoji)
        self.icon_id = canvas.create_text(
            x, y, text="🚀", font=("Segoe UI", self.font_size * 2), fill="white"
        )
        # 2. The Text Label
        self.text_id = canvas.create_text(
            x, y + 30, text=name, font=("Segoe UI", 9), fill="#cccccc"
        )
        
        # Group them for easy reference
        self.ids = [self.icon_id, self.text_id]

        # Bind events
        for item in self.ids:
            canvas.tag_bind(item, "<Button-1>", self.on_click)          # Select/Resize
            canvas.tag_bind(item, "<Double-Button-1>", self.on_double)  # Open
            canvas.tag_bind(item, "<B1-Motion>", self.on_drag)          # Move

        # State for dragging
        self.drag_data = {"x": 0, "y": 0}

    def on_click(self, event):
        # 1. Record start position for drag
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        # 2. Show Resize Controls
        show_resize_controls(self)

    def on_drag(self, event):
        # Hide controls while dragging
        resize_frame.place_forget()
        
        # Calculate distance moved
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        # Move all parts of the icon
        for item in self.ids:
            self.canvas.move(item, dx, dy)
            
        # Update drag data
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_double(self, event):
        bot_msg(f"Opening {self.name}... 📂")
        try:
            os.startfile(self.path)
        except Exception as e:
            bot_msg(f"Error: {e}")

    def resize(self, delta):
        # Limit size
        if self.font_size + delta < 8 or self.font_size + delta > 40:
            return
            
        self.font_size += delta
        # Update Icon Size
        self.canvas.itemconfig(self.icon_id, font=("Segoe UI", int(self.font_size * 2)))
        # Update Label distance (move text down if icon gets bigger)
        # (For simplicity, we just resize the icon here)

# --- RESIZE FLOATING TOOLBAR ---
resize_frame = tk.Frame(root, bg="#ff006e", padx=2, pady=2)
current_selected_app = None

def increase_size():
    if current_selected_app: current_selected_app.resize(2)

def decrease_size():
    if current_selected_app: current_selected_app.resize(-2)

btn_plus = tk.Button(resize_frame, text="+", command=increase_size, font=("Consolas", 8, "bold"), width=3, bg="white", relief="flat")
btn_plus.pack(side="left", padx=1)
btn_minus = tk.Button(resize_frame, text="-", command=decrease_size, font=("Consolas", 8, "bold"), width=3, bg="white", relief="flat")
btn_minus.pack(side="left", padx=1)

def show_resize_controls(app_obj):
    global current_selected_app
    current_selected_app = app_obj
    
    # Get current position of the icon
    coords = canvas.coords(app_obj.icon_id)
    if coords:
        # Place the floating toolbar slightly above the icon
        toolbar_x = coords[0] - 25 
        toolbar_y = coords[1] - 50 
        resize_frame.place(x=toolbar_x, y=toolbar_y)
        resize_frame.lift()

# --- APP LOADING LOGIC ---
def load_apps_to_canvas():
    paths = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.environ.get('PUBLIC', 'C:\\Users\\Public'), "Desktop")
    ]
    
    # Grid positioning variables
    start_x = 50
    start_y = 50
    current_x = start_x
    current_y = start_y
    
    for folder in paths:
        if os.path.exists(folder):
            files = glob.glob(os.path.join(folder, "*.lnk")) + glob.glob(os.path.join(folder, "*.url"))
            for file in files:
                name = os.path.splitext(os.path.basename(file))[0]
                
                # Create the Draggable Icon Object
                DesktopIcon(canvas, name, file, current_x, current_y)
                
                # Grid Logic
                current_y += 100
                if current_y > SCREEN_H - 150:
                    current_y = start_y
                    current_x += 100

# ================= CHAT UI =================
chat_frame = tk.Frame(root, bg="#14182b", bd=1, relief="solid")
chat_frame.place(relx=0.72, rely=0.60, relwidth=0.26, relheight=0.35)

input_frame = tk.Frame(chat_frame, bg="#1f243d", pady=5, padx=5)
input_frame.pack(side="bottom", fill="x")

header = tk.Label(chat_frame, text="Chat Assistant", bg="#0f1221", fg="white", font=("Segoe UI", 10, "bold"), pady=5)
header.pack(side="top", fill="x")

chat_log = scrolledtext.ScrolledText(
    chat_frame, bg="#14182b", fg="#e0e0e0",
    font=("Segoe UI", 10), wrap="word", relief="flat", bd=0, highlightthickness=0
)
chat_log.pack(side="top", fill="both", expand=True, padx=10, pady=5)
chat_log.config(state="disabled")

entry = tk.Entry(
    input_frame, bg="#1f243d", fg="grey",
    insertbackground="white", relief="flat", font=("Segoe UI", 11)
)
entry.pack(side="left", fill="x", expand=True, padx=(5, 5))

def on_entry_click(event):
    if entry.get() == "Type a message...":
        entry.delete(0, "end")
        entry.config(fg="white")

def on_focus_out(event):
    if entry.get() == "":
        entry.insert(0, "Type a message...")
        entry.config(fg="grey")

entry.insert(0, "Type a message...")
entry.bind('<FocusIn>', on_entry_click)
entry.bind('<FocusOut>', on_focus_out)

def handle_send(event=None):
    msg = entry.get().strip()
    if not msg or msg == "Type a message...": return
    entry.delete(0, "end")
    user_msg(msg)
    msg = msg.lower()

    if "play" in msg:
        bot_msg("On it 🎵")
        move_character(player_x + 80, player_y - 50, play_music)
    elif "pause" in msg:
        bot_msg("Pausing ⏸")
        move_character(player_x + 80, player_y - 50, pause_music)
    elif "exit" in msg:
        root.destroy()
    else:
        bot_msg("Commands: play, pause, exit")

send_btn = tk.Button(
    input_frame, text="SEND", bg="#ff006e", fg="white",
    font=("Segoe UI", 9, "bold"), relief="flat",
    activebackground="#d6005c", activeforeground="white",
    command=handle_send
)
send_btn.pack(side="right", padx=5)
entry.bind("<Return>", handle_send)

# ================= STARTUP =================
load_apps_to_canvas()
bot_msg("System Online. Desktop Apps Loaded.")
root.mainloop()
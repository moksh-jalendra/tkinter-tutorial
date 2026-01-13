import tkinter as tk
from tkinter import filedialog, simpledialog, scrolledtext, messagebox, Scale
import os
from PIL import Image, ImageTk, ImageOps

# ================= GLOBAL CONFIG =================
SCREEN_W = 0
SCREEN_H = 0
ASSISTANT_ACTIVE = False

# New Data Structure:
# ACTIONS = {
#    "idle": { "frames": [img1, img2], "delay": 100 },
#    "walk": { "frames": [img1, img2], "delay": 50 }
# }
ACTIONS = {} 
CURRENT_ACTION = "idle"

# ================= MAIN WINDOW =================
root = tk.Tk()
root.title("Custom Assistant Engine")
root.configure(bg="#111")
root.overrideredirect(True) 
SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()
root.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")
root.bind("<Escape>", lambda e: root.destroy())

canvas = tk.Canvas(root, bg="#0b0f1a", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# ================= ASSISTANT ENGINE =================
class Assistant:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2
        self.main_id = None
        self.frame_index = 0
        self.facing_right = True
        self.is_moving = False
        self.anim_job = None
        self.target_x = 0
        self.target_y = 0

    def enable(self):
        if self.main_id: return 
        if "idle" not in ACTIONS: self.create_placeholder()
        
        # Start
        start_data = ACTIONS["idle"]
        self.main_id = self.canvas.create_image(self.x, self.y, image=start_data["frames"][0])
        self.animate()
        
        self.canvas.tag_bind(self.main_id, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.main_id, "<Button-1>", self.drag_start)

    def disable(self):
        if self.main_id:
            self.canvas.delete(self.main_id)
            self.main_id = None
        if self.anim_job:
            root.after_cancel(self.anim_job)
            self.anim_job = None

    def create_placeholder(self):
        img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(img)
        d.ellipse((0,0,50,50), fill='red')
        tk_img = ImageTk.PhotoImage(img)
        ACTIONS["idle"] = {"frames": [tk_img], "delay": 200}

    def animate(self):
        if not self.main_id: return

        # 1. Get Action Data
        action_name = CURRENT_ACTION
        
        # Logic for Left Walk
        if action_name == "walk" and not self.facing_right and "walk_left" in ACTIONS:
            action_name = "walk_left"

        data = ACTIONS.get(action_name, ACTIONS.get("idle"))
        if not data or not data["frames"]: return

        # 2. Cycle Frames
        frames = data["frames"]
        self.frame_index = (self.frame_index + 1) % len(frames)
        img = frames[self.frame_index]
        
        self.canvas.itemconfig(self.main_id, image=img)
        
        # 3. Dynamic FPS (Delay)
        delay = data.get("delay", 100) # Default 100ms if missing
        self.anim_job = root.after(delay, self.animate)

    def set_action(self, name):
        global CURRENT_ACTION
        # CRITICAL FIX: Only reset animation if the action is DIFFERENT.
        # This prevents the "walk" animation from resetting to frame 0 every millisecond.
        if CURRENT_ACTION != name:
            if name in ACTIONS or name == "walk_left":
                CURRENT_ACTION = name
                self.frame_index = 0

    def walk_to(self, tx, ty):
        self.target_x = tx
        self.target_y = ty
        self.is_moving = True
        self.move_step()

    def move_step(self):
        if not self.is_moving or not self.main_id: return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        speed = 5

        if dist < speed:
            self.is_moving = False
            self.set_action("idle")
            return

        move_x = (dx / dist) * speed
        move_y = (dy / dist) * speed
        
        self.x += move_x
        self.y += move_y
        self.canvas.move(self.main_id, move_x, move_y)

        # Direction Logic
        if move_x > 0: self.facing_right = True
        elif move_x < 0: self.facing_right = False
        
        # Trigger Walk Action (Safe now because of the check in set_action)
        self.set_action("walk")
        root.after(20, self.move_step)

    def drag_start(self, e):
        self.drag_offset = (e.x - self.x, e.y - self.y)

    def drag(self, e):
        self.x = e.x - self.drag_offset[0]
        self.y = e.y - self.drag_offset[1]
        self.canvas.coords(self.main_id, self.x, self.y)

assistant = Assistant(canvas)

# ================= SETTINGS MANAGER =================
class SettingsWindow:
    def __init__(self):
        self.win = tk.Toplevel(root)
        self.win.title("Settings")
        self.win.geometry("450x600")
        self.win.configure(bg="#222")

        # Enable/Disable
        self.status_var = tk.StringVar(value="Enable Assistant" if not ASSISTANT_ACTIVE else "Disable Assistant")
        tk.Button(self.win, textvariable=self.status_var, command=self.toggle_active, 
                  bg="#00ff9d", font=("Arial", 11, "bold")).pack(fill="x", padx=10, pady=10)

        # Action List
        tk.Label(self.win, text="Select Action to Edit:", bg="#222", fg="white").pack()
        self.listbox = tk.Listbox(self.win, bg="#333", fg="white", height=6)
        self.listbox.pack(fill="x", padx=10)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_action)
        
        # Action Buttons
        frame_btns = tk.Frame(self.win, bg="#222")
        frame_btns.pack(fill="x", padx=10, pady=5)
        tk.Button(frame_btns, text="+ New Action", command=self.add_action, bg="#444", fg="white").pack(side="left", fill="x", expand=True)
        tk.Button(frame_btns, text="Upload Images", command=self.upload_images, bg="#ff006e", fg="white").pack(side="left", fill="x", expand=True)
        tk.Button(frame_btns, text="Delete", command=self.delete_action, bg="red", fg="white").pack(side="left", fill="x", expand=True)

        # --- FPS CONTROL ---
        tk.Label(self.win, text="Animation Speed (Lower is Faster):", bg="#222", fg="#00ff9d").pack(pady=(20, 0))
        self.fps_slider = Scale(self.win, from_=20, to=500, orient="horizontal", bg="#333", fg="white", command=self.update_fps)
        self.fps_slider.set(100) # Default
        self.fps_slider.pack(fill="x", padx=20)
        
        self.refresh_list()

    def toggle_active(self):
        global ASSISTANT_ACTIVE
        ASSISTANT_ACTIVE = not ASSISTANT_ACTIVE
        if ASSISTANT_ACTIVE:
            self.status_var.set("Disable Assistant")
            assistant.enable()
        else:
            self.status_var.set("Enable Assistant")
            assistant.disable()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for action in ACTIONS:
            count = len(ACTIONS[action]["frames"])
            delay = ACTIONS[action]["delay"]
            self.listbox.insert(tk.END, f"{action} ({count} frames) [Speed: {delay}ms]")

    def on_select_action(self, event):
        # Update Slider when user clicks an action
        sel = self.listbox.curselection()
        if sel:
            txt = self.listbox.get(sel[0])
            name = txt.split(" ")[0]
            if name in ACTIONS:
                current_delay = ACTIONS[name]["delay"]
                self.fps_slider.set(current_delay)

    def update_fps(self, val):
        # Save Slider value to current action
        sel = self.listbox.curselection()
        if sel:
            txt = self.listbox.get(sel[0])
            name = txt.split(" ")[0]
            if name in ACTIONS:
                ACTIONS[name]["delay"] = int(val)
                # Refresh list text to show new speed
                # (Optional optimization: don't full refresh to avoid deselecting)

    def add_action(self):
        name = simpledialog.askstring("New Action", "Action Name (e.g. run, sleep):")
        if name:
            name = name.lower().strip()
            if name not in ACTIONS:
                ACTIONS[name] = {"frames": [], "delay": 100}
                self.refresh_list()

    def delete_action(self):
        sel = self.listbox.curselection()
        if sel:
            name = self.listbox.get(sel[0]).split(" ")[0]
            if name in ACTIONS:
                del ACTIONS[name]
                if name == "walk" and "walk_left" in ACTIONS:
                    del ACTIONS["walk_left"]
                self.refresh_list()

    def upload_images(self):
        sel = self.listbox.curselection()
        if not sel: return
        name = self.listbox.get(sel[0]).split(" ")[0]

        paths = filedialog.askopenfilenames(title=f"Images for {name}", filetypes=[("Images", "*.png;*.jpg;*.gif")])
        if paths:
            frames = []
            for p in paths:
                try:
                    img = Image.open(p).resize((100, 100), Image.Resampling.NEAREST)
                    frames.append(ImageTk.PhotoImage(img))
                except: pass
            
            ACTIONS[name]["frames"] = frames
            
            # Auto-Flip for Walk
            if name == "walk":
                left_frames = []
                for p in paths:
                    try:
                        img = Image.open(p).resize((100, 100), Image.Resampling.NEAREST)
                        img = ImageOps.mirror(img)
                        left_frames.append(ImageTk.PhotoImage(img))
                    except: pass
                # Create walk_left with same delay as walk
                ACTIONS["walk_left"] = {"frames": left_frames, "delay": ACTIONS["walk"]["delay"]}

            self.refresh_list()

# ================= CHAT UI =================
btn_set = tk.Button(root, text="⚙ Settings", command=SettingsWindow, bg="#333", fg="white")
btn_set.place(x=20, y=20)

chat_frame = tk.Frame(root, bg="#14182b")
chat_frame.place(relx=0.75, rely=0.6, relwidth=0.24, relheight=0.35)
log = scrolledtext.ScrolledText(chat_frame, bg="#111", fg="white", height=10)
log.pack(fill="both", expand=True)
entry = tk.Entry(chat_frame, bg="#333", fg="white")
entry.pack(fill="x")

def bot_msg(txt):
    log.insert("end", f"Bot: {txt}\n")
    log.see("end")

def send(e):
    msg = entry.get().strip().lower()
    entry.delete(0, "end")
    if msg == "exit": root.destroy()
    elif "come" in msg: assistant.walk_to(SCREEN_W//2, SCREEN_H//2)
    elif msg in ACTIONS: 
        assistant.set_action(msg)
        bot_msg(f"Action: {msg}")
    else: bot_msg("Unknown action")
entry.bind("<Return>", send)

root.mainloop()
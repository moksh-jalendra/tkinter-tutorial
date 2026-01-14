import tkinter as tk
from tkinter import filedialog, simpledialog, scrolledtext, messagebox, Scale, Checkbutton
import os
import random
from PIL import Image, ImageTk, ImageSequence, ImageOps

# ================= GLOBAL CONFIGURATION =================
SCREEN_W = 0
SCREEN_H = 0
ASSISTANT_ACTIVE = False
EDIT_MODE = False
PATROL_MODE = False
SELECTED_OBJECT = None

# Data Storage
# ACTIONS format: {"idle": [PIL_Image1, PIL_Image2], "walk": [...]} 
# Note: We store raw PIL images now, not PhotoImages, to allow dynamic resizing.
ACTIONS = {}  
APPS = []
WALLPAPER_IMG = None 

# ================= MAIN WINDOW =================
root = tk.Tk()
root.title("Desktop Engine Ultimate")
root.configure(bg="#111")
root.overrideredirect(True) 
SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()
root.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")
root.bind("<Escape>", lambda e: root.destroy())

canvas = tk.Canvas(root, bg="#0b0f1a", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Refs
wallpaper_id = None
gizmo_rect = None
gizmo_handle = None

# ================= UI: DRAGGABLE WINDOW =================
class DraggableWindow(tk.Frame):
    def __init__(self, parent, title="Command Center", x=100, y=100, width=400, height=650):
        super().__init__(parent, bg="#222", bd=2, relief="raised")
        self.place(x=x, y=y, width=width, height=height)
        
        self.title_bar = tk.Frame(self, bg="#333", height=35)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        tk.Label(self.title_bar, text=title, bg="#333", fg="white", font=("Arial", 11, "bold")).pack(side="left", padx=10)
        tk.Button(self.title_bar, text="✕", bg="#ff4444", fg="white", bd=0, command=self.close_panel).pack(side="right", fill="y")

        self.content = tk.Frame(self, bg="#222")
        self.content.pack(fill="both", expand=True, padx=5, pady=5)

        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self._drag_data = {"x": 0, "y": 0}

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self.lift() 

    def do_drag(self, event):
        x = self.winfo_x() + (event.x - self._drag_data["x"])
        y = self.winfo_y() + (event.y - self._drag_data["y"])
        self.place(x=x, y=y)

    def close_panel(self):
        self.place_forget()

settings_panel = None

# ================= CLASS: APP ICON =================
class AppIcon:
    def __init__(self, name, path, x, y):
        self.name = name
        self.path = path
        self.x = x
        self.y = y
        self.size = 60
        self.angle = 0
        self.show_text = True
        
        self.orig_pil = None
        self.frames = []
        self.is_gif = False
        self.frame_index = 0
        self.anim_job = None

        self.icon_id = canvas.create_text(x, y, text="📂", font=("Segoe UI", 30), fill="white")
        self.text_id = canvas.create_text(x, y + 40, text=name[:12], font=("Segoe UI", 10), fill="#ddd")
        self.ids = [self.icon_id, self.text_id]
        
        self.bind_events()

    def bind_events(self):
        for item in self.ids:
            canvas.tag_bind(item, "<Button-1>", self.on_click)
            canvas.tag_bind(item, "<Double-Button-1>", self.open_app)
            canvas.tag_bind(item, "<B1-Motion>", self.on_drag)

    def set_image(self, path):
        try:
            self.stop_animation()
            raw_img = Image.open(path)
            
            if getattr(raw_img, "is_animated", False):
                self.is_gif = True
                self.frames = []
                for frame in ImageSequence.Iterator(raw_img):
                    self.frames.append(frame.convert("RGBA"))
                self.animate_gif()
            else:
                self.is_gif = False
                self.orig_pil = raw_img
                self.redraw()
        except Exception as e:
            print(f"Error: {e}")

    def animate_gif(self):
        if not self.is_gif or not self.frames: return
        
        pil = self.frames[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        
        # Resize dynamically to match Green Box size
        img = pil.resize((self.size, self.size), Image.Resampling.NEAREST)
        if self.angle != 0: img = img.rotate(-self.angle, expand=True)
        self.tk_img = ImageTk.PhotoImage(img)
        
        canvas.delete(self.icon_id)
        self.icon_id = canvas.create_image(self.x, self.y, image=self.tk_img)
        self.ids[0] = self.icon_id
        self.bind_events()
        
        self.anim_job = root.after(100, self.animate_gif)

    def stop_animation(self):
        if self.anim_job:
            root.after_cancel(self.anim_job)
            self.anim_job = None

    def redraw(self):
        # Called when resizing static images
        if self.is_gif: return
        
        if self.orig_pil:
            img = self.orig_pil.resize((self.size, self.size), Image.Resampling.LANCZOS)
            if self.angle != 0: img = img.rotate(-self.angle, expand=True)
            self.tk_img = ImageTk.PhotoImage(img)
            canvas.delete(self.icon_id)
            self.icon_id = canvas.create_image(self.x, self.y, image=self.tk_img)
        else:
            canvas.delete(self.icon_id)
            f_size = int(self.size / 2)
            self.icon_id = canvas.create_text(self.x, self.y, text="📂", font=("Segoe UI", f_size), fill="white")

        offset = (self.size / 2) + 15
        canvas.coords(self.text_id, self.x, self.y + offset)
        canvas.itemconfigure(self.text_id, state="normal" if self.show_text else "hidden")
        
        self.ids = [self.icon_id, self.text_id]
        self.bind_events()

    def on_click(self, e):
        self.drag_offset = (e.x - self.x, e.y - self.y)
        if EDIT_MODE: select_object(self)

    def on_drag(self, e):
        if not EDIT_MODE: return
        self.x = e.x - self.drag_offset[0]
        self.y = e.y - self.drag_offset[1]
        
        if not self.is_gif:
            offset = (self.size / 2) + 15
            canvas.coords(self.icon_id, self.x, self.y)
            canvas.coords(self.text_id, self.x, self.y + offset)
        
        if self == SELECTED_OBJECT: update_gizmo(self)

    def open_app(self, e):
        if not EDIT_MODE:
            try: os.startfile(self.path)
            except: pass

# ================= CLASS: ASSISTANT (FIXED) =================
class Assistant:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x, self.y = SCREEN_W // 2, SCREEN_H // 2
        self.size = 100
        self.name = "Assistant"
        self.main_id = None
        self.frame_index = 0
        self.facing_right = True
        self.is_moving = False
        self.patrol_dir = 1
        
        self.angle = 0 
        self.show_text = False

    def enable(self):
        if self.main_id: return
        if "idle" not in ACTIONS: self.create_placeholder()
        self.animate()
        if PATROL_MODE: self.start_patrol()

    def create_placeholder(self):
        img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(img)
        d.ellipse((0,0,50,50), fill='red')
        ACTIONS["idle"] = [img] # Store as List of PIL Images

    def animate(self):
        if not ASSISTANT_ACTIVE: return

        # 1. Determine Action
        action = "walk" if self.is_moving else "idle"
        
        # 2. Get Frame List
        frames = ACTIONS.get(action, ACTIONS.get("idle"))
        if not frames: return

        # 3. Cycle Frame
        self.frame_index = (self.frame_index + 1) % len(frames)
        pil_frame = frames[self.frame_index]
        
        # 4. CRITICAL FIX: DYNAMIC PROCESSING
        # Resize to current self.size (Gizmo Size)
        processed_img = pil_frame.resize((self.size, self.size), Image.Resampling.NEAREST)
        
        # Mirror Check (If moving left, FLIP it)
        if not self.facing_right:
            processed_img = ImageOps.mirror(processed_img)

        # Convert to Tkinter
        tk_img = ImageTk.PhotoImage(processed_img)
        self._tk_ref = tk_img # Keep reference

        # 5. Draw/Update
        if not self.main_id:
            self.main_id = self.canvas.create_image(self.x, self.y, image=tk_img)
            self.canvas.tag_bind(self.main_id, "<Button-1>", self.on_click)
            self.canvas.tag_bind(self.main_id, "<B1-Motion>", self.drag)
        else:
            self.canvas.itemconfig(self.main_id, image=tk_img)
        
        # 6. Loop (Speed)
        root.after(100, self.animate)

    # --- PATROL LOGIC ---
    def start_patrol(self):
        self.y = SCREEN_H - 120
        self.is_moving = True
        self.patrol_loop()

    def patrol_loop(self):
        if not PATROL_MODE or not ASSISTANT_ACTIVE: 
            self.is_moving = False
            return
        
        self.is_moving = True
        speed = 5
        self.x += speed * self.patrol_dir
        
        # Bounce logic
        if self.x > SCREEN_W - 50:
            self.patrol_dir = -1
            self.facing_right = False # Turn Left
        elif self.x < 50:
            self.patrol_dir = 1
            self.facing_right = True  # Turn Right
            
        self.canvas.coords(self.main_id, self.x, self.y)
        if self == SELECTED_OBJECT: update_gizmo(self)
        root.after(20, self.patrol_loop)

    def pause_patrol(self):
        global PATROL_MODE
        saved = PATROL_MODE
        PATROL_MODE = False
        self.is_moving = False # This forces Idle animation
        
        def resume():
            global PATROL_MODE
            PATROL_MODE = saved
            if PATROL_MODE: self.patrol_loop()
        root.after(3000, resume)

    def on_click(self, e):
        self.drag_offset = (e.x - self.x, e.y - self.y)
        if EDIT_MODE: select_object(self)
        elif PATROL_MODE: self.pause_patrol()
        else: bot_msg("Hello!")

    def drag(self, e):
        if not EDIT_MODE: return
        self.x = e.x - self.drag_offset[0]
        self.y = e.y - self.drag_offset[1]
        self.canvas.coords(self.main_id, self.x, self.y)
        if self == SELECTED_OBJECT: update_gizmo(self)

    # Required for Gizmo (The animate loop handles the actual drawing)
    def redraw(self): pass 
    def set_image(self, path): pass

assistant = Assistant(canvas)

# ================= GIZMO & SELECTION =================
def update_gizmo(obj):
    global gizmo_rect, gizmo_handle
    if gizmo_rect: canvas.delete(gizmo_rect)
    if gizmo_handle: canvas.delete(gizmo_handle)
    
    if not EDIT_MODE or not obj: return
    
    s = obj.size / 2
    x, y = obj.x, obj.y
    gizmo_rect = canvas.create_rectangle(x-s-5, y-s-5, x+s+5, y+s+5, outline="#00ff9d", width=2, dash=(4,4))
    gizmo_handle = canvas.create_rectangle(x+s, y+s, x+s+10, y+s+10, fill="#00ff9d")
    canvas.tag_bind(gizmo_handle, "<B1-Motion>", lambda e: on_gizmo(e, obj))

def on_gizmo(e, obj):
    new_size = max(abs(e.x - obj.x), abs(e.y - obj.y)) * 2
    if 30 < new_size < 800:
        obj.size = int(new_size)
        obj.redraw()
        update_gizmo(obj)
    if settings_panel and settings_panel.winfo_ismapped():
        scale_size.set(obj.size)

def select_object(obj):
    global SELECTED_OBJECT
    SELECTED_OBJECT = obj
    update_gizmo(obj)
    if settings_panel and settings_panel.winfo_ismapped():
        populate_inspector(obj)

# ================= SETTINGS UI =================
def toggle_settings():
    if settings_panel:
        if settings_panel.winfo_ismapped(): settings_panel.place_forget()
        else: settings_panel.place(x=100, y=100); settings_panel.lift()
    else: create_settings_panel()

def create_settings_panel():
    global settings_panel, insp_frame, btn_edit_mode, list_actions, scale_size
    settings_panel = DraggableWindow(root, title="Command Center", width=380, height=650)
    p = settings_panel.content
    
    # 1. Edit Mode
    btn_edit_mode = tk.Button(p, text="Start Edit Mode", command=toggle_edit, bg="#444", fg="white")
    btn_edit_mode.pack(fill="x", pady=5)
    
    # 2. Assistant
    lbl = tk.LabelFrame(p, text="Assistant", bg="#222", fg="#00ff9d")
    lbl.pack(fill="x", pady=5)
    tk.Button(lbl, text="Toggle On/Off", command=toggle_asst, bg="#ff006e", fg="white").pack(fill="x", padx=5)
    
    global var_patrol
    var_patrol = tk.IntVar(value=0)
    tk.Checkbutton(lbl, text="Enable Screen Patrol", variable=var_patrol, bg="#222", fg="white", 
                   selectcolor="#444", command=toggle_patrol).pack(anchor="w", padx=5)

    # 3. Actions
    tk.Label(lbl, text="Animations (Select to Upload):", bg="#222", fg="#aaa").pack(anchor="w", padx=5)
    list_actions = tk.Listbox(lbl, bg="#333", fg="white", height=4)
    list_actions.pack(fill="x", padx=5)
    
    f_btn = tk.Frame(lbl, bg="#222")
    f_btn.pack(fill="x")
    tk.Button(f_btn, text="+ Add Name", command=add_action, bg="#444", fg="white").pack(side="left", expand=True, fill="x")
    tk.Button(f_btn, text="Upload Img", command=upload_act_img, bg="#444", fg="white").pack(side="left", expand=True, fill="x")
    refresh_action_list()

    # 4. Inspector
    insp_frame = tk.LabelFrame(p, text="Inspector", bg="#222", fg="#00ff9d")
    insp_frame.pack(fill="x", pady=5)
    
    # Placeholders
    tk.Label(insp_frame, text="Size / Scale", bg="#222", fg="white").pack(anchor="w")
    scale_size = Scale(insp_frame, from_=30, to=600, orient="horizontal", bg="#333", fg="white")
    scale_size.pack(fill="x")

    # 5. Desktop
    tk.Label(p, text="Desktop", bg="#222", fg="#aaa").pack(pady=(10,0))
    tk.Button(p, text="Set Wallpaper", command=set_wallpaper, bg="#555", fg="white").pack(fill="x")
    tk.Button(p, text="+ Add App", command=add_app, bg="#00ff9d", fg="black").pack(fill="x")

def populate_inspector(obj):
    for w in insp_frame.winfo_children(): w.destroy()
    tk.Label(insp_frame, text=f"Target: {obj.name}", bg="#222", fg="white").pack()
    
    # Scale Slider
    tk.Label(insp_frame, text="Size", bg="#222", fg="white").pack(anchor="w")
    global scale_size
    scale_size = Scale(insp_frame, from_=30, to=600, orient="horizontal", bg="#333", fg="white",
                       command=lambda v: update_prop(obj, "size", int(v)))
    scale_size.set(obj.size)
    scale_size.pack(fill="x")
    
    if hasattr(obj, 'set_image'):
        tk.Button(insp_frame, text="Change Icon", bg="#00d4ff", command=lambda: change_img(obj)).pack(fill="x", pady=5)

def refresh_action_list():
    list_actions.delete(0, tk.END)
    if "idle" not in ACTIONS: ACTIONS["idle"] = []
    if "walk" not in ACTIONS: ACTIONS["walk"] = []
    for k in ACTIONS: list_actions.insert(tk.END, k)

def update_prop(obj, prop, val):
    setattr(obj, prop, val)
    obj.redraw()
    if prop == "size": update_gizmo(obj)

def change_img(obj):
    path = filedialog.askopenfilename()
    if path: obj.set_image(path)

# ================= FUNCTIONS =================
def toggle_edit():
    global EDIT_MODE
    EDIT_MODE = not EDIT_MODE
    btn_edit_mode.config(text="Stop Edit Mode" if EDIT_MODE else "Start Edit Mode", bg="#00ff9d" if EDIT_MODE else "#444")
    if not EDIT_MODE: canvas.delete(gizmo_rect); canvas.delete(gizmo_handle)

def toggle_asst():
    global ASSISTANT_ACTIVE
    ASSISTANT_ACTIVE = not ASSISTANT_ACTIVE
    if ASSISTANT_ACTIVE: assistant.enable()

def toggle_patrol():
    global PATROL_MODE
    PATROL_MODE = bool(var_patrol.get())
    if PATROL_MODE: assistant.start_patrol()

def set_wallpaper():
    global WALLPAPER_IMG, wallpaper_id
    path = filedialog.askopenfilename()
    if path:
        img = Image.open(path).resize((SCREEN_W, SCREEN_H), Image.Resampling.LANCZOS)
        WALLPAPER_IMG = ImageTk.PhotoImage(img)
        if wallpaper_id: canvas.delete(wallpaper_id)
        wallpaper_id = canvas.create_image(0, 0, image=WALLPAPER_IMG, anchor="nw")
        canvas.tag_lower(wallpaper_id)

def add_app():
    path = filedialog.askopenfilename()
    if path: APPS.append(AppIcon(os.path.basename(path), path, 200, 200))

def add_action():
    name = simpledialog.askstring("New", "Action Name:")
    if name: 
        ACTIONS[name] = []
        refresh_action_list()

def upload_act_img():
    sel = list_actions.curselection()
    if not sel: return
    name = list_actions.get(sel[0])
    paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png;*.jpg;*.gif")])
    if paths:
        frames = [Image.open(p) for p in paths]
        ACTIONS[name] = frames # Store List of PIL
        messagebox.showinfo("Success", f"Uploaded {len(frames)} frames to {name}")

# ================= CHAT UI =================
btn_set = tk.Button(root, text="⚙ Settings", command=toggle_settings, bg="#333", fg="white")
btn_set.place(x=20, y=20)

chat_frame = tk.Frame(root, bg="#14182b")
chat_frame.place(relx=0.75, rely=0.6, relwidth=0.24, relheight=0.35)

def toggle_chat():
    if chat_frame.winfo_viewable(): chat_frame.place_forget()
    else: chat_frame.place(relx=0.75, rely=0.6, relwidth=0.24, relheight=0.35)

# Round toggle button
btn_chat_toggle = tk.Button(root, text="💬", command=toggle_chat, bg="#00ff9d", font=("Arial", 14), bd=0)
btn_chat_toggle.place(relx=0.96, rely=0.94, width=40, height=40, anchor="center")

log = scrolledtext.ScrolledText(chat_frame, bg="#111", fg="white", height=10)
log.pack(fill="both", expand=True)
entry = tk.Entry(chat_frame, bg="#333", fg="white")
entry.pack(fill="x")

def bot_msg(txt): log.insert("end", f"Bot: {txt}\n"); log.see("end")
entry.bind("<Return>", lambda e: bot_msg("Echo: " + entry.get()))

root.mainloop()



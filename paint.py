import tkinter as tk
from tkinter import colorchooser

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro Paint - High Precision Zoom")
        self.root.geometry("1000x800")
        
        # --- State Variables ---
        self.brush_color = "black"
        self.eraser_color = "white"
        self.base_brush_size = 5 # The logical size of the brush
        self.old_x = None
        self.old_y = None
        
        # Page & Zoom State
        self.pages = []       
        self.current_page = 0 
        self.zoom_scale = 1.0
        
        # --- UI Layout ---
        self.create_top_toolbar()
        
        self.canvas_container = tk.Frame(self.root, bg="#ccc")
        self.canvas_container.pack(fill=tk.BOTH, expand=True)

        self.create_bottom_nav()

        # Initialize first page
        self.add_new_page()

    def create_top_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED, bg="#e0e0e0")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar, text="Color", command=self.choose_color, bg="white").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="Eraser", command=self.use_eraser, bg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Label(toolbar, text="Size:", bg="#e0e0e0").pack(side=tk.LEFT, padx=(10,0))
        self.size_slider = tk.Scale(toolbar, from_=1, to=50, orient=tk.HORIZONTAL, command=self.change_size, bg="#e0e0e0")
        self.size_slider.set(self.base_brush_size)
        self.size_slider.pack(side=tk.LEFT, padx=5)

        tk.Label(toolbar, text="| Zoom:", bg="#e0e0e0").pack(side=tk.LEFT, padx=10)
        self.lbl_zoom = tk.Label(toolbar, text="100%", width=6, bg="white")
        self.lbl_zoom.pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="(Use Ctrl + Scroll to Zoom)", bg="#e0e0e0", fg="#666").pack(side=tk.LEFT, padx=10)

    def create_bottom_nav(self):
        nav_bar = tk.Frame(self.root, bg="#333", height=40)
        nav_bar.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(nav_bar, text="<< Prev", command=self.prev_page, bg="#666", fg="white").pack(side=tk.LEFT, padx=10, pady=5)
        self.lbl_page_num = tk.Label(nav_bar, text="Page 1 / 1", bg="#333", fg="white")
        self.lbl_page_num.pack(side=tk.LEFT, expand=True)
        tk.Button(nav_bar, text="Next >>", command=self.next_page, bg="#666", fg="white").pack(side=tk.RIGHT, padx=10, pady=5)
        tk.Button(nav_bar, text="+ New Page", command=self.add_new_page, bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=10, pady=5)

    # --- Page Logic ---

    def add_new_page(self):
        frame = tk.Frame(self.canvas_container, bg="#ccc")
        v_bar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        h_bar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)

        # Huge scrollregion to support massive zooming
        canvas = tk.Canvas(frame, bg="white", scrollregion=(0, 0, 3000, 3000),
                           yscrollcommand=v_bar.set, xscrollcommand=h_bar.set)
        
        v_bar.config(command=canvas.yview)
        h_bar.config(command=canvas.xview)

        canvas.grid(row=0, column=0, sticky="nsew")
        v_bar.grid(row=0, column=1, sticky="ns")
        h_bar.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Draw Bindings
        canvas.bind('<B1-Motion>', self.paint)
        canvas.bind('<ButtonRelease-1>', self.reset)
        
        # ZOOM BINDINGS (Windows/Linux use MouseWheel, Linux also uses Button-4/5)
        canvas.bind('<Control-MouseWheel>', self.on_mousewheel) # Windows Zoom
        canvas.bind('<Button-4>', self.on_linux_scroll_up)      # Linux Zoom In
        canvas.bind('<Button-5>', self.on_linux_scroll_down)    # Linux Zoom Out

        self.pages.append({"frame": frame, "canvas": canvas})
        self.switch_to_page(len(self.pages) - 1)

    def switch_to_page(self, index):
        if 0 <= index < len(self.pages):
            self.pages[self.current_page]["frame"].pack_forget()
            self.current_page = index
            self.pages[self.current_page]["frame"].pack(fill=tk.BOTH, expand=True)
            self.lbl_page_num.config(text=f"Page {self.current_page + 1} / {len(self.pages)}")
            
            # Reset zoom when switching pages (optional, but cleaner)
            self.zoom_scale = 1.0
            self.lbl_zoom.config(text="100%")

    def prev_page(self): self.switch_to_page(self.current_page - 1)
    def next_page(self): self.switch_to_page(self.current_page + 1)

    # --- High Precision Drawing Logic ---

    def get_active_canvas(self):
        return self.pages[self.current_page]["canvas"]

    def paint(self, event):
        c = self.get_active_canvas()
        
        # 1. Map screen click to canvas coordinate (accounting for scroll)
        canvas_x = c.canvasx(event.x)
        canvas_y = c.canvasy(event.y)

        # Note: We do NOT divide by zoom_scale for the coordinate here.
        # Why? Because we want to draw exactly where the zoomed canvas is.
        # If the canvas is scaled 2x, point 100 becomes 200. If I click at 200, 
        # I want to draw at 200.

        if self.old_x and self.old_y:
            # 2. Calculate DYNAMIC line width
            # If we are zoomed in 2x, the brush must be 2x thicker to look consistent.
            current_width = self.base_brush_size * self.zoom_scale

            c.create_line(self.old_x, self.old_y, canvas_x, canvas_y,
                          width=current_width, fill=self.brush_color,
                          capstyle=tk.ROUND, smooth=True, splinesteps=36)
        
        self.old_x = canvas_x
        self.old_y = canvas_y

    def reset(self, event):
        self.old_x = None
        self.old_y = None

    # --- Advanced Zoom Logic ---

    def on_mousewheel(self, event):
        """Windows/MacOS Zoom Handling"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def on_linux_scroll_up(self, event): self.zoom_in()
    def on_linux_scroll_down(self, event): self.zoom_out()

    def zoom_in(self):
        if self.zoom_scale < 5.0:
            self.apply_zoom(1.1) # 10% increments for smoothness

    def zoom_out(self):
        if self.zoom_scale > 0.5:
            self.apply_zoom(0.9)

    def apply_zoom(self, factor):
        c = self.get_active_canvas()
        
        # 1. Scale Coordinates (The easy part)
        # This moves the lines further apart or closer together
        c.scale("all", 0, 0, factor, factor)
        
        # 2. Scale Line Thickness (The hard part)
        # We must iterate through every item and adjust its width
        # otherwise lines look like thin wireframes when zoomed in.
        for item in c.find_all():
            try:
                # Get current width
                current_width = float(c.itemcget(item, "width"))
                # Apply scaling factor
                new_width = current_width * factor
                # Update item
                c.itemconfig(item, width=new_width)
            except:
                pass # Ignore items that don't have a width (like images)

        # 3. Update State
        self.zoom_scale *= factor
        
        # 4. Update Scroll Region
        # We assume the base page is 2000x2000. We scale the scrollable area.
        new_region = 3000 * self.zoom_scale
        c.configure(scrollregion=(0, 0, new_region, new_region))
        
        self.lbl_zoom.config(text=f"{int(self.zoom_scale * 100)}%")

    # --- Tools ---

    def choose_color(self):
        color = colorchooser.askcolor(color=self.brush_color)[1]
        if color: self.brush_color = color

    def use_eraser(self):
        self.brush_color = self.eraser_color

    def change_size(self, val):
        self.base_brush_size = float(val)
# pyinstaller --noconsole --onefile main.py    
if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)

    root.mainloop()
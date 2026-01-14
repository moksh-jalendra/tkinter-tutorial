import tkinter as tk
from tkinter import font as tkfont

class RealisticCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("350x500")
        self.root.configure(bg="#202020") # Dark background

        # --- Styling Constants ---
        self.COLORS = {
            'bg': '#202020',          # Window Background
            'display_bg': '#202020',  # Display Background
            'text': '#FFFFFF',        # Text Color
            'btn_num': '#333333',     # Number Buttons (Dark Grey)
            'btn_op': '#FF9500',      # Operator Buttons (Orange)
            'btn_func': '#A5A5A5',    # Function Buttons (Light Grey)
            'btn_hover': '#4c4c4c',   # Hover color for numbers
            'op_hover': '#ffb042'     # Hover color for operators
        }
        
        # Fonts
        self.DEFAULT_FONT = tkfont.Font(family="Helvetica", size=20, weight="bold")
        self.DISPLAY_FONT = tkfont.Font(family="Helvetica", size=40, weight="bold")

        # --- State ---
        self.expression = ""
        self.input_text = tk.StringVar()

        # --- Layout ---
        self.create_display()
        self.create_buttons()

        # Configure Grid Weights so buttons expand evenly when window is resized
        for i in range(6): # 6 rows (0 to 5)
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(4): # 4 columns
            self.root.grid_columnconfigure(i, weight=1)


    def create_display(self):
        # The display area
        display_frame = tk.Frame(self.root, bg=self.COLORS['display_bg'])
        display_frame.grid(row=0, column=0, columnspan=4, sticky="nsew", pady=(20, 10))

        input_field = tk.Entry(
            display_frame, 
            textvariable=self.input_text, 
            font=self.DISPLAY_FONT, 
            bg=self.COLORS['display_bg'], 
            fg=self.COLORS['text'], 
            bd=0, 
            justify=tk.RIGHT,
            insertbackground="white" # Cursor color
        )
        input_field.pack(fill=tk.BOTH, expand=True, padx=20)


    def create_buttons(self):
        # Button layout: (Text, Row, Col, ColorType, ColumnSpan)
        buttons = [
            # Row 1
            ('C', 1, 0, 'func', 1), ('%', 1, 1, 'func', 1), ('//', 1, 2, 'func', 1), ('/', 1, 3, 'op', 1),
            # Row 2
            ('7', 2, 0, 'num', 1),  ('8', 2, 1, 'num', 1),  ('9', 2, 2, 'num', 1),  ('*', 2, 3, 'op', 1),
            # Row 3
            ('4', 3, 0, 'num', 1),  ('5', 3, 1, 'num', 1),  ('6', 3, 2, 'num', 1),  ('-', 3, 3, 'op', 1),
            # Row 4
            ('1', 4, 0, 'num', 1),  ('2', 4, 1, 'num', 1),  ('3', 4, 2, 'num', 1),  ('+', 4, 3, 'op', 1),
            # Row 5 (Bottom Row)
            ('0', 5, 0, 'num', 2),  # Spans 2 columns
            ('.', 5, 2, 'num', 1),  
            ('=', 5, 3, 'op', 1)    
        ]

        for btn_data in buttons:
            text = btn_data[0]
            row = btn_data[1]
            col = btn_data[2]
            color_type = btn_data[3]
            colspan = btn_data[4]

            # Determine colors based on type
            if color_type == 'num':
                bg_color = self.COLORS['btn_num']
                hover_color = self.COLORS['btn_hover']
                fg_color = 'white'
            elif color_type == 'op':
                bg_color = self.COLORS['btn_op']
                hover_color = self.COLORS['op_hover']
                fg_color = 'white'
            else:
                bg_color = self.COLORS['btn_func']
                hover_color = '#d4d4d2'
                fg_color = 'black'
            
            # Create the command
            cmd = lambda t=text: self.on_click(t)

            btn = tk.Button(
                self.root, 
                text=text, 
                bg=bg_color, 
                fg=fg_color, 
                font=self.DEFAULT_FONT, 
                bd=0, 
                relief="flat",
                activebackground=hover_color,
                cursor="hand2",
                command=cmd
            )
            
            # sticky="nsew" ensures the button fills the entire grid cell(s)
            btn.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=1, pady=1)

            # Bind hover events for visual feedback
            btn.bind("<Enter>", lambda e, b=btn, c=hover_color: b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.config(bg=c))


    def on_click(self, char):
        if char == 'C':
            self.expression = ""
            self.input_text.set("")
        elif char == '=':
            try:
                # Evaluate the expression
                result = str(eval(self.expression))
                self.input_text.set(result)
                self.expression = result
            except:
                self.input_text.set("Error")
                self.expression = ""
        else:
            self.expression += str(char)
            self.input_text.set(self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    app = RealisticCalculator(root)
    root.mainloop()
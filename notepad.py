import tkinter as tk
from tkinter import filedialog, messagebox

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Untitled - Notepad")
        self.root.geometry("800x600")

        # --- Text Area ---
        # undo=True enables Ctrl+Z functionality
        self.text_area = tk.Text(self.root, font=("Arial", 14), undo=True, wrap="word")
        self.text_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # --- Scrollbar ---
        scrollbar = tk.Scrollbar(self.root, command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        # --- Menu Bar ---
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit Menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Cut", command=lambda: self.root.focus_get().event_generate('<<Cut>>'))
        edit_menu.add_command(label="Copy", command=lambda: self.root.focus_get().event_generate('<<Copy>>'))
        edit_menu.add_command(label="Paste", command=lambda: self.root.focus_get().event_generate('<<Paste>>'))
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)

    def new_file(self):
        self.root.title("Untitled - Notepad")
        self.text_area.delete(1.0, tk.END)

    def open_file(self):
        file = filedialog.askopenfilename(defaultextension=".txt",
                                          filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if file:
            self.root.title(f"{file} - Notepad")
            self.text_area.delete(1.0, tk.END)
            with open(file, "r") as f:
                self.text_area.insert(1.0, f.read())

    def save_file(self):
        file = filedialog.asksaveasfilename(initialfile="untitled.txt",
                                            defaultextension=".txt",
                                            filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if file:
            with open(file, "w") as f:
                f.write(self.text_area.get(1.0, tk.END))
            self.root.title(f"{file} - Notepad")

if __name__ == "__main__":
    root = tk.Tk()
    app = Notepad(root)
    root.mainloop()
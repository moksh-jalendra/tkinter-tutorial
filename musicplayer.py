import tkinter as tk
from tkinter import filedialog
import pygame
import os

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python MP3 Player")
        self.root.geometry("500x400")
        self.root.configure(bg="#212121")
        self.root.resizable(False, False)

        # Initialize Pygame Mixer
        pygame.mixer.init()

        # Track Variables
        self.playlist = []
        self.current_song_index = 0
        self.is_paused = False

        # --- UI Design ---
        
        # 1. Image/Logo Area (Placeholder for Album Art)
        logo_frame = tk.Frame(self.root, bg="#212121", height=50)
        logo_frame.pack(fill=tk.X, pady=10)
        tk.Label(logo_frame, text="Music Player", bg="#212121", fg="#ff5722", font=("Arial", 18, "bold")).pack()

        # 2. Playlist Box
        frame_list = tk.Frame(self.root, bg="#212121")
        frame_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.playlist_box = tk.Listbox(frame_list, bg="#333333", fg="white", font=("Arial", 11), selectbackground="#ff5722", bd=0)
        self.playlist_box.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar for playlist
        scroll = tk.Scrollbar(frame_list, command=self.playlist_box.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlist_box.config(yscrollcommand=scroll.set)

        # 3. Control Buttons Frame
        control_frame = tk.Frame(self.root, bg="#212121")
        control_frame.pack(fill=tk.X, pady=20)

        # Button Styling
        btn_style = {"bg": "#ff5722", "fg": "white", "width": 8, "font": ("Arial", 10, "bold"), "bd": 0, "activebackground": "#e64a19"}

        # Buttons
        tk.Button(control_frame, text="Load", command=self.load_music, **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="Prev", command=self.prev_song, **btn_style).pack(side=tk.LEFT, padx=5)
        self.play_btn = tk.Button(control_frame, text="Play", command=self.play_music, **btn_style)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Next", command=self.next_song, **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Volume Control
        tk.Label(control_frame, text="Vol", bg="#212121", fg="white").pack(side=tk.LEFT, padx=(15, 5))
        self.vol_scale = tk.Scale(control_frame, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL, bg="#212121", fg="white", highlightthickness=0, command=self.set_volume, length=80)
        self.vol_scale.set(0.5) # Default volume 50%
        self.vol_scale.pack(side=tk.LEFT)

        # Status Bar
        self.status_bar = tk.Label(self.root, text="Waiting for music...", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#333", fg="white")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_music(self):
        """Loads a folder of music"""
        directory = filedialog.askdirectory()
        if directory:
            os.chdir(directory)
            songs = os.listdir(directory)

            self.playlist.clear()
            self.playlist_box.delete(0, tk.END)

            for song in songs:
                if song.endswith(".mp3"):
                    self.playlist.append(song)
                    self.playlist_box.insert(tk.END, song)
            
            if self.playlist:
                self.status_bar.config(text=f"Loaded {len(self.playlist)} songs")
            else:
                self.status_bar.config(text="No MP3 files found in folder.")

    def play_music(self):
        """Handles Play/Pause logic"""
        if not self.playlist:
            return

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.play_btn.config(text="Pause")
            self.is_paused = False
            self.status_bar.config(text=f"Playing: {self.playlist[self.current_song_index]}")
        else:
            try:
                # If music is already playing but not paused, it means we want to pause
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                    self.play_btn.config(text="Play")
                    self.is_paused = True
                    self.status_bar.config(text="Paused")
                else:
                    # Start playing new song or selected song
                    selected = self.playlist_box.curselection()
                    if selected:
                        self.current_song_index = int(selected[0])
                    
                    self.play_song_at_index()
            except Exception as e:
                print(e)

    def play_song_at_index(self):
        """Helper to load and play the specific song index"""
        song_name = self.playlist[self.current_song_index]
        pygame.mixer.music.load(song_name)
        pygame.mixer.music.play()
        
        # Update UI
        self.playlist_box.selection_clear(0, tk.END)
        self.playlist_box.activate(self.current_song_index)
        self.playlist_box.selection_set(self.current_song_index, last=None)
        
        self.play_btn.config(text="Pause")
        self.is_paused = False
        self.status_bar.config(text=f"Playing: {song_name}")

    def next_song(self):
        if self.playlist:
            self.current_song_index = (self.current_song_index + 1) % len(self.playlist)
            self.play_song_at_index()

    def prev_song(self):
        if self.playlist:
            self.current_song_index = (self.current_song_index - 1) % len(self.playlist)
            self.play_song_at_index()

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
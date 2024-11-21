import customtkinter as ctk
from tkinter import filedialog, ttk, StringVar
import pygame
from audio_manager import AudioManager


class UIManager:
    def __init__(self, root):
        self.audio_manager = AudioManager()
        self.root = root
        self.setup_ui()

        # Listen for track end event
        self.root.after(100, self.check_audio_end)

    def setup_ui(self):
        self.root.title("Cheese's Music Player")
        self.root.geometry("900x600")

        # Main Layout
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Control Buttons
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(pady=10)

        ctk.CTkButton(controls_frame, text="Play", command=self.toggle_play_pause).grid(row=0, column=0, padx=5)
        ctk.CTkButton(controls_frame, text="Next", command=self.next_track).grid(row=0, column=1, padx=5)
        ctk.CTkButton(controls_frame, text="Previous", command=self.previous_track).grid(row=0, column=2, padx=5)

        # Volume Slider
        self.volume_slider = ctk.CTkSlider(controls_frame, from_=0, to=1, command=self.set_volume, width=200)
        self.volume_slider.set(0.5)
        self.volume_slider.grid(row=0, column=3, padx=5)

        # Now Playing
        self.now_playing_label = ctk.CTkLabel(main_frame, text="Now Playing: None", font=("Arial", 16))
        self.now_playing_label.pack(pady=10)

        # Search Bar
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(pady=5, fill="x")

        search_label = ctk.CTkLabel(search_frame, text="Search:")
        search_label.pack(side="left", padx=5)

        self.search_var = StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=200)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_playlist)

        # Playlist Treeview with Scrollbar
        tree_frame = ctk.CTkFrame(main_frame)
        tree_frame.pack(fill="both", expand=True)

        self.treeview = ttk.Treeview(tree_frame, columns=("Song", "Artist", "Album"), show="headings")
        self.treeview.pack(side="left", fill="both", expand=True, pady=5, padx=5)

        for col in ("Song", "Artist", "Album"):
            self.treeview.heading(col, text=col)

        # Scrollbar for Treeview
        scrollbar = ctk.CTkScrollbar(tree_frame, command=self.treeview.yview)
        scrollbar.pack(side="right", fill="y")
        self.treeview.configure(yscrollcommand=scrollbar.set)

        self.treeview.bind("<Double-1>", self.play_selected)

        # Add Folder Button
        ctk.CTkButton(main_frame, text="Add Folder", command=self.add_folder).pack(pady=10)

    def add_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            self.audio_manager.load_playlist(folder_path, append=True)  # Append mode
            self.update_playlist()

    def update_playlist(self, filtered_list=None):
        self.treeview.delete(*self.treeview.get_children())
        playlist = filtered_list if filtered_list else self.audio_manager.playlist
        for i, file in enumerate(playlist):
            song, artist, album = self.audio_manager.extract_metadata(file)
            self.treeview.insert("", "end", values=(song, artist, album))

    def filter_playlist(self, event=None):
        query = self.search_var.get().lower()
        filtered = [
            file
            for file in self.audio_manager.playlist
            if query in file.lower() or any(query in str(val).lower() for val in self.audio_manager.extract_metadata(file))
        ]
        self.update_playlist(filtered)

    def play_selected(self, event):
        selected_item = self.treeview.selection()[0]
        index = self.treeview.index(selected_item)
        self.audio_manager.play_audio(index)
        self.update_now_playing()

    def toggle_play_pause(self):
        self.audio_manager.pause_resume_audio()

    def next_track(self):
        self.audio_manager.next_audio()
        self.update_now_playing()

    def previous_track(self):
        self.audio_manager.previous_audio()
        self.update_now_playing()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume))

    def update_now_playing(self):
        if self.audio_manager.current_file:
            song, artist, album = self.audio_manager.extract_metadata(self.audio_manager.current_file)
            self.now_playing_label.configure(text=f"Now Playing: {song} by {artist}")

    def check_audio_end(self):
        if not pygame.mixer.music.get_busy() and self.audio_manager.is_playing:
            self.audio_manager.next_audio()
            self.update_now_playing()
        self.root.after(100, self.check_audio_end)

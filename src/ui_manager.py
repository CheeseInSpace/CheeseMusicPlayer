import os
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.id3 import APIC
import customtkinter as ctk
from tkinter import filedialog, ttk, StringVar
import pygame
from PIL import Image, ImageTk
from io import BytesIO


class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized.")
        except pygame.error as e:
            print(f"Failed to initialize pygame mixer: {e}")
        self.playlist = []  # Initialize the playlist as an empty list
        self.current_index = -1
        self.is_playing = False
        self.looping = False

    def load_playlist(self, folder_path, append=False):
        """Load all supported audio files from a folder into the playlist."""
        supported_formats = (".mp3", ".wav", ".ogg", ".flac")  # Supported formats
        new_tracks = [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.endswith(supported_formats)
        ]

        if append:
            self.playlist.extend(new_tracks)  # Append new tracks to the existing playlist
        else:
            self.playlist = new_tracks  # Replace the playlist

        print(f"{'Appended' if append else 'Loaded'} {len(new_tracks)} tracks into the playlist.")

    def extract_metadata(self, file_path):
        try:
            audio = File(file_path, easy=True)
            title = audio.get("title", ["Unknown Title"])[0]
            artist = audio.get("artist", ["Unknown Artist"])[0]
            album = audio.get("album", ["Unknown Album"])[0]
            return title, artist, album
        except Exception:
            return "Unknown Title", "Unknown Artist", "Unknown Album"

    def get_cover_image(self, file_path):
        try:
            audio = File(file_path)
            if isinstance(audio, MP3) and "APIC:" in audio.tags:
                artwork = audio.tags["APIC:"].data
            elif isinstance(audio, FLAC) and audio.pictures:
                artwork = audio.pictures[0].data
            else:
                return None

            image = Image.open(BytesIO(artwork))
            return image
        except Exception:
            return None

    def get_duration(self, file_path):
        try:
            audio = File(file_path)
            return audio.info.length
        except Exception:
            return 0

    def play_audio(self, index):
        if not self.playlist:
            print("Error: Playlist is empty. Load files before playing.")
            return
        if not (0 <= index < len(self.playlist)):
            print(f"Error: Index {index} out of range.")
            return
        file_path = self.playlist[index]
        if not os.path.exists(file_path):
            print(f"Error: File not found - {file_path}")
            return

        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(loops=-1 if self.looping else 0)
            self.is_playing = True  # Set is_playing to True when playback starts
            self.current_file = file_path
            self.current_index = index
            print(f"Playing: {file_path}")
        except pygame.error as e:
            print(f"Error playing audio: {e}")

    def pause_resume_audio(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            print("Playback paused.")
        else:
            pygame.mixer.music.unpause()
            print("Playback resumed.")
        self.is_playing = not self.is_playing

    def next_audio(self):
        """Play the next audio track in the playlist."""
        if not self.playlist:
            print("Playlist is empty.")
            return
        next_index = (self.current_index + 1) % len(self.playlist)
        self.play_audio(next_index)

    def previous_audio(self):
        """Play the previous audio track in the playlist."""
        if not self.playlist:
            print("Playlist is empty.")
            return
        prev_index = (self.current_index - 1) % len(self.playlist)
        self.play_audio(prev_index)


class UIManager:
    def __init__(self, root):
        self.audio_manager = AudioManager()
        self.root = root
        self.setup_ui()

        # Check for track end periodically
        self.root.after(100, self.check_audio_end)

    def setup_ui(self):
        self.root.title("Cheese's Music Player")
        self.root.geometry("900x600")

        # Header Section
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill="x", pady=10)

        self.cover_image_label = ctk.CTkLabel(header_frame, text=" ", width=120, height=120, fg_color="lightblue")
        self.cover_image_label.grid(row=0, column=0, rowspan=2, padx=20, pady=10)

        self.title_label = ctk.CTkLabel(header_frame, text="Nothing", font=("Arial", 24, "bold"))
        self.title_label.grid(row=0, column=1, sticky="w")

        self.duration_label = ctk.CTkLabel(header_frame, text="0 Tracks - 0 hr 0 min", font=("Arial", 14))
        self.duration_label.grid(row=1, column=1, sticky="w")

        # Treeview
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True)

        columns = ("#", "Title", "Artist", "Album", "Duration")
        self.treeview = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.treeview.heading(col, text=col)
            self.treeview.column(col, width=150 if col != "#" else 50, anchor="center")

        self.treeview.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.treeview.yview)
        scrollbar.pack(side="right", fill="y")
        self.treeview.configure(yscrollcommand=scrollbar.set)
        self.treeview.bind("<Double-1>", self.play_selected)

        # Controls
        controls_frame = ctk.CTkFrame(self.root)
        controls_frame.pack(pady=10)

        ctk.CTkButton(controls_frame, text="▶ Play", command=self.toggle_play_pause, width=70).grid(row=0, column=0, padx=10)
        ctk.CTkButton(controls_frame, text="Next", command=self.next_track, width=70).grid(row=0, column=1, padx=10)
        ctk.CTkButton(controls_frame, text="Previous", command=self.previous_track, width=70).grid(row=0, column=2, padx=10)

        self.volume_slider = ctk.CTkSlider(controls_frame, from_=0, to=1, command=self.set_volume, width=200)
        self.volume_slider.set(0.5)
        self.volume_slider.grid(row=0, column=3, padx=10)

        # Tools
        tools_frame = ctk.CTkFrame(self.root)
        tools_frame.pack(fill="x", pady=10)

        search_label = ctk.CTkLabel(tools_frame, text="🔍 Search:")
        search_label.pack(side="left", padx=10)

        self.search_var = StringVar()
        search_entry = ctk.CTkEntry(tools_frame, textvariable=self.search_var, width=200)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_playlist)

        ctk.CTkButton(tools_frame, text="Add Folder", command=self.add_folder, width=70).pack(side="right", padx=10)

    def add_folder(self):
        folder_path = filedialog.askdirectory(title="Select Music Folder")
        if folder_path:
            self.audio_manager.load_playlist(folder_path, append=True)  # Append the new folder
            self.update_playlist()  # Update the playlist display

    def update_playlist(self, filtered_list=None):
        self.treeview.delete(*self.treeview.get_children())
        playlist = filtered_list if filtered_list else self.audio_manager.playlist
        for i, file in enumerate(playlist):
            song, artist, album = self.audio_manager.extract_metadata(file)
            duration = self.audio_manager.get_duration(file)
            duration_formatted = f"{int(duration // 60)}:{int(duration % 60):02}"
            self.treeview.insert("", "end", values=(i + 1, song, artist, album, duration_formatted))
        self.update_duration_label()

    def update_duration_label(self):
        # Calculate the total duration in seconds and round it to avoid decimals
        total_duration = sum(round(self.audio_manager.get_duration(file)) for file in self.audio_manager.playlist)

        # Convert total duration into hours and minutes
        hours, remainder = divmod(total_duration, 3600)  # 1 hour = 3600 seconds
        minutes, seconds = divmod(remainder, 60)  # 1 minute = 60 seconds

        # Format the label to show "X Tracks - Y hr Z min"
        duration_text = f"{len(self.audio_manager.playlist)} Tracks - "

        if hours > 0:
            duration_text += f"{hours} hr "
        if minutes > 0 or hours > 0:  # To ensure minutes are shown if there are hours
            duration_text += f"{minutes} min"

        self.duration_label.configure(text=duration_text)

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
        if self.audio_manager.current_index >= 0:
            file = self.audio_manager.playlist[self.audio_manager.current_index]
            song, artist, album = self.audio_manager.extract_metadata(file)
            self.title_label.configure(text=f"{song} - {artist}")
            cover = self.audio_manager.get_cover_image(file)
            if cover:
                resized = cover.resize((120, 120))
                self.cover_image_label.configure(image=ImageTk.PhotoImage(resized))


    def check_audio_end(self):
        try:
            if pygame.mixer.get_init() and not pygame.mixer.music.get_busy() and getattr(self.audio_manager,
                                                                                         'is_playing', False):
                print("Track ended. Moving to the next track.")
                self.audio_manager.next_audio()
        except pygame.error as e:
            print(f"Mixer error during playback check: {e}")
        self.root.after(100, self.check_audio_end)


if __name__ == "__main__":
    root = ctk.CTk()
    UIManager(root)
    root.mainloop()

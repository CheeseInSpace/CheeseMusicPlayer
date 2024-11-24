import os
import pygame
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from PIL import Image
from io import BytesIO

class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init()  # Attempt to initialize the mixer
            print("Pygame mixer initialized successfully.")
        except pygame.error as e:
            print(f"Failed to initialize pygame mixer: {e}")
            raise SystemExit("Audio system initialization failed. Ensure an audio device is available.")
        self.current_file = None
        self.is_playing = False
        self.looping = False
        self.playlist = []
        self.current_index = -1

    def load_playlist(self, folder_path, append=False):
        """Load all supported audio files from a folder into the playlist."""
        supported_formats = (".mp3", ".wav", ".ogg", ".flac")  # Add supported formats here
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

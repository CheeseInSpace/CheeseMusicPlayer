import os
import pygame
from mutagen import File

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



    def get_duration(self, file_path):
        try:
            audio = File(file_path)
            if audio and hasattr(audio.info, 'length'):
                return audio.info.length  # Duration in seconds
            else:
                print(f"Warning: No length found for {file_path}")
        except Exception as e:
            print(f"Error getting duration for {file_path}: {e}")
        return 0  # Default duration if metadata is unavailable

    def load_playlist(self, folder_path, append=False):
        """Load all supported audio files from a folder into the playlist."""
        supported_formats = (".mp3", ".wav", ".ogg", ".flac")  # Add supported formats here
        new_tracks = [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.endswith(supported_formats)
        ]

        if append:
            self.playlist.extend(new_tracks)  # Add new tracks to the existing playlist
        else:
            self.playlist = new_tracks  # Replace the playlist

    def play_audio(self, index):
        """Play the audio at the specified index in the playlist."""
        if not (0 <= index < len(self.playlist)):
            return
        self.current_index = index
        self.current_file = self.playlist[index]
        pygame.mixer.music.load(self.current_file)
        pygame.mixer.music.play(loops=-1 if self.looping else 0)
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.is_playing = True

    def pause_resume_audio(self):
        """Pause or resume the current audio playback."""
        if self.is_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.is_playing = not self.is_playing

    def next_audio(self):
        """Play the next audio track in the playlist."""
        next_index = (self.current_index + 1) % len(self.playlist)
        self.play_audio(next_index)

    def previous_audio(self):
        """Play the previous audio track in the playlist."""
        prev_index = (self.current_index - 1) % len(self.playlist)
        self.play_audio(prev_index)

    def toggle_loop(self):
        """Toggle whether the audio should loop."""
        self.looping = not self.looping

    def extract_metadata(self, file_path):
        """Extract the metadata (song name, artist, album) from the audio file."""
        audio = File(file_path)
        song_name = os.path.basename(file_path)  # Default to filename
        artist = "Unknown Artist"
        album = "Unknown Album"

        if audio:
            song_name = audio.get("title", [song_name])[0]
            artist = audio.get("artist", [artist])[0]
            album = audio.get("album", [album])[0]

        return song_name, artist, album

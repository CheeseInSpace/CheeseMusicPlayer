import os
import pygame
from mutagen import File

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.current_file = None
        self.is_playing = False
        self.looping = False
        self.playlist = []
        self.current_index = -1

    def load_playlist(self, folder_path, append=False):
        import os
        supported_formats = (".mp3", ".wav", ".ogg", ".flac")  # Add supported formats TEST
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
        if not (0 <= index < len(self.playlist)):
            return
        self.current_index = index
        self.current_file = self.playlist[index]
        pygame.mixer.music.load(self.current_file)
        pygame.mixer.music.play(loops=-1 if self.looping else 0)
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.is_playing = True

    def pause_resume_audio(self):
        if self.is_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.is_playing = not self.is_playing

    def next_audio(self):
        next_index = (self.current_index + 1) % len(self.playlist)
        self.play_audio(next_index)

    def previous_audio(self):
        prev_index = (self.current_index - 1) % len(self.playlist)
        self.play_audio(prev_index)

    def toggle_loop(self):
        self.looping = not self.looping

    def extract_metadata(self, file_path):
        audio = File(file_path)
        song_name = os.path.basename(file_path)  # Default to filename
        artist = "Unknown Artist"
        album = "Unknown Album"

        if audio:
            song_name = audio.get("title", [song_name])[0]
            artist = audio.get("artist", [artist])[0]
            album = audio.get("album", [album])[0]

        return song_name, artist, album

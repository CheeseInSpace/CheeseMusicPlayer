# Cheese's Music Player

A simple Music player made by Cheese! 
## Features

- **Audio Formats**: Supports MP3, WAV, FLAC, and OGG.
- **Folder Import**: Add multiple folders with music.
- **Searching**: Find songs using a Search bar.


## Development (Windows)

### Prerequisites
Ensure you have Python installed. You'll also need the required libraries, which can be installed using the following command in the directory containing `requirements.txt`:
```bash
pip install -r requirements.txt
```
### Compiling
To compile the application into a standalone executable:
1. Navigate to the `Src` folder.
2. Run the following command:
```bash
pyinstaller --onefile main.py
```
This will generate a single executable file that you can distribute.


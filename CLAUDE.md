# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Streamo-Chromecast is a Python-based video streaming server that transcodes and streams video files to Chromecast devices with subtitle support. It uses FFmpeg for video processing, Flask for the web server, and PyQt5 for the desktop GUI. Currently tested only on Windows.

## Development Setup

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### FFmpeg Requirement
The application expects FFmpeg binaries in a `ffmpeg/` directory at the project root:
- `ffmpeg/ffmpeg` (or `ffmpeg/ffmpeg.exe` on Windows)
- `ffmpeg/ffprobe` (or `ffmpeg/ffprobe.exe` on Windows)

### Database Initialization
The SQLite database (`instance/movies.db`) is created automatically on first run. To prepopulate from an existing JSON file:
```bash
python script_prepopulate_db.py
```

## Running the Application

### GUI Mode (Desktop Application)
```bash
python video_streamer_chromecast.py
```
This launches the PyQt5 GUI and starts the Flask server on port 3432.

### Server Only Mode
```bash
python server_chromecast.py
```
This runs just the Flask server without the desktop GUI.

### Web Interface
After starting the server, access the web interface at:
```
http://<local-ip>:3432/
```
The web interface uses HLS.js to play transcoded video streams with subtitle support.

## Architecture

### Core Components

1. **Flask Server** ([server_chromecast.py](server_chromecast.py))
   - Serves web interface on port 3432
   - Routes: `/` (web UI), `/get_info` (API), `/hls/<file>` (video segments), `/tracks/<file>` (subtitles)
   - Auto-detects local IP address via [get_local_ip.py](get_local_ip.py)
   - Uses SQLAlchemy with SQLite database for movie/subtitle metadata

2. **Database Models** ([models.py](models.py))
   - `Movie`: Stores video metadata (title, duration, studio, sources, images)
   - `Subtitle`: Subtitle tracks with language/contentId, linked to movies via foreign key
   - Relationship: One movie can have multiple subtitle tracks

3. **Video Processing** ([video_streaming_commands.py](video_streaming_commands.py))
   - `get_video_info()`: Uses ffprobe to extract stream metadata (video/audio/subtitle tracks)
   - `stream_video_for_chromecast()`: Transcodes video to H.264/AAC HLS format
   - `stream_subtitle_for_chromecast()`: Extracts subtitle streams as WebVTT
   - `convert_srt_to_vtt()`: Converts external SRT files to WebVTT format
   - Output: HLS segments in `hls/<video-name>/` directory, subtitles in `tracks/` directory

4. **PyQt5 Desktop GUI** ([video_streamer_chromecast.py](video_streamer_chromecast.py))
   - File browser for selecting video files and SRT subtitle files
   - Displays available video/audio/subtitle streams from selected file
   - Triggers transcoding and database updates via background threads
   - Filename sanitization: Replaces `.+-[]` characters with underscores

5. **Database Operations** ([video_list_handler.py](video_list_handler.py))
   - `add_video_to_db()`: Creates/updates movie entries with HLS source URLs
   - `add_subtitle_to_db()`: Adds subtitle tracks to movies
   - Migration tool to import from legacy JSON format

### Data Flow

1. **Desktop GUI Workflow**:
   - User selects video file → ffprobe analyzes streams → dropdowns populated
   - User clicks "Start Video Stream" → FFmpeg transcodes to HLS → database updated → files saved to `hls/`
   - User clicks "Start Subtitles Stream" → subtitles extracted as WebVTT → saved to `tracks/`

2. **Web Interface Workflow**:
   - Browser fetches `/get_info` → receives JSON with all movies/subtitles/URLs
   - User selects video → HLS.js loads from `/hls/<video>.m3u8`
   - Subtitles loaded from `/tracks/<subtitle>.vtt`

3. **FFmpeg Transcoding**:
   - Video: H.264 codec, level 4.1, 10M max bitrate, 10-second HLS segments
   - Audio: AAC codec, stereo (2 channels), 44100 Hz sample rate
   - Output: Master playlist (`<video>.m3u8`) and segment files (`<video>/*.ts`)

### Key Design Patterns

- **Threading**: Video transcoding and FFprobe operations run in background threads to prevent GUI blocking
- **Queue-based Communication**: Main thread receives ffprobe results via `Queue` objects
- **Flask Application Context**: Database operations wrapped in `app.app_context()` for thread safety
- **Dynamic IP Configuration**: Server URLs generated using runtime-detected local IP address

## Important Notes

- **File Naming**: Video filenames are sanitized to replace special characters (`.+-[]`) with underscores for filesystem compatibility
- **HLS Segments**: The `-hls_list_size 0` parameter keeps all segments (no rotation), suitable for VOD streaming
- **Database Schema**: The `sources` field in `Movie` table stores JSON array of source objects
- **CORS**: Flask-CORS is enabled for cross-origin access to the API
- **Subtitle Format**: All subtitles are converted to WebVTT format for browser compatibility

# Streamo-Chromecast Installation Guide

Quick installation guide for getting Streamo-Chromecast up and running.

---

## Prerequisites

### Required
- **Python**: 3.7 or higher (3.12+ recommended)
- **FFmpeg**: Video transcoding tool

### Platform-Specific Notes

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg
```

**Linux (Fedora/RHEL)**:
```bash
sudo dnf install python3 python3-pip ffmpeg
```

**macOS**:
```bash
brew install python3 ffmpeg
```

**Windows**:
- Download Python from [python.org](https://www.python.org/downloads/)
- Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

---

## Installation Steps

### 1. Clone or Download the Project

```bash
cd /path/to/Streamo-Chromecast
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

**For Web-Only Usage** (Recommended):
```bash
pip install Flask==3.0.1 Werkzeug==3.0.1 Flask-CORS==4.0.0 SQLAlchemy==2.0.25 Flask-SqlAlchemy==3.1.1
```

**Or install from requirements.txt**:
```bash
pip install -r requirements.txt
```

**Note**: This includes PyQt5 for desktop GUI. If you only want web interface, you can skip PyQt5:
```bash
pip install Flask Werkzeug Flask-CORS SQLAlchemy Flask-SqlAlchemy
```

### 4. Verify Installation

```bash
python3 check_platform.py
```

You should see all green checkmarks (✓) for critical components.

---

## Running the Application

### Option 1: Web Server Only (Recommended for Linux servers)

```bash
python3 server_chromecast.py
```

Then open your browser to: `http://localhost:3432` or `http://<your-ip>:3432`

### Option 2: Desktop GUI (Requires PyQt5)

```bash
python3 video_streamer_chromecast.py
```

This launches both the GUI and web server.

---

## First-Time Setup

### 1. Prepare Video Directory

Create a directory structure for your videos:
```bash
mkdir -p hls tracks
```

- `hls/` - Stores transcoded video segments
- `tracks/` - Stores subtitle files

### 2. FFmpeg Configuration

The application will look for FFmpeg in:
1. System PATH (`/usr/bin/ffmpeg`, etc.)
2. Local `ffmpeg/` directory

If FFmpeg is not in PATH, you can:
- Install system-wide (recommended)
- Place FFmpeg binaries in `ffmpeg/` directory:
  ```
  ffmpeg/
  ├── ffmpeg (or ffmpeg.exe on Windows)
  └── ffprobe (or ffprobe.exe on Windows)
  ```

### 3. Database Initialization

The SQLite database is created automatically on first run at:
```
instance/movies.db
```

---

## Troubleshooting

### "FFmpeg not found"
**Linux**: `sudo apt install ffmpeg` or `sudo dnf install ffmpeg`
**macOS**: `brew install ffmpeg`
**Windows**: Download from ffmpeg.org and add to PATH

### "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "No module named 'flask_cors'"
```bash
pip install Flask-CORS
```

### "Port 3432 already in use"
- Stop any running Streamo-Chromecast instances
- Or change the port in `server_chromecast.py` (line 18):
  ```python
  self.__port = 3432  # Change to your preferred port
  ```

### PyQt5 Errors on Headless Server
- Skip PyQt5 installation if running web-only mode
- Use `python3 server_chromecast.py` instead of `video_streamer_chromecast.py`

### Permission Denied Errors
- Ensure you have write permissions in the project directory
- Check that `hls/` and `tracks/` directories are writable

---

## Development Setup

For contributors and developers:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run platform assessment
pytest tests/test_platform_assessment.py -v

# Format code
black .

# Lint code
ruff check .
```

---

## Quick Start Summary

**Minimum steps to get running**:

```bash
# 1. Install FFmpeg (if not already installed)
sudo apt install ffmpeg  # Ubuntu/Debian

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python packages
pip install -r requirements.txt

# 4. Verify setup
python3 check_platform.py

# 5. Start server
python3 server_chromecast.py

# 6. Open browser
# http://localhost:3432
```

---

## Next Steps

After installation:
1. Add videos through the GUI or web interface
2. Videos are automatically transcoded to HLS format
3. Stream to Chromecast or watch in browser
4. See [CLAUDE.md](CLAUDE.md) for architecture details
5. See [ROADMAP.md](ROADMAP.md) for planned improvements

---

## Support

- **Issues**: Check [ASSESSMENT_RESULTS.md](ASSESSMENT_RESULTS.md) for known issues
- **Documentation**: See [CLAUDE.md](CLAUDE.md) for technical details
- **Platform Tests**: Run `python3 check_platform.py` to diagnose issues

---

**Installation Guide Version**: 1.0
**Last Updated**: 2025-10-28

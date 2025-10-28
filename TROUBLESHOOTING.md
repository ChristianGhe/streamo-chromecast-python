# Troubleshooting Guide

Common issues and their solutions for Streamo-Chromecast.

---

## Web Interface Issues

### Error: "Bad request version" with garbled characters (SSL/HTTPS Issue)

**Symptoms**:
```
code 400, message Bad request version ('·Ú\x00"\x13\x01\x13\x03...')
```

**Cause**: Browser is trying to connect via HTTPS, but the server only supports HTTP.

**Solution**:

1. **Use HTTP, not HTTPS**:
   ```
   ✗ https://192.168.1.27:3432  (Wrong - will fail)
   ✓ http://192.168.1.27:3432   (Correct)
   ```

2. **Clear browser HSTS cache** (if browser forces HTTPS):

   **Chrome/Edge**:
   - Go to `chrome://net-internals/#hsts`
   - Under "Delete domain security policies", enter your server IP
   - Click "Delete"
   - Try accessing `http://192.168.1.27:3432` again

   **Firefox**:
   - Settings → Privacy & Security → Cookies and Site Data
   - Click "Clear Data"
   - Check "Site settings" and clear

3. **Use incognito/private mode** to test without cached settings

4. **Use localhost instead** (if accessing from same machine):
   ```
   http://localhost:3432
   ```

### Security Error: Cannot load subtitle tracks

**Symptoms**:
```
Security Error: Content at http://192.168.1.27:3432/ may not load data from http://192.168.1.27/tracks/...
```

**Cause**: The tracks URL is missing the port number (`:3432`).

**Fixed in**: This bug has been fixed in [server_chromecast.py:64](server_chromecast.py#L64)

**If you see this error**:
1. Restart the server to load the fixed code
2. Refresh your browser (hard refresh: Ctrl+Shift+R or Cmd+Shift+R)
3. Check the `/get_info` endpoint returns correct tracks URL:
   ```bash
   curl http://192.168.1.27:3432/get_info | jq '.categories[0].tracks'
   # Should show: "http://192.168.1.27:3432/tracks/"
   ```

### Cannot Access Web Interface

**Check server is running**:
```bash
# You should see Flask server logs
python3 server_chromecast.py
```

**Check port is not blocked**:
```bash
# Test if port is listening
netstat -tuln | grep 3432

# Or use curl
curl http://localhost:3432
```

**Check firewall**:
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 3432/tcp

# Fedora/RHEL
sudo firewall-cmd --add-port=3432/tcp --permanent
sudo firewall-cmd --reload
```

---

## FFmpeg Issues

### "FFmpeg not found"

**Check if FFmpeg is installed**:
```bash
which ffmpeg
ffmpeg -version
```

**Install FFmpeg**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Fedora/RHEL
sudo dnf install ffmpeg

# macOS
brew install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**Use bundled FFmpeg**:
Place FFmpeg binaries in `ffmpeg/` directory:
```
ffmpeg/
├── ffmpeg (or ffmpeg.exe on Windows)
└── ffprobe (or ffprobe.exe on Windows)
```

### FFmpeg Hangs or Takes Too Long

**Check video file**:
```bash
# Verify file is not corrupted
ffprobe /path/to/video.mkv
```

**Check available disk space**:
```bash
df -h
```

HLS transcoding can use significant disk space.

**Monitor FFmpeg process**:
```bash
# Check CPU/memory usage
top
htop

# Check FFmpeg processes
ps aux | grep ffmpeg
```

### Orphaned FFmpeg Processes

**Find and kill orphaned processes**:
```bash
# Find FFmpeg processes
ps aux | grep ffmpeg

# Kill specific process
kill <PID>

# Force kill if needed
kill -9 <PID>

# Kill all FFmpeg processes (use with caution!)
pkill ffmpeg
```

---

## Database Issues

### "Database is locked"

**Cause**: Multiple processes trying to write to SQLite simultaneously.

**Solutions**:
1. Close duplicate instances of the application
2. Check for orphaned processes:
   ```bash
   ps aux | grep python
   ps aux | grep video_streamer
   ```
3. Delete database lock file:
   ```bash
   rm instance/.movies.db-journal
   ```

### "Cannot create database"

**Check permissions**:
```bash
# Ensure instance directory is writable
mkdir -p instance
chmod 755 instance
```

### Corrupt Database

**Backup and recreate**:
```bash
# Backup
cp instance/movies.db instance/movies.db.backup

# Delete and let app recreate
rm instance/movies.db

# Restart application
python3 server_chromecast.py
```

---

## PyQt5 Issues

### "No module named 'PyQt5'"

**Web-only mode** (recommended for servers):
```bash
# Use server-only mode, no PyQt5 needed
python3 server_chromecast.py
```

**Install PyQt5** (for desktop GUI):
```bash
pip install PyQt5
```

### PyQt5 Segmentation Fault

**Known issue**: Thread safety violation (see ROADMAP.md Phase 1)

**Workaround**: Use web-only mode:
```bash
python3 server_chromecast.py
```

### PyQt5 on Headless Server

PyQt5 requires display/X11. For headless servers:
- Skip PyQt5 installation
- Use web-only mode
- Access via browser from another machine

---

## Threading Issues

### Application Hangs on Exit

**Cause**: Threads not properly terminating (known issue)

**Force quit**:
```bash
# Find process
ps aux | grep python

# Kill process
kill <PID>

# Force kill if needed
kill -9 <PID>
```

### Orphaned Processes After Crash

**Clean up**:
```bash
# Kill all related processes
pkill -f video_streamer
pkill -f server_chromecast
pkill ffmpeg
```

---

## Network Issues

### Port 3432 Already in Use

**Find what's using the port**:
```bash
# Linux
sudo lsof -i :3432
sudo netstat -tuln | grep 3432

# Or
sudo ss -tuln | grep 3432
```

**Solutions**:
1. Stop the conflicting service
2. Change port in `server_chromecast.py`:
   ```python
   self.__port = 3432  # Change to different port
   ```

### Cannot Connect from Other Devices

**Check server is listening on all interfaces**:
```bash
netstat -tuln | grep 3432
```

Should show `0.0.0.0:3432` or your local IP, not `127.0.0.1:3432`

**Check firewall** (see above)

**Check network**:
```bash
# From another device, test connectivity
ping 192.168.1.27
telnet 192.168.1.27 3432
```

### "Connection Refused"

1. Verify server is running
2. Check correct IP address:
   ```bash
   python3 -c "from get_local_ip import get_local_ip_address; print(get_local_ip_address())"
   ```
3. Try `localhost` if accessing from same machine

---

## File System Issues

### Permission Denied

**Check directory permissions**:
```bash
ls -la
```

**Fix permissions**:
```bash
# For hls and tracks directories
chmod 755 hls tracks

# Or recursively
chmod -R 755 hls tracks
```

### Disk Full

**Check disk space**:
```bash
df -h
```

**Clean up HLS files**:
```bash
# Remove old HLS segments (use with caution!)
rm -rf hls/*

# Or specific video
rm -rf hls/video_name/
rm hls/video_name.m3u8
```

---

## Installation Issues

### "pip: command not found"

**Install pip**:
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# Fedora/RHEL
sudo dnf install python3-pip
```

### "Permission denied" when installing packages

**Use virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Or use --user flag**:
```bash
pip install --user -r requirements.txt
```

### Package installation fails

**Upgrade pip**:
```bash
pip install --upgrade pip
```

**Install dependencies separately**:
```bash
pip install Flask Werkzeug Flask-CORS SQLAlchemy Flask-SqlAlchemy
```

---

## Platform-Specific Issues

### Windows: "ffmpeg is not recognized"

**Add FFmpeg to PATH**:
1. Download FFmpeg from ffmpeg.org
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH
4. Restart terminal/IDE

### macOS: "Operation not permitted"

**Grant permissions**:
- System Preferences → Security & Privacy
- Grant permissions for Terminal/IDE

### Linux: "Cannot open display"

**For headless systems**:
Use web-only mode (no PyQt5):
```bash
python3 server_chromecast.py
```

---

## Getting More Help

### Run Platform Assessment

```bash
python3 check_platform.py
```

This will identify most common issues.

### Enable Debug Logging

Add to start of `server_chromecast.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Logs

Look for error messages in terminal output when running the server.

### Known Issues

See [ASSESSMENT_RESULTS.md](ASSESSMENT_RESULTS.md) for list of known bugs and limitations.

### Report Issues

When reporting issues, include:
1. Platform (OS, version)
2. Python version (`python3 --version`)
3. FFmpeg version (`ffmpeg -version`)
4. Full error message
5. Steps to reproduce
6. Output from `python3 check_platform.py`

---

## Quick Reference

### Start Server (Web-Only)
```bash
python3 server_chromecast.py
```

### Access Web Interface
```bash
http://localhost:3432
# Or from another device:
http://192.168.1.27:3432
```

### Kill All Related Processes
```bash
pkill -f video_streamer
pkill -f server_chromecast
pkill ffmpeg
```

### Reset Database
```bash
rm instance/movies.db
# Restart application to recreate
```

### Clean Up All Generated Files
```bash
rm -rf hls/* tracks/* instance/movies.db
```

---

**Last Updated**: 2025-10-28
**See Also**: [INSTALL.md](INSTALL.md), [ASSESSMENT_RESULTS.md](ASSESSMENT_RESULTS.md)

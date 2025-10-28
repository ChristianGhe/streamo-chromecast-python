#!/usr/bin/env python3
"""
Platform Assessment Tool for Streamo-Chromecast

This script checks if your system meets the requirements for running
Streamo-Chromecast and identifies any potential platform-specific issues.

Usage:
    python check_platform.py
"""

import sys
import platform
import shutil
import subprocess
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_check(name, status, details=""):
    """Print a check result"""
    symbol = "✓" if status else "✗"
    color_start = "\033[92m" if status else "\033[91m"
    color_end = "\033[0m"

    print(f"{color_start}{symbol}{color_end} {name}", end="")
    if details:
        print(f": {details}")
    else:
        print()


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    required = (3, 7)
    status = version >= required

    print_check(
        "Python Version",
        status,
        f"{version.major}.{version.minor}.{version.micro} "
        f"({'OK' if status else f'Need {required[0]}.{required[1]}+'})"
    )
    return status


def check_platform_info():
    """Display platform information"""
    system = platform.system()
    print_check("Operating System", True, f"{system} ({platform.platform()})")
    print_check("Architecture", True, platform.machine())
    return True


def check_ffmpeg():
    """Check FFmpeg installation"""
    ffmpeg_path = shutil.which('ffmpeg')
    ffprobe_path = shutil.which('ffprobe')

    if ffmpeg_path:
        try:
            result = subprocess.run(
                [ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_line = result.stdout.split('\n')[0]
            print_check("FFmpeg", True, f"Found at {ffmpeg_path}")
            print(f"  Version: {version_line.split('version')[1].split()[0]}")

            # Check for required codecs
            result = subprocess.run(
                [ffmpeg_path, '-codecs'],
                capture_output=True,
                text=True,
                timeout=5
            )
            codecs = result.stdout

            required_codecs = ['libx264', 'aac']
            missing = [c for c in required_codecs if c not in codecs]

            if missing:
                print_check("Required Codecs", False, f"Missing: {', '.join(missing)}")
                return False
            else:
                print_check("Required Codecs", True, "All available (libx264, aac)")

        except Exception as e:
            print_check("FFmpeg", False, f"Error checking version: {e}")
            return False
    else:
        # Check for bundled version
        base_dir = Path(__file__).parent
        bundled_paths = [
            base_dir / 'ffmpeg' / 'ffmpeg',
            base_dir / 'ffmpeg' / 'ffmpeg.exe',
        ]

        bundled = next((p for p in bundled_paths if p.exists()), None)

        if bundled:
            print_check("FFmpeg", True, f"Bundled version found at {bundled}")
        else:
            print_check("FFmpeg", False, "Not found in PATH or bundled directory")
            print("  Install FFmpeg: https://ffmpeg.org/download.html")
            return False

    if ffprobe_path:
        print_check("FFprobe", True, f"Found at {ffprobe_path}")
    else:
        bundled_probe = next(
            (p for p in [base_dir / 'ffmpeg' / 'ffprobe', base_dir / 'ffmpeg' / 'ffprobe.exe']
             if p.exists()),
            None
        )
        if bundled_probe:
            print_check("FFprobe", True, f"Bundled at {bundled_probe}")
        else:
            print_check("FFprobe", False, "Not found")
            return False

    return True


def check_dependencies():
    """Check Python dependencies"""
    all_ok = True

    # Required dependencies
    required = {
        'flask': 'Flask',
        'sqlalchemy': 'SQLAlchemy',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
    }

    for module_name, display_name in required.items():
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print_check(display_name, True, f"v{version}")
        except ImportError:
            print_check(display_name, False, "Not installed")
            all_ok = False

    # Optional dependencies
    try:
        from PyQt5 import QtCore
        print_check("PyQt5 (Desktop GUI)", True, f"Qt {QtCore.QT_VERSION_STR}")
    except ImportError:
        print_check("PyQt5 (Desktop GUI)", False, "Not installed (optional for web-only usage)")

    try:
        import flask_cors
        print_check("Flask-CORS", True, getattr(flask_cors, '__version__', 'installed'))
    except ImportError:
        print_check("Flask-CORS", False, "Not installed (recommended)")

    return all_ok


def check_network():
    """Check network capabilities"""
    import socket

    try:
        # Get hostname
        hostname = socket.gethostname()
        print_check("Hostname", True, hostname)

        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        print_check("Local IP", True, ip_address)

        # Check if port 3432 is available
        port = 3432
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(('127.0.0.1', port))
            s.close()
            print_check(f"Port {port} Available", True, "Ready for Flask server")
        except OSError:
            print_check(f"Port {port} Available", False, "Port in use (server may be running)")

        return True

    except Exception as e:
        print_check("Network", False, f"Error: {e}")
        return False


def check_file_system():
    """Check file system capabilities"""
    import tempfile

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test directory creation (simulating hls output)
            test_dir = tmpdir / 'hls' / 'test_video'
            test_dir.mkdir(parents=True, exist_ok=True)

            # Test file writing
            test_file = test_dir / 'test.m3u8'
            test_file.write_text('#EXTM3U\n')

            if test_file.exists():
                print_check("File System Operations", True, "Can create directories and files")
                return True

    except Exception as e:
        print_check("File System Operations", False, f"Error: {e}")
        return False


def check_database():
    """Check SQLite database capabilities"""
    import sqlite3
    import tempfile

    try:
        version = sqlite3.sqlite_version
        print_check("SQLite", True, f"v{version}")

        # Test database creation
        with tempfile.NamedTemporaryFile(suffix='.db', delete=True) as tmpfile:
            conn = sqlite3.connect(tmpfile.name)
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY)')
            conn.commit()
            conn.close()

        print_check("Database Operations", True, "Can create and write to database")
        return True

    except Exception as e:
        print_check("Database", False, f"Error: {e}")
        return False


def main():
    """Run all platform checks"""
    print_header("STREAMO-CHROMECAST PLATFORM ASSESSMENT")

    print("\n📋 System Information")
    platform_ok = check_platform_info()
    python_ok = check_python_version()

    print("\n🎬 FFmpeg")
    ffmpeg_ok = check_ffmpeg()

    print("\n📦 Python Dependencies")
    deps_ok = check_dependencies()

    print("\n🌐 Network")
    network_ok = check_network()

    print("\n💾 File System & Database")
    fs_ok = check_file_system()
    db_ok = check_database()

    # Summary
    print_header("ASSESSMENT SUMMARY")

    all_critical_ok = python_ok and ffmpeg_ok and deps_ok and fs_ok and db_ok

    if all_critical_ok:
        print("\n✅ Your system meets all requirements for Streamo-Chromecast!")
        print("\nNext steps:")
        print("  1. Run the server: python server_chromecast.py")
        print("  2. Or run with GUI: python video_streamer_chromecast.py")
        print("  3. Access web interface at: http://<your-ip>:3432/")
    else:
        print("\n⚠️  Some requirements are not met. Please address the issues above.")
        print("\nCommon fixes:")
        print("  • Install dependencies: pip install -r requirements.txt")
        print("  • Install FFmpeg: https://ffmpeg.org/download.html")
        if not deps_ok:
            print("  • For desktop GUI: pip install PyQt5")

    print("\n" + "=" * 70)

    # Return exit code
    return 0 if all_critical_ok else 1


if __name__ == '__main__':
    sys.exit(main())

"""
Platform Assessment Test Suite

This test suite assesses cross-platform compatibility and identifies
platform-specific issues before beginning the refactoring process.

Run with: pytest tests/test_platform_assessment.py -v
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path
import tempfile
import pytest


class TestPlatformDetection:
    """Test platform detection and environment information"""

    def test_platform_identification(self):
        """Verify platform can be identified"""
        system = platform.system()
        assert system in ['Windows', 'Linux', 'Darwin'], f"Unknown platform: {system}"
        print(f"\n✓ Platform: {system} ({platform.platform()})")

    def test_python_version(self):
        """Verify Python version is 3.7+"""
        version = sys.version_info
        assert version >= (3, 7), f"Python 3.7+ required, found {version.major}.{version.minor}"
        print(f"\n✓ Python version: {version.major}.{version.minor}.{version.micro}")

    def test_architecture(self):
        """Check system architecture"""
        arch = platform.machine()
        print(f"\n✓ Architecture: {arch}")
        assert arch in ['x86_64', 'AMD64', 'arm64', 'aarch64', 'i386', 'i686']


class TestFFmpegDetection:
    """Test FFmpeg installation and path resolution"""

    def test_ffmpeg_in_path(self):
        """Check if FFmpeg is in system PATH"""
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            print(f"\n✓ FFmpeg found in PATH: {ffmpeg_path}")
        else:
            pytest.skip("FFmpeg not in system PATH (may use bundled version)")

    def test_ffprobe_in_path(self):
        """Check if FFprobe is in system PATH"""
        ffprobe_path = shutil.which('ffprobe')
        if ffprobe_path:
            print(f"\n✓ FFprobe found in PATH: {ffprobe_path}")
        else:
            pytest.skip("FFprobe not in system PATH (may use bundled version)")

    def test_bundled_ffmpeg(self):
        """Check for bundled FFmpeg in project directory"""
        base_dir = Path(__file__).parent.parent

        # Check common locations
        possible_paths = [
            base_dir / 'ffmpeg' / 'ffmpeg',
            base_dir / 'ffmpeg' / 'ffmpeg.exe',
            base_dir / 'bin' / 'ffmpeg',
            base_dir / 'bin' / 'ffmpeg.exe',
        ]

        found = [p for p in possible_paths if p.exists()]

        if found:
            print(f"\n✓ Bundled FFmpeg found: {found[0]}")
        else:
            print(f"\n⚠ No bundled FFmpeg found in: {[str(p) for p in possible_paths]}")

    def test_ffmpeg_version(self):
        """Test FFmpeg version and capabilities"""
        ffmpeg_path = shutil.which('ffmpeg')
        if not ffmpeg_path:
            # Try bundled version
            base_dir = Path(__file__).parent.parent
            bundled = base_dir / 'ffmpeg' / ('ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg')
            if bundled.exists():
                ffmpeg_path = str(bundled)
            else:
                pytest.skip("FFmpeg not available")

        try:
            result = subprocess.run(
                [ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_line = result.stdout.split('\n')[0]
            print(f"\n✓ {version_line}")

            # Check for required codecs
            result = subprocess.run(
                [ffmpeg_path, '-codecs'],
                capture_output=True,
                text=True,
                timeout=5
            )
            codecs = result.stdout

            required_codecs = ['libx264', 'aac', 'h264']
            missing = []
            for codec in required_codecs:
                if codec not in codecs:
                    missing.append(codec)

            if missing:
                print(f"\n⚠ Missing codecs: {missing}")
            else:
                print(f"\n✓ All required codecs available")

        except subprocess.TimeoutExpired:
            pytest.fail("FFmpeg version check timed out")
        except Exception as e:
            pytest.fail(f"FFmpeg version check failed: {e}")


class TestFileSystemOperations:
    """Test file system operations for cross-platform compatibility"""

    def test_pathlib_compatibility(self):
        """Test pathlib operations work correctly"""
        test_path = Path('/tmp') / 'test' / 'subdir'

        # Test path construction
        assert isinstance(test_path, Path)

        # Test string conversion
        path_str = str(test_path)
        assert path_str

        # Test path separators are handled correctly
        if platform.system() == 'Windows':
            assert '\\' in path_str or '/' in path_str
        else:
            assert '/' in path_str

        print(f"\n✓ Path construction: {test_path}")

    def test_temp_directory_creation(self):
        """Test creating directories in temp location"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / 'hls' / 'video_test'
            test_dir.mkdir(parents=True, exist_ok=True)

            assert test_dir.exists()
            assert test_dir.is_dir()

            print(f"\n✓ Temp directory creation: {test_dir}")

    def test_file_write_operations(self):
        """Test writing files with various extensions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Test .m3u8 file (HLS playlist)
            m3u8_file = tmpdir / 'test.m3u8'
            m3u8_file.write_text('#EXTM3U\n#EXT-X-VERSION:3\n')
            assert m3u8_file.exists()

            # Test .ts file (HLS segment)
            ts_file = tmpdir / 'segment001.ts'
            ts_file.write_bytes(b'\x00' * 1024)
            assert ts_file.exists()

            # Test .vtt file (subtitle)
            vtt_file = tmpdir / 'subtitle.vtt'
            vtt_file.write_text('WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nTest subtitle\n')
            assert vtt_file.exists()

            print(f"\n✓ File write operations successful")

    def test_filename_sanitization(self):
        """Test filename sanitization works on current platform"""
        # Import the sanitization logic
        test_filenames = [
            "video.with.dots.mkv",
            "video-with-dashes.mp4",
            "video+with+plus.avi",
            "video[with]brackets.mkv",
        ]

        trans = str.maketrans(".+-[]", "_____")

        for filename in test_filenames:
            base = os.path.splitext(filename)[0]
            sanitized = base.translate(trans)

            # Test that sanitized name can be used in path
            with tempfile.TemporaryDirectory() as tmpdir:
                test_path = Path(tmpdir) / sanitized
                test_path.mkdir()
                assert test_path.exists()

        print(f"\n✓ Filename sanitization compatible")


class TestDatabaseOperations:
    """Test database operations for cross-platform compatibility"""

    def test_sqlite_availability(self):
        """Check SQLite is available"""
        import sqlite3
        version = sqlite3.sqlite_version
        print(f"\n✓ SQLite version: {version}")
        assert version >= '3.0.0'

    def test_database_creation(self):
        """Test database can be created in temp location"""
        import sqlite3

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'test.db'

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()

            assert db_path.exists()
            print(f"\n✓ Database creation successful: {db_path}")


class TestNetworking:
    """Test networking capabilities"""

    def test_socket_availability(self):
        """Test socket module availability"""
        import socket

        # Test getting hostname
        hostname = socket.gethostname()
        print(f"\n✓ Hostname: {hostname}")

        # Test getting local IP (same method used in get_local_ip.py)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            print(f"\n✓ Local IP: {ip_address}")

            # Verify it's a valid IP
            parts = ip_address.split('.')
            assert len(parts) == 4
            for part in parts:
                assert 0 <= int(part) <= 255

        except Exception as e:
            pytest.skip(f"Network not available: {e}")

    def test_port_availability(self):
        """Test if port 3432 is available for Flask server"""
        import socket

        port = 3432
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind(('127.0.0.1', port))
            s.close()
            print(f"\n✓ Port {port} is available")
        except OSError as e:
            print(f"\n⚠ Port {port} is in use or unavailable: {e}")


class TestDependencies:
    """Test Python dependencies are available"""

    def test_flask_import(self):
        """Test Flask can be imported"""
        try:
            import flask
            print(f"\n✓ Flask version: {flask.__version__}")
        except ImportError:
            pytest.fail("Flask not installed (pip install -r requirements.txt)")

    def test_sqlalchemy_import(self):
        """Test SQLAlchemy can be imported"""
        try:
            import sqlalchemy
            print(f"\n✓ SQLAlchemy version: {sqlalchemy.__version__}")
        except ImportError:
            pytest.fail("SQLAlchemy not installed")

    def test_pyqt5_import(self):
        """Test PyQt5 can be imported (may fail on headless systems)"""
        try:
            from PyQt5 import QtCore
            print(f"\n✓ PyQt5 Qt version: {QtCore.QT_VERSION_STR}")
        except ImportError:
            pytest.skip("PyQt5 not installed or not available")
        except Exception as e:
            pytest.skip(f"PyQt5 not available: {e}")

    def test_flask_sqlalchemy_import(self):
        """Test Flask-SQLAlchemy can be imported"""
        try:
            import flask_sqlalchemy
            print(f"\n✓ Flask-SQLAlchemy available")
        except ImportError:
            pytest.fail("Flask-SQLAlchemy not installed")


class TestProcessManagement:
    """Test subprocess and process management"""

    def test_subprocess_basic(self):
        """Test basic subprocess execution"""
        # Use platform-appropriate command
        if platform.system() == 'Windows':
            cmd = ['cmd', '/c', 'echo', 'test']
        else:
            cmd = ['echo', 'test']

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        assert result.returncode == 0
        print(f"\n✓ Subprocess execution successful")

    def test_subprocess_timeout(self):
        """Test subprocess timeout works"""
        # Use platform-appropriate sleep command
        if platform.system() == 'Windows':
            cmd = ['timeout', '/t', '10']
        else:
            cmd = ['sleep', '10']

        with pytest.raises(subprocess.TimeoutExpired):
            subprocess.run(cmd, timeout=1)

        print(f"\n✓ Subprocess timeout works correctly")


class TestThreading:
    """Test threading capabilities"""

    def test_threading_import(self):
        """Test threading module availability"""
        import threading
        import queue

        print(f"\n✓ Threading module available")
        print(f"✓ Queue module available")

    def test_thread_creation(self):
        """Test basic thread creation and joining"""
        import threading
        import time

        result = []

        def worker():
            time.sleep(0.1)
            result.append('done')

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join(timeout=1.0)

        assert not thread.is_alive()
        assert result == ['done']
        print(f"\n✓ Thread creation and joining works")


# Platform-specific summary
def test_platform_summary(capsys):
    """Generate platform assessment summary"""
    print("\n" + "="*70)
    print("PLATFORM ASSESSMENT SUMMARY")
    print("="*70)

    system = platform.system()
    print(f"Operating System: {system}")
    print(f"Platform: {platform.platform()}")
    print(f"Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"Architecture: {platform.machine()}")

    # FFmpeg check
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg:
        print(f"FFmpeg: Available at {ffmpeg}")
    else:
        print(f"FFmpeg: Not in PATH (check for bundled version)")

    # Dependencies
    try:
        import flask
        print(f"Flask: {flask.__version__}")
    except:
        print(f"Flask: NOT INSTALLED")

    try:
        import sqlalchemy
        print(f"SQLAlchemy: {sqlalchemy.__version__}")
    except:
        print(f"SQLAlchemy: NOT INSTALLED")

    try:
        from PyQt5 import QtCore
        print(f"PyQt5: {QtCore.QT_VERSION_STR}")
    except:
        print(f"PyQt5: Not available (may be normal on headless systems)")

    print("="*70)
    print("\nRun full test suite with: pytest tests/test_platform_assessment.py -v")
    print("="*70 + "\n")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

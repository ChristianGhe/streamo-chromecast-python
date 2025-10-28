# Streamo-Chromecast Test Suite

This directory contains tests for the Streamo-Chromecast application.

## Platform Assessment Tests

Before beginning the refactoring process, run the platform assessment tests to identify any cross-platform compatibility issues.

### Quick Start

**Option 1: Standalone Platform Check** (No pytest required)
```bash
python check_platform.py
```

This will check:
- Python version compatibility
- FFmpeg installation and codecs
- Required Python dependencies
- Network capabilities
- File system operations
- Database functionality

**Option 2: Full Test Suite** (Requires pytest)
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run platform assessment tests
pytest tests/test_platform_assessment.py -v

# Run with detailed output
pytest tests/test_platform_assessment.py -v -s
```

### Test Categories

#### System Tests
- Platform detection (Windows/Linux/macOS)
- Python version verification (3.7+)
- Architecture detection

#### FFmpeg Tests
- FFmpeg/FFprobe detection in PATH
- Bundled FFmpeg location check
- Version verification
- Required codec availability (libx264, aac, h264)

#### File System Tests
- Pathlib compatibility
- Directory creation (hls/, tracks/)
- File write operations (.m3u8, .ts, .vtt)
- Filename sanitization

#### Database Tests
- SQLite availability
- Database creation and operations
- Session management

#### Network Tests
- Socket operations
- Local IP detection
- Port availability (3432)

#### Dependency Tests
- Flask import and version
- SQLAlchemy import and version
- PyQt5 availability (optional)
- Flask-SQLAlchemy import

#### Process Management Tests
- Subprocess execution
- Timeout handling
- Thread creation and joining

## Expected Results

### Linux (Current Platform)
All tests should pass on Linux with:
- Python 3.7+
- FFmpeg installed (system or bundled)
- All dependencies from requirements.txt

### Windows
Tests should identify:
- Path separator differences
- .exe extension requirements
- PyQt5 availability

### macOS
Tests should identify:
- FFmpeg installation via Homebrew
- Application bundle requirements
- System permissions

## Interpreting Results

**All Green (✓)**: Platform is fully compatible
**Some Yellow/Skip**: Optional features not available (e.g., PyQt5 on headless server)
**Red (✗)**: Critical issue that must be fixed

## Adding Tests

When adding new functionality, include platform-specific tests:

1. Create test file: `tests/test_<feature>.py`
2. Use pytest fixtures for common setup
3. Test on multiple platforms if possible
4. Mark platform-specific tests with `@pytest.mark.skipif`

Example:
```python
import pytest
import platform

@pytest.mark.skipif(
    platform.system() != 'Windows',
    reason="Windows-specific test"
)
def test_windows_feature():
    # Test Windows-specific code
    pass
```

## CI/CD Integration

These tests will be integrated into GitHub Actions to run on:
- Ubuntu (latest)
- Windows (latest)
- macOS (latest)

## Troubleshooting

**FFmpeg not found**:
- Install system FFmpeg: `sudo apt install ffmpeg` (Linux) or download from ffmpeg.org
- Or place FFmpeg binaries in `ffmpeg/` directory

**Import errors**:
- Install dependencies: `pip install -r requirements.txt`
- For dev dependencies: `pip install -r requirements-dev.txt`

**PyQt5 errors on headless systems**:
- These are expected and tests will skip
- PyQt5 is only needed for desktop GUI mode

**Port 3432 in use**:
- Stop existing Streamo-Chromecast instance
- Or change port in configuration

## Next Steps

After running platform assessment:
1. Review ROADMAP.md for improvement plan
2. Address any critical failures
3. Begin Phase 1: Stabilization (threading fixes)

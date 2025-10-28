# Streamo-Chromecast Improvement Roadmap

**Document Version**: 1.0
**Date**: 2025-10-28
**Status**: Planning Phase

---

## 🎯 Project Goals

### Primary Objectives
1. **Stabilization**: Fix critical bugs, especially threading issues
2. **Cross-Platform Support**: Windows, Linux, macOS compatibility
3. **Code Quality**: Improve architecture, maintainability, and testability
4. **UI/UX Enhancement**: Modern, responsive web interface
5. **Deployment**: Easy installation and distribution

### Target Users
- **Phase 1**: Personal use
- **Phase 2**: General public release

---

## 🐛 Critical Issues Identified

### Threading & Concurrency Issues

#### CRITICAL - PyQt5 Thread Safety Violation
**Location**: `video_streamer_chromecast.py:127`
**Issue**: GUI widgets manipulated from worker thread
**Impact**: Segmentation faults, crashes, undefined behavior
**Fix**: Use Qt signals/slots for cross-thread communication

#### HIGH - Unjoined Threads
**Locations**: `video_streamer_chromecast.py:146, 171-192`
**Issue**: Fire-and-forget threads without lifecycle management
**Impact**: Resource leaks, orphaned FFmpeg processes, incomplete database transactions
**Fix**: Store thread references, implement proper cleanup

#### HIGH - Shared State Race Conditions
**Locations**: `video_streamer_chromecast.py:58-63, 124-127, 140-142`
**Issue**: Multiple threads access instance variables without synchronization
**Impact**: Wrong video processed, data corruption
**Fix**: Add threading.Lock for shared state

#### HIGH - Orphaned FFmpeg Processes
**Location**: `video_streaming_commands.py:75, 94, 114`
**Issue**: Long-running FFmpeg processes without process handle retention
**Impact**: CPU/disk resource exhaustion, zombie processes
**Fix**: Store process handles, implement cancellation mechanism

#### MEDIUM - Database Race Conditions
**Location**: `video_list_handler.py:35`
**Issue**: Duplicate video checks without proper locking
**Impact**: Unique constraint violations, inconsistent state
**Fix**: Use database-level locking or retry logic

#### MEDIUM - Subprocess Hangs
**Location**: `video_streaming_commands.py:25-32`
**Issue**: No timeout on ffprobe subprocess calls
**Impact**: Application hangs indefinitely
**Fix**: Add timeout parameter to subprocess calls

### Cross-Platform Issues

1. **FFmpeg Path Hardcoding**: `ffmpeg/ffmpeg` assumes relative path and no .exe extension
2. **Path Separators**: Mixed usage of `/` instead of `pathlib.Path`
3. **Windows-Only Testing**: No validation on Linux/macOS platforms

### Architecture Issues

1. **Tight Coupling**: Business logic mixed with UI code
2. **No Separation of Concerns**: API routes contain business logic
3. **Missing Error Handling**: Many operations lack try-except blocks
4. **No Logging Strategy**: Inconsistent print statements
5. **No Configuration Management**: Hardcoded values throughout

---

## 📋 Implementation Phases

### PHASE 1: Stabilization & Bug Fixes (Priority: CRITICAL)
**Duration**: 1-2 weeks
**Goal**: Achieve stable, crash-free application

#### Tasks

**1.1 Fix Critical Threading Bugs**
- [ ] Implement Qt signals for thread-safe GUI updates
- [ ] Add thread pool manager class for lifecycle management
- [ ] Implement thread synchronization with locks for shared state
- [ ] Add FFmpeg process manager for tracking and cleanup
- [ ] Add timeouts to all subprocess calls (5-10 minute default)
- [ ] Add graceful shutdown mechanism

**1.2 Error Handling & Logging**
- [ ] Set up Python logging module (replace print statements)
- [ ] Add try-except blocks for all I/O operations
- [ ] Add exception handlers for all thread targets
- [ ] Create error reporting mechanism for users
- [ ] Add logging levels (DEBUG, INFO, WARNING, ERROR)

**1.3 Database Improvements**
- [ ] Implement proper SQLAlchemy session scoping
- [ ] Add retry logic for database operations
- [ ] Add database schema versioning (Alembic)
- [ ] Add unique constraint error handling
- [ ] Add database backup/restore functionality

**1.4 Testing Infrastructure**
- [ ] Set up pytest framework
- [ ] Write unit tests for core utilities
- [ ] Add mock FFmpeg for testing
- [ ] Create integration tests for API endpoints
- [ ] Add CI pipeline (GitHub Actions)

**Success Criteria**:
- No segmentation faults or crashes during normal operation
- All threads properly cleaned up on application exit
- No orphaned FFmpeg processes
- 80%+ code coverage for critical paths

---

### PHASE 2: Cross-Platform Support
**Duration**: 1 week
**Goal**: Run seamlessly on Windows, Linux, and macOS

#### Tasks

**2.1 FFmpeg Path Resolution**
- [ ] Implement FFmpeg auto-detection using `shutil.which()`
- [ ] Add platform-specific binary path resolution
- [ ] Create FFmpeg download/setup wizard for first run
- [ ] Add configuration option for custom FFmpeg path
- [ ] Test with system-installed and bundled FFmpeg

**2.2 File Path Abstraction**
- [ ] Replace all string path operations with `pathlib.Path`
- [ ] Remove hardcoded path separators
- [ ] Add platform-specific directory creation logic
- [ ] Test file operations on all platforms

**2.3 Platform-Specific Testing**
- [ ] Set up Linux test environment (Ubuntu, Fedora)
- [ ] Set up macOS test environment
- [ ] Document platform-specific dependencies
- [ ] Create platform-specific installation guides

**2.4 Configuration Management**
- [ ] Implement .env file support (python-dotenv)
- [ ] Add config.py for centralized configuration
- [ ] Support environment variable overrides
- [ ] Add settings validation

**Success Criteria**:
- Application runs on Windows, Linux, and macOS without code changes
- FFmpeg automatically detected or easy to configure
- All file operations work correctly on all platforms

---

### PHASE 3: Architecture Refactoring
**Duration**: 1-2 weeks
**Goal**: Clean, maintainable, testable codebase

#### Tasks

**3.1 Project Restructuring**
```
streamo-chromecast/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # Flask routes
│   │   └── schemas.py         # Request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── transcoding.py     # FFmpeg operations
│   │   ├── video_info.py      # Video metadata extraction
│   │   └── job_queue.py       # Background task management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── movie.py
│   │   └── subtitle.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── paths.py           # Path utilities
│   │   └── process.py         # Subprocess management
│   ├── config.py
│   └── app.py                 # Application factory
├── frontend/                   # Modern web UI
├── desktop/                    # Optional desktop wrapper
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/
│   ├── setup_ffmpeg.py
│   └── migrate_db.py
├── docs/
│   ├── installation.md
│   ├── user_guide.md
│   └── api_docs.md
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── docker-compose.yml
```

**3.2 Separate Concerns**
- [ ] Extract business logic from UI code
- [ ] Create service layer for transcoding operations
- [ ] Implement repository pattern for database access
- [ ] Create dedicated API layer (Flask blueprints)
- [ ] Add dependency injection where appropriate

**3.3 Code Quality Improvements**
- [ ] Add type hints to all functions
- [ ] Set up black for code formatting
- [ ] Add flake8/ruff for linting
- [ ] Add mypy for static type checking
- [ ] Add pre-commit hooks
- [ ] Document all public APIs with docstrings

**3.4 Background Job System**
- [ ] Evaluate task queue options (Celery, RQ, or custom)
- [ ] Implement job queue for transcoding tasks
- [ ] Add job status tracking (queued, processing, completed, failed)
- [ ] Add job cancellation mechanism
- [ ] Add progress reporting via WebSockets

**Success Criteria**:
- Clear separation between UI, API, business logic, and data layers
- All code passes linting and type checking
- Easy to add new features without touching multiple layers
- 90%+ code coverage

---

### PHASE 4: UI/UX Improvements
**Duration**: 1-2 weeks
**Goal**: Modern, intuitive user interface

#### Tasks

**4.1 Technology Selection**
- [ ] Choose frontend framework (React/Vue/Svelte)
- [ ] Select UI component library (Tailwind + shadcn, MUI, etc.)
- [ ] Choose video player (Video.js, Plyr)
- [ ] Set up build system (Vite, webpack)

**4.2 Web Interface Features**
- [ ] Video library grid view with thumbnails
- [ ] Drag-and-drop file upload
- [ ] Real-time transcoding progress with WebSockets
- [ ] Video player with subtitle selection
- [ ] Settings page (server config, FFmpeg path, etc.)
- [ ] Dark/light theme toggle
- [ ] Responsive mobile design
- [ ] Search and filter functionality
- [ ] Batch operations (delete, re-transcode)

**4.3 Desktop Application Decision**
**Options**:
1. Keep PyQt5 (fix existing issues)
2. Migrate to Tauri (Rust-based, lightweight)
3. Use Electron (JavaScript-based)
4. Web-only with system tray icon

**Recommendation**: Tauri or web-only approach

**4.4 User Experience**
- [ ] First-run setup wizard
- [ ] Progress notifications
- [ ] Error message improvements
- [ ] Keyboard shortcuts
- [ ] Accessibility improvements (ARIA labels, etc.)

**Success Criteria**:
- Modern, visually appealing interface
- Intuitive user workflows
- Mobile-friendly
- Accessible
- Fast and responsive

---

### PHASE 5: Deployment & Distribution
**Duration**: 1 week
**Goal**: Easy installation for end users

#### Tasks

**5.1 Docker Deployment**
- [ ] Create Dockerfile for backend
- [ ] Create docker-compose.yml with volumes
- [ ] Include FFmpeg in Docker image
- [ ] Add health checks
- [ ] Document Docker deployment
- [ ] Publish to Docker Hub

**5.2 Platform-Specific Packaging**

**Windows**:
- [ ] PyInstaller/cx_Freeze executable
- [ ] NSIS installer with FFmpeg bundled
- [ ] Add to Windows startup (optional)
- [ ] Code signing certificate (for public release)

**macOS**:
- [ ] .app bundle creation
- [ ] DMG installer
- [ ] Code signing and notarization
- [ ] Homebrew formula (optional)

**Linux**:
- [ ] AppImage (universal)
- [ ] .deb package (Debian/Ubuntu)
- [ ] .rpm package (Fedora/RHEL)
- [ ] Snap/Flatpak (optional)
- [ ] AUR package (Arch Linux, optional)

**5.3 Distribution Channels**
- [ ] GitHub Releases with auto-built binaries
- [ ] Docker Hub automated builds
- [ ] Website with download links
- [ ] Package manager submissions (Homebrew, Chocolatey, etc.)

**5.4 Documentation**
- [ ] Installation guide per platform
- [ ] User manual with screenshots
- [ ] Troubleshooting guide
- [ ] FAQ
- [ ] Developer setup guide
- [ ] API documentation (if exposing API)
- [ ] Video tutorials (optional)

**5.5 Monitoring & Telemetry (for public release)**
- [ ] Error reporting (Sentry or similar)
- [ ] Anonymous usage analytics (optional, opt-in)
- [ ] Update checking mechanism
- [ ] Changelog and release notes

**Success Criteria**:
- One-command installation on each platform
- Clear, comprehensive documentation
- Automated release process via CI/CD

---

## 🛠️ Technology Stack

### Current Stack
- **Backend**: Python 3.x, Flask, SQLAlchemy
- **Frontend**: HTML, vanilla JavaScript, HLS.js
- **Desktop**: PyQt5
- **Database**: SQLite
- **Media Processing**: FFmpeg

### Proposed Stack

#### Backend
- **Framework**: Flask (keep) or FastAPI (async support)
- **Database**: SQLAlchemy + SQLite (add PostgreSQL support optional)
- **Task Queue**: Celery with Redis, or RQ (simpler)
- **CORS**: Flask-CORS
- **Config**: python-dotenv
- **Validation**: Pydantic
- **WebSockets**: Flask-SocketIO or FastAPI WebSockets

#### Frontend
- **Framework**: React (popular) or Svelte (lightweight)
- **Build Tool**: Vite
- **UI Library**: Tailwind CSS + shadcn/ui
- **Video Player**: Video.js or Plyr
- **State Management**: Zustand or React Context
- **HTTP Client**: Axios or Fetch API
- **WebSockets**: Socket.IO client

#### Desktop Wrapper (Optional)
- **Tauri** (recommended) - Rust-based, small bundle size, secure
- Electron (alternative) - Larger but more mature

#### DevOps
- **Containerization**: Docker + docker-compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest, pytest-cov, pytest-mock
- **Code Quality**: black, ruff/flake8, mypy
- **Pre-commit**: pre-commit hooks
- **Documentation**: MkDocs or Sphinx

---

## 📊 Success Metrics

### Stability
- [ ] Zero crashes during 24-hour stress test
- [ ] All threads cleaned up properly on shutdown
- [ ] No orphaned processes after operation
- [ ] Database integrity maintained under concurrent access

### Performance
- [ ] Transcoding starts within 5 seconds of user request
- [ ] Web UI loads in under 2 seconds
- [ ] API response time < 100ms for metadata
- [ ] Support for concurrent transcode jobs (at least 2)

### Code Quality
- [ ] 80%+ test coverage for critical paths
- [ ] 90%+ test coverage for Phase 3+ code
- [ ] Zero critical linting errors
- [ ] All functions have type hints
- [ ] All public APIs documented

### User Experience
- [ ] Installation completes in under 5 minutes
- [ ] First video streaming in under 10 minutes from install
- [ ] Intuitive UI (user testing feedback)
- [ ] Mobile-responsive web interface

---

## 🚀 Quick Wins (Immediate Actions)

These can be implemented immediately to show progress:

1. **Add Logging Framework** (4 hours)
   - Replace print() with logging module
   - Set up file and console handlers
   - Add log rotation

2. **Fix FFmpeg Path Handling** (2 hours)
   - Use shutil.which() for FFmpeg detection
   - Add platform-specific path resolution

3. **Add .env Support** (2 hours)
   - Install python-dotenv
   - Create config.py
   - Add .env.example

4. **Fix Critical Thread Safety Bug** (4-6 hours)
   - Implement Qt signals in VideoStreamer
   - Test on current platform

5. **Add requirements-dev.txt** (1 hour)
   - Separate dev dependencies (pytest, black, etc.)

6. **Set up .editorconfig** (1 hour)
   - Consistent code formatting across editors

**Total Effort**: ~2 days for all quick wins

---

## 📅 Suggested Timeline

### Sprint 1 (Week 1-2): Stabilization
- Fix critical threading bugs
- Add error handling and logging
- Set up testing infrastructure
- Database improvements

### Sprint 2 (Week 3): Cross-Platform
- FFmpeg path abstraction
- File path handling
- Platform testing
- Configuration management

### Sprint 3 (Week 4-5): Architecture
- Project restructuring
- Separate concerns
- Code quality improvements
- Background job system

### Sprint 4 (Week 6-7): UI/UX
- Build modern web interface
- Improve video library management
- Add real-time progress
- Mobile responsiveness

### Sprint 5 (Week 8): Deployment
- Docker setup
- Platform-specific packaging
- Documentation
- CI/CD pipeline

### Sprint 6 (Week 9): Polish & Release
- Bug fixes from testing
- Performance optimization
- Final documentation
- First stable release (v1.0.0)

---

## 🔄 Migration Strategy

### Saving Current Version
```bash
# Tag current version as baseline
git tag -a v0.9.0-baseline -m "Pre-refactor baseline version"
git push origin v0.9.0-baseline

# Create development branch
git checkout -b refactor/phase1-stabilization
```

### Incremental Approach
1. **Branch per phase**: Create separate branch for each major phase
2. **Feature flags**: Keep old code paths during migration
3. **Backward compatibility**: Maintain database compatibility
4. **Gradual rollout**: Test each phase thoroughly before moving forward

### Data Migration
- Keep database schema compatible during refactoring
- Add Alembic migrations for schema changes
- Provide migration scripts for users upgrading

---

## 📝 Open Questions & Decisions Needed

1. **Backend Framework**: Stick with Flask or migrate to FastAPI?
2. **Frontend Framework**: React, Vue, or Svelte?
3. **Desktop App**: Keep PyQt5, migrate to Tauri/Electron, or web-only?
4. **Task Queue**: Celery (powerful) vs RQ (simpler) vs custom?
5. **Deployment Priority**: Docker first or platform installers?
6. **Android Integration**: Merge Android Chromecast code or keep separate?
7. **Authentication**: Add user authentication for public release?
8. **Multi-tenancy**: Support multiple users on same server?

---

## 📚 References & Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

### Threading Resources
- [Python Threading Best Practices](https://docs.python.org/3/library/threading.html)
- [PyQt5 Threading Guidelines](https://doc.qt.io/qt-5/threads-qobject.html)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [Testing Flask Applications](https://flask.palletsprojects.com/en/2.3.x/testing/)

---

## 📞 Support & Communication

### Development Workflow
- Use GitHub Issues for bug tracking
- Use GitHub Projects for task management
- Use Pull Requests for code review
- Tag releases with semantic versioning

### Version Numbering
- **v0.9.x**: Current baseline version
- **v1.0.0**: First stable release after refactoring
- **v1.x.x**: Incremental improvements
- **v2.0.0**: Major architectural changes (if needed)

---

**Last Updated**: 2025-10-28
**Next Review**: After Phase 1 completion

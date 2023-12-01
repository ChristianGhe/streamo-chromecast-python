import os
import sys
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtBoundSignal, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

from server_chromecast import Server


class Worker(QThread):
    progress: pyqtBoundSignal = pyqtSignal(int)

    def run(self):
        for i in range(100):
            time.sleep(0.1)
            self.progress.emit(i + 1)


def parse_filename(path):
    # Extract the base filename from the path
    base_filename = os.path.basename(path)

    # Remove the file extension
    filename_without_extension = os.path.splitext(base_filename)[0]

    # Replace '.' with '_' in the filename
    filename_with_underscores = filename_without_extension.replace('.', '_')

    return filename_with_underscores


class VideoStreamerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = VideoStreamer()
        self.window.setWindowTitle("Streamo Chromecast")
        self.window.thread.progress.connect(lambda i: {
            print("Progress: ", i),
        })
        self.window.show()

    def run(self, on_exit_callback=None):
        def on_exit():
            print("Application is about to exit.")
            if on_exit_callback is not None:
                on_exit_callback()

        QCoreApplication.instance().aboutToQuit.connect(on_exit)
        sys.exit(self.app.exec_())


class VideoStreamer(QWidget):
    def __init__(self):
        super().__init__()

        self.video = None
        self.filename = None
        self.thread = Worker()
        self.btn_start_subtitle_stream = None
        self.btn_start_video_stream = None
        self.btn_browse = None
        self.label = None
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()

        self.label = QLabel("No video selected")
        vbox.addWidget(self.label)

        self.btn_browse = QPushButton("Browse", self)
        self.btn_browse.clicked.connect(self.select_file)
        vbox.addWidget(self.btn_browse)

        self.btn_start_video_stream = QPushButton("Start Video Stream", self)
        self.btn_start_video_stream.clicked.connect(self.start_video_stream)
        vbox.addWidget(self.btn_start_video_stream)

        self.btn_start_subtitle_stream = QPushButton("Start Subtitles Stream", self)
        self.btn_start_subtitle_stream.clicked.connect(self.start_subtitles_stream)
        vbox.addWidget(self.btn_start_subtitle_stream)

        self.setLayout(vbox)

    def select_file(self):
        self.thread.start()

        # Open file dialog that only allows video files
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home', 'Video files (*.mp4 *.mkv *.avi)')

        # Update label text
        self.label.setText(fname[0])

        # Set filename
        self.filename = fname[0]
        self.video = (parse_filename(self.filename))

    def start_video_stream(self):
        self.thread.start()

    def start_subtitles_stream(self):
        self.thread.start()

    def callback(self, i):
        print(i)
        print(self.filename)


if __name__ == "__main__":
    server = Server()
    server.start()
    app = VideoStreamerApp()
    app.run(lambda: {
        server.stop()
    })

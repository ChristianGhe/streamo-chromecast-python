import os
import queue
import sys
import threading
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox

from server_chromecast import Server
from video_streaming_commands import get_video_info, stream_video_for_chromecast, stream_subtitle_for_chromecast


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
        # self.window.thread.progress.connect(lambda i: {
        #     print("Progress: ", i),
        # })
        self.window.show()

    def run(self, on_exit_callback=None):
        def on_exit():
            print("Application is about to exit.")
            self.window.dispose()
            print("window disposed")
            if on_exit_callback is not None:
                on_exit_callback()

        QCoreApplication.instance().aboutToQuit.connect(on_exit)
        sys.exit(self.app.exec_())


class VideoStreamer(QWidget):
    def __init__(self):
        super().__init__()

        self.video = None
        self.filename = None
        self.__connection_thread_running = True
        self.__queue_get_info = queue.Queue()
        self.__thread_get_info = threading.Thread(target=self.handle_get_info_queue)
        self.__thread_get_info.daemon = True
        self.__thread_get_info.start()
        self.btn_start_subtitle_stream = None
        self.btn_start_video_stream = None
        self.btn_browse = None
        self.audio_dropdown = QComboBox(self)
        self.video_dropdown = QComboBox(self)
        self.subtitle_dropdown = QComboBox(self)
        self.label = None
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()

        self.label = QLabel("No video selected")
        vbox.addWidget(self.label)

        self.btn_browse = QPushButton("Browse", self)
        self.btn_browse.clicked.connect(self.select_file)
        vbox.addWidget(self.btn_browse)

        vbox.addWidget(self.video_dropdown)
        vbox.addWidget(self.audio_dropdown)
        vbox.addWidget(self.subtitle_dropdown)

        self.btn_start_video_stream = QPushButton("Start Video Stream", self)
        self.btn_start_video_stream.clicked.connect(self.start_video_stream)
        vbox.addWidget(self.btn_start_video_stream)

        self.btn_start_subtitle_stream = QPushButton("Start Subtitles Stream", self)
        self.btn_start_subtitle_stream.clicked.connect(self.start_subtitles_stream)
        vbox.addWidget(self.btn_start_subtitle_stream)

        self.setLayout(vbox)

    def update_dropdowns(self, video_streams, audio_streams, subtitle_streams):
        print("Updating dropdowns")
        self.video_dropdown.clear()
        self.audio_dropdown.clear()
        self.subtitle_dropdown.clear()
        self.video_dropdown.addItems(video_streams)
        self.audio_dropdown.addItems(audio_streams)
        self.subtitle_dropdown.addItems(subtitle_streams)

    def handle_get_info_queue(self):
        print("Starting get info thread")
        while self.__connection_thread_running:
            try:
                video_info = self.__queue_get_info.get(timeout=0.5)
                print("Got video info")
                self.update_dropdowns(video_info[0], video_info[1], video_info[2])
            except queue.Empty:
                continue
        print("Stopping get info thread")

    def select_file(self):
        # Open file dialog that only allows video files
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home', 'Video files (*.mp4 *.mkv *.avi)')

        # Update label text
        self.label.setText(fname[0])

        # Set filename
        self.filename = fname[0]
        self.video = (parse_filename(self.filename))

        # Get video info
        threading.Thread(target=get_video_info, args=(self.filename, self.__queue_get_info)).start()

    def start_video_stream(self):
        print("Starting video stream")
        # get selected items from combo boxes
        video_stream_index = self.video_dropdown.currentIndex()
        audio_stream_index = self.audio_dropdown.currentIndex()

        print("options", video_stream_index, audio_stream_index)

    def start_subtitles_stream(self):
        print("Starting subtitles stream")
        subtitle_stream_index = self.subtitle_dropdown.currentIndex()
        print("options", subtitle_stream_index)

        # threading.Thread(target=get_video_info, args=(self.filename, self.__queue_get_info)).start()

    def dispose(self):
        self.__connection_thread_running = False
        self.__thread_get_info.join()
        print('debug 1')

    def callback(self, i):
        print(i)
        print(self.filename)


if __name__ == "__main__":
    server = Server()
    server.start()
    app = VideoStreamerApp()
    app.run(lambda: server.stop())

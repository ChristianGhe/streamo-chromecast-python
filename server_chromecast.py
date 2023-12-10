import os

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from threading import Thread

from werkzeug.serving import make_server
from get_local_ip import get_local_ip_address
from video_list_handler import init_video_list, set_ip_address_to_data


class Server:
    def __init__(self, data):
        self.app = Flask(__name__)
        self.cors = CORS(self.app)
        self.__data = data
        self.__video_list_file = 'video_list.json'

        @self.app.route('/favicon.ico')
        def favicon():
            return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/video_list.json')
        def get_info_json():
            print(os.getcwd())
            print(self.app.config.get('APPLICATION_ROOT'))
            filename = self.__video_list_file
            directory = '.'
            return send_from_directory(directory, filename)

        @self.app.route('/tracks/<path:filename>')
        def get_subtitle(filename):
            # return subtitles with file
            return send_from_directory('tracks', filename, mimetype="text/vtt")

        @self.app.route('/hls/<path:filename>')
        def stream(filename):
            # return mime type based on file extension
            mimetype = 'application/vnd.apple.mpegurl'
            if filename.endswith('.ts'):
                # mime type for ts files
                mimetype = 'video/MP2T'

            directory = 'hls'
            return send_from_directory(directory, filename, mimetype=mimetype)

        self.server = None
        self.thread = None

    def start(self):
        ip_address = get_local_ip_address()
        port = 3423
        init_video_list(self.__video_list_file, self.__data, ip_address, port)
        set_ip_address_to_data(self.__video_list_file, ip_address, port)
        self.server = make_server(ip_address, port, self.app)
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.start()

    def stop(self):
        if self.server is not None:
            self.server.shutdown()
            self.thread.join()
            self.server = None

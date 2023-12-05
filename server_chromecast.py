import os

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from threading import Thread

from werkzeug.serving import make_server
from get_local_ip import get_local_ip_address


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.cors = CORS(self.app)

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
            filename = 'video_list.json'
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
        self.server = make_server(get_local_ip_address(), 3432, self.app)
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.start()

    def stop(self):
        if self.server is not None:
            self.server.shutdown()
            self.thread.join()
            self.server = None

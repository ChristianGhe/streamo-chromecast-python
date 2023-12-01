from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from threading import Thread


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
            return send_from_directory('.', 'video_list.json')

        @self.app.route('/tracks/<path:filename>')
        def get_subtitle(filename):
            # return subtitles with file
            return send_from_directory('tracks/', filename, mimetype="text/vtt")

        @self.app.route('/hls/<path:filename>')
        def stream(filename):
            # return mime type based on file extension
            mimetype = 'application/vnd.apple.mpegurl'
            if filename.endswith('.ts'):
                # mime type for ts files
                mimetype = 'video/MP2T'

            return send_from_directory("hls/", filename, mimetype=mimetype)

        self.server = None

    def start(self):
        self.server = Thread(target=self.app.run,
                             kwargs={"host": "0.0.0.0", "port": 3432, "threaded": True, "debug": True,
                                     "use_reloader": False})
        self.server.start()

    def stop(self):
        if self.server is not None:
            self.server.terminate()
            self.server = None

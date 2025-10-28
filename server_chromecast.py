import json
from threading import Thread

from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.serving import make_server

from get_local_ip import get_local_ip_address
from models import init_db, Movie


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
        self.cors = CORS(self.app)
        self.__ip_address = get_local_ip_address()
        self.__port = 3432

        init_db(self.app)

        @self.app.route('/favicon.ico')
        def favicon():
            return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/get_info')
        def get_info():
            movies = Movie.query.all()
            movie_list = []

            for movie in movies:
                sources = json.loads(movie.sources) if movie.sources else []
                movie_info = {
                    "subtitle": movie.subtitle,
                    "sources": sources,
                    "thumb": movie.thumb,
                    "image-480x270": movie.image_480x270,
                    "image-780x1200": movie.image_780x1200,
                    "title": movie.title,
                    "studio": movie.studio,
                    "duration": movie.duration,
                    "tracks": [{
                        "id": str(track.id),
                        "type": "text",
                        "subtype": "captions",
                        "contentId": track.contentId,
                        "name": track.name,
                        "language": track.language
                    } for track in movie.subtitles]
                }
                movie_list.append(movie_info)

            return jsonify({
                "categories": [{
                    "name": "Movies",
                    "hls": f"http://{self.__ip_address}:{self.__port}/hls/",
                    "dash": "https://commondatastorage.googleapis.com/gtv-videos-bucket/CastVideos/dash/",
                    "mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/CastVideos/mp4/",
                    "images": "https://commondatastorage.googleapis.com/gtv-videos-bucket/CastVideos/images/",
                    "tracks": f"http://{self.__ip_address}/tracks/",
                    "videos": movie_list
                }]
            })

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
        self.server = make_server(self.__ip_address, self.__port, self.app)
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.start()

    def stop(self):
        if self.server is not None:
            self.server.shutdown()
            self.thread.join()
            self.server = None


if __name__ == '__main__':
    server = Server()
    server.start()

import json
import os
from sqlalchemy.exc import SQLAlchemyError
from models import db, Movie, Subtitle


def init_video_list( filename, data, ip_address, port):
    print(f"Initializing video_list.json with ip address {ip_address} and port {port}")
    # Create video_list.json if it doesn't exist and create base structure
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            data_str = json.dumps(data)
            data_str = data_str.replace("{ip}", ip_address)
            data_str = data_str.replace("{port}", port)
            data = json.loads(data_str)
            json.dump(data, f, indent=4)


def set_ip_address_to_data(file_name, ip_address, port):
    print(f"Setting ip address {ip_address} to video_list.json")
    with open(file_name, 'r') as f:
        # load json file and replace ip of tracks and hls for "Movies" category
        data = json.load(f)
        data["categories"][0]["hls"] = f"http://{ip_address}:{port}/hls/"
        data["categories"][0]["tracks"] = f"http://{ip_address}:{port}/tracks/"
        # save json file
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)


def add_video_to_db(app, video_name, duration, sources=None):
    """Add or update a video in the database"""
    with app.app_context():
        try:
            movie = Movie.query.filter_by(title=video_name).first()
            if not movie:
                default_sources = [{
                    "type": "hls",
                    "mime": "application/x-mpegurl",
                    "url": f"{video_name}.m3u8"
                }]
                movie = Movie(
                    title=video_name,
                    studio="",
                    duration=duration,
                    subtitle="description",
                    sources=json.dumps(sources or default_sources)
                )
                db.session.add(movie)
            else:
                movie.duration = duration
                if sources:
                    movie.sources = json.dumps(sources)

            db.session.commit()
            return movie
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            db.session.rollback()
            raise


def add_subtitle_to_db(app, video_name, subtitle_name, subtitle_language, content_id=None):
    """Add a subtitle track to a video in the database"""
    with app.app_context():
        try:
            movie = Movie.query.filter_by(title=video_name).first()
            if not movie:
                movie = add_video_to_db(video_name, 0)

            content_id = content_id or f"{video_name}.vtt"
            existing_subtitle = Subtitle.query.filter_by(
                contentId=content_id,
                movie_id=movie.id
            ).first()

            if not existing_subtitle:
                subtitle = Subtitle(
                    contentId=content_id,
                    language=subtitle_language,
                    name=subtitle_name,
                    movie_id=movie.id
                )
                db.session.add(subtitle)
                db.session.commit()

        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            db.session.rollback()
            raise


def select_video_from_db(video_name):
    try:
        movie = Movie.query.filter_by(title=video_name).first()
        if not movie:
            print(f"Video {video_name} not found in database. Adding video.")

        return movie

    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        db.session.rollback()
        # Handle the exception or re-raise it
        raise


def select_all_videos_from_db():
    try:
        movies = Movie.query.all()
        return movies

    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        db.session.rollback()
        # Handle the exception or re-raise it


if __name__ == '__main__':
    # add_video_to_list('video_list.json', "apvral-scenes.from.a.marriage.720p[flt]", 10196, "English", "en")
    # select_video_from_db("apvral-scenes.from.a.marriage.720p[flt]")
    movies = select_all_videos_from_db()
    print(movies)

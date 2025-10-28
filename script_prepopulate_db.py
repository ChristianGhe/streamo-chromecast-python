import json
from models import db, Movie, Subtitle


def migrate_json_to_db(json_file_path):
    """
    Migrate movie data from JSON file to SQLAlchemy database.

    Args:
        json_file_path (str): Path to the JSON file containing movie data
    """
    # Read JSON file
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Iterate through all movies in the JSON
    for category in data['categories']:
        for video in category['videos']:
            # Check if movie already exists
            existing_movie = Movie.query.filter_by(title=video['title']).first()
            if existing_movie:
                print(f"Movie {video['title']} already exists, skipping...")
                continue

            # Create new movie
            movie = Movie(
                title=video['title'],
                studio=video['studio'],
                duration=video['duration'],
                subtitle=video['subtitle'],
                thumb=video.get('thumb', ''),
                image_480x270=video.get('image-480x270', ''),
                image_780x1200=video.get('image-780x1200', ''),
                sources=json.dumps(video['sources'])
            )

            # Add all subtitle tracks
            for track in video['tracks']:
                subtitle = Subtitle(
                    contentId=track['contentId'],
                    language=track['language'],
                    name=track['name'],
                    movie=movie  # SQLAlchemy will handle the relationship
                )
                db.session.add(subtitle)

            db.session.add(movie)
            print(f"Added movie: {video['title']}")

    # Commit all changes
    try:
        db.session.commit()
        print("Migration completed successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error during migration: {str(e)}")
        raise


if __name__ == '__main__':
    # Make sure to initialize your Flask app and db before running this
    from flask import Flask

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Run migration
        migrate_json_to_db('video_list.json')

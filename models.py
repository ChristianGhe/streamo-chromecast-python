from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    studio = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    subtitle = db.Column(db.Text)  # Description field from JSON
    thumb = db.Column(db.String(255))
    image_480x270 = db.Column(db.String(255))
    image_780x1200 = db.Column(db.String(255))
    sources = db.Column(db.Text)  # JSON string of sources array

    # Relationship with subtitles
    subtitles = relationship("Subtitle", back_populates="movie", cascade="all, delete-orphan")


class Subtitle(db.Model):
    __tablename__ = 'subtitles'

    id = db.Column(db.Integer, primary_key=True)
    contentId = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(50))
    name = db.Column(db.String(255))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)

    # Relationship with movie
    movie = relationship("Movie", back_populates="subtitles")


def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

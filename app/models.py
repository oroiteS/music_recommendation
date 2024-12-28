# app/models.py
from datetime import datetime, UTC

from sqlalchemy import PrimaryKeyConstraint, CheckConstraint, Unicode, UnicodeText

from app import db


class User(db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.String(255), primary_key=True)
    username = db.Column(db.Unicode(255), nullable=False)
    login_id = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    user_identity = db.Column(db.Integer, default=0)


class Music(db.Model):
    __tablename__ = 'music'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(Unicode(255), nullable=False)
    artist_name = db.Column(Unicode(255), nullable=False)
    genre = db.Column(Unicode(255))
    play_count = db.Column(db.Integer, default=0)
    cover_url = db.Column(db.String(255), default='/static/music_img/default_cover.jpg')


class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(255), nullable=False)
    title = db.Column(Unicode(255), nullable=False)
    description = db.Column(UnicodeText)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))  # 数据库已设置默认值


class PlaylistSongs(db.Model):
    __tablename__ = 'playlist_songs'
    playlist_id = db.Column(db.Integer, nullable=False)
    music_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('playlist_id', 'music_id'),
    )


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(255), nullable=False)
    music_id = db.Column(db.Integer, nullable=False)
    comment_text = db.Column(UnicodeText)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))  # 数据库已设置默认值


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(255), nullable=False)
    music_id = db.Column(db.Integer, nullable=False)
    rating_value = db.Column(db.Integer, CheckConstraint('rating_value BETWEEN 1 AND 5'))


class UserPlayHistory(db.Model):
    __tablename__ = 'user_play_history'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(255), nullable=False)
    music_id = db.Column(db.Integer, nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.now(UTC))  # 数据库已设置默认值


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(255), db.ForeignKey('users.userid'), nullable=False)
    favorite_genres = db.Column(db.Unicode(255))
    favorite_artists = db.Column(db.Unicode(255))
    listening_times = db.Column(db.Unicode(255))

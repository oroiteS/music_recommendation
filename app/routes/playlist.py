import codecs
from datetime import datetime, UTC, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify, request
from app import db
from app.models import Playlist, Music, PlaylistSongs

playlist_bp = Blueprint('playlist', __name__)


# 获取用户的所有歌单
@playlist_bp.route('/user/<string:userid>', methods=['GET'])
def get_user_playlists(userid):
    try:
        playlists = Playlist.query.filter_by(userid=userid).all()
        playlists_list = []
        for playlist in playlists:
            playlists_list.append({
                'id': playlist.id,
                'title': playlist.title,
                'description': playlist.description,
                'created_at': (playlist.created_at+timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({'success': True, 'data': playlists_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# 创建新歌单
@playlist_bp.route('/', methods=['POST'])
def create_playlist():
    try:
        data = request.get_json()
        userid = data.get('userid')
        title = data.get('title')
        description = data.get('description', '')

        new_playlist = Playlist(
            userid=userid,
            title=title,
            description=description,
            created_at=datetime.now(UTC)
        )
        db.session.add(new_playlist)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'id': new_playlist.id,
                'title': new_playlist.title,
                'description': new_playlist.description,
                'created_at': new_playlist.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# 删除歌单
@playlist_bp.route('/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    try:
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'success': False, 'message': '歌单不存在'})

        # 先删除歌单中的所有歌曲
        PlaylistSongs.query.filter_by(playlist_id=playlist_id).delete()
        # 再删除歌单
        db.session.delete(playlist)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# 获取歌单详情
@playlist_bp.route('/<int:playlist_id>', methods=['GET'])
def get_playlist_detail(playlist_id):
    try:
        playlist = Playlist.query.get(playlist_id)
        if not playlist:
            return jsonify({'success': False, 'message': '歌单不存在'})

        # 修改查询方式，明确指定join条件
        songs = db.session.query(Music) \
            .join(PlaylistSongs, Music.id == PlaylistSongs.music_id) \
            .filter(PlaylistSongs.playlist_id == playlist_id) \
            .all()

        songs_list = []
        for song in songs:
            songs_list.append({
                'id': song.id,
                'title': song.title,
                'artist_name': song.artist_name,
                'genre': song.genre,
                'cover_url': song.cover_url
            })

        return jsonify({
            'success': True,
            'data': {
                'id': playlist.id,
                'title': playlist.title,
                'description': playlist.description,
                'created_at': (playlist.created_at+timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
                'songs': songs_list
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# 添加歌曲到歌单
@playlist_bp.route('/<int:playlist_id>/songs', methods=['POST'])
def add_song_to_playlist(playlist_id):
    try:
        data = request.get_json()
        music_id = data.get('music_id')

        # 检查是否已存在
        existing = PlaylistSongs.query.filter_by(
            playlist_id=playlist_id,
            music_id=music_id
        ).first()

        if existing:
            return jsonify({'success': False, 'message': '歌曲已在歌单中'})

        # 添加歌曲到歌单
        playlist_song = PlaylistSongs(
            playlist_id=playlist_id,
            music_id=music_id
        )
        db.session.add(playlist_song)
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# 从歌单中删除歌曲
@playlist_bp.route('/<int:playlist_id>/songs/<int:music_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_id, music_id):
    try:
        PlaylistSongs.query.filter_by(
            playlist_id=playlist_id,
            music_id=music_id
        ).delete()
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

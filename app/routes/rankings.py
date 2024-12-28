from flask import Blueprint, jsonify
from sqlalchemy import func
from app import db
from app.models import UserPlayHistory, Music

rankings_bp = Blueprint('rankings', __name__)


@rankings_bp.route('/rankings', methods=['GET'])
def get_rankings():
    try:
        # 歌手排行榜
        artist_rankings = db.session.query(
            Music.artist_name,
            func.count(UserPlayHistory.id).label('play_count')
        ).join(
            UserPlayHistory, UserPlayHistory.music_id == Music.id
        ).group_by(
            Music.artist_name
        ).order_by(
            func.count(UserPlayHistory.id).desc()
        ).limit(10).all()

        # 热歌排行榜
        pop_index_rankings = db.session.query(
            Music.id,
            Music.title,
            Music.artist_name,
            Music.genre,
            func.count(UserPlayHistory.id).label('play_count')
        ).join(
            UserPlayHistory, UserPlayHistory.music_id == Music.id
        ).group_by(
            Music.id, Music.title, Music.artist_name, Music.genre
        ).order_by(
            func.count(UserPlayHistory.id).desc()
        ).limit(10).all()

        return jsonify({
            'success': True,
            'rankings': {
                'artists': [
                    {'name': artist, 'popularity': count}
                    for artist, count in artist_rankings
                ],
                'hotSongs': [
                    {'id': id, 'title': title, 'artist': artist, 'genre': genre, 'popularity': count}
                    for id, title, artist, genre, count in pop_index_rankings
                ]
            }
        })

    except Exception as e:
        print(f"Error in get_rankings: {str(e)}")
        return jsonify({'success': False, 'message': f'获取排行榜失败: {str(e)}'})

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta, UTC
from app import db
from app.models import UserPlayHistory, Music

user_stats_bp = Blueprint('user_stats', __name__)


@user_stats_bp.route('/stats/music', methods=['GET'])
def get_music_stats():
    userid = request.args.get('userid')
    if not userid:
        return jsonify({'success': False, 'message': '未提供用户ID'})

    try:
        # 获取最近30天的播放记录
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)

        # 1. 最常听的音乐类型统计
        genre_stats = db.session.query(
            Music.genre,
            func.count(UserPlayHistory.id).label('play_count')
        ).join(
            UserPlayHistory, UserPlayHistory.music_id == Music.id
        ).filter(
            UserPlayHistory.userid == userid,
            UserPlayHistory.played_at >= thirty_days_ago
        ).group_by(
            Music.genre
        ).order_by(
            func.count(UserPlayHistory.id).desc()
        ).limit(5).all()

        # 2. 最常听的艺术家统计
        artist_stats = db.session.query(
            Music.artist_name,
            func.count(UserPlayHistory.id).label('play_count')
        ).join(
            UserPlayHistory, UserPlayHistory.music_id == Music.id
        ).filter(
            UserPlayHistory.userid == userid,
            UserPlayHistory.played_at >= thirty_days_ago
        ).group_by(
            Music.artist_name
        ).order_by(
            func.count(UserPlayHistory.id).desc()
        ).limit(5).all()

        # 3. 总播放次数
        total_plays = UserPlayHistory.query.filter(
            UserPlayHistory.userid == userid,
            UserPlayHistory.played_at >= thirty_days_ago
        ).count()

        return jsonify({
            'success': True,
            'stats': {
                'genre_stats': [
                    {'genre': genre, 'count': int(count)}
                    for genre, count in genre_stats
                ],
                'artist_stats': [
                    {'artist': artist, 'count': int(count)}
                    for artist, count in artist_stats
                ],
                'total_plays': total_plays
            }
        })

    except Exception as e:
        print(f"Error in get_music_stats: {str(e)}")  # 添加调试日志
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        })


@user_stats_bp.route('/stats/recent', methods=['GET'])
def get_recent_stats():
    userid = request.args.get('userid')
    if not userid:
        return jsonify({'success': False, 'message': '未提供用户ID'})

    try:
        # 获取最近播放的10首歌
        recent_plays = db.session.query(
            Music.title,
            Music.artist_name,
            UserPlayHistory.played_at
        ).join(
            Music, Music.id == UserPlayHistory.music_id
        ).filter(
            UserPlayHistory.userid == userid
        ).order_by(
            UserPlayHistory.played_at.desc()
        ).limit(10).all()

        return jsonify({
            'success': True,
            'recent_plays': [
                {
                    'title': title,
                    'artist': artist,
                    'played_at': (played_at+timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
                }
                for title, artist, played_at in recent_plays
            ]
        })

    except Exception as e:
        print(f"Error in get_recent_stats: {str(e)}")  # 添加调试日志
        return jsonify({
            'success': False,
            'message': f'获取最近播放记录失败: {str(e)}'
        })

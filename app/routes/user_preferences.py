from flask import Blueprint, request, jsonify
from app import db
from app.models import UserPreference

user_pref_bp = Blueprint('user_preferences', __name__)


@user_pref_bp.route('/preferences', methods=['POST'])
def update_preferences():
    data = request.get_json()
    userid = data.get('userid')

    if not userid:
        return jsonify({'success': False, 'message': '未提供用户ID'})

    # 确保输入数据是列表
    favorite_genres = data.get('favorite_genres', [])
    favorite_artists = data.get('favorite_artists', [])
    listening_times = data.get('listening_times', [])

    if not isinstance(favorite_genres, list) or not isinstance(favorite_artists, list) or not isinstance(
            listening_times, list):
        return jsonify({'success': False, 'message': '输入数据格式错误'})

    try:
        pref = UserPreference.query.filter_by(userid=userid).first()
        if not pref:
            pref = UserPreference(userid=userid)
            db.session.add(pref)

        # 将列表转换为字符串存储
        pref.favorite_genres = ','.join(favorite_genres) if favorite_genres else ''
        pref.favorite_artists = ','.join(favorite_artists) if favorite_artists else ''
        pref.listening_times = ','.join(listening_times) if listening_times else ''

        db.session.commit()
        return jsonify({'success': True, 'message': '偏好设置已更新',
                        'data': {'favorite_genres': pref.favorite_genres, 'favorite_artists': pref.favorite_artists,
                                 'listening_times': pref.listening_times}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'})


@user_pref_bp.route('/preferences', methods=['GET'])
def get_preferences():
    userid = request.args.get('userid')
    if not userid:
        return jsonify({'success': False, 'message': '未提供用户ID'})

    pref = UserPreference.query.filter_by(userid=userid).first()
    if pref:
        return jsonify({
            'success': True,
            'preferences': {
                'favorite_genres': pref.favorite_genres.split(',') if pref.favorite_genres else [],
                'favorite_artists': pref.favorite_artists.split(',') if pref.favorite_artists else [],
                'listening_times': pref.listening_times.split(',') if pref.listening_times else []
            }
        })
    return jsonify({
        'success': True,
        'preferences': {
            'favorite_genres': [],
            'favorite_artists': [],
            'listening_times': []
        }
    })

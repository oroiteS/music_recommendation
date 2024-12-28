from flask import Blueprint, request, jsonify
from app import db
from app.models import Music
from sqlalchemy import or_

search_bp = Blueprint('search', __name__)


@search_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({
            'success': False,
            'message': '搜索关键词不能为空'
        })

    try:
        # 使用 LIKE 进行模糊查询，同时搜索歌名和歌手
        results = Music.query.filter(
            or_(
                Music.title.like(f'%{query}%'),
                Music.artist_name.like(f'%{query}%')
            )
        ).all()

        return jsonify({
            'success': True,
            'results': [{
                'id': song.id,
                'title': song.title,
                'artist': song.artist_name,
                'cover': song.cover_url
            } for song in results]
        })

    except Exception as e:
        print(f"Error in search: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'搜索失败: {str(e)}'
        })

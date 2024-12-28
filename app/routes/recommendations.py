from flask import Blueprint, request, jsonify
from scipy.spatial.distance import cosine
from sqlalchemy import func, text

from app import db
from app.models import UserPlayHistory, Music, Rating, UserPreference

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    userid = request.args.get('userid')
    if not userid:
        return jsonify({'success': False, 'message': '未提供用户ID'})

    try:
        # 1. 获取用户评分数据
        ratings = db.session.query(
            Rating.userid,
            Rating.music_id,
            Rating.rating_value
        ).all()

        # 如果评分数据太少，添加播放历史数据作为隐式反馈
        play_history = db.session.query(
            UserPlayHistory.userid,
            UserPlayHistory.music_id,
            func.count(UserPlayHistory.id).label('play_count')
        ).group_by(
            UserPlayHistory.userid,
            UserPlayHistory.music_id
        ).all()

        # 2. 构建用户-歌曲矩阵
        user_song_matrix = {}
        for r in ratings:
            if r.userid not in user_song_matrix:
                user_song_matrix[r.userid] = {}
            user_song_matrix[r.userid][r.music_id] = r.rating_value

        # 将播放次数转换为评分（1-5分）
        for p in play_history:
            if p.userid not in user_song_matrix:
                user_song_matrix[p.userid] = {}
            if p.music_id not in user_song_matrix[p.userid]:
                # 将播放次数映射到1-5分
                play_score = min(5, p.play_count)
                user_song_matrix[p.userid][p.music_id] = play_score

        # 3. 计算用户相似度
        def calculate_similarity(user1_id, user2_id):
            user1_songs = user_song_matrix.get(user1_id, {})
            user2_songs = user_song_matrix.get(user2_id, {})

            # 获取两个用户的偏好信息
            user1_pref = UserPreference.query.filter_by(userid=user1_id).first()
            user2_pref = UserPreference.query.filter_by(userid=user2_id).first()

            # 基础相似度（基于评分的余弦相似度）
            rating_similarity = 0
            # 获取两个用户共同评价过的歌曲
            common_songs = set(user1_songs.keys()) & set(user2_songs.keys())
            if common_songs:
                user1_ratings = [user1_songs[song] for song in common_songs]
                user2_ratings = [user2_songs[song] for song in common_songs]
                try:
                    rating_similarity = 1 - cosine(user1_ratings, user2_ratings)
                except:
                    rating_similarity = 0

            # 计算偏好相似度
            preference_similarity = 0
            if user1_pref and user2_pref:
                # 使用的是 Jaccard 相似度系数，即重合的喜好的个数占据两个人总喜欢个数的百分之多少
                # 计算流派匹配度
                genres1 = set(user1_pref.favorite_genres.split(',')) if user1_pref.favorite_genres else set()
                genres2 = set(user2_pref.favorite_genres.split(',')) if user2_pref.favorite_genres else set()
                genre_similarity = len(genres1 & genres2) / max(len(genres1 | genres2), 1)
                # 计算艺术家匹配度
                artists1 = set(user1_pref.favorite_artists.split(',')) if user1_pref.favorite_artists else set()
                artists2 = set(user2_pref.favorite_artists.split(',')) if user2_pref.favorite_artists else set()
                artist_similarity = len(artists1 & artists2) / max(len(artists1 | genres2), 1)
                # 计算时段匹配度
                times1 = set(user1_pref.listening_times.split(',')) if user1_pref.listening_times else set()
                times2 = set(user2_pref.listening_times.split(',')) if user2_pref.listening_times else set()
                time_similarity = len(times1 & times2) / max(len(times1 | times2), 1)
                # 综合偏好相似度（可以调整权重）
                preference_similarity = (genre_similarity * 0.4 + artist_similarity * 0.4 + time_similarity * 0.2)
            # 最终相似度：评分相似度和偏好相似度的加权平均
            final_similarity = rating_similarity * 0.6 + preference_similarity * 0.4
            return final_similarity

        # 4. 获取相似用户
        user_similarities = []
        for other_userid in user_song_matrix:
            if other_userid != userid:
                similarity = calculate_similarity(userid, other_userid)
                user_similarities.append((other_userid, similarity))

        # 按相似度排序
        user_similarities.sort(key=lambda x: x[1], reverse=True)
        similar_users = user_similarities[:5]  # 取前5个最相似的用户

        # 5. 获取推荐歌曲
        recommended_songs = {}
        for similar_user, similarity in similar_users:
            for song_id, rating in user_song_matrix[similar_user].items():
                # 跳过用户已经听过的歌
                if song_id in user_song_matrix.get(userid, {}):
                    continue
                if song_id not in recommended_songs:
                    recommended_songs[song_id] = 0
                recommended_songs[song_id] += rating * similarity

        # 按推荐分数排序
        recommended_song_ids = sorted(recommended_songs.items(), key=lambda x: x[1], reverse=True)
        recommended_song_ids = [song_id for song_id, _ in recommended_song_ids]

        # 6. 如果推荐歌曲不足15首，从热门歌曲中补充
        if len(recommended_song_ids) < 15:
            # 获取热门歌（不包括已推荐的歌曲）
            popular_songs = db.session.query(
                Music.id
            ).outerjoin(
                UserPlayHistory, UserPlayHistory.music_id == Music.id
            ).group_by(
                Music.id
            ).order_by(
                text('COUNT(user_play_history.id) DESC')
            ).filter(
                ~Music.id.in_(recommended_song_ids)
            ).limit(15).all()

            popular_song_ids = [song.id for song in popular_songs]
            recommended_song_ids.extend(popular_song_ids)
            recommended_song_ids = recommended_song_ids[:15]  # 限制为15首歌

        # 7. 获取推荐歌曲的详细信息
        recommended_songs = Music.query.filter(
            Music.id.in_(recommended_song_ids)
        ).all()

        # 按照推荐顺序排序
        recommended_songs.sort(key=lambda x: recommended_song_ids.index(x.id))

        return jsonify({
            'success': True,
            'recommendations': {
                'collaborative': [
                    {
                        'id': song.id,
                        'title': song.title,
                        'artist': song.artist_name,
                        'cover': song.cover_url
                    }
                    for song in recommended_songs
                ]
            }
        })

    except Exception as e:
        print(f"Error in get_recommendations: {str(e)}")
        return jsonify({'success': False, 'message': f'获取推荐歌单失败: {str(e)}'})

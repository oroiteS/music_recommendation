import os
import shutil
from datetime import datetime, UTC
from flask import Blueprint, jsonify, request
from sqlalchemy import func
from app import db
from app.models import Music, Comment, User, Rating, UserPlayHistory

music_bp = Blueprint('music', __name__)


@music_bp.route('/list', methods=['GET'])
def get_music_list():
    try:
        musics = Music.query.all()
        music_list = []
        for music in musics:
            music_list.append({
                'id': music.id,
                'title': music.title,
                'artist_name': music.artist_name,
                'genre': music.genre,
                'cover_url': music.cover_url
            })
        return jsonify({'success': True, 'data': music_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/<int:music_id>', methods=['GET'])
def get_music_detail(music_id):
    try:
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'success': False, 'message': '音乐不存在'})

        music_data = {
            'id': music.id,
            'title': music.title,
            'artist_name': music.artist_name,
            'genre': music.genre,
            'play_count': music.play_count,
            'cover_url': music.cover_url
        }
        return jsonify({'success': True, 'data': music_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/<int:music_id>/comments', methods=['GET'])
def get_music_comments(music_id):
    try:
        comments = Comment.query.filter_by(music_id=music_id).order_by(Comment.created_at.desc()).all()
        comments_list = []
        for comment in comments:
            user = User.query.filter_by(userid=comment.userid).first()
            comments_list.append({
                'id': comment.id,
                'username': user.username if user else '未知用户',
                'comment_text': comment.comment_text,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({'success': True, 'data': comments_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/<int:music_id>/comments', methods=['POST'])
def add_comment(music_id):
    try:
        data = request.get_json()
        comment_text = data.get('comment_text')
        userid = data.get('userid')

        new_comment = Comment(
            userid=userid,
            music_id=music_id,
            comment_text=comment_text
        )
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'id': new_comment.id,
                'username': '当前用户',  # 临时使用
                'comment_text': comment_text,
                'created_at': new_comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/<int:music_id>/ratings', methods=['GET'])
def get_ratings(music_id):
    try:
        rating_stats = db.session.query(
            func.avg(Rating.rating_value).label('average'),
            func.count(Rating.id).label('count')
        ).filter(Rating.music_id == music_id).first()

        return jsonify({
            'success': True,
            'data': {
                'average_rating': float(rating_stats.average) if rating_stats.average else 0,
                'rating_count': rating_stats.count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/<int:music_id>/ratings', methods=['POST'])
def submit_rating(music_id):
    try:
        data = request.get_json()
        rating_value = data.get('rating_value')
        userid = data.get('userid')

        if not rating_value or not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
            return jsonify({'success': False, 'message': '无效的评分值'})

        existing_rating = Rating.query.filter_by(
            music_id=music_id,
            userid=userid
        ).first()

        if existing_rating:
            existing_rating.rating_value = rating_value
        else:
            new_rating = Rating(
                music_id=music_id,
                userid=userid,
                rating_value=rating_value
            )
            db.session.add(new_rating)

        db.session.commit()

        rating_stats = db.session.query(
            func.avg(Rating.rating_value).label('average'),
            func.count(Rating.id).label('count')
        ).filter(Rating.music_id == music_id).first()

        return jsonify({
            'success': True,
            'data': {
                'new_average': float(rating_stats.average),
                'new_count': rating_stats.count
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/<int:music_id>/play', methods=['POST'])
def record_play(music_id):
    try:
        data = request.get_json()
        userid = data.get('userid')

        if not userid:
            return jsonify({'success': False, 'message': '未登录用户'})

        # 更新音乐播放次数
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'success': False, 'message': '音乐不存在'})

        music.play_count += 1

        # 添加播放记录
        play_history = UserPlayHistory(
            userid=userid,
            music_id=music_id,
            played_at=datetime.now(UTC)
        )

        db.session.add(play_history)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'play_count': music.play_count
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/play-history/<string:userid>', methods=['GET'])
def get_play_history(userid):
    try:
        # 获取用户最近的20条播放记录
        history = UserPlayHistory.query \
            .filter_by(userid=userid) \
            .order_by(UserPlayHistory.played_at.desc()) \
            .limit(20) \
            .all()

        history_list = []
        for record in history:
            music = Music.query.get(record.music_id)
            if music:
                history_list.append({
                    'id': music.id,
                    'title': music.title,
                    'artist_name': music.artist_name,
                    'played_at': record.played_at.strftime('%Y-%m-%d %H:%M:%S')
                })

        return jsonify({'success': True, 'data': history_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/upload-cover', methods=['POST'])
def upload_cover():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有文件'})

        file = request.files['file']
        artist_name = request.form.get('artist_name')
        title = request.form.get('title')

        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})

        if file:
            # 生成新文件名
            filename = f"{artist_name}-{title}.jpg"

            # 临时保存路径
            temp_path = os.path.join('web', 'public', 'static', 'music_img', 'temp')
            os.makedirs(temp_path, exist_ok=True)

            # 保存文件到临时目录
            temp_file_path = os.path.join(temp_path, filename)
            file.save(temp_file_path)

            # 返回相对URL路径
            url = f'/static/music_img/temp/{filename}'

            return jsonify({
                'success': True,
                'url': url,
                'filename': filename
            })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/<int:music_id>', methods=['PUT'])
def update_music(music_id):
    try:
        data = request.get_json()
        print("Received update data:", data)  # 调试日志
        
        music = Music.query.get(music_id)
        if not music:
            return jsonify({'success': False, 'message': '音乐不存在'})
        
        # 更新基本信息
        music.title = data.get('title', music.title)
        music.artist_name = data.get('artist_name', music.artist_name)
        music.genre = data.get('genre', music.genre)
        
        # 处理封面图片
        cover_url = data.get('cover_url')
        print("Cover URL:", cover_url)  # 调试日志
        
        if cover_url and 'temp' in cover_url:
            # 从临时URL中获取文件名
            filename = os.path.basename(cover_url)
            print("Filename:", filename)  # 调试日志
            
            # 设置源路径和目标路径
            temp_path = os.path.join('web', 'public', 'static', 'music_img', 'temp', filename)
            final_path = os.path.join('web', 'public', 'static', 'music_img', filename)
            
            print("Moving from:", temp_path)  # 调试日志
            print("Moving to:", final_path)   # 调试日志
            
            # 移动文件
            if os.path.exists(temp_path):
                shutil.move(temp_path, final_path)
                # 更新数据库中的URL
                music.cover_url = f'/static/music_img/{filename}'
                print("New cover URL:", music.cover_url)  # 调试日志
            else:
                print("Temp file not found:", temp_path)  # 调试日志
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': music.id,
                'title': music.title,
                'artist_name': music.artist_name,
                'genre': music.genre,
                'cover_url': music.cover_url
            }
        })
    except Exception as e:
        db.session.rollback()
        print("Error:", str(e))  # 调试日志
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/upload', methods=['POST'])
def upload_music():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有文件'})

        file = request.files['file']
        artist_name = request.form.get('artist_name')
        title = request.form.get('title')

        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})

        if file:
            # 生成新文件名
            filename = f"{artist_name}-{title}.mp3"

            # 保存路径
            save_path = os.path.join('web', 'public', 'static', 'music')
            os.makedirs(save_path, exist_ok=True)

            # 保存文件
            file_path = os.path.join(save_path, filename)
            file.save(file_path)

            return jsonify({
                'success': True,
                'file_path': f'/static/music/{filename}'
            })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@music_bp.route('/create', methods=['POST'])
def create_music():
    try:
        data = request.get_json()

        new_music = Music(
            title=data['title'],
            artist_name=data['artist_name'],
            genre=data.get('genre', ''),
            cover_url=data.get('cover_url')
        )
        if new_music.cover_url == '':
            new_music.cover_url = '/static/music_img/default_cover.jpg'
        db.session.add(new_music)
        db.session.commit()

        return jsonify({'success': True, 'message': '音乐创建成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

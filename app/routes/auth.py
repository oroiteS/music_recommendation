# app/routes/auth.py
import uuid

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    login_id = data.get('login_id')
    username = data.get('username')
    password = data.get('password')

    # 验证必填字段
    if not all([login_id, username, password]):
        return jsonify({'success': False, 'message': '所有字段都是必填的'})

    # 验证登录ID格式（只允许字母和数字）
    if not login_id.isalnum():
        return jsonify({'success': False, 'message': '登录账号只能包含字母和数字'})

    # 检查登录ID是否已存在
    if User.query.filter_by(login_id=login_id).first():
        return jsonify({'success': False, 'message': '该登录账号已被使用'})

    # 生成唯一的userid
    userid = str(uuid.uuid4())

    # 创建新用户
    new_user = User(
        userid=userid,
        username=username,
        login_id=login_id,
        password=generate_password_hash(password)
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': '注册成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login_id = data.get('login_id')
    password = data.get('password')

    # 验证必填字段
    if not all([login_id, password]):
        return jsonify({'success': False, 'message': '请输入登录账号和密码'})

    # 查找用户
    user = User.query.filter_by(login_id=login_id).first()
    if not user:
        return jsonify({'success': False, 'message': '账号不存在'})

    # 验证密码
    if not check_password_hash(user.password, password):
        return jsonify({'success': False, 'message': '密码错误'})

    # 返回用户信息（用于前端存储）
    return jsonify({
        'success': True,
        'message': '登录成功',
        'user': {
            'userid': user.userid,
            'username': user.username,
            'user_identity': user.user_identity
        }
    })


@auth_bp.route('/change-username', methods=['POST'])
def change_username():
    data = request.get_json()
    userid = data.get('userid')
    new_username = data.get('new_username')

    # 验证必填字段
    if not all([userid, new_username]):
        return jsonify({'success': False, 'message': '所有字段都是必填的'})

    # 验证用户名长度
    if len(new_username.strip()) == 0:
        return jsonify({'success': False, 'message': '用户名不能为空'})

    # 查找用户
    user = User.query.get(userid)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'})

    try:
        # 更新用户名
        user.username = new_username
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '用户名修改成功',
            'user': {
                'userid': user.userid,
                'username': new_username,
                'user_identity': user.user_identity
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'用户名修改失败: {str(e)}'})


@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    userid = data.get('userid')
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    # 验证必填字段
    if not all([userid, old_password, new_password]):
        return jsonify({'success': False, 'message': '所有字段都是必填的'})

    # 验证新密码长度
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度不能少于6位'})

    # 查找用户
    user = User.query.get(userid)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'})

    # 验证旧密码
    if not check_password_hash(user.password, old_password):
        return jsonify({'success': False, 'message': '原密码错误'})

    try:
        # 更新密码
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'密码修改失败: {str(e)}'})

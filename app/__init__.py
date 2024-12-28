# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import Config

# 创建一个数据库实例
db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 允许跨域请求
    CORS(app, supports_credentials=True)  # 允许跨域请求时携带凭证

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图（模块化路由）
    from app.routes.auth import auth_bp
    from app.routes.music import music_bp
    from app.routes.playlist import playlist_bp
    from app.routes.user_preferences import user_pref_bp
    from app.routes.user_stats import user_stats_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.rankings import rankings_bp
    from app.routes.search import search_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(music_bp, url_prefix='/music')
    app.register_blueprint(playlist_bp, url_prefix='/playlist')
    app.register_blueprint(user_pref_bp, url_prefix='/preferences')
    app.register_blueprint(user_stats_bp, url_prefix='/user_stats')
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(rankings_bp)
    app.register_blueprint(search_bp)

    return app

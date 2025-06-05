import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import config
from app.models import db, User, Province

jwt = JWTManager()

def create_app(config_name=None):
    """创建Flask应用"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:8080']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })
    
    # 配置日志
    configure_logging(app)
    
    # 注册蓝图
    from app.auth import auth_bp
    from app.api.ledger import ledger_bp
    from app.api.admin import admin_bp
    from app.api.meta import meta_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(ledger_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(meta_bp, url_prefix='/api/meta')
    
    # 错误处理
    register_error_handlers(app)
    
    # JWT错误处理
    register_jwt_handlers(jwt)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        init_database(app)
    
    app.logger.info(f'Application started in {config_name} mode')

    # 打印所有注册的路由
    for rule in app.url_map.iter_rules():
        print(f"[ROUTE] {rule}")

    return app

def configure_logging(app):
    """配置日志"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 使用不同的日志文件名
    log_file = app.config['LOG_FILE_PATH']
    if os.path.exists(log_file):
        try:
            os.remove(log_file)
        except:
            pass
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=app.config['LOG_MAX_BYTES'],
        backupCount=app.config['LOG_BACKUP_COUNT'],
        delay=True  # 延迟文件创建
    )
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())
    file_handler.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    
    if app.config.get('LOG_TO_STDOUT'):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)

def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'error': str(error)
        }), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': 'Forbidden',
            'error': str(error)
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found',
            'error': str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'An unexpected error occurred'
        }), 500

def register_jwt_handlers(jwt):
    """注册JWT错误处理器"""
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({
            'success': False,
            'message': 'Missing or invalid token',
            'error': str(error)
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has expired',
            'error': 'Token expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Invalid token',
            'error': str(error)
        }), 401

def init_database(app):
    """初始化数据库数据"""
    # 创建默认管理员用户
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')  # 请在生产环境中修改
        db.session.add(admin)
        db.session.commit()
        app.logger.info('Created default admin user')
    
    # 初始化省份数据
    if not Province.query.first():
        provinces = [
            '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '其他', '另外'
        ]
        for province_name in provinces:
            province = Province(name=province_name)
            db.session.add(province)
        db.session.commit()
        app.logger.info('Initialized province data')
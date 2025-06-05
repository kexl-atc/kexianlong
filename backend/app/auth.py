from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

from app.models import db, User, ActivityLog

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 50:
            return jsonify({
                'success': False,
                'message': 'Username must be between 3 and 50 characters'
            }), 400
        
        # 验证密码强度
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 409
        
        # 获取角色，默认为 user
        role = data.get('role', 'user')
        if role not in ['user', 'power_user', 'admin']:
            role = 'user'
        
        # 创建新用户
        new_user = User(username=username, role=role)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # 记录日志
        log_activity('INFO', f'New user registered: {username}', user_id=new_user.id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'id': new_user.id,
                'username': new_user.username,
                'role': new_user.role
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f'Registration error: {str(e)}')
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': str(e) if current_app.debug else 'Internal error'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            # 记录失败登录
            log_activity('WARNING', f'Failed login attempt for username: {username}')
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
        
        # 创建JWT token
        access_token = create_access_token(
            identity=str(user.id),  # 一定要转成字符串
            additional_claims={
                'role': user.role,
                'username': user.username
            }
        )
        
        # 记录成功登录
        log_activity('INFO', f'User logged in: {username}', user_id=user.id)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Login error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error': str(e) if current_app.debug else 'Internal error'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get user error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Failed to get user info',
            'error': str(e) if current_app.debug else 'Internal error'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Old password and new password are required'
            }), 400
        
        # 验证旧密码
        if not user.check_password(old_password):
            return jsonify({
                'success': False,
                'message': 'Old password is incorrect'
            }), 401
        
        # 验证新密码强度
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'New password must be at least 6 characters long'
            }), 400
        
        # 更新密码
        user.set_password(new_password)
        db.session.commit()
        
        # 记录日志
        log_activity('INFO', f'Password changed for user: {user.username}', user_id=user_id)
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Change password error: {str(e)}')
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to change password',
            'error': str(e) if current_app.debug else 'Internal error'
        }), 500

def log_activity(level, message, user_id=None):
    """记录活动日志"""
    try:
        log = ActivityLog(
            level=level,
            message=message,
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'Failed to log activity: {str(e)}')
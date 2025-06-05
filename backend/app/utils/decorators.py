from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(allowed_roles):
    """角色权限检查装饰器"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.method == 'OPTIONS':
                return '', 204
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role', 'user')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': 'Insufficient permissions',
                    'error': 'FORBIDDEN'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
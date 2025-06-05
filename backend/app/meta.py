from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import db, Ledger, User

meta_bp = Blueprint('meta', __name__, url_prefix='/api/meta')

@meta_bp.route('/stats/ledger_by_user', methods=['GET'])
@jwt_required()
def get_ledger_stats_by_user():
    """获取各用户台账统计"""
    try:
        # 获取时间范围参数
        days = request.args.get('days', default=30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        
        # 查询每个用户的台账数量
        stats = db.session.query(
            User.username,
            func.count(Ledger.id).label('count')
        ).join(
            Ledger, User.id == Ledger.user_id
        ).filter(
            Ledger.created_at >= start_date
        ).group_by(
            User.username
        ).all()
        
        # 查询每个用户的月度趋势
        monthly_stats = db.session.query(
            User.username,
            func.date_format(Ledger.created_at, '%Y-%m').label('month'),
            func.count(Ledger.id).label('count')
        ).join(
            Ledger, User.id == Ledger.user_id
        ).filter(
            Ledger.created_at >= start_date
        ).group_by(
            User.username,
            func.date_format(Ledger.created_at, '%Y-%m')
        ).order_by(
            func.date_format(Ledger.created_at, '%Y-%m')
        ).all()
        
        # 处理月度趋势数据
        trend_data = {}
        for username, month, count in monthly_stats:
            if username not in trend_data:
                trend_data[username] = []
            trend_data[username].append({
                'month': month,
                'count': count
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total': [{'username': username, 'count': count} for username, count in stats],
                'trend': [{'username': username, 'records': records} for username, records in trend_data.items()]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get ledger stats error: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Failed to get ledger statistics',
            'error': str(e) if current_app.debug else 'Internal error'
        }), 500 
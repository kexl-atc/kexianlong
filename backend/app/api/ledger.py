from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_

from app.models import db, LedgerEntry, ActivityLog, User, Province
from app.auth import log_activity

ledger_bp = Blueprint('ledger', __name__)

@ledger_bp.route('/ledger', methods=['GET'])
@jwt_required()
def get_ledger_entries():
    """获取台账列表"""
    try:
        user_id = get_jwt_identity()
        user_role = get_jwt().get('role', 'user')
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', current_app.config['DEFAULT_PAGE_SIZE'], type=int)
        
        # 限制每页最大数量
        page_size = min(page_size, current_app.config['MAX_PAGE_SIZE'])
        
        # 搜索参数
        project_name = request.args.get('project_name', '').strip()
        location = request.args.get('location', '').strip()
        province = request.args.get('province', '').strip()
        recorder = request.args.get('recorder', '').strip()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = LedgerEntry.query
        
        # 搜索过滤
        if project_name:
            project_pattern = f'%{project_name}%'
            query = query.filter(LedgerEntry.project_name.ilike(project_pattern))
        if location:
            location_pattern = f'%{location}%'
            query = query.filter(LedgerEntry.location.ilike(location_pattern))
        
        # 省份过滤
        if province:
            query = query.filter_by(province=province)
        
        # 录入人员过滤
        if recorder:
            # 需要join User表来过滤录入人员
            query = query.join(User).filter(User.username == recorder)
        
        # 日期范围过滤
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(LedgerEntry.date >= start)
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(LedgerEntry.date <= end)
            except ValueError:
                pass
        
        # 排序
        query = query.order_by(LedgerEntry.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=page_size,
            error_out=False
        )
        
        # 构建响应
        items = [entry.to_dict() for entry in pagination.items]
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'items': items,
                'total': pagination.total,
                'page': pagination.page,
                'pageSize': page_size,
                'totalPages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get ledger entries error: {str(e)}')
        return jsonify({
            'code': 500,
            'message': 'Failed to get ledger entries',
            'data': None
        }), 500

@ledger_bp.route('/ledger/<int:entry_id>', methods=['GET'])
@jwt_required()
def get_ledger_entry(entry_id):
    """获取单个台账条目"""
    try:
        entry = LedgerEntry.query.get(entry_id)
        if not entry:
            return jsonify({
                'code': 404,
                'message': 'Entry not found'
            }), 404
        # 允许所有已登录用户查看详情
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': entry.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f'Get ledger entry error: {str(e)}')
        return jsonify({
            'code': 500,
            'message': 'Failed to get ledger entry',
            'data': None
        }), 500

@ledger_bp.route('/ledger', methods=['POST'])
@jwt_required()
def create_ledger_entry():
    """创建台账条目"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['province', 'project_name', 'date', 'location', 
                         'personnel', 'nature', 'specific_matters']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'code': 400,
                    'message': f'Field "{field}" is required'
                }), 400
        
        # 验证日期格式
        try:
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'code': 400,
                'message': 'Invalid date format, use YYYY-MM-DD'
            }), 400
        
        # 创建新条目
        new_entry = LedgerEntry(
            user_id=user_id,
            province=data['province'],
            project_name=data['project_name'],
            date=date_obj,
            location=data['location'],
            personnel=data['personnel'],
            nature=data['nature'],
            specific_matters=data['specific_matters'],
            follow_up_points=data.get('follow_up_points', '')
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        # 记录日志
        log_activity('INFO', f'Created ledger entry: {new_entry.id}', user_id=user_id)
        
        return jsonify({
            'code': 0,
            'message': 'Entry created successfully',
            'data': new_entry.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f'Create ledger entry error: {str(e)}')
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': 'Failed to create ledger entry',
            'data': None
        }), 500

@ledger_bp.route('/ledger/<int:entry_id>', methods=['PUT'])
@jwt_required()
def update_ledger_entry(entry_id):
    """更新台账条目"""
    try:
        user_id = get_jwt_identity()
        user_role = get_jwt().get('role', 'user')
        entry = LedgerEntry.query.get(entry_id)
        if not entry:
            return jsonify({
                'code': 404,
                'message': 'Entry not found'
            }), 404
        # 只有普通用户(user)才限制只能操作自己录入的
        if user_role == 'user' and entry.user_id != user_id:
            return jsonify({
                'code': 403,
                'message': 'Access denied'
            }), 403
        # power_user和admin可以编辑所有台账
        data = request.get_json()
        update_fields = ['province', 'project_name', 'date', 'location', 
                        'personnel', 'nature', 'specific_matters', 'follow_up_points']
        for field in update_fields:
            if field in data:
                if field == 'date':
                    try:
                        setattr(entry, field, datetime.strptime(data[field], '%Y-%m-%d').date())
                    except ValueError:
                        return jsonify({
                            'code': 400,
                            'message': 'Invalid date format, use YYYY-MM-DD'
                        }), 400
                else:
                    setattr(entry, field, data[field])
        entry.updated_at = datetime.utcnow()
        db.session.commit()
        log_activity('INFO', f'Updated ledger entry: {entry_id}', user_id=user_id)
        return jsonify({
            'code': 0,
            'message': 'Entry updated successfully',
            'data': entry.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f'Update ledger entry error: {str(e)}')
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': 'Failed to update ledger entry',
            'data': None
        }), 500

@ledger_bp.route('/ledger/<int:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_ledger_entry(entry_id):
    """删除台账条目"""
    try:
        user_id = get_jwt_identity()
        user_role = get_jwt().get('role', 'user')
        entry = LedgerEntry.query.get(entry_id)
        if not entry:
            return jsonify({
                'code': 404,
                'message': 'Entry not found'
            }), 404
        # 只有普通用户(user)才限制只能操作自己录入的
        if user_role == 'user' and entry.user_id != user_id:
            return jsonify({
                'code': 403,
                'message': 'Access denied'
            }), 403
        # power_user和admin可以删除所有台账
        db.session.delete(entry)
        db.session.commit()
        log_activity('INFO', f'Deleted ledger entry: {entry_id}', user_id=user_id)
        return jsonify({
            'code': 0,
            'message': 'Entry deleted successfully',
            'data': None
        }), 200
    except Exception as e:
        current_app.logger.error(f'Delete ledger entry error: {str(e)}')
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': 'Failed to delete ledger entry',
            'data': None
        }), 500

# ========== 新增的路由 ==========

@ledger_bp.route('/provinces', methods=['GET'])
@jwt_required()
def get_provinces():
    """获取省份列表"""
    try:
        # 获取所有省份，按名称排序
        provinces = Province.query.order_by(Province.name).all()
        province_list = [p.name for p in provinces]
        
        # 如果数据库中没有省份数据，返回默认列表
        if not province_list:
            province_list = [
                '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '其他', '另外'
            ]
            # 将默认省份保存到数据库
            for province_name in province_list:
                province = Province(name=province_name)
                db.session.add(province)
            db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': province_list
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get provinces error: {str(e)}')
        return jsonify({
            'code': 500,
            'message': 'Failed to get provinces',
            'data': None
        }), 500

@ledger_bp.route('/nature-options', methods=['GET'])
@jwt_required()
def get_nature_options():
    """获取性质选项列表"""
    try:
        nature_options = [
            '会议纪要',
            '工作安排',
            '问题反馈',
            '质量管理',
            '临时任务',
            '研讨交流',
            '资料交接',
            '人员对接',
            '常规项目工作',
            '其他'
        ]
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': nature_options
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get nature options error: {str(e)}')
        return jsonify({
            'code': 500,
            'message': 'Failed to get nature options',
            'data': None
        }), 500

@ledger_bp.route('/suggestions/project_items', methods=['GET'])
@jwt_required()
def get_project_suggestions():
    """获取项目名称搜索建议"""
    try:
        query_text = request.args.get('query', '').strip()
        
        if not query_text:
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': []
            }), 200
        
        # 搜索模式
        search_pattern = f'%{query_text}%'
        
        # 查询匹配的条目
        suggestions = LedgerEntry.query.filter(
            or_(
                LedgerEntry.province.ilike(search_pattern),
                LedgerEntry.project_name.ilike(search_pattern),
                LedgerEntry.specific_matters.ilike(search_pattern)
            )
        ).limit(20).all()
        
        # 提取唯一的建议值
        result_values = set()
        for entry in suggestions:
            if entry.province and query_text.lower() in entry.province.lower():
                result_values.add(entry.province)
            if entry.project_name and query_text.lower() in entry.project_name.lower():
                result_values.add(entry.project_name)
        
        # 格式化为前端期望的格式
        formatted_suggestions = [{"value": value} for value in result_values]
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': formatted_suggestions
        }), 200
        
    except Exception as e:
        current_app.logger.error(f'Get project suggestions error: {str(e)}')
        return jsonify({
            'code': 500,
            'message': 'Failed to get suggestions',
            'data': None
        }), 500
#!/usr/bin/env python
"""
Flask应用启动脚本
用于开发环境运行
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import click
from app import create_app, db
from app.models import User, Province, LedgerEntry, ActivityLog

# 创建应用实例
app = create_app()

# 配置日志
if not os.path.exists('logs'):
    os.mkdir('logs')

# 使用不同的日志文件名
log_file = 'logs/app.log'
if os.path.exists(log_file):
    # 如果文件存在，尝试删除它
    try:
        os.remove(log_file)
    except:
        pass

file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10240,
    backupCount=10,
    delay=True  # 延迟文件创建
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('应用启动')

# 打印配置信息（仅在开发环境）
if app.debug:
    print('JWT_SECRET_KEY:', app.config['JWT_SECRET_KEY'])
    
@app.shell_context_processor
def make_shell_context():
    """为Flask shell创建上下文"""
    return {
        'db': db,
        'User': User,
        'Province': Province,
        'LedgerEntry': LedgerEntry,
        'ActivityLog': ActivityLog
    }

@app.cli.command()
def init_db():
    """初始化数据库"""
    click.echo('Initializing database...')
    db.create_all()
    click.echo('Database initialized.')

@app.cli.command()
@click.argument('username')
@click.argument('password')
@click.option('--role', default='admin', help='User role (admin/power_user/user)')
def create_user(username, password, role):
    """创建新用户"""
    if User.query.filter_by(username=username).first():
        click.echo(f'Error: User {username} already exists.')
        return
    
    if len(password) < 8:
        click.echo('Error: Password must be at least 8 characters long.')
        return
    
    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    app.logger.info(f'Created new user: {username} with role {role}')
    click.echo(f'User {username} created successfully with role {role}.')

@app.cli.command()
@click.password_option()
def reset_db(password):
    """重置数据库（需要管理员密码）"""
    admin = User.query.filter_by(role='admin').first()
    if not admin or not admin.check_password(password):
        click.echo('Error: Invalid admin password.')
        return
        
    if click.confirm('This will delete all data. Are you sure?'):
        db.drop_all()
        db.create_all()
        app.logger.warning('Database reset by admin')
        click.echo('Database reset completed.')
    else:
        click.echo('Operation cancelled.')

@app.cli.command()
def seed_data():
    """填充测试数据"""
    click.echo('Seeding test data...')
    
    # 创建测试用户（使用更安全的密码）
    test_users = [
        ('test_user', 'Test@123456', 'user'),
        ('test_power', 'Power@123456', 'power_user'),
        ('test_admin', 'Admin@123456', 'admin')
    ]
    
    for username, password, role in test_users:
        if not User.query.filter_by(username=username).first():
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
    
    db.session.commit()
    app.logger.info('Test data seeded')
    click.echo('Test data seeded.')

if __name__ == '__main__':
    # 设置开发环境
    os.environ.setdefault('FLASK_ENV', 'development')
    
    # 打印所有路由
    print('Flask 路由列表:')
    for rule in app.url_map.iter_rules():
        print(f'{rule.methods} {rule}')
    
    # 运行应用
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.debug)


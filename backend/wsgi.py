"""
WSGI入口文件
用于生产环境部署（如Gunicorn）
"""
import os
from app import create_app

# 设置生产环境
os.environ.setdefault('FLASK_ENV', 'production')

# 创建应用实例
application = create_app('production')

if __name__ == '__main__':
    application.run()
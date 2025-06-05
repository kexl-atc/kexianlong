#!/usr/bin/env python
"""
系统健康检查脚本
检查后端服务、数据库、磁盘空间等
"""
import os
import sys
import psutil
import requests
import sqlite3
from datetime import datetime

# 配置
BACKEND_URL = 'http://localhost:5000/api'
DB_FILE = '../ledger.db'
LOG_FILE = '../logs/health_check.log'
DISK_THRESHOLD = 90  # 磁盘使用率阈值
MEMORY_THRESHOLD = 90  # 内存使用率阈值

def log(message, level='INFO'):
    """写入日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] [{level}] {message}"
    print(log_message)
    
    # 写入文件
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')

def check_backend_service():
    """检查后端服务状态"""
    try:
        response = requests.get(BACKEND_URL, timeout=5)
        if response.status_code == 404:  # API根路径通常返回404
            log("后端服务运行正常")
            return True
        else:
            log(f"后端服务异常，状态码: {response.status_code}", 'WARNING')
            return False
    except requests.exceptions.RequestException as e:
        log(f"后端服务连接失败: {e}", 'ERROR')
        return False

def check_database():
    """检查数据库状态"""
    try:
        # 检查数据库文件是否存在
        if not os.path.exists(DB_FILE):
            log("数据库文件不存在", 'ERROR')
            return False
        
        # 尝试连接数据库
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ledger_entries")
        entry_count = cursor.fetchone()[0]
        
        conn.close()
        
        log(f"数据库正常 - 用户数: {user_count}, 台账数: {entry_count}")
        return True
        
    except sqlite3.Error as e:
        log(f"数据库错误: {e}", 'ERROR')
        return False

def check_disk_space():
    """检查磁盘空间"""
    disk_usage = psutil.disk_usage('/')
    usage_percent = disk_usage.percent
    
    if usage_percent > DISK_THRESHOLD:
        log(f"磁盘空间不足: {usage_percent}% (阈值: {DISK_THRESHOLD}%)", 'WARNING')
        return False
    else:
        log(f"磁盘空间正常: {usage_percent}%")
        return True

def check_memory():
    """检查内存使用"""
    memory = psutil.virtual_memory()
    usage_percent = memory.percent
    
    if usage_percent > MEMORY_THRESHOLD:
        log(f"内存使用率过高: {usage_percent}% (阈值: {MEMORY_THRESHOLD}%)", 'WARNING')
        return False
    else:
        log(f"内存使用正常: {usage_percent}%")
        return True

def check_log_size():
    """检查日志文件大小"""
    log_dir = '../logs'
    total_size = 0
    
    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        if os.path.isfile(filepath):
            total_size += os.path.getsize(filepath)
    
    # 转换为MB
    size_mb = total_size / (1024 * 1024)
    
    if size_mb > 100:  # 超过100MB
        log(f"日志文件过大: {size_mb:.2f}MB", 'WARNING')
        return False
    else:
        log(f"日志文件大小正常: {size_mb:.2f}MB")
        return True

def main():
    """主函数"""
    log("=" * 50)
    log("开始系统健康检查")
    
    checks = [
        ("后端服务", check_backend_service),
        ("数据库", check_database),
        ("磁盘空间", check_disk_space),
        ("内存使用", check_memory),
        ("日志大小", check_log_size)
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        log(f"检查 {name}...")
        if not check_func():
            all_passed = False
    
    if all_passed:
        log("所有检查通过 ✓", 'INFO')
    else:
        log("部分检查失败，请检查日志", 'ERROR')
        sys.exit(1)
    
    log("健康检查完成")
    log("=" * 50)

if __name__ == '__main__':
    main()
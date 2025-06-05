#!/usr/bin/env python
import os
import sys
import oss2
from datetime import datetime, timedelta

# OSS配置
ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID')
ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET')
BUCKET_NAME = 'your-bucket-name'
ENDPOINT = 'oss-cn-hangzhou.aliyuncs.com'

def backup_to_oss():
    # 创建OSS连接
    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)
    
    # 备份文件路径
    db_file = '../ledger.db'
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    oss_key = f'ledger-backups/ledger_backup_{timestamp}.db'
    
    # 上传到OSS
    print(f'正在上传备份到OSS: {oss_key}')
    bucket.put_object_from_file(oss_key, db_file)
    print('上传成功！')
    
    # 清理30天前的备份
    prefix = 'ledger-backups/'
    for obj in oss2.ObjectIterator(bucket, prefix=prefix):
        obj_time = datetime.strptime(obj.last_modified, '%Y-%m-%dT%H:%M:%S.%fZ')
        if obj_time < datetime.now() - timedelta(days=30):
            bucket.delete_object(obj.key)
            print(f'已删除旧备份: {obj.key}')

if __name__ == '__main__':
    try:
        backup_to_oss()
    except Exception as e:
        print(f'备份失败: {e}')
        sys.exit(1)
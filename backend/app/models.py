from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    entries = db.relationship('LedgerEntry', backref='author', lazy='dynamic', 
                            cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LedgerEntry(db.Model):
    """台账条目模型"""
    __tablename__ = 'ledger_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    province = db.Column(db.String(100), nullable=False, index=True)
    project_name = db.Column(db.String(200), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    personnel = db.Column(db.String(500), nullable=False)
    nature = db.Column(db.String(100), nullable=False)
    specific_matters = db.Column(db.Text, nullable=False)
    follow_up_points = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LedgerEntry {self.id} - {self.project_name}>'
    
    def to_dict(self, include_author=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'province': self.province,
            'project_name': self.project_name,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'personnel': self.personnel,
            'nature': self.nature,
            'specific_matters': self.specific_matters,
            'follow_up_points': self.follow_up_points,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_author and self.author:
            data['recorder'] = self.author.username
        
        return data

class ActivityLog(db.Model):
    """活动日志模型"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    level = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<ActivityLog {self.timestamp} - {self.level}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'level': self.level,
            'message': self.message,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'details': self.details,
            'ip_address': self.ip_address
        }

class Province(db.Model):
    """省份模型"""
    __tablename__ = 'provinces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True)
    
    def __repr__(self):
        return f'<Province {self.name}>'
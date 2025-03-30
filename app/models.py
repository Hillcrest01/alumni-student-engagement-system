from datetime import datetime
from app import db
from flask_login import UserMixin

# Association table for user-interests relationship
user_interest = db.Table('user_interest',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User model with authentication fields"""
    __tablename__ = 'user'  # table name
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    password_changed = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    profile_complete = db.Column(db.Boolean, default=False)
    interests = db.relationship('Interest', secondary=user_interest,
                               backref=db.backref('users', lazy=True))

class Interest(db.Model):
    """Tag-like system for skills/specializations"""
    __tablename__ = 'interest'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(20))  # Optional grouping
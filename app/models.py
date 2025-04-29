from datetime import datetime
from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for user-interests relationship
user_interest = db.Table('user_interest',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'), primary_key=True)
)


#table for users
class User(UserMixin, db.Model):
    """User model with authentication fields"""
    __tablename__ = 'user'  
    
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
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    linkedin_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    current_position = db.Column(db.String(100))  # For alumni
    company = db.Column(db.String(100))           # For alumni
    graduation_year = db.Column(db.Integer)       # For students
    availability = db.Column(db.String(20), default='away')
    last_active = db.Column(db.DateTime)
    password_changed = db.Column(db.Boolean, default=False, nullable=False)
    
    def set_password(self, password):
        """Security-focused password hashing"""
        self.password_hash = generate_password_hash(
            password,
            method='pbkdf2:sha512',
            salt_length=16
        )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_changed = True

    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check admin privileges"""
        return self.role == 'admin'
    
    def is_student(self):
        """Check if the user is a student"""
        return self.role == 'student'


class Interest(db.Model):
    __tablename__ = 'interest'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(20))

    @classmethod
    def seed_default_interests(cls):
        default_interests = [
            'Frontend Development',
            'Backend Development',
            'Mobile Development',
            'Data Science',
            'Machine Learning',
            'Cybersecurity',
            'Cloud Computing',
            'DevOps',
            'UI/UX Design',
            'Project Management',
            'Networking',
            'Database Administration'
        ]
        
        for interest_name in default_interests:
            if not cls.query.filter_by(name=interest_name).first():
                new_interest = cls(name=interest_name)
                db.session.add(new_interest)
        db.session.commit()

    @property
    def interest_ids(self):
        return {i.id for i in self.interests}
    
    def get_unread_count(self):
        return Message.query.filter_by(receiver_id=self.id, read=False).count()
    



class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')


    @staticmethod
    def get_unread_count(user_id):
        return Message.query.filter_by(receiver_id=user_id, read=False).count()
    

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    image = db.Column(db.String(255))  # Stores image path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    creator = db.relationship('User', backref=db.backref('created_events', lazy=True))




class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(20), nullable=False)  # 'job' or 'internship'
    location = db.Column(db.String(100))
    application_link = db.Column(db.String(200))
    image = db.Column(db.String(255))  # Stores image path
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    creator = db.relationship('User', backref=db.backref('posted_jobs', lazy=True))


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)  # Optional for logged-in users
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    is_responded = db.Column(db.Boolean, default=False)
    response = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationship
    user = db.relationship('User', backref='contact_messages')

    def __repr__(self):
        return f'<ContactMessage {self.id} from {self.email}>'
    
class VerificationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending/approved/rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



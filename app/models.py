from app import db, app
from flask_login import UserMixin
from cryptography.fernet import Fernet
import base64
import hashlib

def get_cipher_suite():
    try:
        key = app.config['SECRET_KEY'].encode()
        digest = hashlib.sha256(key).digest()
        fernet_key = base64.urlsafe_b64encode(digest)
        return Fernet(fernet_key)
    except Exception:
        return None

def encrypt_value(value):
    if not value: return None
    cipher = get_cipher_suite()
    if not cipher: return value
    try:
        return cipher.encrypt(value.encode()).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return value

def decrypt_value(value):
    if not value: return None
    cipher = get_cipher_suite()
    if not cipher: return value
    try:
        return cipher.decrypt(value.encode()).decode()
    except Exception:
        return value

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    name = db.Column(db.String(100))
    picture = db.Column(db.String(200))
    
    # OAuth tokens (Stored encrypted)
    _access_token = db.Column('access_token', db.Text)
    _refresh_token = db.Column('refresh_token', db.Text)
    token_expiry = db.Column(db.DateTime)
    token_uri = db.Column(db.String(200))
    _client_id = db.Column('client_id', db.Text)
    _client_secret = db.Column('client_secret', db.Text)
    scopes = db.Column(db.String(500))
    
    courses = db.relationship('Course', backref='user', lazy='dynamic')

    @property
    def access_token(self):
        return decrypt_value(self._access_token)

    @access_token.setter
    def access_token(self, value):
        self._access_token = encrypt_value(value)

    @property
    def refresh_token(self):
        return decrypt_value(self._refresh_token)

    @refresh_token.setter
    def refresh_token(self, value):
        self._refresh_token = encrypt_value(value)

    @property
    def client_id(self):
        return decrypt_value(self._client_id)

    @client_id.setter
    def client_id(self, value):
        self._client_id = encrypt_value(value)

    @property
    def client_secret(self):
        return decrypt_value(self._client_secret)

    @client_secret.setter
    def client_secret(self, value):
        self._client_secret = encrypt_value(value)

    def __repr__(self):
        return '<User {}>'.format(self.email)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    google_course_id = db.Column(db.String(100), nullable=False)
    
    # Local overrides
    custom_name = db.Column(db.String(200))
    custom_section = db.Column(db.String(200))
    custom_code = db.Column(db.String(100)) # For "Class Code" rename
    custom_banner = db.Column(db.String(500))
    custom_icon = db.Column(db.String(500))
    
    # Teacher info
    cached_teacher_name = db.Column(db.String(100))
    custom_teacher_name = db.Column(db.String(100))
    
    is_archived = db.Column(db.Boolean, default=False) # User archived
    is_pinned = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)

    user_tags = db.relationship('UserTag', secondary='course_tags_map', lazy='subquery',
        backref=db.backref('courses', lazy=True))

    __table_args__ = (db.UniqueConstraint('user_id', 'google_course_id', name='_user_course_uc'),)

    def __repr__(self):
        return '<Course {}>'.format(self.google_course_id)

class CourseTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='blue')
    
    course = db.relationship('Course', backref=db.backref('tags', lazy=True, cascade='all, delete-orphan'))
    
    __table_args__ = (db.UniqueConstraint('course_id', 'name', name='_course_tag_uc'),)

class ItemTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('course_tag.id'), nullable=False)
    google_item_id = db.Column(db.String(100), nullable=False)
    
    tag = db.relationship('CourseTag', backref=db.backref('item_assignments', lazy=True, cascade='all, delete-orphan'))
    
    __table_args__ = (db.UniqueConstraint('tag_id', 'google_item_id', name='_tag_item_uc'),)

class MutedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    google_item_id = db.Column(db.String(100), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'google_item_id', name='_user_item_mute_uc'),)

# Association table for Course <-> UserTag
course_tags_map = db.Table('course_tags_map',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('user_tag_id', db.Integer, db.ForeignKey('user_tag.id'), primary_key=True)
)

class UserTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='_user_tag_name_uc'),)

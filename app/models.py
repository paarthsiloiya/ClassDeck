from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    name = db.Column(db.String(100))
    picture = db.Column(db.String(200))
    
    # OAuth tokens
    access_token = db.Column(db.String(200))
    refresh_token = db.Column(db.String(200))
    token_expiry = db.Column(db.DateTime)
    token_uri = db.Column(db.String(200))
    client_id = db.Column(db.String(200))
    client_secret = db.Column(db.String(200))
    scopes = db.Column(db.String(500))
    
    courses = db.relationship('Course', backref='user', lazy='dynamic')

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
    
    is_archived = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)

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

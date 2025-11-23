from app import db, app
from flask_login import UserMixin
from cryptography.fernet import Fernet
import base64
import hashlib

def get_cipher_suite():
    """
    Generates a Fernet cipher suite based on the application's SECRET_KEY.

    Returns:
        cryptography.fernet.Fernet: A Fernet instance for encryption/decryption.
        None: If an error occurs during key generation.
    """
    try:
        key = app.config['SECRET_KEY'].encode()
        digest = hashlib.sha256(key).digest()
        fernet_key = base64.urlsafe_b64encode(digest)
        return Fernet(fernet_key)
    except Exception:
        return None

def encrypt_value(value):
    """
    Encrypts a string value using the application's cipher suite.

    Args:
        value (str): The string to encrypt.

    Returns:
        str: The encrypted string, or the original value if encryption fails or value is None.
    """
    if not value: return None
    cipher = get_cipher_suite()
    if not cipher: return value
    try:
        return cipher.encrypt(value.encode()).decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return value

def decrypt_value(value):
    """
    Decrypts an encrypted string value using the application's cipher suite.

    Args:
        value (str): The encrypted string to decrypt.

    Returns:
        str: The decrypted string, or the original value if decryption fails or value is None.
    """
    if not value: return None
    cipher = get_cipher_suite()
    if not cipher: return value
    try:
        return cipher.decrypt(value.encode()).decode()
    except Exception:
        return value

class User(UserMixin, db.Model):
    """
    Represents a user of the application.

    Attributes:
        id (int): Primary key.
        google_id (str): Unique Google ID of the user.
        email (str): User's email address.
        name (str): User's full name.
        picture (str): URL to the user's profile picture.
        _access_token (str): Encrypted OAuth access token.
        _refresh_token (str): Encrypted OAuth refresh token.
        token_expiry (datetime): Expiration time of the access token.
        token_uri (str): URI for token refreshing.
        _client_id (str): Encrypted OAuth client ID.
        _client_secret (str): Encrypted OAuth client secret.
        scopes (str): Comma-separated list of granted OAuth scopes.
        courses (dynamic): Relationship to the user's courses.
    """
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
        """Decrypted OAuth access token."""
        return decrypt_value(self._access_token)

    @access_token.setter
    def access_token(self, value):
        self._access_token = encrypt_value(value)

    @property
    def refresh_token(self):
        """Decrypted OAuth refresh token."""
        return decrypt_value(self._refresh_token)

    @refresh_token.setter
    def refresh_token(self, value):
        self._refresh_token = encrypt_value(value)

    @property
    def client_id(self):
        """Decrypted OAuth client ID."""
        return decrypt_value(self._client_id)

    @client_id.setter
    def client_id(self, value):
        self._client_id = encrypt_value(value)

    @property
    def client_secret(self):
        """Decrypted OAuth client secret."""
        return decrypt_value(self._client_secret)

    @client_secret.setter
    def client_secret(self, value):
        self._client_secret = encrypt_value(value)

    def __repr__(self):
        return '<User {}>'.format(self.email)

class Course(db.Model):
    """
    Represents a course (class) in the application.
    Stores local overrides and settings for a Google Classroom course.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the User.
        google_course_id (str): ID of the course in Google Classroom.
        custom_name (str): User-defined name for the course.
        custom_section (str): User-defined section for the course.
        custom_code (str): User-defined class code (enrollment code).
        custom_banner (str): URL to a custom banner image.
        custom_icon (str): URL to a custom icon.
        cached_teacher_name (str): Cached name of the teacher from Google.
        custom_teacher_name (str): User-defined teacher name.
        is_archived (bool): Whether the course is archived locally.
        is_pinned (bool): Whether the course is pinned (not currently used).
        display_order (int): Order index for display sorting.
        user_tags (list): List of UserTags associated with this course.
    """
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
    """
    Represents a tag specific to a course, used for tagging items within that course.
    (Note: This seems to be a legacy or specific-use tag, distinct from UserTag).

    Attributes:
        id (int): Primary key.
        course_id (int): Foreign key to the Course.
        name (str): Name of the tag.
        color (str): Color code for the tag.
    """
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='blue')
    
    course = db.relationship('Course', backref=db.backref('tags', lazy=True, cascade='all, delete-orphan'))
    
    __table_args__ = (db.UniqueConstraint('course_id', 'name', name='_course_tag_uc'),)

class ItemTag(db.Model):
    """
    Associates a CourseTag with a specific item (assignment/material) in Google Classroom.

    Attributes:
        id (int): Primary key.
        tag_id (int): Foreign key to the CourseTag.
        google_item_id (str): ID of the item in Google Classroom.
    """
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('course_tag.id'), nullable=False)
    google_item_id = db.Column(db.String(100), nullable=False)
    
    tag = db.relationship('CourseTag', backref=db.backref('item_assignments', lazy=True, cascade='all, delete-orphan'))
    
    __table_args__ = (db.UniqueConstraint('tag_id', 'google_item_id', name='_tag_item_uc'),)

class MutedItem(db.Model):
    """
    Represents an item (assignment) that a user has muted/hidden from the 'Missing Assignments' list.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the User.
        google_item_id (str): ID of the item in Google Classroom.
    """
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
    """
    Represents a global tag created by a user to organize their courses.

    Attributes:
        id (int): Primary key.
        user_id (int): Foreign key to the User.
        name (str): Name of the tag.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='_user_tag_name_uc'),)

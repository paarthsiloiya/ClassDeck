import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration class for the Flask application.
    Reads settings from environment variables or uses default values.

    Attributes:
        SECRET_KEY (str): Secret key for session management and encryption.
        SQLALCHEMY_DATABASE_URI (str): Database connection URI.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable SQLAlchemy modification tracking.
        OAUTHLIB_INSECURE_TRANSPORT (str): Allow OAuth over HTTP (dev only).
        GOOGLE_CLIENT_SECRETS_FILE (str): Path to the Google OAuth client secrets file.
        GOOGLE_SCOPES (list): List of required Google API scopes.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OAuth 2.0 settings
    OAUTHLIB_INSECURE_TRANSPORT = '1' # For local development only
    GOOGLE_CLIENT_SECRETS_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'client_secret.json')
    GOOGLE_SCOPES = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.announcements.readonly',
        'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
        'https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly',
        'https://www.googleapis.com/auth/classroom.rosters.readonly',
        'https://www.googleapis.com/auth/calendar',
        'openid'
    ]

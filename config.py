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
    
    # Database URL fix for Vercel/Heroku (postgres -> postgresql)
    # Vercel Postgres uses POSTGRES_URL by default
    uri = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    if uri and uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = uri or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OAuth 2.0 settings
    # Only allow insecure transport if explicitly set (local dev)
    OAUTHLIB_INSECURE_TRANSPORT = os.environ.get('OAUTHLIB_INSECURE_TRANSPORT')

    # Handle Google Client Secrets from Env (for Vercel) or File
    google_secrets_json = os.environ.get('GOOGLE_CLIENT_SECRETS_JSON')
    if google_secrets_json:
        import tempfile
        # Create a temp file in /tmp (Vercel writable)
        # We use a fixed path in /tmp to avoid creating multiple files on reloads if possible, 
        # but NamedTemporaryFile is safer.
        # However, on Vercel, /tmp is ephemeral per request/instance.
        try:
            temp_secrets = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json', dir='/tmp')
            temp_secrets.write(google_secrets_json)
            temp_secrets.close()
            GOOGLE_CLIENT_SECRETS_FILE = temp_secrets.name
        except Exception as e:
            print(f"Error creating temp secrets file: {e}")
            GOOGLE_CLIENT_SECRETS_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'client_secret.json')
    else:
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

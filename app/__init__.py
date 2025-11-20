from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

# Allow OAuth over HTTP for local development
if app.config.get('OAUTHLIB_INSECURE_TRANSPORT'):
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = app.config['OAUTHLIB_INSECURE_TRANSPORT']

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models

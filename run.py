"""
Entry point for running the ClassDeck application.
Starts the Flask development server.
"""
import os

# Allow OAuth over HTTP for local testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from app import app

if __name__ == '__main__':
    app.run(debug=True)

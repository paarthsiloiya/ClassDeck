"""
Entry point for running the ClassDeck application.
Starts the Flask development server.
"""
from app import app

if __name__ == '__main__':
    app.run(debug=True)

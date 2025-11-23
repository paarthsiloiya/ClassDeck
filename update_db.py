"""
Database update script.
Creates any missing tables based on the current models without dropping existing data.
Useful for adding new tables (like MutedItem) to an existing database.
"""
from app import app, db
from app.models import MutedItem

with app.app_context():
    db.create_all()
    print("Database tables updated.")

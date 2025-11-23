"""
Database initialization script.
Drops all existing tables and recreates them based on the current models.
WARNING: This will delete all data in the database.
"""
from app import app, db
from app.models import User, Course, CourseTag, ItemTag

with app.app_context():
    db.drop_all() # Drop existing tables to handle schema changes
    db.create_all()
    print("Database initialized with new schema!")

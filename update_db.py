from app import app, db
from app.models import MutedItem

with app.app_context():
    db.create_all()
    print("Database tables updated.")

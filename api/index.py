import sys
import os

# Add the parent directory to sys.path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# This is required for Vercel to find the Flask app instance
# The variable name 'app' here must match the Flask instance

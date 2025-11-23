# This file is needed for Render deployment
# It imports the Flask app from the Backend directory

import sys
import os

# Add the Backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

# Import the app from Backend/app.py
from Backend.app import app, db

# Initialize the database
if 'MONGO_URI' in os.environ:
    db.init_app(app)

if __name__ == "__main__":
    # This is just a fallback for local development
    # Render will use gunicorn command: gunicorn --bind 0.0.0.0:$PORT app:app
    app.run()
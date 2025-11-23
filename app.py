import os
import sys

# Add the Backend directory to the Python path to avoid circular imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

# Import the app from the Backend directory
from Backend.app import app

if __name__ == "__main__":
    # Use the PORT environment variable provided by Render, default to 3001 for local development
    port = int(os.environ.get("PORT", 3001))
    print(f"Starting server on port {port}")
    
    app.run(host="0.0.0.0", port=port, debug=False)
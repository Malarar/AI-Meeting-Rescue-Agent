"""
Quick start script for AI Meeting Rescue Agent
"""
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("AI Meeting Rescue Agent")
    print("=" * 60)
    print(f"Starting server on http://{app.config['HOST']}:{app.config['PORT']}")
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )

# Made with Bob

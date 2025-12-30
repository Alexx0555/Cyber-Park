import sys
import os
from waitress import serve

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    # Use Waitress for production deployment
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Waitress server on 0.0.0.0:{port}")
    serve(app, host="0.0.0.0", port=port)
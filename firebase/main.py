import os
import sys
from firebase_functions import https_fn
from firebase_admin import initialize_app

# Add project root to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Initialize Firebase app
initialize_app()

# Import the FastAPI app
from app.main import app as fastapi_app

@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    """
    Main Firebase Cloud Function entry point for the FastAPI app.
    Routes all incoming HTTP requests to the FastAPI application.
    """
    # Convert Firebase request to ASGI format and process with FastAPI
    return https_fn.AsgiResponse(fastapi_app, req) 
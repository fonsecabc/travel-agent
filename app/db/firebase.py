import os
import firebase_admin
from firebase_admin import credentials, firestore
import logging

logger = logging.getLogger("travel-agent")

def initialize_firebase():
    """Initialize Firebase application."""
    try:
        # First look for credentials file in the root directory
        root_cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'firebase-credentials.json')
        
        if os.path.exists(root_cred_path):
            cred = credentials.Certificate(root_cred_path)
            app = firebase_admin.initialize_app(cred)
            logger.info(f"Firebase initialized successfully using credentials file at: {root_cred_path}")
            return app
        
        # Then check for credentials path in environment
        cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
        
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            app = firebase_admin.initialize_app(cred)
            logger.info(f"Firebase initialized successfully using credentials file at: {cred_path}")
            return app
            
        logger.error("No Firebase credentials available. Please place a 'firebase-credentials.json' file in the project root.")
        return None
    except Exception as e:
        logger.error(f"Firebase initialization failed: {str(e)}")
        return None

def get_db():
    """Get Firestore database client instance."""
    try:
        if not firebase_admin._apps:
            initialize_firebase()
        
        # Get regular Firestore client
        db = firestore.client()
        
        # Set the custom database name using the internal attribute
        # This is a workaround until the Firebase Admin SDK officially supports
        # specifying database names in the Python client
        project_id = firebase_admin.get_app().project_id
        db._database_string_internal = f"projects/{project_id}/databases/travel-agent"
        logger.info(f"Using Firestore database: travel-agent in project {project_id}")
        
        return db
    except Exception as e:
        logger.error(f"Failed to get Firestore client: {str(e)}")
        return None

# Collections
USERS_COLLECTION = "users"
PREFERENCES_COLLECTION = "preferences"
TRIPS_COLLECTION = "trips"
SEARCH_HISTORY_COLLECTION = "search_history"
DEALS_COLLECTION = "deals"
NOTIFICATIONS_COLLECTION = "notifications" 
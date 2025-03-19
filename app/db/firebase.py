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
            return app
  
        return None
    except Exception as e:
        logger.error(f"Firebase initialization failed: {str(e)}")
        return None

def get_db():
    global _in_memory_db
    """Get Firestore database client instance."""
    try:
        if not firebase_admin._apps:
            app = initialize_firebase()
            if app is None:
                if _in_memory_db is None:
                    _in_memory_db = InMemoryFirestore()
                return _in_memory_db
        
        # Get regular Firestore client
        db = firestore.client()
        
        # Set the custom database name using the internal attribute
        # This is a workaround until the Firebase Admin SDK officially supports
        # specifying database names in the Python client
        project_id = firebase_admin.get_app().project_id
        db._database_string_internal = f"projects/{project_id}/databases/travel-agent"
        
        return db
    except Exception as e:
        logger.error(f"Failed to get Firestore client: {str(e)}")
        if _in_memory_db is None:
            _in_memory_db = InMemoryFirestore()
        return _in_memory_db

# Collections
USERS_COLLECTION = "users"
PREFERENCES_COLLECTION = "preferences"
TRIPS_COLLECTION = "trips"
SEARCH_HISTORY_COLLECTION = "search_history"
DEALS_COLLECTION = "deals"
NOTIFICATIONS_COLLECTION = "notifications"

# Begin in-memory Firestore mock implementation
class InMemoryFirestore:
    def __init__(self):
        self._data = {}

    def collection(self, collection_name):
        if collection_name not in self._data:
            self._data[collection_name] = {}
        return InMemoryCollection(self._data[collection_name])

class InMemoryCollection:
    def __init__(self, data):
        self._data = data

    def document(self, doc_id):
        if doc_id not in self._data:
            self._data[doc_id] = InMemoryDocument(doc_id)
        return self._data[doc_id]

    def stream(self):
        return list(self._data.values())

    def where(self, field, op, value):
        if op != "==":
            raise NotImplementedError("Only '==' operator is supported in the in-memory mock")
        results = []
        for doc in self._data.values():
            if doc.data.get(field) == value:
                results.append(doc)
        return InMemoryQuery(results)

class InMemoryDocument:
    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.data = {}
        self.subcollections = {}

    def set(self, data):
        self.data = data.copy()

    def get(self):
        self.exists = bool(self.data)
        return self

    def to_dict(self):
        return self.data

    def update(self, data):
        self.data.update(data)

    def collection(self, collection_name):
        if collection_name not in self.subcollections:
            self.subcollections[collection_name] = {}
        return InMemoryCollection(self.subcollections[collection_name])

class InMemoryQuery:
    def __init__(self, docs):
        self.docs = docs

    def limit(self, count):
        self.docs = self.docs[:count]
        return self

    def stream(self):
        return self.docs
# End in-memory Firestore mock implementation 

# Persistent instance of in-memory Firestore mock
_in_memory_db = None 
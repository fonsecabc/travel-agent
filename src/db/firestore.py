import os
import logging

import firebase_admin
from firebase_admin import credentials, firestore
from .firebase_mock import FirebaseMock

class Firestore:
    def __init__(self):
        self.db = None
        root_cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials.json')
        
        if os.path.exists(root_cred_path):
            try:
                cred = credentials.Certificate(root_cred_path)
                app = firebase_admin.initialize_app(cred)

                db = firestore.client(app=app)

                project_id = firebase_admin.get_app().project_id
                db._database_string_internal = f"projects/{project_id}/databases/travel-agent"

                self.db = db
                logging.info("Firestore initialized with real client")
            except Exception as e:
                logging.error(f"Failed to initialize Firestore: {str(e)}")
                self.db = FirebaseMock()
        else:
            logging.info("Credentials file not found, using mock Firestore")
            self.db = FirebaseMock()

    @property
    def client(self):
        return self.db

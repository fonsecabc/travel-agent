import os

import firebase_admin
from firebase_admin import credentials, firestore

class Firestore:
    def __init__(self):
        root_cred_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials.json')
        
        if os.path.exists(root_cred_path):
            cred = credentials.Certificate(root_cred_path)
            app = firebase_admin.initialize_app(cred)

            db = firestore.client(app=app)

            project_id = firebase_admin.get_app().project_id
            db._database_string_internal = f"projects/{project_id}/databases/travel-agent"

            self.db = db

    @property
    def client(self):
        return self.db

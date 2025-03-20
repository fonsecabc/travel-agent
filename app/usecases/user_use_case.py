from app.models import User
from app.db import Firestore

class UserUseCase:
    """
    Use case for user operations.
    """
    def __init__(self, db: Firestore):
        """
        Initialize the user use case.
        """
        self.db = db

    async def get_user(self, phone_number: str) -> User:
        """
        Get a user by phone number.
        """
        doc = self.db.collection("users").document(phone_number).get()
        if not doc.exists:
            user = User(phone_number=phone_number)
            self.db.collection("users").document(phone_number).set(user.model_dump())
            return user
        return User.model_validate(doc)
    
    async def save_user(self, user: User) -> User:
        """
        Save a user.
        """
        self.db.collection("users").document(user.phone_number).set(user.model_dump())
        return user

from typing import List
from app.models.chat import Chat, Message
from app.db import Firestore

class ChatUseCase:
    """
    Use case for chat operations.
    """
    def __init__(self, db: Firestore):
        """
        Initialize the chat use case.
        """
        self.db = db

    def get_chat(self, user_id: str) -> Chat:
        """
        Get a chat by user ID.
        """
        docs = self.db.collection("chats").where("user_id", "==", user_id).limit(1).get()
        if not docs[0]:
            chat = Chat(user_id=user_id)
            self.db.collection("chats").document(chat.id).set(chat.model_dump())
            return chat
        
        return Chat.model_validate(docs[0])

    def add_message(self, user_id: str, role: str, content: str) -> Message:
        """
        Add a message to the chat.
        """
        chat = self.get_chat(user_id=user_id)

        message = Message(chat_id=chat.id, role=role, content=content)
        self.db.collection("chats").document(chat.id).collection("messages").add(message.model_dump())
        
        return message
    
    def get_messages(self, chat_id: str) -> List[Message]:
        """
        Get all messages for a chat.
        """
        docs = self.db.collection("chats").document(chat_id).collection("messages").get()
        return [Message.model_validate(doc) for doc in docs]
from typing import List, Dict, Any

from src.db import Firestore
from src.models import Chat, Message

class ChatUseCase:
    """
    Use case for chat operations.
    """
    def __init__(self, db: Firestore):
        """
        Initialize the chat use case.
        """
        self.db = db

    async def get_chat(self, user_id: str) -> Chat:
        """
        Get a chat by user ID.
        """
        docs = self.db.client.collection("chats").where(filter=("user_id", "==", user_id)).limit(1).get()
        if not docs or len(docs) == 0:
            chat = Chat(user_id=user_id)
            self.db.client.collection("chats").document(chat.id).set(chat.model_dump())
            return chat
        
        return Chat.model_validate(docs[0].to_dict())

    async def add_message(self, user_id: str, role: str, content: str) -> Message:
        """
        Add a message to the chat.
        """
        chat = await self.get_chat(user_id=user_id)

        message = Message(chat_id=chat.id, role=role, content=content)
        self.db.client.collection("chats").document(chat.id).collection("messages").add(message.model_dump())
        
        return message
    
    async def get_messages(self, chat_id: str) -> List[Message]:
        """
        Get all messages for a chat.
        """
        docs = self.db.client.collection("chats").document(chat_id).collection("messages").order_by("created_at").get()
        return [Message.model_validate(doc.to_dict()) for doc in docs]
    
    async def get_chat_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get formatted chat history for a user to be used in agent context.
        """
        chat = await self.get_chat(user_id=user_id)
        messages = await self.get_messages(chat_id=chat.id)
        
        # Format messages for the agent
        formatted_history = []
        for message in messages:
            formatted_history.append({
                "role": message.role,
                "content": message.content
            })
        
        return formatted_history
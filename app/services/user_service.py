from app.db.firebase import get_db, USERS_COLLECTION, PREFERENCES_COLLECTION
from app.models.user import User, UserPreferences, SearchHistory, FlightDeal, TravelPreference, Conversation, Message
from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime

logger = logging.getLogger("travel-agent")

# Collection names
SEARCH_HISTORY_COLLECTION = "search_history"
FLIGHT_DEALS_COLLECTION = "flight_deals"
CONVERSATIONS_COLLECTION = "conversations"

async def create_user(user_id: str, phone_number: str, name: Optional[str] = None, email: Optional[str] = None) -> User:
    """Create a new user in the database."""
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        now = datetime.now()
        
        # Create user object
        user = User(
            id=user_id,
            phone_number=phone_number,
            name=name,
            email=email,
            created_at=now,
            updated_at=now
        )
        
        # Save to Firestore
        db.collection(USERS_COLLECTION).document(user_id).set(user.dict())
        
        logger.info(f"Created user with ID: {user_id}")
        return user
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise

async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by ID."""
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Get user from Firestore
        user_doc = db.collection(USERS_COLLECTION).document(user_id).get()
        
        if not user_doc.exists:
            logger.info(f"User not found with ID: {user_id}")
            return None
            
        user_data = user_doc.to_dict()
        
        # Get preferences if they exist
        user_preferences = None
        preferences_ref = db.collection(USERS_COLLECTION).document(user_id).collection(PREFERENCES_COLLECTION).document("preferences")
        preferences_doc = preferences_ref.get()
        
        if preferences_doc.exists:
            user_preferences = UserPreferences(**preferences_doc.to_dict())
            
        # Create User object
        user = User(**user_data)
        user.preferences = user_preferences
        
        return user
        
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        raise

async def get_user_by_phone(phone_number: str) -> Optional[User]:
    """Get a user by phone number."""
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Query user by phone number
        users_ref = db.collection(USERS_COLLECTION).where("phone_number", "==", phone_number).limit(1)
        users = users_ref.stream()
        
        user_doc = next(users, None)
        if not user_doc:
            logger.info(f"User not found with phone number: {phone_number}")
            return None
            
        user_data = user_doc.to_dict()
        user_id = user_doc.id
        
        # Get preferences if they exist
        user_preferences = None
        preferences_ref = db.collection(USERS_COLLECTION).document(user_id).collection(PREFERENCES_COLLECTION).document("preferences")
        preferences_doc = preferences_ref.get()
        
        if preferences_doc.exists:
            user_preferences = UserPreferences(**preferences_doc.to_dict())
            
        # Create User object
        user = User(**user_data)
        user.preferences = user_preferences
        user.id = user_id  # Ensure ID is set correctly
        
        return user
        
    except Exception as e:
        logger.error(f"Error getting user by phone: {str(e)}")
        raise

async def update_user_preferences(user_id: str, preferences: UserPreferences) -> User:
    """Update user preferences."""
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Save preferences to Firestore
        db.collection(USERS_COLLECTION).document(user_id).collection(PREFERENCES_COLLECTION).document("preferences").set(
            preferences.dict()
        )
        
        # Update user's updated_at timestamp
        db.collection(USERS_COLLECTION).document(user_id).update({
            "updated_at": datetime.now()
        })
        
        # Get updated user
        return await get_user_by_id(user_id)
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        raise

async def get_all_users() -> List[User]:
    """Get all users."""
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Get all users from Firestore
        users_ref = db.collection(USERS_COLLECTION).stream()
        
        users = []
        for user_doc in users_ref:
            user_data = user_doc.to_dict()
            user_id = user_doc.id
            
            # Get preferences if they exist
            user_preferences = None
            preferences_ref = db.collection(USERS_COLLECTION).document(user_id).collection(PREFERENCES_COLLECTION).document("preferences")
            preferences_doc = preferences_ref.get()
            
            if preferences_doc.exists:
                user_preferences = UserPreferences(**preferences_doc.to_dict())
                
            # Create User object
            user = User(**user_data)
            user.preferences = user_preferences
            user.id = user_id  # Ensure ID is set correctly
            
            users.append(user)
            
        return users
        
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        raise

async def save_search_history(search_history: SearchHistory) -> str:
    """Save a search history record."""
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Generate ID if not provided
        if not search_history.id:
            search_history.id = str(uuid.uuid4())
            
        # Save to Firestore
        db.collection(USERS_COLLECTION).document(search_history.user_id).collection(SEARCH_HISTORY_COLLECTION).document(search_history.id).set(
            search_history.dict()
        )
        
        logger.info(f"Saved search history with ID: {search_history.id}")
        return search_history.id
        
    except Exception as e:
        logger.error(f"Error saving search history: {str(e)}")
        raise

async def get_search_history(user_id: str, limit: int = 10) -> List[SearchHistory]:
    """Get search history for a user."""
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Get search history from Firestore
        history_ref = db.collection(USERS_COLLECTION).document(user_id).collection(SEARCH_HISTORY_COLLECTION).order_by(
            "search_timestamp", direction="DESCENDING"
        ).limit(limit)
        
        history_docs = history_ref.stream()
        
        search_history = []
        for doc in history_docs:
            history_data = doc.to_dict()
            search_history.append(SearchHistory(**history_data))
            
        return search_history
        
    except Exception as e:
        logger.error(f"Error getting search history: {str(e)}")
        raise

async def save_flight_deal(flight_deal: FlightDeal) -> str:
    """Save a flight deal."""
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Generate ID if not provided
        if not flight_deal.id:
            flight_deal.id = str(uuid.uuid4())
            
        # Save to Firestore
        db.collection(USERS_COLLECTION).document(flight_deal.user_id).collection(FLIGHT_DEALS_COLLECTION).document(flight_deal.id).set(
            flight_deal.dict()
        )
        
        logger.info(f"Saved flight deal with ID: {flight_deal.id}")
        return flight_deal.id
        
    except Exception as e:
        logger.error(f"Error saving flight deal: {str(e)}")
        raise

async def get_flight_deals(user_id: str, limit: int = 10) -> List[FlightDeal]:
    """Get flight deals for a user."""
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Get flight deals from Firestore
        deals_ref = db.collection(USERS_COLLECTION).document(user_id).collection(FLIGHT_DEALS_COLLECTION).order_by(
            "found_at", direction="DESCENDING"
        ).limit(limit)
        
        deal_docs = deals_ref.stream()
        
        flight_deals = []
        for doc in deal_docs:
            deal_data = doc.to_dict()
            flight_deals.append(FlightDeal(**deal_data))
            
        return flight_deals
        
    except Exception as e:
        logger.error(f"Error getting flight deals: {str(e)}")
        raise

async def get_user_conversation(user_id: str) -> Optional[Conversation]:
    """
    Get a user's conversation history.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        The user's conversation or None if not found
    """
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Check if a conversation already exists for this user
        query = db.collection(CONVERSATIONS_COLLECTION).where("user_id", "==", user_id).limit(1)
        conversations = query.stream()
        
        for doc in conversations:
            # Return the first conversation found
            conversation_data = doc.to_dict()
            return Conversation.from_dict(conversation_data)
        
        # No existing conversation found, create a new one
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(
            id=conversation_id,
            user_id=user_id
        )
        
        # Save the new conversation
        await save_conversation(conversation)
        
        return conversation
    
    except Exception as e:
        logger.error(f"Error getting user conversation: {str(e)}")
        return None

async def save_conversation(conversation: Conversation) -> str:
    """
    Save a conversation to the database.
    
    Args:
        conversation: The conversation to save
        
    Returns:
        The ID of the saved conversation
    """
    try:
        db = get_db()
        if not db:
            raise Exception("Database connection failed")
            
        # Update timestamps
        conversation.updated_at = datetime.now()
        
        # Save to Firestore
        db.collection(CONVERSATIONS_COLLECTION).document(conversation.id).set(conversation.dict())
        
        logger.info(f"Saved conversation with ID: {conversation.id}")
        return conversation.id
        
    except Exception as e:
        logger.error(f"Error saving conversation: {str(e)}")
        raise

async def add_message_to_conversation(user_id: str, role: str, content: str) -> Optional[Message]:
    """
    Add a message to a user's conversation.
    
    Args:
        user_id: The ID of the user
        role: The role of the message sender ('user' or 'assistant')
        content: The content of the message
        
    Returns:
        The added message or None if there was an error
    """
    try:
        # Get the user's conversation
        conversation = await get_user_conversation(user_id)
        
        if not conversation:
            logger.error(f"No conversation found for user {user_id}")
            return None
            
        # Add the message
        message = conversation.add_message(role, content)
        
        # Save the updated conversation
        await save_conversation(conversation)
        
        return message
        
    except Exception as e:
        logger.error(f"Error adding message to conversation: {str(e)}")
        return None 
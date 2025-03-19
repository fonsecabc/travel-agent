import logging
from app.services.user_service import get_user_by_phone, create_user
from app.services.whatsapp_service import send_whatsapp_message
from app.models.user import UserCreate
from typing import Dict, Any, Optional
import os

logger = logging.getLogger("travel-agent")

async def handle_incoming_message(sender_phone: str, message_text: str) -> Dict[str, Any]:
    """
    Process an incoming WhatsApp message using CrewAI.
    
    This is the main entry point for all incoming messages. It:
    1. Creates or retrieves the user
    2. Processes the message through CrewAI
    3. Returns a response to be sent back to the user
    """
    try:
        # Get or create user
        user = await get_or_create_user(sender_phone)
        
        # In a future version, this will integrate with CrewAI
        # For now, we'll return a simple response for testing
        response = await process_message_with_crew_ai(user.id, message_text)
        
        # Send response back to the user (in a real implementation)
        # await send_whatsapp_message(sender_phone, response)
        
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        logger.error(f"Error handling incoming message: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

async def get_or_create_user(phone_number: str):
    """Get an existing user or create a new one."""
    try:
        # Try to find user
        user = await get_user_by_phone(phone_number)
        
        if user:
            return user
            
        # Create new user if not found
        user_create = UserCreate(phone_number=phone_number)
        user = await create_user(user_create)
        
        return user
    except Exception as e:
        logger.error(f"Error in get_or_create_user: {str(e)}")
        raise

async def process_message_with_crew_ai(user_id: str, message_text: str) -> str:
    """
    Process a message using CrewAI.
    
    This is a placeholder that will be replaced with actual CrewAI integration.
    """
    # TODO: Implement CrewAI integration
    # For now, return a simple response for testing
    
    # Check for common patterns to simulate basic conversation
    message_lower = message_text.lower()
    
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! I'm your AI Travel Assistant. I can help you find great flight deals. What destination are you interested in?"
        
    if "help" in message_lower:
        return ("I can help you find flight deals based on your preferences. "
                "Tell me about destinations you're interested in, your home airport, "
                "when you want to travel, and your budget.")
                
    if any(word in message_lower for word in ["flight", "ticket", "travel", "trip"]):
        return ("I'd be happy to help you find flights! "
                "To get started, please tell me:\n"
                "1. Your home airport\n"
                "2. Where you want to go\n"
                "3. When you want to travel\n"
                "4. Your budget (optional)")
                
    # Default response
    return ("Thanks for your message! I'm your AI Travel Assistant. "
            "I'm still learning, but I can help you find great flight deals. "
            "Try asking me about flights to a specific destination, or type 'help' for more information.") 
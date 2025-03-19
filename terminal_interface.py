#!/usr/bin/env python
"""
Simplified terminal chat interface for the AI Travel Agent.
This provides a command-line interface to interact with the travel agent.
"""

import asyncio
import os
import uuid
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger("travel-agent")

# Import agent and database related services
from app.services.user_service import create_user, get_user_by_id
from app.agents.travel_crew import get_travel_crew

async def main():
    """
    Main function to run the terminal chat interface.
    """
    print("===================================")
    print("🌍 AI Travel Agent - Terminal Chat")
    print("===================================")
    print("Type 'exit' to quit the chat.")
    print()
    
    # Get or create user
    user_id = os.environ.get("TEST_USER_ID")
    
    if not user_id:
        # Create a test user with a random ID
        user_id = str(uuid.uuid4())
        try:
            await create_user(
                user_id=user_id,
                phone_number="+1234567890",  # Fake phone number for testing
                name="Terminal Test User"
            )
            print(f"Created new test user with ID: {user_id}")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            print("Failed to create user. Exiting.")
            return
    else:
        # Check if user exists, create if not
        user = await get_user_by_id(user_id)
        if not user:
            try:
                await create_user(
                    user_id=user_id,
                    phone_number="+1234567890",  # Fake phone number for testing
                    name="Terminal Test User"
                )
                print(f"Created new test user with ID: {user_id}")
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                print("Failed to create user. Exiting.")
                return
        else:
            print(f"Using existing user with ID: {user_id}")
    
    # Create travel agent crew
    travel_crew = get_travel_crew(user_id)
    
    # Check if user has preferences
    user = await get_user_by_id(user_id)
    is_new_user = user is None or not user.preferences
    
    # Main chat loop
    while True:
        # Get user input
        user_input = input("\nYou > ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break
            
        # Process message with travel agent
        print("\nAI Travel Agent is thinking...")
        
        try:
            response = await travel_crew.process_message(message=user_input, is_new_user=is_new_user)
            
            # Print the response
            print(f"\nAI > {response}")
            
            # After first message, user is no longer considered new
            is_new_user = False
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            print("\nAI > Sorry, I encountered an error. Please try again.")

if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main()) 
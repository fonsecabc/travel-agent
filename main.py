import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.db import Firestore
from app.usecases import ChatUseCase, UserUseCase
from app.processors.message_processor import MessageProcessor
from app.agent import TravelAgent
from app.agent.tools import FlightSearchTool

logger = logging.getLogger(__name__)

async def main():
    """
    Main function to run the terminal chat interface.
    """
    print("===================================")
    print("🌍 AI Travel Agent")
    print("===================================")
    print("Type 'exit' to quit the chat.")
    print()

    firestore = Firestore()
    message_processor = MessageProcessor(
        chat_use_case=ChatUseCase(firestore),
        user_use_case=UserUseCase(firestore),
        travel_agent=TravelAgent(
            flight_tool=FlightSearchTool()
        ),
    )

    phone_number = input("Enter your phone number (default: +1234567890): ") or "+1234567890"
    
    # Main chat loop
    while True:
        user_input = input("\nYou > ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! 👋")
            break
            
        try:
            response = await message_processor.process(phone_number, user_input)

            # Print the response
            print(f"\nAI > {response}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            print("\nAI > Sorry, I encountered an error. Please try again.")

if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main()) 
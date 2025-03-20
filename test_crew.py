import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.agent import TravelAgent
from app.agent.tools import FlightSearchTool

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_test():
    """Run a simple test of the TravelAgent crew"""
    print("===================================")
    print("🌍 Test AI Travel Agent Crew")
    print("===================================")
    
    # Create the TravelAgent with the FlightSearchTool
    travel_agent = TravelAgent(
        flight_tool=FlightSearchTool()
    )
    
    # Sample test messages
    test_messages = [
        "I want to find flights from New York to London next week",
        "What's the best price for flights to Tokyo in June?",
        "Are there any flights from San Francisco to Miami on May 15?",
    ]
    
    # Process each test message
    for message in test_messages:
        print(f"\nTest message: {message}")
        
        try:
            # Prepare input for the crew
            inputs = {
                'user_message': message
            }
            
            # Run the crew with the input
            print("Running crew with input...")
            response = travel_agent.crew().kickoff(inputs=inputs)
            
            # Print the response
            print(f"\nCrew response: {response}")
            print("-----------------------------------")
            
        except Exception as e:
            logger.error(f"Error processing with CrewAI: {str(e)}")
            print(f"Error: {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(run_test()) 
from app.agent import TravelAgent
from app.usecases import ChatUseCase, UserUseCase
from fast_flights import Passengers

class MessageProcessor:
    """
    Process messages from the user.
    """
    def __init__(
        self,
        chat_use_case: ChatUseCase,
        user_use_case: UserUseCase,
        travel_agent: TravelAgent,
    ):
        """
        Initialize the message processor.
        """
        self.chat_use_case = chat_use_case
        self.user_use_case = user_use_case
        self.travel_agent = travel_agent

    async def process(self, phone_number: str, content: str) -> str:
        """
        Process a message from the user.
        """
        # Get or create user
        user = await self.user_use_case.get_user(phone_number)
        await self.chat_use_case.add_message(user.id, "user", content)
        
        # Get chat history
        chat_history = await self.chat_use_case.get_chat_history(user.id)
        
        # Process the message with CrewAI
        try:
            # Pass content and conversation history as inputs for the crew
            inputs = {
                'user_message': content,
                'chat_history': chat_history
            }
            
            response = self.travel_agent.crew().kickoff(inputs=inputs)
            
            # Add the response to the chat
            await self.chat_use_case.add_message(user.id, "agent", response)
            
            return response
        except Exception as e:
            error_msg = f"Error processing with CrewAI: {str(e)}"
            # Log error but return user-friendly message
            return "I'm sorry, I couldn't process your request. Please try again."

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
        # user = self.user_use_case.get_user(phone_number)
        # message = self.chat_use_case.add_message(user.id, "user", content)

        # Process the message with CrewAI
        try:
            # For now, just pass content as inputs for the crew
            # In a more advanced implementation, we would parse the content
            # to extract structured information like origin, destination, etc.
            inputs = {
                'user_message': content
            }
            
            response = self.travel_agent.crew().kickoff(inputs=inputs)
            
            # Add the response to the chat
            # self.chat_use_case.add_message(user.id, "agent", response)
            
            return response
        except Exception as e:
            error_msg = f"Error processing with CrewAI: {str(e)}"
            # Log error but return user-friendly message
            return "I'm sorry, I couldn't process your request. Please try again."

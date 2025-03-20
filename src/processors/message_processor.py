import logging

from src.usecases import ChatUseCase, UserUseCase
from src.nlp.crews import TravelAgentCrew, TravelAgentCrewInput

class MessageProcessor:
    """
    Process messages from the user.
    """
    def __init__(
        self,
        chat_use_case: ChatUseCase,
        user_use_case: UserUseCase,
        travel_agent_crew: TravelAgentCrew,
    ):
        """
        Initialize the message processor.
        """
        self.chat_use_case = chat_use_case
        self.user_use_case = user_use_case
        self.travel_agent_crew = travel_agent_crew

        self.logger = logging.getLogger(__name__)

    async def process(self, phone_number: str, content: str) -> str:
        """
        Process a message from the user.
        """
        user = await self.user_use_case.get_user(phone_number=phone_number)

        await self.chat_use_case.add_message(
            user_id=user.id,
            role="user",
            content=content
        )

        chat_history = await self.chat_use_case.get_chat_history(user_id=user.id)
        
        try:
            inputs = TravelAgentCrewInput(
                message=content,
                history=chat_history
            )

            response = self.travel_agent_crew.run(inputs)
            
            await self.chat_use_case.add_message(
                user_id=user.id,
                role="agent",
                content=response
            )

            return response
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return "I'm sorry, I couldn't process your request. Please try again."

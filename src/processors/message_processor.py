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
        self.logger.info(f"Processing message from {phone_number}: {content}")
        print(f"Processing message from {phone_number}: {content}")
        user = await self.user_use_case.get_user(phone_number=phone_number)

        self.logger.info(f"Adding message to chat history for user {user.id}")
        print(f"Adding message to chat history for user {user.id}")
        await self.chat_use_case.add_message(
            user_id=user.id,
            role="user",
            content=content
        )

        self.logger.info(f"Getting chat history for user {user.id}")
        print(f"Getting chat history for user {user.id}")
        chat_history = await self.chat_use_case.get_chat_history(user_id=user.id)
        
        try:
            inputs = TravelAgentCrewInput(
                message=content,
                history=chat_history
            )

            self.logger.info(f"Running travel agent crew for user {user.id}")
            print(f"Running travel agent crew for user {user.id}")
            response = self.travel_agent_crew.run(inputs)
            
            self.logger.info(f"Adding response to chat history for user {user.id}")
            print(f"Adding response to chat history for user {user.id}")
            await self.chat_use_case.add_message(
                user_id=user.id,
                role="agent",
                content=response
            )

            self.logger.info(f"Returning response to user {phone_number}")
            print(f"Returning response to user {phone_number}")
            return response
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return "I'm sorry, I couldn't process your request. Please try again."

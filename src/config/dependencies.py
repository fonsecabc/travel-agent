from src.db import Firestore
from src.processors import MessageProcessor
from src.usecases import ChatUseCase, UserUseCase

from src.nlp.crews import TravelAgentCrew
from crewai_tools import SerperDevTool
from src.nlp.tasks import ConversationTask
from src.nlp.agents import ConversationAgent

class Dependencies:
    def __init__(self):
        self.db = Firestore()
        
        self.chat_use_case = ChatUseCase(
            db=self.db
        )
        self.user_use_case = UserUseCase(
            db=self.db
        )

        self.serper_tool = SerperDevTool()

        self.conversation_agent = ConversationAgent(
            agent_model="gpt-4",
            temperature=0.3,
            tools=[self.serper_tool]
        )
        self.conversation_task = ConversationTask(
            agent=self.conversation_agent
        )

        self.travel_agent_crew = TravelAgentCrew(
            conversation_agent=self.conversation_agent,
            conversation_task=self.conversation_task
        )

        self.message_processor = MessageProcessor(
            chat_use_case=self.chat_use_case,
            user_use_case=self.user_use_case,
            travel_agent_crew=self.travel_agent_crew
        ) 

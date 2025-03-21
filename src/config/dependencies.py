from src.db import Firestore
from src.processors import MessageProcessor
from src.usecases import ChatUseCase, UserUseCase

from src.nlp.crews import TravelAgentCrew
from src.nlp.tools import FlightSearchTool
from src.nlp.tasks import ConversationTask, SearchFlightTask
from src.nlp.agents import ConversationAgent, FlightSearchAgent

class Dependencies:
    def __init__(self):
        self.db = Firestore()
        
        self.chat_use_case = ChatUseCase(
            db=self.db
        )
        self.user_use_case = UserUseCase(
            db=self.db
        )

        self.flight_search_tool = FlightSearchTool()

        self.conversation_agent = ConversationAgent(
            agent_model="gpt-4o-mini",
            temperature=0.3
        )
        self.conversation_task = ConversationTask(
            agent=self.conversation_agent
        )

        self.flight_search_agent = FlightSearchAgent(
            agent_model="gpt-4o-mini",
            temperature=0.3,
            tools=[self.flight_search_tool]
        )
        self.search_flight_task = SearchFlightTask(
            agent=self.flight_search_agent,
        )

        self.travel_agent_crew = TravelAgentCrew(
            conversation_agent=self.conversation_agent,
            flight_search_agent=self.flight_search_agent,
            conversation_task=self.conversation_task,
            search_flight_task=self.search_flight_task
        )

        self.message_processor = MessageProcessor(
            chat_use_case=self.chat_use_case,
            user_use_case=self.user_use_case,
            travel_agent_crew=self.travel_agent_crew
        )


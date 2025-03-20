from  src.nlp.tasks import ConversationTask, SearchFlightTask
from  src.nlp.agents import ConversationAgent, FlightSearchAgent

from crewai import Crew, Process
from pydantic import BaseModel
from typing import List, Dict

class TravelAgentCrewInput(BaseModel):
    message: str
    history: List[Dict[str, str]]

class TravelAgentCrew:
    """
    Main class that sets up and manages the Travel Agent Crew.
    """
    
    def __init__(
            self,
            conversation_agent: ConversationAgent,
            flight_search_agent: FlightSearchAgent,
            conversation_task: ConversationTask,
            search_flight_task: SearchFlightTask
    ):
        """
        Initialize the TravelAgentCrew with tools and agents.
        """
        self.crew = Crew(
            agents=[conversation_agent, flight_search_agent],
            tasks=[conversation_task, search_flight_task],
            process=Process.sequential,
            verbose=False,
            max_rpm=20
        )
    
    def run(self, input: TravelAgentCrewInput):
        """
        Run the crew with the provided input data.
        
        Args:
            input: Dictionary containing input parameters like user message and chat history
        
        Returns:    
            The result from the crew execution
        """
        result = self.crew.kickoff(
            inputs={
                "message": input.message,
                "history": input.history
            }
        )

        return result.raw

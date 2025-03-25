from datetime import datetime
from src.nlp.tasks import ConversationTask
from src.nlp.agents import ConversationAgent

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
            conversation_task: ConversationTask,
    ):
        """
        Initialize the TravelAgentCrew with tools and agents.
        """
        self.crew = Crew(
            agents=[conversation_agent],
            tasks=[conversation_task],
            process=Process.sequential,
            verbose=True,
            max_rpm=20,
            max_retries=3
        )
    
    def run(self, input: TravelAgentCrewInput):
        """
        Run the crew with the provided input data.
        
        Args:
            input: Dictionary containing input parameters like user message and chat history
        
        Returns:    
            The result from the crew execution
        """

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = self.crew.kickoff(
            inputs={
                "message": input.message,
                "history": input.history,
                "date": date
            }
        )

        return result.raw

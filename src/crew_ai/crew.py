from src.config.variables import *
from src.crew_ai.tasks.travel_tasks import TravelTasks
from src.crew_ai.tools.flight_search_tool import FlightSearchTool
from src.crew_ai.agents.travel_agents import TravelAgents

from crewai import Crew, Process

class TravelAgentCrew:
    """
    Main class that sets up and manages the Travel Agent Crew.
    """
    
    def __init__(self):
        """Initialize the TravelAgentCrew with tools and agents."""
        # Initialize tools
        self.flight_search_tool = FlightSearchTool()
        
        # Initialize agents
        self.flight_search_agent = TravelAgents.flight_search_agent(
            AGENT_MODEL,
            AGENT_TEMPERATURE,
            [self.flight_search_tool]
        )
        
        self.conversation_agent = TravelAgents.conversation_agent(
            AGENT_MODEL,
            AGENT_TEMPERATURE
        )
        
        # Initialize tasks
        self.flight_search_task = TravelTasks.flight_search_task(
            agent=self.flight_search_agent
        )
        
        self.conversation_task = TravelTasks.conversation_task(
            agent=self.conversation_agent
        )
        
        # Create crew
        self.crew = Crew(
            agents=[self.conversation_agent, self.flight_search_agent],
            tasks=[self.conversation_task, self.flight_search_task],
            process=Process.sequential,
            verbose=False,
            max_rpm=20
        )
    
    def run(self, input_data):
        """
        Run the crew with the provided input data.
        
        Args:
            input_data: Dictionary containing input parameters like user message and chat history
        
        Returns:
            The result from the crew execution
        """
        # Simplify: we directly pass the general inputs to the crew
        # Instead of trying to map to specific task IDs
        
        # Process the input data and run the crew
        result = self.crew.kickoff(
            inputs={
                "message": input_data.get("user_message", ""),
                "history": input_data.get("chat_history", [])
            }
        )
        
        return result.raw


# Function to run the travel agent crew from external code
def run_travel_agent_crew(user_message, chat_history=None):
    """
    Run the travel agent crew with a user message and optional chat history.
    
    Args:
        user_message: The message from the user
        chat_history: Optional list of previous messages
    
    Returns:
        The response from the travel agent crew
    """
    if chat_history is None:
        chat_history = []
    
    # Create input data for the crew
    input_data = {
        "user_message": user_message,
        "chat_history": chat_history
    }
    
    # Initialize and run the crew
    travel_crew = TravelAgentCrew()
    result = travel_crew.run(input_data)
    
    return result 
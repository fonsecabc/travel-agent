from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class TravelAgent():
    """
    TravelAgent crew
    """
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self, flight_tool=None):
        """Initialize the TravelAgent with optional tools."""
        self.flight_tool = flight_tool
    
    @agent
    def flight_search_agent(self) -> Agent:
        tools = [self.flight_tool] if self.flight_tool else []
        
        return Agent(
            config=self.agents_config['flight_search_agent'],
            tools=tools,
            respect_context_window=True,
            verbose=False
        )
    
    @agent
    def conversation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['conversation_agent'],
            verbose=False
        )

    @task
    def flight_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['flight_search_task'],
        )

    @task
    def conversation_task(self) -> Task:
        return Task(
            config=self.tasks_config['conversation_task'],
        )

    @crew
    def crew(self) -> Crew:
        """
        Creates the TravelAgent crew
        """

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )

from crewai import Task, Agent

class SearchFlightTask(Task):
    def __init__(self, agent: Agent):
        """
        Creates a task for searching flights based on user criteria.
        """
        super().__init__(
            description="""
                <DESCRIPTION>
                    Search for flight options based on the provided criteria. Analyze the results
                    and present the best options to the user in a clear, organized manner.
                </DESCRIPTION>
                
                <RULES>
                    - Use the FlightSearchTool to search for flights matching the provided criteria
                    - Process and organize the search results into a clear format
                    - Present options with all relevant details:
                        - Price
                        - Airline
                        - Departure and arrival times
                        - Flight duration
                        - Number of stops
                    - Highlight the best 2-3 options based on price, duration, and convenience
                    - If no flights are found, suggest alternative search criteria
                    - Explain your recommendations with reasoning
                </RULES>
            """,
            agent=agent,
            expected_output="""
                <EXPECTED_OUTPUT>
                    - A list of flight options with complete details for each option
                    - Highlighted recommendations for the best options with explanations
                    - Clear organization of information that's easy to understand
                    - If applicable, suggestions for alternative search criteria
                </EXPECTED_OUTPUT>
            """
        )
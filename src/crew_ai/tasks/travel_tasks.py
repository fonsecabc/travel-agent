from crewai import Task

class TravelTasks:
    @staticmethod
    def flight_search_task(agent):
        """
        Creates a task for searching flights based on user criteria.
        """
        return Task(
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
    
    @staticmethod
    def conversation_task(agent):
        """
        Creates a task for handling user conversation about travel.
        """
        return Task(
            description="""
                <DESCRIPTION>
                    Engage in natural conversation with the user about their travel needs
                    and interests. Understand their requirements, answer questions, and
                    facilitate the flight search process.
                </DESCRIPTION>
                
                <RULES>
                    - Maintain a natural, conversational tone throughout the interaction
                    - Respond appropriately to greetings and casual conversation
                    - Ask clarifying questions when necessary to understand travel needs
                    - If user is interested in finding flights, gather necessary details:
                        - Origin location
                        - Destination location
                        - Departure date
                        - Return date (if applicable)
                        - Number of passengers
                    - Keep track of conversation context
                    - When the user asks about flights, use that information to help the flight search agent
                    - The user message will be available in the 'message' variable
                    - The chat history will be available in the 'history' variable
                </RULES>
            """,
            agent=agent,
            expected_output="""
                <EXPECTED_OUTPUT>
                    - Natural, relevant responses to user messages
                    - Appropriate follow-up questions when needed
                    - Clear explanations of flight options when provided
                    - Helpful travel-related information based on user queries
                </EXPECTED_OUTPUT>
            """
        )
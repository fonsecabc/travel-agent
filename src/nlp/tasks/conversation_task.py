from crewai import Task, Agent

class ConversationTask(Task):
    def __init__(self, agent: Agent):
        """
        Creates a task for handling user conversation about travel.
        """
        super().__init__(
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
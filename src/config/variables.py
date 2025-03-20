# Configuration variables for the Travel Agent Crew

# LLM Configuration
AGENT_MODEL = "gpt-4o"
AGENT_TEMPERATURE = 0.3

# API Keys Configuration
# Note: In production, these should be loaded from environment variables
# using something like:
# import os
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Other Configuration Parameters
MAX_FLIGHT_RESULTS = 5  # Maximum number of flight results to process
DEFAULT_SEAT_CLASS = "economy"  # Default seat class for flight searches
MAX_STOPS = 1  # Default maximum number of stops 
#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from agent.crew import TravelAgent
from fast_flights import Passengers

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the crew.
    """
    inputs = {
        'origin': 'SFO',
        'destination': 'LAX',
        'departure_date': '2025-03-20',
        'return_date': '2025-03-25',
        'passengers': Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0)
    }
    
    try:
        TravelAgent().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "origin": "SFO",
        "destination": "LAX",
        "departure_date": "2025-03-20",
        "return_date": "2025-03-25",
        "passengers": Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0)
    }
    try:
        TravelAgent().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

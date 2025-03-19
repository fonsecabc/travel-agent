"""
Flight search service for the Travel Agent.

This module provides functions to search for flights and process flight data using the fast-flights package.
We rely entirely on the LLM's knowledge to determine airport codes for cities mentioned by users.
"""

import os
import logging
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode

# Import fast-flights package
from fast_flights import (
    get_flights,
    FlightData,
    Passengers,
    Result,
    TFSData
)

from app.models.user import SearchHistory

logger = logging.getLogger("travel-agent")

async def search_flights(
    user_id: str,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: int = 1,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search for flights using the fast-flights package which scrapes Google Flights.
    
    Args:
        user_id: The ID of the user making the search
        origin: Origin location (can be an airport code or city name)
        destination: Destination location (can be an airport code or city name)
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (optional for one-way)
        adults: Number of adult passengers
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with search results
    """
    logger.info(f"Searching flights from {origin} to {destination} on {departure_date}")
    
    try:
        # Format dates and validate
        departure_date = departure_date.strip()
        
        # Convert origin and destination to uppercase for airport codes
        origin = origin.upper()
        destination = destination.upper()
        
        # Validate dates
        today = datetime.now().date()
        input_departure_date = None
        input_return_date = None
        
        try:
            input_departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            if return_date:
                input_return_date = datetime.strptime(return_date.strip(), "%Y-%m-%d").date()
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid date format. Please use YYYY-MM-DD format."
            }
        
        # Check if dates are in the future
        if input_departure_date < today:
            # If date is in the past, use a date one month from now
            departure_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
            if return_date:
                return_date = (today + timedelta(days=37)).strftime("%Y-%m-%d")
            
        # Ensure return date is after departure date
        if input_return_date and input_return_date < input_departure_date:
            return_date = (input_departure_date + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Set up flight data
        outbound_flight = FlightData(
            date=departure_date,
            from_airport=origin,
            to_airport=destination
        )
        
        # Set up passengers
        passengers = Passengers(
            adults=adults,
            children=0,
            infants_in_seat=0,
            infants_on_lap=0
        )
        
        # Determine trip type and execute search
        if return_date:
            # Round trip
            inbound_flight = FlightData(
                date=return_date,
                from_airport=destination,
                to_airport=origin
            )
            
            flights = await _get_flights(
                flight_data=[outbound_flight, inbound_flight],
                trip="round-trip",
                seat="economy",  # Default to economy, can be customized based on user preference
                passengers=passengers,
                currency="USD",
                max_stops=0
            )
        else:
            # One-way trip
            flights = await _get_flights(
                flight_data=[outbound_flight],
                trip="one-way",
                seat="economy",
                passengers=passengers,
                currency="USD",
                max_stops=0
            )
        
        # Process the results
        processed_results = []
        
        # The fast-flights package returns a Result object with a 'flights' attribute
        if hasattr(flights, 'flights') and flights.flights:
            # Process each flight result
            for flight in flights.flights[:max_results]:  # Limit to max_results
                try:
                    # Get price from the flight
                    price_str = flight.price if hasattr(flight, 'price') else '0'
                    # Remove currency symbol and convert to float
                    # Assuming price is in format like 'R$2313'
                    numeric_price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_str)))
                    
                    # Parse the duration string if available (format: "6 hr 34 min")
                    duration_minutes = 0
                    if hasattr(flight, 'duration') and flight.duration:
                        duration_str = flight.duration
                        try:
                            # Extract hours and minutes
                            hours = 0
                            minutes = 0
                            
                            if 'hr' in duration_str:
                                hours_part = duration_str.split('hr')[0].strip()
                                hours = int(hours_part)
                            
                            if 'min' in duration_str:
                                if 'hr' in duration_str:
                                    minutes_part = duration_str.split('hr')[1].split('min')[0].strip()
                                else:
                                    minutes_part = duration_str.split('min')[0].strip()
                                minutes = int(minutes_part)
                            
                            duration_minutes = hours * 60 + minutes
                        except (ValueError, IndexError):
                            # If parsing fails, keep the default of 0
                            pass
                    
                    # Create a simplified result structure
                    result = {
                        "price": {
                            "total": numeric_price,
                            "currency": "USD"  # Default to USD, actual currency may vary
                        },
                        "itineraries": [],
                        "airline": flight.name if hasattr(flight, 'name') else "Unknown"
                    }
                    
                    # Create segments for the outbound journey
                    outbound_segments = []
                    if hasattr(flight, 'departure') and hasattr(flight, 'arrival'):
                        # Parse departure and arrival times
                        outbound_segments.append({
                            "departure": {
                                "at": flight.departure,
                                "iataCode": origin
                            },
                            "arrival": {
                                "at": flight.arrival,
                                "iataCode": destination
                            },
                            "carrierCode": flight.name if hasattr(flight, 'name') else "Unknown",
                            "number": "N/A",
                            "duration": duration_minutes  # Use parsed duration in minutes
                        })
                    
                    # Add the outbound itinerary
                    result["itineraries"].append({
                        "segments": outbound_segments,
                        "duration": duration_minutes  # Use parsed duration in minutes
                    })
                    
                    # Add return itinerary if it's a round trip
                    if return_date:
                        return_segments = []
                        # We don't have specific return flight details in the flight object
                        # So create a placeholder segment with estimated info
                        return_segments.append({
                            "departure": {
                                "at": f"Unknown time on {return_date}",
                                "iataCode": destination
                            },
                            "arrival": {
                                "at": f"Unknown time on {return_date}",
                                "iataCode": origin
                            },
                            "carrierCode": flight.name if hasattr(flight, 'name') else "Unknown",
                            "number": "N/A",
                            "duration": 0  # Use a default numeric value
                        })
                        
                        result["itineraries"].append({
                            "segments": return_segments,
                            "duration": 0  # Use a default numeric value
                        })

                    processed_results.append(result)
                except Exception as e:
                    logger.error(f"Error processing flight result: {str(e)}")
                    continue

        # Record search history with processed data
        search_id = await record_search_history(
            user_id=user_id,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            results=processed_results
        )
        
        return {
            "status": "success",
            "search_id": search_id,
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "flights": processed_results,
            "result_count": len(processed_results)
        }
        
    except Exception as e:
        logger.error(f"Error searching flights: {str(e)}")
        return {
            "status": "error",
            "message": f"An error occurred while searching flights: {str(e)}"
        }
    
async def _get_flights(
    flight_data: List[FlightData],
    trip: str,
    passengers: Passengers,
    seat: str,
    max_stops: int,
    currency: str
) -> List[Result]:
    flights = get_flights(
        flight_data=flight_data,
        trip=trip,
        passengers=passengers,
        seat=seat,
        max_stops=max_stops,
        fetch_mode="fallback"  # Use fallback mode to avoid asyncio issues
    )

    return flights


async def record_search_history(
    user_id: str,
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str],
    results: List[Dict[str, Any]]
) -> str:
    """
    Record search history for a user.
    
    Args:
        user_id: The ID of the user
        origin: Origin airport code
        destination: Destination airport code
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (optional)
        results: List of flight results
        
    Returns:
        The ID of the search history record
    """
    # Import save_search_history here to avoid circular dependency
    from app.services.user_service import save_search_history
    
    try:
        # Find lowest price
        lowest_price = None
        if results:
            try:
                lowest_price = min([float(result.get("price", {}).get("total", float("inf"))) for result in results])
            except (ValueError, TypeError):
                logger.warning("Could not determine lowest price from results")
        
        # Create search history record
        search_history = SearchHistory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            search_timestamp=datetime.now(),
            results=results[:3],  # Store only the top 3 results to save space
            lowest_price=lowest_price
        )
        
        # Save to database
        search_id = await save_search_history(search_history)
        
        return search_id
        
    except Exception as e:
        logger.error(f"Error recording search history: {str(e)}")
        raise 
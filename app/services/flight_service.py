"""
Flight search service for the Travel Agent.

This module provides functions to search for flights and process flight data using the Amadeus API.
We rely entirely on the LLM's knowledge to determine airport codes for cities mentioned by users.
"""

import os
import logging
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import httpx
from amadeus import Client, ResponseError

from app.models.user import SearchHistory, FlightDeal
# Import user_service functions within each function to avoid circular dependencies

logger = logging.getLogger("travel-agent")

# Initialize Amadeus client
amadeus_client_id = os.environ.get("AMADEUS_CLIENT_ID")
amadeus_client_secret = os.environ.get("AMADEUS_CLIENT_SECRET")

if not amadeus_client_id or not amadeus_client_secret:
    logger.warning("Amadeus API credentials not set. Flight search will not function correctly.")
    amadeus = None
else:
    try:
        amadeus = Client(
            client_id=amadeus_client_id,
            client_secret=amadeus_client_secret
        )
        logger.info("Amadeus client initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Amadeus client: {str(e)}")
        amadeus = None

# No pre-defined airport mappings - we rely entirely on the LLM's knowledge

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
    Search for flights using the Amadeus API.
    
    Args:
        user_id: The ID of the user making the search
        origin: Origin location (can be an airport code or city name)
        destination: Destination location (can be an airport code or city name)
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (optional for one-way)
        adults: Number of adult passengers
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with search results containing raw Amadeus data
    """
    logger.info(f"Searching flights from {origin} to {destination} on {departure_date}")
    
    if not amadeus:
        logger.error("Amadeus client not initialized. Cannot search flights.")
        return {
            "status": "error",
            "message": "Flight search service is not available at the moment."
        }
    
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
            
            logger.info(f"Adjusted past date to future: {departure_date}")
        
        # Ensure return date is after departure date
        if input_return_date and input_return_date < input_departure_date:
            return_date = (input_departure_date + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Build search parameters
        search_params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "currencyCode": "USD",
            "max": max_results
        }
        
        if return_date:
            search_params["returnDate"] = return_date.strip()
        
        # Call Amadeus API
        response = amadeus.shopping.flight_offers_search.get(**search_params)
        
        # Record search history with raw data
        search_id = await record_search_history(
            user_id=user_id,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            results=response.data  # Store raw Amadeus data
        )
        
        return {
            "status": "success",
            "search_id": search_id,
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "raw_data": response.data,  # Return raw Amadeus data
            "result_count": len(response.data)
        }
        
    except ResponseError as e:
        logger.error(f"Amadeus API error: {str(e)}")
        error_message = "An error occurred while searching flights."
        
        # Try to extract more detailed error information
        try:
            error_detail = e.response.result.get("errors", [{}])[0].get("detail", "")
            if error_detail:
                error_message = error_detail
        except:
            pass
        
        return {
            "status": "error",
            "message": error_message
        }
        
    except Exception as e:
        logger.error(f"Error searching flights: {str(e)}")
        return {
            "status": "error",
            "message": f"An error occurred while searching flights: {str(e)}"
        }

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
    from app.services.user_service import save_search_history, save_flight_deal
    
    try:
        # Find lowest price
        lowest_price = None
        if results:
            lowest_price = min([result.get("price", float("inf")) for result in results])
        
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
        
        # If we found a good deal, save it
        if lowest_price:
            price_analysis = await analyze_flight_deal(
                user_id=user_id,
                origin=origin,
                destination=destination,
                price=lowest_price,
                departure_date=departure_date,
                return_date=return_date
            )
            
            if price_analysis.get("is_deal", False):
                airline = results[0].get("airline") if results else "Unknown"
                
                await save_deal(
                    user_id=user_id,
                    origin=origin,
                    destination=destination,
                    price=lowest_price,
                    airline=airline,
                    departure_date=departure_date,
                    return_date=return_date,
                    deal_quality=price_analysis.get("deal_quality"),
                    price_difference_percentage=price_analysis.get("price_difference_percentage"),
                    details=results[0] if results else {}
                )
        
        return search_id
        
    except Exception as e:
        logger.error(f"Error recording search history: {str(e)}")
        raise

async def analyze_flight_deal(
    user_id: str,
    origin: str,
    destination: str,
    price: float,
    departure_date: str,
    return_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze if a flight price is a good deal.
    
    Args:
        user_id: The ID of the user
        origin: Origin airport code
        destination: Destination airport code
        price: The flight price in USD
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (optional)
        
    Returns:
        Dictionary with price analysis
    """
    # In a real implementation, this would compare against historical prices
    # For now, we'll use a simple rule-based approach
    
    # Example baseline prices for common routes (in USD)
    # These would normally come from a database or API
    BASELINE_PRICES = {
        "JFK-LAX": 350,
        "JFK-SFO": 400,
        "JFK-LHR": 800,
        "LAX-JFK": 350,
        "LAX-HND": 950,
        "LHR-JFK": 800,
        "SFO-JFK": 400,
        "SFO-HND": 900,
    }
    
    # Default baseline price if route not found
    DEFAULT_DOMESTIC_BASELINE = 300
    DEFAULT_INTERNATIONAL_BASELINE = 800
    
    try:
        # Get route key
        route_key = f"{origin}-{destination}"
        
        # Get baseline price for this route
        baseline_price = BASELINE_PRICES.get(route_key)
        
        if not baseline_price:
            # Determine if international or domestic (simplified logic)
            is_international = len(set([origin[:2], destination[:2]])) > 1
            baseline_price = DEFAULT_INTERNATIONAL_BASELINE if is_international else DEFAULT_DOMESTIC_BASELINE
        
        # Calculate price difference percentage
        price_diff_percentage = ((baseline_price - price) / baseline_price) * 100
        
        # Determine deal quality
        is_deal = price_diff_percentage > 0
        
        if price_diff_percentage >= 25:
            deal_quality = "great"
        elif price_diff_percentage >= 10:
            deal_quality = "good"
        else:
            deal_quality = "normal"
        
        return {
            "status": "success",
            "is_deal": is_deal,
            "deal_quality": deal_quality,
            "price": price,
            "baseline_price": baseline_price,
            "price_difference": baseline_price - price,
            "price_difference_percentage": price_diff_percentage,
            "route": route_key
        }
        
    except Exception as e:
        logger.error(f"Error analyzing flight deal: {str(e)}")
        return {
            "status": "error",
            "message": f"Error analyzing flight deal: {str(e)}"
        }

async def save_deal(
    user_id: str,
    origin: str,
    destination: str,
    price: float,
    airline: str,
    departure_date: str,
    return_date: Optional[str],
    deal_quality: str,
    price_difference_percentage: float,
    details: Dict[str, Any] = {}
) -> str:
    """
    Save a flight deal to the database.
    
    Args:
        user_id: The ID of the user
        origin: Origin airport code
        destination: Destination airport code
        price: The flight price in USD
        airline: The airline code
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (optional)
        deal_quality: The quality of the deal ("great", "good", "normal")
        price_difference_percentage: The percentage difference from baseline price
        details: Additional details about the flight
        
    Returns:
        The ID of the saved deal
    """
    # Import already done in record_search_history function
    
    try:
        # Create flight deal record
        flight_deal = FlightDeal(
            id=str(uuid.uuid4()),
            user_id=user_id,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            price=price,
            airline=airline,
            deal_quality=deal_quality,
            price_difference_percentage=price_difference_percentage,
            found_at=datetime.now(),
            details=details
        )
        
        # Save to database
        from app.services.user_service import save_flight_deal
        deal_id = await save_flight_deal(flight_deal)
        
        logger.info(f"Saved {deal_quality} deal from {origin} to {destination} at ${price}")
        return deal_id
        
    except Exception as e:
        logger.error(f"Error saving flight deal: {str(e)}")
        raise

async def find_deals_for_user(user_id: str, max_deals_per_destination: int = 1) -> List[Dict[str, Any]]:
    """
    Find flight deals based on user preferences.
    
    Args:
        user_id: The ID of the user
        max_deals_per_destination: Maximum number of deals to find per destination
        
    Returns:
        List of flight deals
    """
    # Import within function to avoid circular dependencies
    from app.services.user_service import get_user_by_id, get_flight_deals
    
    try:
        # Get user preferences
        user = await get_user_by_id(user_id)
        
        if not user or not user.preferences:
            logger.warning(f"No preferences found for user {user_id}")
            return []
            
        preferences = user.preferences
        
        # Get home airports and travel preferences
        home_airports = preferences.home_airports
        travel_preferences = preferences.travel_preferences
        
        if not home_airports or not travel_preferences:
            logger.warning(f"Incomplete preferences for user {user_id}")
            return []
            
        # Find deals for each destination
        all_deals = []
        
        for travel_pref in travel_preferences:
            destination = travel_pref.destination
            
            # Use the destination directly - CrewAI agent will handle airport code determination
            # using its knowledge
            
            # Search from each home airport
            for origin in home_airports:
                # Generate search dates (simplified - in a real app, this would be more sophisticated)
                search_dates = []
                
                if travel_pref.flexible_dates:
                    # Search for dates in the next 3 months
                    for i in range(1, 4):
                        departure_date = (datetime.now() + timedelta(days=30*i)).strftime("%Y-%m-%d")
                        search_dates.append((departure_date, return_date))
                else:
                    # Just search for dates 2 months from now
                    departure_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
                    return_date = (datetime.now() + timedelta(days=67)).strftime("%Y-%m-%d")
                    search_dates.append((departure_date, return_date))
                
                # Search for each date pair
                for departure_date, return_date in search_dates:
                    result = await search_flights(
                        user_id=user_id,
                        origin=origin,
                        destination=destination,
                        departure_date=departure_date,
                        return_date=return_date
                    )
                    
                    if result.get("status") == "success" and result.get("results"):
                        # Deal was saved during search if it's good enough
                        # We don't need to do anything here
                        pass
        
        # Get the saved deals from the database
        deals = await get_flight_deals(user_id)
        
        # Convert to dictionaries
        deals_list = [deal.dict() for deal in deals]
        
        return deals_list
        
    except Exception as e:
        logger.error(f"Error finding deals for user: {str(e)}")
        return [] 
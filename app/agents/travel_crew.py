"""
Travel Agent AI module.

This module implements the AI functionality for the travel agent, handling user messages
and providing responses based on the user's preferences and requests.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime

# Import the OpenAI client
from openai import OpenAI

# Import models
from app.models.user import UserPreferences, TravelPreference, Conversation, Message

# Import services (avoids circular imports by importing within functions)
from app.services import user_service as user_service_module
from app.services import flight_service as flight_service_module

# Set up logging
logger = logging.getLogger("travel-agent")

# Configure the OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set. AI assistant will not function correctly.")

client = OpenAI(api_key=OPENAI_API_KEY)

# Maximum number of previous messages to include in context
MAX_CONVERSATION_CONTEXT = 10

class TravelAgentCrew:
    """
    A handler for travel-related user messages that provides intelligent responses.
    """
    
    def __init__(self, user_id: str):
        """
        Initialize the travel agent.
        
        Args:
            user_id: The ID of the user
        """
        self.user_id = user_id
        logger.info(f"Initializing TravelAgent for user {user_id}")
    
    async def process_message(self, message: str, is_new_user: bool = False, language: str = None) -> str:
        """
        Process a message from a user and return a response.
        
        Args:
            message: The message from the user
            is_new_user: Whether this is a new user (for onboarding)
            language: Force response in a specific language (e.g., "English")
            
        Returns:
            Response message
        """
        try:
            # Store the user's message in the conversation history
            await user_service_module.add_message_to_conversation(self.user_id, "user", message)
            
            # Get user info and preferences
            user_info = await self._get_user_info()
            
            # Get conversation history
            conversation = await user_service_module.get_user_conversation(self.user_id)
            conversation_messages = conversation.messages if conversation else []
            
            # Limit to recent messages for context
            recent_messages = conversation_messages[-MAX_CONVERSATION_CONTEXT:] if len(conversation_messages) > MAX_CONVERSATION_CONTEXT else conversation_messages
            
            # Create the appropriate system prompt
            if is_new_user:
                system_prompt = self._create_onboarding_prompt()
            else:
                system_prompt = self._create_conversation_prompt(user_info)
                
            # Add language preference if specified
            if language:
                system_prompt += f"\n\nIMPORTANT: You MUST always respond in {language} regardless of the language of the user's message."
            
            # Build the messages array for the API call
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            for msg in recent_messages:
                # Skip system messages if any
                if msg.role == "system":
                    continue
                messages.append({"role": msg.role, "content": msg.content})
            
            # Call the OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            
            # Get the assistant's response
            assistant_response = response.choices[0].message.content
            
            # Process the response for any action requests
            processed_response = await self._process_actions(assistant_response)
            
            # Store the response in the conversation history
            await user_service_module.add_message_to_conversation(self.user_id, "assistant", processed_response)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"I'm sorry, something went wrong. Please try again. Error: {str(e)}"
    
    def _create_onboarding_prompt(self) -> str:
        """
        Create a system prompt for onboarding a new user.
        
        Returns:
            The system prompt
        """
        return """You are an AI Travel Agent that helps users find flight deals. 
        
Since this is a new user, you need to collect their travel preferences. Ask about:

1. Home airport(s): Where they typically fly from
2. Preferred destinations: Places they're interested in visiting
3. Travel preferences: Budget, preferred airlines, seat class (economy, premium economy, business, first)
4. Trip duration: How long they typically travel for

Be friendly and conversational. Collect information naturally over the conversation, not all at once.
After collecting preferences, offer to help them find flights or answer any other travel-related questions.

You can search for flights when the user provides:
- Origin and destination
- Travel dates (departure and optional return)

IMPORTANT: To execute a flight search, you MUST include the following pattern in your response:
{search_flights("ORIGIN", "DESTINATION", "YYYY-MM-DD", "RETURN_DATE", ADULTS)}

For example:
{search_flights("JFK", "LAX", "2023-12-25", "2024-01-02", 1)}
or for one-way:
{search_flights("JFK", "LAX", "2023-12-25")}

To update preferences, use:
{update_preferences("home_airports", ["JFK", "LGA"])}
{update_preferences("preferred_airlines", ["AA", "DL"])}
{update_preferences("seat_class", "economy")}

If the user provides all necessary information for a flight search (origin, destination, dates), 
ALWAYS include the search_flights function call in your response.

Do not ask for personal information beyond what's needed for travel preferences.
"""

    def _create_conversation_prompt(self, user_info: Dict[str, Any]) -> str:
        """
        Create a system prompt for a conversation with an existing user.
        
        Args:
            user_info: User information including preferences
            
        Returns:
            The system prompt
        """
        # Build the prompt with user preferences
        has_preferences = user_info.get("preferences") is not None
        
        # Build a base prompt
        prompt = """You are an AI Travel Agent that helps users find flight deals.

Your capabilities:
1. Search for flights based on the user's criteria
2. Update user preferences (home airports, destinations, airlines, etc.)
3. Provide travel recommendations

"""
        
        # Add user preferences if available
        if has_preferences:
            preferences = user_info.get("preferences", {})
            
            prompt += "User's current preferences:\n"
            
            # Add home airports
            home_airports = preferences.get("home_airports", [])
            if home_airports:
                prompt += f"- Home airports: {', '.join(home_airports)}\n"
            
            # Add preferred airlines
            preferred_airlines = preferences.get("preferred_airlines", [])
            if preferred_airlines:
                prompt += f"- Preferred airlines: {', '.join(preferred_airlines)}\n"
            
            # Add seat class
            seat_class = preferences.get("seat_class", "economy")
            prompt += f"- Preferred seat class: {seat_class}\n"
            
            # Add travel preferences
            travel_preferences = preferences.get("travel_preferences", [])
            if travel_preferences:
                prompt += "- Interested in traveling to:\n"
                for pref in travel_preferences:
                    destination = pref.get("destination", "")
                    budget = pref.get("budget", "Not specified")
                    budget_str = f"${budget}" if budget else "Not specified"
                    
                    prompt += f"  * {destination} (Budget: {budget_str})\n"
        else:
            prompt += "The user hasn't set any preferences yet. You should help them set up their preferences.\n"
        
        prompt += """
When the user wants to search for flights, you need:
- Origin and destination airports/cities
- Departure date
- Return date (if it's a round trip)

IMPORTANT: To execute a flight search, you MUST include the following pattern in your response:
{search_flights("ORIGIN", "DESTINATION", "YYYY-MM-DD", "RETURN_DATE", ADULTS)}

For example:
{search_flights("JFK", "LAX", "2023-12-25", "2024-01-02", 1)}
or for one-way:
{search_flights("JFK", "LAX", "2023-12-25")}

To update preferences, use:
{update_preferences("home_airports", ["JFK", "LGA"])}
{update_preferences("preferred_airlines", ["AA", "DL"])}
{update_preferences("seat_class", "economy")}

If the user provides all necessary information for a flight search (origin, destination, dates), 
ALWAYS include the search_flights function call in your response.

Speak in a friendly, helpful manner. Provide concise, relevant responses.
"""
        
        return prompt
    
    async def _get_user_info(self) -> Dict[str, Any]:
        """
        Get information about the user.
        
        Returns:
            Dictionary with user information
        """
        try:
            user = await user_service_module.get_user_by_id(self.user_id)
            if user:
                # Convert to dict for easier handling
                return {
                    "id": user.id,
                    "name": user.name,
                    "preferences": user.preferences.dict() if user.preferences else None
                }
            else:
                logger.warning(f"User {self.user_id} not found")
                return {"id": self.user_id}
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return {"id": self.user_id}
    
    async def _process_actions(self, response: str) -> str:
        """
        Process any action requests in the assistant's response.
        
        Args:
            response: The original response from the assistant
            
        Returns:
            The processed response
        """
        # Look for function call patterns like {function_name(args)}
        if "{search_flights(" in response:
            try:
                # Extract the function call
                start = response.find("{search_flights(")
                end = response.find(")}", start)
                if end == -1:
                    end = response.find(")", start)
                
                if start != -1 and end != -1:
                    function_call = response[start+1:end+1]
                    function_name = "search_flights"
                    args_str = function_call[function_call.find("(")+1:function_call.find(")")]
                    
                    # Execute the function
                    result = await self._execute_function(function_name, args_str)
                    
                    # Replace the function call with the result
                    response = response[:start] + result + response[end+2:]
            except Exception as e:
                logger.error(f"Error processing search_flights action: {str(e)}")
                response += f"\n\nI tried to search for flights but encountered an error: {str(e)}"
        # Detectar intenção de busca de voos mesmo sem o padrão exato
        elif any(pattern in response.lower() for pattern in ["procurar voos", "buscar voos", "search for flights", "encontrar passagens", "buscar passagens"]):
            # Tentativa de extrair origem, destino e datas da conversa
            try:
                # Verificar se temos informações suficientes na conversa para realizar a busca
                conversation = await user_service_module.get_user_conversation(self.user_id)
                conversation_messages = conversation.messages if conversation else []
                
                origin = None
                destination = None
                departure_date = None
                return_date = None
                
                # Obter preferências do usuário para aeroporto de origem
                user_info = await self._get_user_info()
                if user_info.get("preferences") and user_info["preferences"].get("home_airports"):
                    origin = user_info["preferences"]["home_airports"][0]
                
                # Analisar mensagens recentes para extrair informações
                recent_messages = conversation_messages[-5:] if len(conversation_messages) > 5 else conversation_messages
                
                # Buscar destino nas mensagens recentes
                for msg in recent_messages:
                    if msg.role == "user":
                        content = msg.content.lower()
                        
                        # Identificar destino
                        if "para " in content and not destination:
                            parts = content.split("para ")
                            if len(parts) > 1:
                                destination_part = parts[1].split()[0].strip(",.:;?!")
                                if destination_part and len(destination_part) >= 2:
                                    destination = destination_part.upper()
                        
                        # Identificar origem
                        if "de " in content and not origin:
                            parts = content.split("de ")
                            if len(parts) > 1:
                                origin_part = parts[1].split()[0].strip(",.:;?!")
                                if origin_part and len(origin_part) >= 2:
                                    origin = origin_part.upper()
                
                # Para testes, se ainda não temos origem ou destino, usar valores padrão
                if not origin:
                    origin = "GRU"  # São Paulo Guarulhos como padrão
                
                if not destination:
                    destination = "JFK"  # Nova York como padrão
                
                # Usar data atual + 30 dias como padrão para data de partida
                from datetime import datetime, timedelta
                departure_date = (datetime.now().date() + timedelta(days=30)).strftime("%Y-%m-%d")
                
                logger.info(f"Extracted search parameters - Origin: {origin}, Destination: {destination}, Date: {departure_date}")
                
                # Executar a busca com os parâmetros extraídos
                result = await self._search_flights(origin, destination, departure_date, return_date)
                
                # Adicionar resultados à resposta
                response = response.rstrip() + "\n\n" + result
                
            except Exception as e:
                logger.error(f"Error with automatic flight search: {str(e)}")
                response += f"\n\nTentei buscar voos, mas encontrei um erro: {str(e)}"
        
        if "{update_preferences(" in response:
            try:
                # Extract the function call
                start = response.find("{update_preferences(")
                end = response.find(")}", start)
                if end == -1:
                    end = response.find(")", start)
                
                if start != -1 and end != -1:
                    function_call = response[start+1:end+1]
                    function_name = "update_preferences"
                    args_str = function_call[function_call.find("(")+1:function_call.find(")")]
                    
                    # Execute the function
                    result = await self._execute_function(function_name, args_str)
                    
                    # Replace the function call with the result
                    response = response[:start] + result + response[end+2:]
            except Exception as e:
                logger.error(f"Error processing update_preferences action: {str(e)}")
                response += f"\n\nI tried to update your preferences but encountered an error: {str(e)}"
                
        return response
    
    async def _execute_function(self, function_name: str, args_str: str) -> str:
        """
        Execute a function based on the function name and arguments.
        
        Args:
            function_name: The name of the function to execute
            args_str: The arguments as a string
            
        Returns:
            The result of the function execution
        """
        # Parse arguments
        # This is a simple parser that handles comma-separated arguments
        # It's not perfect but works for basic cases
        args = []
        kwargs = {}
        
        # Handle quotes in arguments
        in_quotes = False
        quote_char = None
        current_arg = ""
        i = 0
        
        while i < len(args_str):
            char = args_str[i]
            
            if char in ('"', "'") and (i == 0 or args_str[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current_arg += char
            elif char == ',' and not in_quotes:
                if '=' in current_arg:
                    key, value = current_arg.split('=', 1)
                    kwargs[key.strip()] = self._parse_arg_value(value.strip())
                else:
                    args.append(self._parse_arg_value(current_arg.strip()))
                current_arg = ""
            else:
                current_arg += char
            
            i += 1
        
        # Don't forget the last argument
        if current_arg:
            if '=' in current_arg:
                key, value = current_arg.split('=', 1)
                kwargs[key.strip()] = self._parse_arg_value(value.strip())
            else:
                args.append(self._parse_arg_value(current_arg.strip()))
        
        # Execute the function
        if function_name == "search_flights":
            return await self._search_flights(*args, **kwargs)
        elif function_name == "update_preferences":
            return await self._update_preferences(*args, **kwargs)
        else:
            return f"Unknown function: {function_name}"
    
    def _parse_arg_value(self, value: str) -> Any:
        """
        Parse an argument value from string to the appropriate type.
        
        Args:
            value: The string value to parse
            
        Returns:
            The parsed value
        """
        # Remove quotes
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        
        # Try to parse as JSON
        try:
            return json.loads(value)
        except:
            pass
        
        # Try to parse as number
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except:
            pass
        
        # Handle None/null
        if value.lower() in ('none', 'null'):
            return None
        
        # Handle boolean
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        
        # Default to string
        return value
    
    async def _search_flights(self, origin: str, destination: str, departure_date: str, 
                        return_date: Optional[str] = None, adults: int = 1) -> str:
        """
        Search for flights and return the results as a formatted string.
        
        Args:
            origin: Origin airport or city
            destination: Destination airport or city
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Return date in YYYY-MM-DD format (optional)
            adults: Number of adult passengers
            
        Returns:
            Formatted string with flight results
        """
        try:
            flight_service = flight_service_module
            
            # Search for flights
            results = await flight_service.search_flights(
                user_id=self.user_id,
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=adults
            )
            
            # Get the flights
            flights = results.get("flights", [])
            
            if not flights:
                return f"I couldn't find any flights from {origin} to {destination} on {departure_date}."
            
            # Format the results
            response = f"Here are flights from {origin} to {destination} on {departure_date}"
            if return_date:
                response += f" with return on {return_date}"
            response += ":\n\n"
            
            # Add each flight
            for i, flight in enumerate(flights[:5], 1):  # Limit to 5 flights
                price = flight.get("price", {})
                price_value = price.get("total", "N/A")
                currency = price.get("currency", "USD")
                
                itineraries = flight.get("itineraries", [])
                
                response += f"{i}. ${price_value} {currency}\n"
                
                # Outbound journey
                if itineraries and len(itineraries) > 0:
                    outbound = itineraries[0]
                    segments = outbound.get("segments", [])
                    
                    # Calculate total duration
                    total_duration = outbound.get("duration", "")
                    if total_duration:
                        hours = total_duration // 60
                        minutes = total_duration % 60
                        duration_str = f"{hours}h {minutes}m" if minutes else f"{hours}h"
                        response += f"   Duration: {duration_str}, Stops: {len(segments) - 1}\n"
                    
                    # Add segments
                    for j, segment in enumerate(segments):
                        departure = segment.get("departure", {})
                        arrival = segment.get("arrival", {})
                        carrier = segment.get("carrierCode", "")
                        
                        dep_time = departure.get("at", "").split("T")[1][:5]
                        arr_time = arrival.get("at", "").split("T")[1][:5]
                        dep_airport = departure.get("iataCode", "")
                        arr_airport = arrival.get("iataCode", "")
                        
                        response += f"   {dep_time} {dep_airport} → {arr_time} {arr_airport} ({carrier})\n"
                        
                        if j < len(segments) - 1:
                            response += "   |\n"
                
                # Return journey
                if return_date and itineraries and len(itineraries) > 1:
                    response += "   ---\n"
                    return_journey = itineraries[1]
                    segments = return_journey.get("segments", [])
                    
                    # Calculate total duration
                    total_duration = return_journey.get("duration", "")
                    if total_duration:
                        hours = total_duration // 60
                        minutes = total_duration % 60
                        duration_str = f"{hours}h {minutes}m" if minutes else f"{hours}h"
                        response += f"   Return Duration: {duration_str}, Stops: {len(segments) - 1}\n"
                    
                    # Add segments
                    for j, segment in enumerate(segments):
                        departure = segment.get("departure", {})
                        arrival = segment.get("arrival", {})
                        carrier = segment.get("carrierCode", "")
                        
                        dep_time = departure.get("at", "").split("T")[1][:5]
                        arr_time = arrival.get("at", "").split("T")[1][:5]
                        dep_airport = departure.get("iataCode", "")
                        arr_airport = arrival.get("iataCode", "")
                        
                        response += f"   {dep_time} {dep_airport} → {arr_time} {arr_airport} ({carrier})\n"
                        
                        if j < len(segments) - 1:
                            response += "   |\n"
                
                response += "\n"
            
            if len(flights) > 5:
                response += f"There are {len(flights) - 5} more flights available. Let me know if you'd like to see more options."
            
            return response
        
        except Exception as e:
            logger.error(f"Error searching flights: {str(e)}")
            return f"I encountered an error while searching for flights: {str(e)}"
    
    async def _update_preferences(self, preference_type: str, value: Any) -> str:
        """
        Update user preferences.
        
        Args:
            preference_type: The type of preference to update
            value: The new value for the preference
            
        Returns:
            Confirmation message
        """
        try:
            # Get current user and preferences
            user = await user_service_module.get_user_by_id(self.user_id)
            
            if not user:
                return "I couldn't find your user profile. Please try again later."
            
            # Initialize preferences if not exist
            if not user.preferences:
                user.preferences = UserPreferences(home_airports=[])
            
            # Update the appropriate preference
            if preference_type == "home_airports":
                if isinstance(value, list):
                    user.preferences.home_airports = value
                else:
                    user.preferences.home_airports = [value]
                
                await user_service_module.update_user_preferences(self.user_id, user.preferences)
                return f"I've updated your home airport(s) to {', '.join(user.preferences.home_airports)}."
            
            elif preference_type == "add_destination":
                if not isinstance(value, dict):
                    return "Invalid destination format. Please provide a destination name at minimum."
                
                destination = value.get("destination", "")
                if not destination:
                    return "Please provide a destination name."
                
                # Create a new travel preference
                new_pref = TravelPreference(
                    destination=destination,
                    flexible_dates=value.get("flexible_dates", True),
                    budget=value.get("budget"),
                    preferred_airlines=value.get("preferred_airlines", [])
                )
                
                # Add to the list
                user.preferences.travel_preferences.append(new_pref)
                
                await user_service_module.update_user_preferences(self.user_id, user.preferences)
                return f"I've added {destination} to your list of preferred destinations."
            
            elif preference_type == "remove_destination":
                destination = value
                
                # Find and remove the destination
                initial_count = len(user.preferences.travel_preferences)
                user.preferences.travel_preferences = [
                    pref for pref in user.preferences.travel_preferences 
                    if pref.destination.lower() != destination.lower()
                ]
                
                if len(user.preferences.travel_preferences) < initial_count:
                    await user_service_module.update_user_preferences(self.user_id, user.preferences)
                    return f"I've removed {destination} from your list of preferred destinations."
                else:
                    return f"I couldn't find {destination} in your list of preferred destinations."
            
            elif preference_type == "preferred_airlines":
                if isinstance(value, list):
                    user.preferences.preferred_airlines = value
                else:
                    user.preferences.preferred_airlines = [value]
                
                await user_service_module.update_user_preferences(self.user_id, user.preferences)
                return f"I've updated your preferred airlines to {', '.join(user.preferences.preferred_airlines)}."
            
            elif preference_type == "seat_class":
                if value.lower() in ["economy", "premium_economy", "business", "first"]:
                    user.preferences.seat_class = value.lower()
                    
                    await user_service_module.update_user_preferences(self.user_id, user.preferences)
                    return f"I've updated your preferred seat class to {user.preferences.seat_class}."
                else:
                    return f"Invalid seat class: {value}. Please choose from economy, premium_economy, business, or first."
            
            else:
                return f"I don't know how to update {preference_type} preferences."
        
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            return f"I encountered an error while updating your preferences: {str(e)}"


def get_travel_crew(user_id: str) -> TravelAgentCrew:
    """
    Factory function to get a travel agent for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        A TravelAgentCrew instance
    """
    return TravelAgentCrew(user_id) 
#!/usr/bin/env python3
"""
Terminal-based testing interface for AI Travel Agent.
This allows for rapid testing of conversation flows without the need for WhatsApp.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Set up environment
os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))

# Import application modules
from app.services.conversation import handle_incoming_message
from app.services.user_service import get_user_by_phone, create_user, update_user_preferences
from app.models.user import UserCreate, UserPreferences, TravelPreference

# Test user phone number
TEST_PHONE = "+1234567890"

async def main():
    """Main function for the terminal testing interface."""
    print("\n=== AI Travel Agent Terminal Testing Interface ===\n")
    
    # Create or get test user
    user = await get_or_create_test_user()
    print(f"Test user: {user.name or 'Unnamed'} ({user.phone_number})")
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting terminal test...")
                break
                
            # Handle special commands
            if user_input.startswith("/"):
                await handle_command(user_input, user.id)
                continue
                
            # Process message through the conversation handler
            print("\nProcessing...")
            response = await handle_incoming_message(TEST_PHONE, user_input)
            
            # Display response
            if response["status"] == "success":
                print(f"\nAI Travel Agent: {response['response']}")
            else:
                print(f"\nError: {response.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            print("\nExiting terminal test...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

async def get_or_create_test_user():
    """Get or create a test user for the terminal interface."""
    # Try to get existing user
    user = await get_user_by_phone(TEST_PHONE)
    
    if user:
        return user
        
    # Create new test user
    user_create = UserCreate(
        phone_number=TEST_PHONE,
        name="Test User"
    )
    
    return await create_user(user_create)

async def handle_command(command: str, user_id: str):
    """Handle special commands for testing."""
    parts = command.split()
    cmd = parts[0].lower()
    
    if cmd == "/help":
        print_help()
    elif cmd == "/setpref":
        await set_test_preferences(user_id)
    elif cmd == "/status":
        await show_user_status(user_id)
    else:
        print(f"Unknown command: {cmd}")
        print_help()

def print_help():
    """Print help information for the terminal interface."""
    print("\nAvailable commands:")
    print("  /help           - Show this help message")
    print("  /setpref        - Set test preferences")
    print("  /status         - Show current user status")
    print("  exit/quit/q     - Exit the terminal test")

async def set_test_preferences(user_id: str):
    """Set test preferences for the user."""
    preferences = UserPreferences(
        home_airports=["JFK", "LGA"],
        travel_preferences=[
            TravelPreference(
                destination="Paris",
                flexible_dates=True,
                budget=1000.0
            ),
            TravelPreference(
                destination="Tokyo",
                flexible_dates=False,
                budget=1500.0
            )
        ],
        preferred_airlines=["Delta", "United"],
        seat_class="economy",
        notification_preferences={
            "enabled": True,
            "frequency": "daily",
            "max_per_day": 3
        }
    )
    
    await update_user_preferences(user_id, preferences)
    print("Test preferences have been set!")

async def show_user_status(user_id: str):
    """Show current user status."""
    user = await get_user_by_phone(TEST_PHONE)
    
    if not user:
        print("User not found")
        return
        
    print("\nUser Status:")
    print(f"ID: {user.id}")
    print(f"Name: {user.name or 'Unnamed'}")
    print(f"Phone: {user.phone_number}")
    print(f"Created: {user.created_at}")
    
    if user.preferences:
        print("\nPreferences:")
        print(f"Home Airports: {', '.join(user.preferences.home_airports)}")
        print(f"Seat Class: {user.preferences.seat_class}")
        print(f"Preferred Airlines: {', '.join(user.preferences.preferred_airlines) or 'None'}")
        
        print("\nTravel Preferences:")
        for i, pref in enumerate(user.preferences.travel_preferences, 1):
            print(f"  {i}. {pref.destination} (Budget: ${pref.budget or 'Not set'}, Flexible: {pref.flexible_dates})")
    else:
        print("\nNo preferences set")

if __name__ == "__main__":
    asyncio.run(main()) 
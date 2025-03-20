#!/usr/bin/env python
"""
Enhanced terminal chat interface for the AI Travel Agent.
This provides a colorful and well-formatted command-line interface to interact with the travel agent.
"""

import asyncio
import os
import uuid
import logging
import re
from dotenv import load_dotenv
from termcolor import colored
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger("travel-agent")

# Import agent and database related services
from app.services.user_service import create_user, get_user_by_id
from app.agents.travel_crew import get_travel_crew

# Initialize Rich console
console = Console()

def extract_links(text):
    """Extract URLs from text and return formatted links."""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    urls = re.findall(url_pattern, text)
    
    # Replace URLs with formatted links in the text
    formatted_text = text
    for url in urls:
        formatted_text = formatted_text.replace(url, f"[link={url}]{url}[/link]")
    
    return formatted_text

def print_welcome():
    """Print a stylish welcome message."""
    console.print(Panel.fit(
        "[bold cyan]🌍 AI TRAVEL AGENT - TERMINAL CHAT[/bold cyan]\n"
        "[green]Your personal assistant for travel planning[/green]",
        border_style="blue",
        padding=(1, 2)
    ))
    console.print("[yellow]Type [bold]'exit'[/bold] to quit the chat.[/yellow]")
    console.print()

async def main():
    """
    Main function to run the enhanced terminal chat interface.
    """
    print_welcome()
    
    # Get or create user
    user_id = os.environ.get("TEST_USER_ID")
    
    if not user_id:
        # Create a test user with a random ID
        user_id = str(uuid.uuid4())
        try:
            await create_user(
                user_id=user_id,
                phone_number="+1234567890",  # Fake phone number for testing
                name="Terminal Test User"
            )
            console.print(f"[green]Created new test user with ID:[/green] [bold]{user_id}[/bold]")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            console.print("[bold red]Failed to create user. Exiting.[/bold red]")
            return
    else:
        # Check if user exists, create if not
        user = await get_user_by_id(user_id)
        if not user:
            try:
                await create_user(
                    user_id=user_id,
                    phone_number="+1234567890",  # Fake phone number for testing
                    name="Terminal Test User"
                )
                console.print(f"[green]Created new test user with ID:[/green] [bold]{user_id}[/bold]")
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                console.print("[bold red]Failed to create user. Exiting.[/bold red]")
                return
        else:
            console.print(f"[green]Using existing user with ID:[/green] [bold]{user_id}[/bold]")
    
    # Create travel agent crew
    travel_crew = get_travel_crew(user_id)
    
    # Check if user has preferences
    user = await get_user_by_id(user_id)
    is_new_user = user is None or not user.preferences
    
    # Main chat loop
    while True:
        # Get user input
        user_input = input(colored("\nYou > ", "green", attrs=["bold"]))
        
        if user_input.lower() in ["exit", "quit"]:
            console.print("[yellow]Goodbye! 👋[/yellow]")
            break
            
        # Process message with travel agent
        with console.status("[blue]AI Travel Agent is thinking...[/blue]"):
            try:
                response = await travel_crew.process_message(
                    message=user_input, 
                    is_new_user=is_new_user,
                    language="English"  # Force English responses
                )
                
                # Extract and format links in the response
                formatted_response = extract_links(response)
                
                # Print the response in a nice panel
                console.print()
                console.print(Panel(
                    Markdown(formatted_response),
                    title="[bold blue]AI Travel Agent[/bold blue]",
                    border_style="blue",
                    expand=False
                ))
                
                # After first message, user is no longer considered new
                is_new_user = False
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                console.print("\n[bold red]AI >[/bold red] Sorry, I encountered an error. Please try again.")

if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main()) 
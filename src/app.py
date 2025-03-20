
import time
import os
import dotenv
from pyfiglet import Figlet
from termcolor import colored

from src.config.dependencies import Dependencies

dotenv.load_dotenv()

dependencies = Dependencies()

async def app():
    """
    Main function to run the Travel Agent application.
    This is a simple console interface for testing the crew.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

    print(colored("Welcome To".center(78), "yellow", attrs=["bold"]))
    time.sleep(1)

    f = Figlet(font='slant')
    header = f.renderText('   Travel Agent')

    # Border with aviation theme
    print("\n" + colored("╔" + "═"*78 + "╗", "cyan", attrs=["bold"]))
    print(colored("║", "cyan", attrs=["bold"]) + colored(header.center(78), "yellow", attrs=["bold"]) + colored("║", "cyan", attrs=["bold"]))
    print(colored("║", "cyan", attrs=["bold"]) + colored("✈️  Kevin & Caio 🌍 ".center(78), "yellow", attrs=["bold"]) + colored("║", "cyan", attrs=["bold"]))
    print(colored("╚" + "═"*78 + "╝", "cyan", attrs=["bold"]))
    
    # Welcome message with aviation theme
    print("\n" + colored("▶ Prepare to take off!", "green", attrs=["bold"]))
    print(colored("  I'm your travel assistant. Where do you want to go today?", "white", attrs=["bold"]))
    print(colored("  I can help finding the best flight options,", "white", attrs=["bold"]))
    print(colored("  and much more! Just tell me what you need.", "white", attrs=["bold"]))
    
    # Tips section
    print("\n" + colored("▶ Tips for Flight Search:", "green", attrs=["bold"]))
    print(colored("  • Origin and destination", "white", attrs=["bold"]))
    print(colored("  • Departure date (and return date, if applicable)", "white", attrs=["bold"]))
    print(colored("  • Number of passengers", "white", attrs=["bold"]))
    
    print("\n" + colored("  Type 'exit' at any time to end the conversation.", "yellow", attrs=["bold"]))
    print(colored("═"*80, "cyan", attrs=["bold"]))

    phone_number = input("\n" + colored("👤 You: Type your phone number (default: 5551999999999)", "blue", attrs=["bold"])) or "5551999999999"
        
    while True:
        # Get user input
        user_message = input("\n" + colored("👤 You: ", "blue", attrs=["bold"]))
        
        if user_message.lower() in ['exit', 'quit', 'bye', 'sair']:
            print("\n" + colored("🤖 Assistant: ", "green", attrs=["bold"]) + 
                  colored("Thank you for using our service! Have a great trip! ✈️", "white", attrs=["bold"]))
            break
        
        # Run the travel agent crew
        try:
            print("\n" + colored("🔍 Processing your message...", "yellow", attrs=["bold"]))
            
            response = await dependencies.message_processor.process(phone_number=phone_number, content=user_message)
            print(response)

            print("\n" + colored("🤖 Assistant: ", "green", attrs=["bold"]))
            
            formatted_response = format_response(response)
            print(formatted_response)
            
            print(colored("─"*80, "cyan", attrs=["bold"]))
            
        except Exception as e:
            print("\n" + colored("❌ Error: ", "red", attrs=["bold"]) + colored(str(e), "white", attrs=["bold"]))
            print(colored("Please try again or contact support.", "white", attrs=["bold"]))

def format_response(response):
    """Format the response with proper styling and structure."""
    lines = response.split('\n')
    result = []
    
    for line in lines:
        # Highlight flight options
        if "Flight Option" in line:
            result.append(colored(line, "cyan", attrs=["bold"]))
        # Highlight prices
        elif "$" in line or "€" in line:
            result.append(colored(line, "green", attrs=["bold"]))
        # Highlight dates and times
        elif any(time_marker in line for time_marker in ["AM", "PM", ":", "departure", "arrival"]):
            result.append(colored(line, "yellow", attrs=["bold"]))
        # Highlight recommendations
        elif any(rec in line.lower() for rec in ["recommend", "best option", "suggestion"]):
            result.append(colored(line, "yellow", attrs=["bold"]))
        # Default formatting
        else:
            result.append(colored(line, "white", attrs=["bold"]))
    
    return "\n".join(result)
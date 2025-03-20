import time
import os
import dotenv
import termcolor
from termcolor import colored
from src.crew_ai.crew import run_travel_agent_crew
from pyfiglet import Figlet

# Load environment variables
dotenv.load_dotenv()

def main():
    """
    Main function to run the Travel Agent application.
    This is a simple console interface for testing the crew.
    """
    # Clear terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    def airplane_animation():
        for i in range(30):
            os.system('cls' if os.name == 'nt' else 'clear')
            spaces = " " * i
            print("\n\n" + spaces + colored("✈️", "yellow", attrs=["bold"]))
            
            time.sleep(0.1)
        
        os.system('cls' if os.name == 'nt' else 'clear')
    
    airplane_animation()
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
        
    chat_history = []
    
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
            
            # Add a spinner or loading animation here if desired
            
            response = run_travel_agent_crew(user_message, chat_history)
            
            # Update chat history
            chat_history.append({"role": "user", "content": user_message})
            chat_history.append({"role": "assistant", "content": response})
            
            # Display the response in a formatted way
            print("\n" + colored("🤖 Assistant: ", "green", attrs=["bold"]))
            
            # Format the response with proper line breaks and highlighting
            formatted_response = format_response(response)
            print(formatted_response)
            
            # Add separator for better readability
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

if __name__ == "__main__":
    main() 
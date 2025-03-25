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

    f = Figlet(font='slant')
    header = f.renderText('   Travel Agent')

    # Border with aviation theme
    print("\n" + colored("╔" + "═"*78 + "╗", "cyan", attrs=["bold"]))
    print(colored("║", "cyan", attrs=["bold"]) + colored(header.center(78), "yellow", attrs=["bold"]) + colored("║", "cyan", attrs=["bold"]))
    print(colored("║", "cyan", attrs=["bold"]) + colored("✈️  Kevin & Caio 🌍 ".center(78), "yellow", attrs=["bold"]) + colored("║", "cyan", attrs=["bold"]))
    print(colored("╚" + "═"*78 + "╝", "cyan", attrs=["bold"]))
    
    # Welcome message with aviation theme
    print("\n" + colored("▶ Prepare-se para decolar!", "green", attrs=["bold"]))
    print(colored("  Sou seu assistente de viagens. Para onde você quer ir hoje?", "white", attrs=["bold"]))
    print(colored("  Posso ajudar a encontrar as melhores opções de voo,", "white", attrs=["bold"]))
    print(colored("  e muito mais! Basta me dizer o que você precisa.", "white", attrs=["bold"]))
    
    # Tips section
    print("\n" + colored("▶ Dicas para Busca de Voos:", "green", attrs=["bold"]))
    print(colored("  • Origem e destino", "white", attrs=["bold"]))
    print(colored("  • Data de partida (e data de retorno, se aplicável)", "white", attrs=["bold"]))
    print(colored("  • Número de passageiros", "white", attrs=["bold"]))
    
    print("\n" + colored("  Digite 'sair' a qualquer momento para encerrar a conversa.", "yellow", attrs=["bold"]))
    print(colored("═"*80, "cyan", attrs=["bold"]))

    phone_number = input("\n" + colored("👤 Você: Digite seu número de telefone (padrão: 5551999999999)", "blue", attrs=["bold"])) or "5551999999999"
        
    while True:
        # Get user input
        user_message = input("\n" + colored("👤 Você: ", "blue", attrs=["bold"]))
        
        if user_message.lower() in ['exit', 'quit', 'bye', 'sair']:
            print("\n" + colored("🤖 Assistente: ", "green", attrs=["bold"]) + 
                  colored("Obrigado por usar nosso serviço! Tenha uma ótima viagem! ✈️", "white", attrs=["bold"]))
            break
        
        # Run the travel agent crew
        try:
            print("\n" + colored("🔍 Processando sua mensagem...", "yellow", attrs=["bold"]))
            
            response = await dependencies.message_processor.process(phone_number=phone_number, content=user_message)
            print("\n" + colored("🤖 Assistente: ", "green", attrs=["bold"]))
            
            formatted_response = format_response(response)
            print(formatted_response)
            
            print(colored("─"*80, "cyan", attrs=["bold"]))
            
        except Exception as e:
            print("\n" + colored("❌ Erro: ", "red", attrs=["bold"]) + colored(str(e), "white", attrs=["bold"]))
            print(colored("Por favor, tente novamente ou entre em contato com o suporte.", "white", attrs=["bold"]))

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
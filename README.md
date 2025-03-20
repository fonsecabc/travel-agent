# AI Travel Agent

A terminal-based AI travel assistant that helps users find flight deals and manage their travel preferences.

## Features

- AI-powered travel agent with natural language understanding
- Flight search and comparison
- User preference management
- Colorful terminal interface with rich formatting

## Technical Stack

- **Backend**: Python
- **AI**: OpenAI GPT models
- **Database**: Firebase Firestore (optional - can run in-memory)
- **UI**: Rich terminal interface with colorful formatting

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file based on `.env.example`
   - Add required API keys:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `SERPER_API_KEY`: Your Serper API key
     - `FIREBASE_CREDENTIALS_PATH`: Path to Firebase credentials JSON (optional)

3. Run the terminal interface:
   ```
   python3 terminal_interface.py
   ```

> **Note**: The application can run without Firebase configuration, using local in-memory storage instead. This is perfect for testing or when you don't need persistent data storage.

## How It Works

The application uses OpenAI's GPT models to understand user queries and provide intelligent responses. The system can search for flights, manage user preferences, and offer travel recommendations.

When searching for flights, the agent communicates with flight search services and returns formatted results, including prices, flight times, and airline information.

## Usage

Simply interact with the agent in natural language. Here are some example queries:

- "Find flights from New York to London next month"
- "What are the cheapest flights to Tokyo in December?"
- "Update my home airport to LAX"
- "Show me business class flights to Paris"

## Development

This project was built using Python with a focus on:
- Natural language processing for query understanding
- Rich terminal interface for improved user experience
- Firebase for stateful data storage
- Modular design for easy extensibility 
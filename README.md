# AI Travel Agent
An AI-powered travel assistant that monitors flight prices and sends personalized flight deals directly to users on WhatsApp.

## Features

- WhatsApp-based travel agent powered by CrewAI
- Autonomous flight search based on user preferences
- Personalized notifications for flight deals
- User profile memory and search history tracking
- Conversational interface for all interactions

> **Current Development Status**: This project is being built incrementally. The current version focuses on core functionality through a terminal interface. WhatsApp integration, notification system, and other features will be implemented in subsequent development phases.

## Technical Stack

- **Backend**: Python with FastAPI (WIP)
- **Database**: Firebase Firestore
- **NLP**: CrewAI for dynamic conversation handling
- **Messaging**: WaAPI for WhatsApp integration (WIP)
- **Flight Data**: fast-flights package for flight search and pricing
- **Deployment**: Firebase Cloud Functions and Hosting (WIP)

## Architecture

This application follows a conversation-first design where user interactions happen through a conversational interface. The CrewAI agent is responsible for:

- User onboarding and preference collection (WIP)
- Understanding and responding to user queries
- Managing flight searches
- Sending personalized deal notifications (WIP)
- Maintaining context across conversations

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/fonsecabc/travel-agent.git
   cd travel-agent
   ```

2. Start environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file based on `.env.example`
   - Add required API keys and configuration:
     - OpenAI API key for CrewAI

5. Setup firebase credentials (optional):
   - Not necessary to test locally, the application can use a mock database
   - To set up Firebase:
      1. Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/)
      2. Generate a service account key from Project Settings > Service Accounts
      3. Save the JSON key as `credentials.json` in the project root directory
      4. The application will automatically connect to a Firestore database named "travel-agent" in your project

6. Run the application:
   ```
   python main.py
   ```

## Flight Search and Price Analysis

The application now uses the `fast-flights` package for flight search and price analysis. The library scrapes flight data from Google Flights and provides real-time pricing without external API keys.

Key points:
1. **Flight Search**: Directly scrapes Google Flights with fallback support.
2. **Price Analysis**: Retrieves current flight prices from Google Flights.
3. **Deal Tracking**: Provides direct booking links for flight reservations. (WIP)

## CrewAI Agent System

The core intelligence is powered by a team of CrewAI agents that work together:

1. **Conversation Agent**: Handles general user interactions
2. **Flight Search Agent**: Specializes in flight search operations

## Project Structure

- `app/`: Main application code
  - `config/`: Configuration files
  - `db/`: Database configuration and operations
  - `models/`: Pydantic models
  - `nlp/`: NLP configuration and operations
    - `agents/`: CrewAI agent definitions
    - `crews/`: CrewAI crew definitions
    - `tasks/`: CrewAI task definitions
    - `tools/`: CrewAI tool definitions
  - `processors/`: Message processing and response formatting
  - `usecases/`: Use case classes
- `main.py`: Entry point for the application

## Development Phases

### Phase 1: Core Functionality ✅
- Basic app structure ✅
- Firebase integration ✅
- CrewAI agent implementation ✅
- Flight search and price analysis integration ✅
- Terminal testing interface ✅

### Phase 2: Expanded Features (WIP)
- Web API implementation with FastAPI
- WhatsApp webhook configuration
- Notification system
- Deal analysis and recording

### Phase 3: Intelligence (WIP)
- Improved conversation handling
- Advanced price prediction
- User preference learning
- Deal quality improvements

### Phase 4: Deployment (WIP)
- Production configuration
- Scheduled deal searching
- Monitoring and analytics 
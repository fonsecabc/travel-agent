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

- **Backend**: Python with FastAPI
- **Database**: Firebase Firestore
- **NLP**: CrewAI for dynamic conversation handling
- **Messaging**: WaAPI for WhatsApp integration
- **Flight Data**: Amadeus API for flight search and pricing
- **Deployment**: Firebase Cloud Functions and Hosting

## Architecture

This application follows a conversation-first design where user interactions happen through a conversational interface. The CrewAI agent is responsible for:

- User onboarding and preference collection
- Understanding and responding to user queries
- Managing flight searches
- Sending personalized deal notifications
- Maintaining context across conversations

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file based on `.env.example`
   - Add required API keys and configuration:
     - OpenAI API key for CrewAI
     - Amadeus API credentials (client ID and secret)
     - Firebase configuration (as a JSON service account key)

3. Run the terminal interface for testing:
   ```
   python terminal_interface.py
   ```

## Amadeus API Integration

The application uses the Amadeus API for flight search and price analysis:

1. **Flight Search**: Search for flights between destinations with flexible date options
2. **Price Analysis**: Analyze if current prices are good deals based on historical data
3. **Deal Tracking**: Save good deals for notification to users

To use the Amadeus API:
1. Sign up for an Amadeus API key at [Amadeus Developers Portal](https://developers.amadeus.com/)
2. Add your credentials to the `.env` file

## CrewAI Agent System

The core intelligence is powered by a team of CrewAI agents that work together:

1. **Conversation Agent**: Handles general user interactions
2. **Search Agent**: Specializes in flight search operations
3. **Recommendation Agent**: Analyzes deals and makes recommendations
4. **Onboarding Agent**: Guides new users through setup process

## Firebase Configuration

The application uses Firebase Firestore for data storage. Firebase authentication works as follows:

1. **Default Method**: By default, the application looks for a `firebase-credentials.json` file in the project root directory.
2. **Environment Variable**: If the root file is not found, it checks for the `FIREBASE_CREDENTIALS_PATH` environment variable pointing to a credentials file.

To set up Firebase:
1. Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/)
2. Generate a service account key from Project Settings > Service Accounts
3. Save the JSON key as `firebase-credentials.json` in the project root directory
4. The application will automatically connect to a Firestore database named "travel-agent" in your project

> Note: Ensure your Firebase project has Firestore enabled before running the application.

## Project Structure

- `app/`: Main application code
  - `models/`: Pydantic models
  - `services/`: Business logic services
  - `db/`: Database configuration and operations
  - `agents/`: CrewAI agent definitions
- `terminal_interface.py`: Terminal interface for testing

## Development Phases

### Phase 1: Core Functionality ✅
- Basic app structure
- Firebase integration
- CrewAI agent implementation 
- Amadeus flight service integration
- Terminal testing interface

### Phase 2: Expanded Features (Upcoming)
- Web API implementation with FastAPI
- WhatsApp webhook configuration
- Notification system
- Deal analysis and recording

### Phase 3: Intelligence (Upcoming)
- Improved conversation handling
- Advanced price prediction
- User preference learning
- Deal quality improvements

### Phase 4: Deployment (Upcoming)
- Production configuration
- Scheduled deal searching
- Monitoring and analytics 
# LangChain Conversational Chatbot using Relational Database
This repository contains a Streamlit application that enables users to interact with a conversational chatbot powered by the LangChain API and Groq. The application leverages Groq's high-performance inference capabilities to generate responses while maintaining conversation history for contextual interactions.

## Features
- **Conversational Interface**: Clean chat interface for natural interactions with the AI
- **Contextual Responses**: Maintains conversation history to provide relevant contextual responses
- **Multiple LLM Support**: Choose between different Groq models including:
  - Mixtral-8x7B
  - Gemma-7B
  - Deepseek-70B
- **Database-Augmented Generation using SQL**: Database-Augmented Generation using:
  - PostgreSQL for storing structured data
  - Dynamic knowledge integration into responses

## Installation

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Groq API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/abhiyankhanal/groq-langchain-chatbot.git
cd groq-langchain-chatbot
```

2. Create and activate virtual environment:
```bash
# For Unix/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install required dependencies
```bash
pip install -r requirements.txt
```

4. Setup environemnt variables
```bash
# Create .env file
cp .env.example .env
```

- Add your credentials to .env file
```
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

5. Set up the database:
```bash
docker compose up
```

6. Run the application
```bash
streamlit run app.py
```

7. You can run the migration and seed according to your requirements.

## Screenshots
1. Deepseek thinking
![alt text](deepseek-think.png)

2. Deepseek results
![alt text](deepseek-result.png)




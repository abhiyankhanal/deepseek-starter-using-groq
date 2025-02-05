import re
import streamlit as st
from langchain_groq import ChatGroq
from chat_message import ChatMessage
from chatbot_config import ChatbotConfig
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from typing import Any, Dict, List, Optional, Union

from database_config import DatabaseConfig
from langchain.prompts import PromptTemplate

class ChatInterface:
    """Class to handle the chat interface"""
    def __init__(self, config: ChatbotConfig) -> None:
        self.config = config
        self.db_config = DatabaseConfig()  # Initialize database configuration
        self.memory = ConversationBufferWindowMemory(
            k=config.memory_length,
            memory_key="chat_history",
            return_messages=True
        )
        self.groq_chat = ChatGroq(
            groq_api_key=config.api_key,
            model_name=config.selected_model
        )
        self.db_schema = config.db_schema

    def setup_ui(self) -> None:
        """Setup the main UI components"""
    col1, col2 = st.columns([4, 2])  # Less extreme ratio

    with col1:
        st.title("Hello!")
        st.markdown("""  
            You can feed your schema in `migration.sql` and play around with the code for amazing results!
        """)


    def initialize_session_state(self) -> None:
        """Initialize or update session state"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        else:
            for message in st.session_state.chat_history:
                self.memory.save_context(
                    {'input': message.human},
                    {'output': message.AI}
                )

    def create_conversation_chain(self) -> LLMChain:
        """Create the conversation chain with prompt template"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.config.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ])

        return LLMChain(
            llm=self.groq_chat,
            prompt=prompt,
            verbose=True,
            memory=self.memory
        )

    def create_sql_query_chain(self) -> LLMChain:
        """Create a chain for generating SQL queries"""
        sql_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""You are a SQL expert. You will generate PostgreSQL queries based on the following schema:

    {self.db_schema}

    Important rules:
    1. Generate ONLY the SQL query, nothing else
    2. Always include semicolon at the end of queries
    3. Only use columns that exist in the schema
    4. Use proper PostgreSQL syntax
    5. Always start with SELECT (not with comments or explanations)
    6. Don't include markdown formatting or code blocks

    Example format:
    SELECT column1, column2 FROM table WHERE condition;"""),
            HumanMessagePromptTemplate.from_template("{question}")
        ])

        return LLMChain(
            llm=self.groq_chat,
            prompt=sql_prompt,
            verbose=True
        )


    def analyze_and_execute_query(self, user_question: str) -> Dict[str, Any]:
        """Analyze user input, generate and execute SQL query if needed"""
        # Check if the question is about hotels
        hotel_keywords = ['hotel', 'room', 'price', 'night', 'stay', 'accommodation']
        is_hotel_query = any(keyword in user_question.lower() for keyword in hotel_keywords)

        if not is_hotel_query:
            return {
                "type": "general",
                "response": None
            }

        try:
            # Generate SQL query with more specific prompt
            sql_chain = self.create_sql_query_chain()
            generated_query = sql_chain.predict(question=f"""
            Using this schema:
            {self.db_schema}
            
            Generate a SQL query for PostgreSQL to answer: {user_question}
            
            Rules:
            - Return ONLY the SQL query using pagination lim=5
            - Include semicolon at the end
            - Use proper SQL syntax
            - Only use existing columns from the schema
            """)

            print(f'Results here: {generated_query}')
                
            generated_query = self.remove_think_tags(generated_query)

            print(f'generated_query after removing think: {generated_query}')

            generated_query = (
                generated_query
                .strip()                     # Remove leading/trailing whitespace
                .replace('\n', ' ')          # Replace newlines with spaces
                .replace('```sql', '')       # Remove SQL code block markers
                .replace('```', '')          # Remove code block markers
                .replace('\\_', '_')         # Unescape underscores
                .replace('\_', '_')          # Alternative escape pattern for underscores
            )

            # Verify if the response looks like SQL
            if not any(generated_query.upper().startswith(prefix) for prefix in ('SELECT')):
                return {
                    "type": "error",
                    "error": "Failed to generate valid SQL query, the model may have returned <think> as well"
                }

            # Log the query for debugging (optional)
            print(f"Executing query: {generated_query}")

            # Execute the query
            try:
                results = self.db_config.execute_query(generated_query)

                # If no results but query executed successfully
                if not results and generated_query.upper().startswith('SELECT'):
                    return {
                        "type": "tour_query",
                        "query": generated_query,
                        "results": [],
                        "message": "No results found"
                    }

                return {
                    "type": "tour_query",
                    "query": generated_query,
                    "results": results
                }

            except Exception as db_error:
                return {
                    "type": "error",
                    "error": f"Database error: {str(db_error)}"
                }

        except Exception as e:
            print({
                "type": "error",
                "error": f"Query generation error: {str(e)}"
            }
)
            return {
                "type": "error",
                "error": f"Query generation error: {str(e)}"
            }

    def remove_think_tags(self, text: str) -> str:
        """
        Remove multiline <think> tags and their content, then clean up whitespace.
        
        Args:
            text (str): Input text that may contain multiline <think> tags
            
        Returns:
            str: Cleaned text with tags removed and whitespace normalized
        """
        # Handle multiline think tags with any content between them
        pattern = r'<think>[\s\S]*?</think>'
        
        if '<think>' in text:
            # Remove think tags and their content, handling multiline content
            cleaned_text = re.sub(pattern, '', text)
            # Normalize whitespace: remove extra spaces, newlines, and tabs
            cleaned_text = ' '.join(cleaned_text.split())
            return cleaned_text.strip()
        
        # If no think tags, just normalize whitespace
        return ' '.join(text.split()).strip()
    
    def process_user_input(self, user_question: str) -> Union[str, Dict[str, Any]]:
        """Process user input and return response"""
        if not user_question:
            return None

        try:
            # Analyze and potentially execute SQL query
            query_result = self.analyze_and_execute_query(user_question)

            if query_result["type"] == "tour_query":
                # Format the database results into a natural language response
                conversation = self.create_conversation_chain()
                
                if not query_result.get('results'):
                    context = f"""
                    The user asked: {user_question}
                    No results were found in the database.
                    Please provide a friendly response indicating that no matching records were found.
                    """
                else:
                    context = f"""
                    The user asked: {user_question}
                    Database query results: {query_result['results']}
                    Please provide a natural language response based on these results.
                    """
                
                natural_response = conversation.predict(human_input=context)
                
                # Store in chat history
                message = ChatMessage(human=user_question, AI=natural_response)
                st.session_state.chat_history.append(message)
                
                # Return structured response
                return {
                    "type": "tour_query",
                    "query": query_result["query"],
                    "results": query_result.get('results', []),
                    "response": natural_response
                }


            elif query_result["type"] == "error":
                error_message = f"I apologize, but I encountered an error: {query_result['error']}"
                message = ChatMessage(human=user_question, AI=error_message)
                st.session_state.chat_history.append(message)
                return {
                    "type": "error",
                    "error": error_message
                }
            else:
                # Handle non-hotel related questions with regular conversation
                conversation = self.create_conversation_chain()
                response = conversation.predict(human_input=user_question)
                
                # Store in chat history
                message = ChatMessage(human=user_question, AI=response)
                st.session_state.chat_history.append(message)
                
                return {
                    "type": "general",
                    "response": response
                }

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            message = ChatMessage(human=user_question, AI=error_message)
            st.session_state.chat_history.append(message)
            return {
                "type": "error",
                "error": error_message
            }

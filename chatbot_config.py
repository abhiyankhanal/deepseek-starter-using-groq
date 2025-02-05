import os
import streamlit as st
from typing import List
from environment_manager import EnvironmentManager


class ChatbotConfig:
    def __init__(self):
        EnvironmentManager.load_environment()
        self.api_key = EnvironmentManager.get_env_var("GROQ_API_KEY")
        self.memory_length = 5
        self.selected_model = "deepseek-r1-distill-llama-70b"
        self.system_prompt = self.get_system_prompt()
        self.db_schema = self.get_db_schema() 

    
    def get_system_prompt(self) -> str:
        """Return the system prompt"""
        return """You are a hotel guide."""

    def get_db_schema(self) -> str:
        """Return the database schema from migration.sql file"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            migration_file = os.path.join(current_dir, 'migration.sql')
            
            with open(migration_file, 'r') as file:
                content = file.read()
                
                up_markers = ['-- Up Migration']
                down_markers = ['-- Down Migration']
                
                start_index = -1
                for marker in up_markers:
                    if marker in content:
                        start_index = content.find(marker)
                        break
                        
                end_index = len(content)
                for marker in down_markers:
                    if marker in content:
                        end_index = content.find(marker)
                        break
                
                if start_index == -1:
                    raise ValueError("Could not find UP migration section")
                    
                schema = content[start_index:end_index].strip()
                
                for marker in up_markers:
                    schema = schema.replace(marker, '').strip()
                    
                return schema
                
        # except FileNotFoundError:
        #      # Fallback schema here
        #     return """
        #     CREATE TABLE hotel (
        #         id SERIAL PRIMARY KEY,
        #         name VARCHAR(255) NOT NULL,
        #         description TEXT,
        #         price_per_night DECIMAL(10,2) NOT NULL
        #     );
        #     """
        except Exception as e:
            print(f"Error reading migration file: {str(e)}")
            return None

    def setup_sidebar(self) -> None:
        with st.sidebar:
            st.text_input("API Key:", value=self.api_key, key="api_key", type="password")
            self.memory_length = st.slider("Memory Length:", min_value=1, max_value=10, value=5)
            self.selected_model = st.selectbox(
            "Select Model:",
            ["mixtral-8x7b-32768", "deepseek-r1-distill-llama-70b", "gemma2-9b-it", "llama-3.1-8b-instant"]

            )

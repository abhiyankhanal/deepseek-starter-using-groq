import streamlit as st
from chatbot_config import ChatbotConfig
from environment_manager import EnvironmentManager


import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict, Any
import streamlit as st
from contextlib import contextmanager

class DatabaseConfig:
    """Configuration class for database connection"""
    def __init__(self) -> None:
        self.host = EnvironmentManager.get_env_var("POSTGRES_HOST")
        self.port = EnvironmentManager.get_env_var("POSTGRES_PORT")
        self.database = EnvironmentManager.get_env_var("POSTGRES_DB")
        self.user = EnvironmentManager.get_env_var("POSTGRES_USER")
        self.password = EnvironmentManager.get_env_var("POSTGRES_PASSWORD")
        self._connection = None

    def get_connection_string(self) -> str:
        """Generate PostgreSQL connection string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters as a dictionary"""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password
        }

    def create_connection(self) -> psycopg2.extensions.connection:
        """Create a new database connection"""
        try:
            connection = psycopg2.connect(**self.get_connection_params())
            return connection
        except psycopg2.Error as e:
            st.error(f"Error connecting to database: {e}")
            raise

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = self.create_connection()
            yield conn
        finally:
            if conn is not None:
                conn.close()

    @contextmanager
    def get_db_cursor(self, cursor_factory=RealDictCursor):
        """Context manager for database cursors"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()

    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict[str, Any]]]:
        """Execute a SQL query and return results"""
        try:
            with self.get_db_cursor() as cursor:
                # Ensure the query is properly formatted
                query = query.strip()
                if not query.endswith(';'):
                    query += ';'
                    
                cursor.execute(query, params)
                
                # For SELECT queries, return the results
                if cursor.description:
                    return cursor.fetchall()
                
                # For other queries (INSERT, UPDATE, DELETE), return None
                return None
                
        except psycopg2.Error as e:
            st.error(f"Database error: {e}")
            raise

                
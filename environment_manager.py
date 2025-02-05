import os
from pathlib import Path
from dotenv import load_dotenv


class EnvironmentManager:
    """Manages environment variables and configuration"""
    @staticmethod
    def load_environment() -> None:
        """Load environment variables from .env file"""
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)

    @staticmethod
    def get_env_var(key_name: str) -> str:
        """Get API key from environment variables
        Args:
            key_name: Name of the environment variable to retrieve
        """
        api_key = os.environ.get(key_name)
        if not api_key:
            raise ValueError(f"{key_name} not found in environment variables")
        return api_key

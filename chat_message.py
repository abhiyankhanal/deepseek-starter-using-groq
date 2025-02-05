from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Data class for chat messages"""
    human: str
    AI: str
"""
MemCore - A Hierarchical Memory System for AI Agents
"""

from .core.memory import MemoryManager, CoreMemory, RecallMemory, ArchivalMemory
from .core.types import Message, MessageType, MemoryType, MemoryEntry, CoreMemoryBlock
from .storage.base import MemoryStorage
from .storage.in_memory import InMemoryStorage

__version__ = "0.1.0"
__all__ = [
    "MemoryManager",
    "CoreMemory",
    "RecallMemory",
    "ArchivalMemory",
    "Message",
    "MessageType",
    "MemoryType",
    "MemoryEntry",
    "CoreMemoryBlock",
    "MemoryStorage",
    "InMemoryStorage",
]
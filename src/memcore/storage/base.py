"""
Memory Storage Interface
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ..core.types import MemoryEntry, MemoryType


class MemoryStorage(ABC):
    """Abstract base class for memory storage backends"""

    @abstractmethod
    def save(self, entry: MemoryEntry) -> str:
        """Save a memory entry, return its ID"""
        pass

    @abstractmethod
    def load(self, entry_id: str) -> Optional[MemoryEntry]:
        """Load a memory entry by ID"""
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry"""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        """Search for entries"""
        pass

    @abstractmethod
    def list_all(self, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        """List all entries, optionally filtered by type"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all entries"""
        pass
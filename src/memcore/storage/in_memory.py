"""
In-Memory Storage Implementation
"""

from typing import Optional, List, Dict, Any
from ..core.types import MemoryEntry, MemoryType
from .base import MemoryStorage


class InMemoryStorage(MemoryStorage):
    """Simple in-memory storage backend"""

    def __init__(self):
        self._entries: Dict[str, MemoryEntry] = {}

    def save(self, entry: MemoryEntry) -> str:
        self._entries[entry.id] = entry
        return entry.id

    def load(self, entry_id: str) -> Optional[MemoryEntry]:
        return self._entries.get(entry_id)

    def delete(self, entry_id: str) -> bool:
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False

    def search(self, query: str, limit: int = 10, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        results = []
        query_lower = query.lower()

        for entry in self._entries.values():
            if memory_type and entry.memory_type != memory_type:
                continue
            if query_lower in entry.content.lower():
                results.append(entry)
                if len(results) >= limit:
                    break

        return results

    def list_all(self, memory_type: Optional[MemoryType] = None) -> List[MemoryEntry]:
        if memory_type:
            return [e for e in self._entries.values() if e.memory_type == memory_type]
        return list(self._entries.values())

    def clear(self) -> None:
        self._entries.clear()

    def count(self) -> int:
        return len(self._entries)
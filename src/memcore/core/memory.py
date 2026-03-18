"""
Core Memory Components

Implements the three-tier memory architecture:
- Core Memory: Limited capacity, stores essential context
- Recall Memory: Conversation history
- Archival Memory: Long-term semantic storage
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import json
import uuid

from .types import MemoryType, MemoryEntry, Message, MessageType, CoreMemoryBlock


class CoreMemory:
    """
    Core Memory - Limited capacity storage for essential context.

    This is the "working memory" of the agent, containing information
    that should always be available. Like human working memory, it has
    limited capacity and should only store the most important information.
    """

    def __init__(self, max_blocks: int = 10, max_tokens: int = 2000):
        self._blocks: Dict[str, CoreMemoryBlock] = {}
        self._max_blocks = max_blocks
        self._max_tokens = max_tokens
        self._order: List[str] = []

    def add(self, label: str, content: str, priority: int = 0) -> str:
        """Add a new block to core memory"""
        if len(self._blocks) >= self._max_blocks:
            self._evict_lowest_priority()

        block_id = str(uuid.uuid4())[:8]
        block = CoreMemoryBlock(label=label, content=content, priority=priority)
        self._blocks[block_id] = block
        self._order.append(block_id)
        return block_id

    def update(self, block_id: str, content: str) -> bool:
        """Update a block's content"""
        if block_id not in self._blocks:
            return False
        self._blocks[block_id].content = content
        return True

    def delete(self, block_id: str) -> bool:
        """Delete a block from core memory"""
        if block_id not in self._blocks:
            return False
        del self._blocks[block_id]
        self._order.remove(block_id)
        return True

    def get(self, block_id: str) -> Optional[CoreMemoryBlock]:
        """Get a block by ID"""
        return self._blocks.get(block_id)

    def find_by_label(self, label: str) -> Optional[CoreMemoryBlock]:
        """Find a block by its label"""
        for block in self._blocks.values():
            if block.label == label:
                return block
        return None

    def list_all(self) -> List[CoreMemoryBlock]:
        """List all blocks in order"""
        return [self._blocks[bid] for bid in self._order if bid in self._blocks]

    def to_prompt(self) -> str:
        """Format core memory as a prompt for the LLM"""
        lines = ["### CORE MEMORY ###"]
        for block in self.list_all():
            lines.append(f"[{block.label}] {block.content}")
        lines.append("### END CORE MEMORY ###")
        return "\n".join(lines)

    def _evict_lowest_priority(self) -> None:
        """Remove the lowest priority block when at capacity"""
        if not self._blocks:
            return

        min_priority = float('inf')
        min_id = None
        for bid, block in self._blocks.items():
            if block.priority < min_priority:
                min_priority = block.priority
                min_id = bid

        if min_id:
            self.delete(min_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blocks": {bid: block.to_dict() for bid, block in self._blocks.items()},
            "order": self._order,
            "max_blocks": self._max_blocks,
            "max_tokens": self._max_tokens
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoreMemory":
        memory = cls(max_blocks=data.get("max_blocks", 10), max_tokens=data.get("max_tokens", 2000))
        memory._blocks = {bid: CoreMemoryBlock.from_dict(block) for bid, block in data.get("blocks", {}).items()}
        memory._order = data.get("order", [])
        return memory


class RecallMemory:
    """
    Recall Memory - Conversation history storage.

    Stores the full history of interactions, allowing the agent to
    "recall" previous conversations. This is like episodic memory in humans.
    """

    def __init__(self, max_messages: int = 1000):
        self._messages: List[Message] = []
        self._max_messages = max_messages

    def add(self, role: MessageType, content: str, name: Optional[str] = None, metadata: Optional[Dict] = None) -> Message:
        """Add a message to recall memory"""
        if len(self._messages) >= self._max_messages:
            self._messages = self._messages[-self._max_messages + 1:]

        message = Message(
            role=role,
            content=content,
            name=name,
            metadata=metadata or {}
        )
        self._messages.append(message)
        return message

    def get_recent(self, n: int = 10) -> List[Message]:
        """Get the n most recent messages"""
        return self._messages[-n:]

    def search(self, query: str, limit: int = 10) -> List[Message]:
        """Simple text search through messages"""
        results = []
        query_lower = query.lower()
        for msg in reversed(self._messages):
            if query_lower in msg.content.lower():
                results.append(msg)
                if len(results) >= limit:
                    break
        return results

    def get_all(self) -> List[Message]:
        """Get all messages"""
        return self._messages.copy()

    def to_openai_messages(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Convert to OpenAI message format"""
        messages = self._messages[-limit:] if limit else self._messages
        return [msg.to_openai_format() for msg in messages]

    def clear(self) -> None:
        """Clear all messages"""
        self._messages = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "messages": [msg.to_dict() for msg in self._messages],
            "max_messages": self._max_messages
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecallMemory":
        memory = cls(max_messages=data.get("max_messages", 1000))
        memory._messages = [Message.from_dict(msg) for msg in data.get("messages", [])]
        return memory


class ArchivalMemory:
    """
    Archival Memory - Long-term semantic storage.

    Stores information for long-term retrieval. Unlike core and recall memory,
    archival memory can store unlimited information but requires explicit
    search to access. This is like semantic memory in humans.

    Can be backed by vector stores for semantic search.
    """

    def __init__(self):
        self._entries: Dict[str, MemoryEntry] = {}
        self._search_func: Optional[Callable] = None

    def add(self, content: str, metadata: Optional[Dict] = None) -> str:
        """Add an entry to archival memory"""
        entry_id = str(uuid.uuid4())
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            memory_type=MemoryType.ARCHIVAL,
            metadata=metadata or {}
        )
        self._entries[entry_id] = entry
        return entry_id

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get an entry by ID"""
        return self._entries.get(entry_id)

    def delete(self, entry_id: str) -> bool:
        """Delete an entry"""
        if entry_id not in self._entries:
            return False
        del self._entries[entry_id]
        return True

    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search for entries (simple text matching by default)"""
        results = []
        query_lower = query.lower()
        for entry in self._entries.values():
            if query_lower in entry.content.lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def list_all(self) -> List[MemoryEntry]:
        """List all entries"""
        return list(self._entries.values())

    def count(self) -> int:
        """Count total entries"""
        return len(self._entries)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entries": {eid: entry.to_dict() for eid, entry in self._entries.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArchivalMemory":
        memory = cls()
        memory._entries = {eid: MemoryEntry.from_dict(entry) for eid, entry in data.get("entries", {}).items()}
        return memory


class MemoryManager:
    """
    Central manager for the three-tier memory system.

    Coordinates Core, Recall, and Archival memory components.
    """

    def __init__(
        self,
        core_max_blocks: int = 10,
        recall_max_messages: int = 1000
    ):
        self.core = CoreMemory(max_blocks=core_max_blocks)
        self.recall = RecallMemory(max_messages=recall_max_messages)
        self.archival = ArchivalMemory()

    def add_core_memory(self, label: str, content: str, priority: int = 0) -> str:
        """Add to core memory"""
        return self.core.add(label, content, priority)

    def add_message(self, role: MessageType, content: str, name: Optional[str] = None) -> Message:
        """Add a message to recall memory"""
        return self.recall.add(role, content, name)

    def user_message(self, content: str) -> Message:
        """Add a user message"""
        return self.add_message(MessageType.USER, content)

    def assistant_message(self, content: str) -> Message:
        """Add an assistant message"""
        return self.add_message(MessageType.ASSISTANT, content)

    def system_message(self, content: str) -> Message:
        """Add a system message"""
        return self.add_message(MessageType.SYSTEM, content)

    def archive(self, content: str, metadata: Optional[Dict] = None) -> str:
        """Store in archival memory"""
        return self.archival.add(content, metadata)

    def get_context_for_prompt(self, include_recall: int = 10) -> str:
        """Build context string for LLM prompt"""
        parts = [self.core.to_prompt()]

        if include_recall > 0 and self.recall.get_all():
            parts.append("\n### RECENT CONVERSATION ###")
            for msg in self.recall.get_recent(include_recall):
                role_name = msg.role.value.upper()
                parts.append(f"{role_name}: {msg.content}")
            parts.append("### END CONVERSATION ###")

        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "core": self.core.to_dict(),
            "recall": self.recall.to_dict(),
            "archival": self.archival.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryManager":
        manager = cls()
        manager.core = CoreMemory.from_dict(data.get("core", {}))
        manager.recall = RecallMemory.from_dict(data.get("recall", {}))
        manager.archival = ArchivalMemory.from_dict(data.get("archival", {}))
        return manager

    def save(self, filepath: str) -> None:
        """Save memory state to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> "MemoryManager":
        """Load memory state from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
"""
Memory Types and Data Structures
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json


class MemoryType(Enum):
    """Types of memory in the hierarchy"""
    CORE = "core"        # Limited, important context
    RECALL = "recall"    # Conversation history
    ARCHIVAL = "archival"  # Long-term storage


class MessageType(Enum):
    """Types of messages in recall memory"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


@dataclass
class MemoryEntry:
    """Base memory entry"""
    id: str
    content: str
    memory_type: MemoryType
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class Message:
    """A message in recall memory"""
    role: MessageType
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "name": self.name,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=MessageType(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            name=data.get("name"),
            metadata=data.get("metadata", {})
        )

    def to_openai_format(self) -> Dict[str, str]:
        """Convert to OpenAI API format"""
        result = {"role": self.role.value, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


@dataclass
class CoreMemoryBlock:
    """A block in core memory with a label"""
    label: str
    content: str
    priority: int = 0  # Higher priority = more important

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "content": self.content,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoreMemoryBlock":
        return cls(
            label=data["label"],
            content=data["content"],
            priority=data.get("priority", 0)
        )
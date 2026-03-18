"""
Tests for MemCore Memory System
"""

import pytest
import tempfile
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from memcore import (
    MemoryManager, CoreMemory, RecallMemory, ArchivalMemory,
    Message, MessageType, MemoryType, CoreMemoryBlock,
    InMemoryStorage, MemoryEntry
)


class TestCoreMemory:
    """Test CoreMemory functionality"""

    def test_add_block(self):
        memory = CoreMemory()
        block_id = memory.add("user_info", "Name: Alice", priority=1)
        assert block_id in memory._blocks
        assert memory.find_by_label("user_info").content == "Name: Alice"

    def test_max_blocks_limit(self):
        memory = CoreMemory(max_blocks=3)
        memory.add("block1", "content1")
        memory.add("block2", "content2")
        memory.add("block3", "content3")
        memory.add("block4", "content4")  # Should evict lowest priority

        assert len(memory._blocks) == 3

    def test_update_block(self):
        memory = CoreMemory()
        block_id = memory.add("test", "original")
        memory.update(block_id, "updated")
        assert memory.get(block_id).content == "updated"

    def test_delete_block(self):
        memory = CoreMemory()
        block_id = memory.add("test", "content")
        assert memory.delete(block_id) is True
        assert memory.get(block_id) is None

    def test_to_prompt(self):
        memory = CoreMemory()
        memory.add("user", "Alice")
        memory.add("task", "Testing")
        prompt = memory.to_prompt()
        assert "CORE MEMORY" in prompt
        assert "[user]" in prompt
        assert "Alice" in prompt

    def test_serialization(self):
        memory = CoreMemory()
        memory.add("user", "Alice", priority=1)
        data = memory.to_dict()
        restored = CoreMemory.from_dict(data)
        assert len(restored._blocks) == 1
        assert restored.find_by_label("user").content == "Alice"


class TestRecallMemory:
    """Test RecallMemory functionality"""

    def test_add_message(self):
        memory = RecallMemory()
        msg = memory.add(MessageType.USER, "Hello")
        assert msg.role == MessageType.USER
        assert msg.content == "Hello"

    def test_get_recent(self):
        memory = RecallMemory()
        memory.add(MessageType.USER, "msg1")
        memory.add(MessageType.ASSISTANT, "msg2")
        memory.add(MessageType.USER, "msg3")

        recent = memory.get_recent(2)
        assert len(recent) == 2
        assert recent[0].content == "msg2"
        assert recent[1].content == "msg3"

    def test_search(self):
        memory = RecallMemory()
        memory.add(MessageType.USER, "What is Python?")
        memory.add(MessageType.ASSISTANT, "Python is a programming language")
        memory.add(MessageType.USER, "What is JavaScript?")

        results = memory.search("Python")
        assert len(results) == 2

    def test_to_openai_format(self):
        memory = RecallMemory()
        memory.add(MessageType.USER, "Hello")
        memory.add(MessageType.ASSISTANT, "Hi there!")

        messages = memory.to_openai_messages()
        assert messages[0] == {"role": "user", "content": "Hello"}
        assert messages[1] == {"role": "assistant", "content": "Hi there!"}

    def test_serialization(self):
        memory = RecallMemory()
        memory.add(MessageType.USER, "Hello")
        data = memory.to_dict()
        restored = RecallMemory.from_dict(data)
        assert len(restored.get_all()) == 1


class TestArchivalMemory:
    """Test ArchivalMemory functionality"""

    def test_add_entry(self):
        memory = ArchivalMemory()
        entry_id = memory.add("Important fact to remember")
        assert entry_id in memory._entries

    def test_search(self):
        memory = ArchivalMemory()
        memory.add("Python was created by Guido van Rossum")
        memory.add("JavaScript was created by Brendan Eich")
        memory.add("Python is great for AI")

        results = memory.search("Python")
        assert len(results) == 2

    def test_delete(self):
        memory = ArchivalMemory()
        entry_id = memory.add("Test content")
        assert memory.delete(entry_id) is True
        assert memory.count() == 0

    def test_count(self):
        memory = ArchivalMemory()
        memory.add("Entry 1")
        memory.add("Entry 2")
        memory.add("Entry 3")
        assert memory.count() == 3


class TestMemoryManager:
    """Test MemoryManager"""

    def test_initialization(self):
        manager = MemoryManager()
        assert manager.core is not None
        assert manager.recall is not None
        assert manager.archival is not None

    def test_convenience_methods(self):
        manager = MemoryManager()
        manager.user_message("Hello")
        manager.assistant_message("Hi!")
        manager.system_message("System initialized")

        messages = manager.recall.get_all()
        assert len(messages) == 3

    def test_archive_method(self):
        manager = MemoryManager()
        manager.archive("Important fact", {"source": "user"})
        assert manager.archival.count() == 1

    def test_get_context_for_prompt(self):
        manager = MemoryManager()
        manager.add_core_memory("user", "Alice")
        manager.user_message("Hello")

        context = manager.get_context_for_prompt()
        assert "CORE MEMORY" in context
        assert "RECENT CONVERSATION" in context

    def test_save_and_load(self):
        manager = MemoryManager()
        manager.add_core_memory("user", "Alice")
        manager.user_message("Hello")
        manager.archive("Important fact")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            manager.save(filepath)
            loaded = MemoryManager.load(filepath)

            assert len(loaded.core._blocks) == 1
            assert len(loaded.recall.get_all()) == 1
            assert loaded.archival.count() == 1
        finally:
            os.unlink(filepath)


class TestMessage:
    """Test Message class"""

    def test_message_creation(self):
        msg = Message(role=MessageType.USER, content="Hello")
        assert msg.role == MessageType.USER
        assert msg.content == "Hello"

    def test_to_openai_format(self):
        msg = Message(role=MessageType.USER, content="Hello", name="Alice")
        result = msg.to_openai_format()
        assert result == {"role": "user", "content": "Hello", "name": "Alice"}

    def test_serialization(self):
        msg = Message(role=MessageType.ASSISTANT, content="Hi!")
        data = msg.to_dict()
        restored = Message.from_dict(data)
        assert restored.role == MessageType.ASSISTANT
        assert restored.content == "Hi!"


class TestInMemoryStorage:
    """Test InMemoryStorage"""

    def test_save_and_load(self):
        storage = InMemoryStorage()
        entry = MemoryEntry(
            id="test-id",
            content="Test content",
            memory_type=MemoryType.ARCHIVAL
        )
        storage.save(entry)
        loaded = storage.load("test-id")
        assert loaded.content == "Test content"

    def test_search(self):
        storage = InMemoryStorage()
        storage.save(MemoryEntry(id="1", content="Python programming", memory_type=MemoryType.ARCHIVAL))
        storage.save(MemoryEntry(id="2", content="JavaScript development", memory_type=MemoryType.ARCHIVAL))

        results = storage.search("Python")
        assert len(results) == 1

    def test_delete(self):
        storage = InMemoryStorage()
        storage.save(MemoryEntry(id="test", content="content", memory_type=MemoryType.ARCHIVAL))
        assert storage.delete("test") is True
        assert storage.load("test") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
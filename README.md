# MemCore - Hierarchical Memory System for AI Agents

A Python implementation of a three-tier memory architecture inspired by MemGPT, designed to give AI agents human-like memory capabilities.

## Architecture

MemCore implements three types of memory:

### Core Memory
- **Limited capacity** working memory
- Stores essential context that should always be available
- Like human working memory - small but critical

### Recall Memory
- **Conversation history** storage
- Full history of user-assistant interactions
- Like human episodic memory

### Archival Memory
- **Long-term** semantic storage
- Unlimited capacity, explicit search required
- Like human semantic memory

## Installation

```bash
pip install memcore
```

For vector search support:

```bash
pip install memcore[vector]
```

## Quick Start

```python
from memcore import MemoryManager, MessageType

# Initialize memory manager
manager = MemoryManager()

# Add to core memory (always available)
manager.add_core_memory("user_profile", "Name: Alice, Role: Developer")

# Add messages to recall memory
manager.user_message("What's the weather today?")
manager.assistant_message("I don't have access to real-time weather data.")

# Archive important information
manager.archive("User prefers concise responses", {"source": "preference"})

# Get context for LLM prompt
context = manager.get_context_for_prompt()
print(context)
```

## Core Memory Operations

```python
from memcore import CoreMemory

core = CoreMemory(max_blocks=10)

# Add blocks
block_id = core.add("preferences", "Dark mode enabled", priority=1)

# Find by label
block = core.find_by_label("preferences")

# Update content
core.update(block_id, "Dark mode and large fonts enabled")

# Format for prompt
print(core.to_prompt())
```

## Recall Memory Operations

```python
from memcore import RecallMemory, MessageType

recall = RecallMemory()

# Add messages
recall.add(MessageType.USER, "Hello!")
recall.add(MessageType.ASSISTANT, "Hi there! How can I help?")

# Get recent messages
recent = recall.get_recent(5)

# Search messages
results = recall.search("hello")

# Export to OpenAI format
messages = recall.to_openai_messages()
```

## Archival Memory Operations

```python
from memcore import ArchivalMemory

archive = ArchivalMemory()

# Store information
entry_id = archive.add("Important fact about user preferences")

# Search (simple text matching by default)
results = archive.search("preferences")

# Count entries
print(f"Archived items: {archive.count()}")
```

## Persistence

```python
# Save to file
manager.save("memory_state.json")

# Load from file
manager = MemoryManager.load("memory_state.json")
```

## CLI Usage

```bash
# Initialize
memcore init

# Core memory
memcore core add --label "user" --content "Alice"
memcore core list

# Recall memory
memcore recall add --role user --content "Hello"
memcore recall list
memcore recall search --query "hello"

# Archival memory
memcore archive add --content "Important fact"
memcore archive search --query "fact"

# Status
memcore status
```

## API Reference

### MemoryManager

| Method | Description |
|--------|-------------|
| `add_core_memory(label, content, priority)` | Add to core memory |
| `user_message(content)` | Add user message |
| `assistant_message(content)` | Add assistant message |
| `system_message(content)` | Add system message |
| `archive(content, metadata)` | Store in archival memory |
| `get_context_for_prompt(limit)` | Build context string |
| `save(filepath)` | Save to file |
| `load(filepath)` | Load from file |

## Custom Storage Backends

```python
from memcore.storage import MemoryStorage
from memcore.core.types import MemoryEntry

class MyCustomStorage(MemoryStorage):
    def save(self, entry: MemoryEntry) -> str:
        # Implement custom save logic
        pass

    def load(self, entry_id: str):
        # Implement custom load logic
        pass

    # ... implement other methods
```

## License

MIT License - see LICENSE file for details.
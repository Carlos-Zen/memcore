# MemCore

<p align="center">
  <strong>Hierarchical Memory System for AI Agents</strong>
</p>

<p align="center">
  <a href="README_CN.md">中文文档</a> | <a href="README.md">English</a>
</p>

<p align="center">
  <a href="#architecture">Architecture</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#core-workflow">Core Workflow</a> •
  <a href="#api-reference">API Reference</a>
</p>

---

A Python implementation of a three-tier memory architecture inspired by MemGPT, designed to give AI agents human-like memory capabilities.

## Architecture

MemCore implements a **three-tier hierarchical memory architecture**, mirroring human cognitive memory systems:

```
MemCore Architecture
│
├── Core Memory (Working Memory)
│   ├── Limited capacity (~10 blocks, ~2000 tokens)
│   ├── Always available in context
│   ├── Stores essential user info, preferences
│   └── Priority-based eviction
│
├── Recall Memory (Episodic Memory)
│   ├── Conversation history
│   ├── Chronologically ordered messages
│   ├── Searchable by content
│   └── Export to OpenAI format
│
└── Archival Memory (Semantic Memory)
    ├── Unlimited long-term storage
    ├── Explicit search required
    ├── Metadata support
    └── Pluggable storage backends
```

### Memory Types Comparison

| Feature | Core Memory | Recall Memory | Archival Memory |
|---------|-------------|---------------|-----------------|
| **Capacity** | Limited | Moderate | Unlimited |
| **Access** | Always visible | Search/Recent | Explicit search |
| **Content** | Essential context | Conversations | Long-term facts |
| **Human Analogy** | Working memory | Episodic memory | Semantic memory |

## Core Workflow

```
┌────────────────────────────────────────────────────────────────┐
│                    Memory Management Flow                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User Input ──▶ MemoryManager                                   │
│                      │                                          │
│         ┌────────────┼────────────┐                            │
│         ▼            ▼            ▼                            │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐                      │
│   │  Core    │ │  Recall  │ │ Archival │                      │
│   │  Memory  │ │  Memory  │ │  Memory  │                      │
│   └──────────┘ └──────────┘ └──────────┘                      │
│         │            │            │                            │
│         └────────────┴────────────┘                            │
│                      │                                          │
│                      ▼                                          │
│         ┌──────────────────────┐                               │
│         │ get_context_for_prompt│                               │
│         │   (Build LLM Context) │                               │
│         └──────────────────────┘                               │
│                      │                                          │
│                      ▼                                          │
│              LLM Response                                       │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Memory Flow Example

```python
# 1. Initialize memory
manager = MemoryManager()

# 2. Store essential info in Core Memory
manager.add_core_memory("user", "Name: Alice, Developer", priority=2)
manager.add_core_memory("preferences", "Prefers concise responses", priority=1)

# 3. Track conversation in Recall Memory
manager.user_message("Help me write a Python function")
manager.assistant_message("Sure! What should the function do?")

# 4. Archive important facts for later
manager.archive("Alice is working on a Python project", {"topic": "project"})

# 5. Build context for LLM
context = manager.get_context_for_prompt(include_recall=5)
# This combines:
# - Core memory (always included)
# - Recent 5 messages from recall
# - Does NOT include archival (requires explicit search)
```

## Installation

```bash
pip install memcore-ai
```

For vector search support:

```bash
pip install memcore-ai[vector]
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

## Academic Reference

This framework implements the memory architecture inspired by **MemGPT**:

> **MemGPT: Towards LLMs as Operating Systems**
>
> Charles Packer, Vivian Fang, Shishir G. Patil, Kevin Lin, Sarah Wooders, Joseph E. Gonzalez
>
> *arXiv 2023*
>
> Paper: https://arxiv.org/abs/2310.08560

```bibtex
@article{packer2023memgpt,
  title={MemGPT: Towards LLMs as Operating Systems},
  author={Packer, Charles and Fang, Vivian and Patil, Shishir G and Lin, Kevin and Wooders, Sarah and Gonzalez, Joseph E},
  journal={arXiv preprint arXiv:2310.08560},
  year={2023}
}
```

## License

This project is licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2024 AI Agent Research Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<p align="center">
  Made with ❤️ by AI Agent Research Team
</p>
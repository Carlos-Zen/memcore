# MemCore

<p align="center">
  <strong>AI Agent 分层内存系统</strong>
</p>

<p align="center">
  <a href="README.md">English</a> | <a href="README_CN.md">中文文档</a>
</p>

<p align="center">
  <a href="#架构设计">架构设计</a> •
  <a href="#安装">安装</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#核心流程">核心流程</a> •
  <a href="#api参考">API参考</a>
</p>

---

一个受 MemGPT 启发的三层内存架构 Python 实现，为 AI Agent 提供类似人类的记忆能力。

## 架构设计

MemCore 实现了**三层分层内存架构**，模拟人类认知记忆系统：

```
MemCore 架构
│
├── Core Memory（核心记忆/工作记忆）
│   ├── 容量有限（约10个块，约2000 tokens）
│   ├── 始终在上下文中可用
│   ├── 存储关键用户信息、偏好设置
│   └── 基于优先级的淘汰机制
│
├── Recall Memory（回忆记忆/情景记忆）
│   ├── 对话历史记录
│   ├── 按时间排序的消息
│   ├── 支持内容搜索
│   └── 可导出为 OpenAI 格式
│
└── Archival Memory（归档记忆/语义记忆）
    ├── 无限长期存储
    ├── 需要显式搜索访问
    ├── 支持元数据
    └── 可插拔存储后端
```

### 记忆类型对比

| 特性 | Core Memory | Recall Memory | Archival Memory |
|------|-------------|---------------|-----------------|
| **容量** | 有限 | 中等 | 无限 |
| **访问方式** | 始终可见 | 搜索/最近记录 | 显式搜索 |
| **内容** | 核心上下文 | 对话记录 | 长期事实 |
| **人类类比** | 工作记忆 | 情景记忆 | 语义记忆 |

## 核心流程

```
┌────────────────────────────────────────────────────────────────┐
│                    内存管理流程                                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户输入 ──▶ MemoryManager                                      │
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
│         │   (构建 LLM 上下文)   │                               │
│         └──────────────────────┘                               │
│                      │                                          │
│                      ▼                                          │
│              LLM 响应                                           │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 内存使用示例

```python
# 1. 初始化内存
manager = MemoryManager()

# 2. 在 Core Memory 存储关键信息
manager.add_core_memory("user", "姓名: Alice, 开发者", priority=2)
manager.add_core_memory("preferences", "偏好简洁回复", priority=1)

# 3. 在 Recall Memory 追踪对话
manager.user_message("帮我写一个 Python 函数")
manager.assistant_message("好的！请问这个函数需要做什么？")

# 4. 归档重要事实以备后用
manager.archive("Alice 正在进行一个 Python 项目", {"topic": "project"})

# 5. 构建 LLM 上下文
context = manager.get_context_for_prompt(include_recall=5)
# 这会合并:
# - Core memory (始终包含)
# - Recall 中最近的 5 条消息
# - 不包含 Archival (需要显式搜索)
```

## 安装

```bash
pip install memcore-ai
```

如需向量搜索支持:

```bash
pip install memcore-ai[vector]
```

## 快速开始

```python
from memcore import MemoryManager, MessageType

# 初始化内存管理器
manager = MemoryManager()

# 添加到核心记忆 (始终可用)
manager.add_core_memory("user_profile", "姓名: Alice, 角色: 开发者")

# 添加消息到回忆记忆
manager.user_message("今天天气怎么样?")
manager.assistant_message("我无法获取实时天气数据。")

# 归档重要信息
manager.archive("用户偏好简洁回复", {"source": "preference"})

# 获取 LLM 提示的上下文
context = manager.get_context_for_prompt()
print(context)
```

## Core Memory 操作

```python
from memcore import CoreMemory

core = CoreMemory(max_blocks=10)

# 添加块
block_id = core.add("preferences", "深色模式已启用", priority=1)

# 按标签查找
block = core.find_by_label("preferences")

# 更新内容
core.update(block_id, "深色模式和大字体已启用")

# 格式化为提示
print(core.to_prompt())
```

## Recall Memory 操作

```python
from memcore import RecallMemory, MessageType

recall = RecallMemory()

# 添加消息
recall.add(MessageType.USER, "你好!")
recall.add(MessageType.ASSISTANT, "你好！有什么可以帮助你的？")

# 获取最近消息
recent = recall.get_recent(5)

# 搜索消息
results = recall.search("你好")

# 导出为 OpenAI 格式
messages = recall.to_openai_messages()
```

## Archival Memory 操作

```python
from memcore import ArchivalMemory

archive = ArchivalMemory()

# 存储信息
entry_id = archive.add("关于用户偏好的重要事实")

# 搜索 (默认简单文本匹配)
results = archive.search("偏好")

# 统计条目数
print(f"已归档: {archive.count()} 条")
```

## 持久化

```python
# 保存到文件
manager.save("memory_state.json")

# 从文件加载
manager = MemoryManager.load("memory_state.json")
```

## 命令行使用

```bash
# 初始化
memcore init

# 核心记忆
memcore core add --label "user" --content "Alice"
memcore core list

# 回忆记忆
memcore recall add --role user --content "你好"
memcore recall list
memcore recall search --query "你好"

# 归档记忆
memcore archive add --content "重要事实"
memcore archive search --query "事实"

# 状态
memcore status
```

## API 参考

### MemoryManager

| 方法 | 描述 |
|------|------|
| `add_core_memory(label, content, priority)` | 添加到核心记忆 |
| `user_message(content)` | 添加用户消息 |
| `assistant_message(content)` | 添加助手消息 |
| `system_message(content)` | 添加系统消息 |
| `archive(content, metadata)` | 存储到归档记忆 |
| `get_context_for_prompt(limit)` | 构建上下文字符串 |
| `save(filepath)` | 保存到文件 |
| `load(filepath)` | 从文件加载 |

## 自定义存储后端

```python
from memcore.storage import MemoryStorage
from memcore.core.types import MemoryEntry

class MyCustomStorage(MemoryStorage):
    def save(self, entry: MemoryEntry) -> str:
        # 实现自定义保存逻辑
        pass

    def load(self, entry_id: str):
        # 实现自定义加载逻辑
        pass

    # ... 实现其他方法
```

## 学术引用

本框架实现的内存架构受 **MemGPT** 启发：

> **MemGPT: Towards LLMs as Operating Systems**
>
> Charles Packer, Vivian Fang, Shishir G. Patil, Kevin Lin, Sarah Wooders, Joseph E. Gonzalez
>
> *arXiv 2023*
>
> 论文链接: https://arxiv.org/abs/2310.08560

```bibtex
@article{packer2023memgpt,
  title={MemGPT: Towards LLMs as Operating Systems},
  author={Packer, Charles and Fang, Vivian and Patil, Shishir G and Lin, Kevin and Wooders, Sarah and Gonzalez, Joseph E},
  journal={arXiv preprint arXiv:2310.08560},
  year={2023}
}
```

## 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

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
  由 AI Agent Research Team 用 ❤️ 构建
</p>
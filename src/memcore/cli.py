"""
CLI Entry Point
"""

import argparse
import json
import sys
from . import MemoryManager, MessageType


def main():
    parser = argparse.ArgumentParser(description="MemCore - Memory Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Init command
    subparsers.add_parser("init", help="Initialize a new memory store")

    # Core memory commands
    core_parser = subparsers.add_parser("core", help="Core memory operations")
    core_parser.add_argument("action", choices=["add", "list", "clear"], help="Action to perform")
    core_parser.add_argument("--label", help="Block label")
    core_parser.add_argument("--content", help="Block content")

    # Recall memory commands
    recall_parser = subparsers.add_parser("recall", help="Recall memory operations")
    recall_parser.add_argument("action", choices=["add", "list", "search", "clear"], help="Action to perform")
    recall_parser.add_argument("--role", choices=["user", "assistant", "system"], help="Message role")
    recall_parser.add_argument("--content", help="Message content")
    recall_parser.add_argument("--query", help="Search query")

    # Archival memory commands
    archive_parser = subparsers.add_parser("archive", help="Archival memory operations")
    archive_parser.add_argument("action", choices=["add", "list", "search", "clear"], help="Action to perform")
    archive_parser.add_argument("--content", help="Entry content")
    archive_parser.add_argument("--query", help="Search query")

    # Status command
    subparsers.add_parser("status", help="Show memory status")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "init":
        manager = MemoryManager()
        manager.save("memory.json")
        print("Initialized new memory store in memory.json")
        return

    # Load existing memory
    try:
        manager = MemoryManager.load("memory.json")
    except FileNotFoundError:
        manager = MemoryManager()

    if args.command == "core":
        if args.action == "add":
            if not args.label or not args.content:
                print("Error: --label and --content required for add")
                sys.exit(1)
            manager.add_core_memory(args.label, args.content)
            print(f"Added core memory block: {args.label}")

        elif args.action == "list":
            for block in manager.core.list_all():
                print(f"[{block.label}] {block.content}")

        elif args.action == "clear":
            manager.core._blocks.clear()
            manager.core._order.clear()
            print("Core memory cleared")

    elif args.command == "recall":
        if args.action == "add":
            if not args.role or not args.content:
                print("Error: --role and --content required for add")
                sys.exit(1)
            role_map = {
                "user": MessageType.USER,
                "assistant": MessageType.ASSISTANT,
                "system": MessageType.SYSTEM
            }
            manager.add_message(role_map[args.role], args.content)
            print(f"Added {args.role} message")

        elif args.action == "list":
            for msg in manager.recall.get_all():
                print(f"[{msg.role.value}] {msg.content}")

        elif args.action == "search":
            if not args.query:
                print("Error: --query required for search")
                sys.exit(1)
            results = manager.recall.search(args.query)
            for msg in results:
                print(f"[{msg.role.value}] {msg.content}")

        elif args.action == "clear":
            manager.recall.clear()
            print("Recall memory cleared")

    elif args.command == "archive":
        if args.action == "add":
            if not args.content:
                print("Error: --content required for add")
                sys.exit(1)
            manager.archive(args.content)
            print("Added to archival memory")

        elif args.action == "list":
            for entry in manager.archival.list_all():
                print(f"[{entry.id}] {entry.content[:50]}...")

        elif args.action == "search":
            if not args.query:
                print("Error: --query required for search")
                sys.exit(1)
            results = manager.archival.search(args.query)
            for entry in results:
                print(f"[{entry.id}] {entry.content[:100]}")

        elif args.action == "clear":
            manager.archival._entries.clear()
            print("Archival memory cleared")

    elif args.command == "status":
        print(f"Core memory blocks: {len(manager.core._blocks)}")
        print(f"Recall messages: {len(manager.recall.get_all())}")
        print(f"Archival entries: {manager.archival.count()}")

    # Save changes
    manager.save("memory.json")


if __name__ == "__main__":
    main()
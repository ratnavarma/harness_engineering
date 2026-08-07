"""
Task Manager CLI application.

Provides a simple command-line interface to manage tasks.
"""
import argparse
import json
import os
import sys
import tempfile
from typing import List, Dict, Any

__all__ = ["main"]

Task = Dict[str, Any]

def get_store_path() -> str:
    """Get the path to the task store JSON file."""
    return os.environ.get("TASKMAN_STORE", os.path.expanduser("~/.taskman.json"))

def load_tasks() -> List[Task]:
    """Load tasks from the JSON store."""
    path = get_store_path()
    try:
        if os.path.getsize(path) == 0:
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"Error: Task store at {path} is corrupted ({e}).", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading task store: {e}", file=sys.stderr)
        sys.exit(1)

def save_tasks(tasks: List[Task]) -> None:
    """Save tasks to the JSON store atomically."""
    path = get_store_path()
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name, exist_ok=True)
        except OSError as e:
            print(f"Error creating directory: {e}", file=sys.stderr)
            sys.exit(1)
            
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name or ".", prefix=".taskman-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
        os.replace(tmp_path, path)
    except OSError as e:
        print(f"Error saving tasks: {e}", file=sys.stderr)
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        sys.exit(1)

def get_next_id(tasks: List[Task]) -> int:
    """Calculate the next available task ID."""
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1

def add_task(args: argparse.Namespace) -> None:
    """Add a new task."""
    description = args.description.strip()
    if not description:
        print("Error: Task description cannot be empty.", file=sys.stderr)
        sys.exit(1)
        
    tasks = load_tasks()
    task_id = get_next_id(tasks)
    task = {
        "id": task_id,
        "description": description,
        "status": "pending"
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task {task_id}")

def list_tasks(args: argparse.Namespace) -> None:
    """List tasks, optionally including done tasks."""
    tasks = load_tasks()
    if args.all:
        filtered = tasks
    else:
        filtered = [t for t in tasks if t["status"] == "pending"]
    
    if not filtered:
        print("No tasks found.")
        return

    max_id_len = max(5, max(len(str(t["id"])) for t in filtered))
    
    # Aligned table output
    print(f"{'ID':<{max_id_len}} | {'Status':<10} | {'Description'}")
    print("-" * (max_id_len + 15 + 20)) # Approximate width
    for t in filtered:
        print(f"{t['id']:<{max_id_len}} | {t['status']:<10} | {t['description']}")

def done_task(args: argparse.Namespace) -> None:
    """Mark a task as done."""
    tasks = load_tasks()
    found = False
    for t in tasks:
        if t["id"] == args.id:
            found = True
            if t["status"] == "done":
                print(f"Task {args.id} is already done.")
                return
            t["status"] = "done"
            break
            
    if found:
        save_tasks(tasks)
        print(f"Task {args.id} marked as done.")
    else:
        print(f"Task {args.id} not found.", file=sys.stderr)
        sys.exit(1)

def rm_task(args: argparse.Namespace) -> None:
    """Remove a task by ID."""
    tasks = load_tasks()
    initial_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != args.id]
    
    if len(tasks) < initial_len:
        save_tasks(tasks)
        print(f"Task {args.id} removed.")
    else:
        print(f"Task {args.id} not found.", file=sys.stderr)
        sys.exit(1)

def stats_tasks(args: argparse.Namespace) -> None:
    """Show statistics about tasks."""
    tasks = load_tasks()
    total = len(tasks)
    done = sum(1 for t in tasks if t["status"] == "done")
    pending = total - done
    
    print(f"{'Total':<10}: {total}")
    print(f"{'Pending':<10}: {pending}")
    print(f"{'Done':<10}: {done}")

def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Task Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add
    parser_add = subparsers.add_parser("add", help="Add a new task")
    parser_add.add_argument("description", help="Task description")
    parser_add.set_defaults(func=add_task)

    # List
    parser_list = subparsers.add_parser("list", help="List tasks")
    parser_list.add_argument("--all", action="store_true", help="Show all tasks (including done)")
    parser_list.set_defaults(func=list_tasks)

    # Done
    parser_done = subparsers.add_parser("done", help="Mark a task as done")
    parser_done.add_argument("id", type=int, help="Task ID")
    parser_done.set_defaults(func=done_task)

    # Rm
    parser_rm = subparsers.add_parser("rm", help="Remove a task")
    parser_rm.add_argument("id", type=int, help="Task ID")
    parser_rm.set_defaults(func=rm_task)

    # Stats
    parser_stats = subparsers.add_parser("stats", help="Show task statistics")
    parser_stats.set_defaults(func=stats_tasks)

    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)

if __name__ == "__main__":
    main()

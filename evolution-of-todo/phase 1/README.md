# Phase I In-Memory Python Console Todo Application

A simple command-line todo application that demonstrates core CRUD functionality with a clean, user-friendly interface.

## Features

- **Add Tasks**: Create new tasks with titles and descriptions
- **View Tasks**: Display all tasks in a clear, tabular format
- **Update Tasks**: Modify existing task details
- **Delete Tasks**: Remove tasks by ID
- **Mark Complete/Incomplete**: Toggle task completion status
- **Help System**: Built-in help for all operations

## Requirements

- Python 3.13 or higher
- UV package manager

## Setup

1. Clone or download the repository
2. Navigate to the project directory
3. Install dependencies using UV:
   ```bash
   uv sync
   ```

## Usage

Run the application using UV:

```bash
uv run python -m src.main
```

Or if you have the project installed in your environment:

```bash
python -m src.main
```

## Example Session

```
Welcome to the Todo Application!
========================================
Todo Application - Main Menu
========================================
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete/Incomplete
6. Help
0. Exit
========================================
Choose an option (0-6): 1
Enter task title: Buy groceries
Enter task description (optional): Need to buy milk, bread, and eggs
Task added successfully with ID: 1

Choose an option (0-6): 2

Current Tasks:
+----+-------------------+----------------------------------+--------+
| ID | Title             | Description                      | Status |
+----+-------------------+----------------------------------+--------+
|  1 | Buy groceries     | Need to buy milk, bread, and eggs | [ ]    |
+----+-------------------+----------------------------------+--------+
```

## Project Structure

```
src/
├── __init__.py
├── main.py              # Main CLI entry point with menu loop
├── todo.py              # Core task management logic
├── models.py            # Task data model definition
├── exceptions.py        # Custom exception classes for error handling
└── cli.py               # CLI interface and command parsing

tests/
├── __init__.py
├── test_todo.py         # Unit tests for core functionality
├── test_models.py       # Unit tests for data models
└── test_cli.py          # Unit tests for CLI interface
```

## Development

To run the tests:

```bash
uv run python -m pytest tests/ -v
```

## Architecture

- **Task**: Dataclass representing a todo item with ID, title, description, and completion status
- **TaskManager**: Service class handling all task operations with auto-incrementing IDs
- **CLI Functions**: User interface layer handling input/output and user interactions
- **Exceptions**: Custom exception classes for specific error conditions

## Design Principles

- In-memory storage (tasks reset on application restart)
- Clean separation of concerns (data, logic, interface)
- User-friendly command-line interface
- Comprehensive error handling and validation
- Follows Python 3.13+ best practices
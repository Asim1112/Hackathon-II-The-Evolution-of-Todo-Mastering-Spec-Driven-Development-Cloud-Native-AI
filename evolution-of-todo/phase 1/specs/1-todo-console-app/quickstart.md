# Quickstart Guide: Phase I Todo Console Application

## Prerequisites
- Python 3.13+
- UV package manager

## Setup
1. Clone or create the project directory
2. Initialize UV environment:
   ```bash
   uv init
   ```
3. Install dependencies (if any):
   ```bash
   uv add tabulate  # Optional, for table formatting
   ```

## Running the Application
```bash
uv run python src/main.py
```

## Basic Usage
1. Launch the application with the command above
2. Use the interactive menu to perform operations:
   - Press '1' to add a new task
   - Press '2' to view all tasks
   - Press '3' to update a task
   - Press '4' to delete a task
   - Press '5' to mark a task as complete/incomplete
   - Press '6' for help
   - Press '0' to exit

## Example Session
```
Welcome to the Todo App!
Choose an option:
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Complete/Incomplete
6. Help
0. Exit

> 1
Enter task title: Buy groceries
Enter task description: Need to buy milk, bread, eggs
Task added with ID: 1

> 2
ID  | Title            | Description              | Status
----|------------------|--------------------------|--------
1   | Buy groceries    | Need to buy milk, bread, eggs | [ ]
```

## Troubleshooting
- If getting import errors, ensure all source files are in the correct directories
- If UV is not recognized, install it using: `pip install uv`
- For any runtime errors, check that Python 3.13+ is installed
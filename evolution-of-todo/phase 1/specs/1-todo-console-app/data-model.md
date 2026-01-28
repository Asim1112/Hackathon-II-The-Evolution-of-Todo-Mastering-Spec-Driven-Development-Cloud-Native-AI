# Data Model: Phase I Todo Console Application

## Task Entity

### Fields
- **id** (int): Unique auto-incrementing identifier for the task
- **title** (str): Title/description of the task (required)
- **description** (str): Detailed description of the task (optional)
- **completed** (bool): Completion status of the task (default: False)
- **created_at** (datetime): Timestamp when the task was created (optional)

### Validation Rules
- **id**: Must be a positive integer, auto-assigned by system
- **title**: Must be non-empty string (length > 0)
- **description**: Optional, can be empty string
- **completed**: Boolean value only (True/False)
- **created_at**: Datetime object, set automatically on creation

### State Transitions
- **Incomplete → Complete**: When user marks task as complete
- **Complete → Incomplete**: When user marks task as incomplete
- **New → Incomplete**: When task is initially created

## Task Manager Service

### Responsibilities
- Maintain collection of all tasks
- Handle CRUD operations on tasks
- Manage auto-incrementing ID assignment
- Validate input data
- Handle error cases gracefully

### Methods
- **add_task(title: str, description: str) -> int**: Creates new task, returns assigned ID
- **get_task(task_id: int) -> Task**: Retrieves task by ID
- **get_all_tasks() -> List[Task]**: Returns all tasks in the system
- **update_task(task_id: int, title: str = None, description: str = None) -> bool**: Updates task details, returns success status
- **delete_task(task_id: int) -> bool**: Removes task by ID, returns success status
- **toggle_completion(task_id: int) -> bool**: Toggles completion status, returns success status
- **validate_task_data(title: str, description: str = None) -> ValidationResult**: Validates input data

## Relationships
- Task Manager contains a collection of Task entities
- Each Task has a unique ID within the Task Manager's scope
---
description: "Task list for Phase I Todo Console Application implementation"
---

# Tasks: Phase I In-Memory Python Console Todo App

**Input**: Design documents from `/specs/1-todo-console-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan in src/, tests/, pyproject.toml, README.md
- [x] T002 Initialize Python 3.13 project with UV dependencies in pyproject.toml
- [x] T003 [P] Configure linting and formatting tools (black, flake8, mypy)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Task data model with all required fields in src/models.py
- [x] T005 [P] Create custom exception classes for error handling in src/exceptions.py
- [x] T006 Create TaskManager service with all required methods in src/todo.py
- [x] T007 Create CLI utility functions for input/output in src/cli.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable users to add new tasks with titles and descriptions, then view all their tasks in a clear, organized format.

**Independent Test**: Can be fully tested by adding several tasks and verifying they appear in the task list with proper formatting, delivering the fundamental value of task management.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Unit test for Task model validation in tests/test_models.py
- [x] T009 [P] [US1] Unit test for TaskManager add_task method in tests/test_todo.py
- [x] T010 [P] [US1] Unit test for TaskManager get_all_tasks method in tests/test_todo.py
- [x] T011 [P] [US1] Integration test for adding and viewing tasks in tests/test_todo.py

### Implementation for User Story 1

- [x] T012 [P] [US1] Implement Task dataclass with all required fields in src/models.py
- [x] T013 [US1] Implement add_task method in src/todo.py (depends on T012)
- [x] T014 [US1] Implement get_all_tasks method in src/todo.py
- [x] T015 [US1] Implement display_tasks function in src/cli.py (depends on T014)
- [x] T016 [US1] Implement add_task CLI function in src/cli.py (depends on T013)
- [x] T017 [US1] Implement main menu loop with add/view options in src/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Update and Complete Tasks (Priority: P2)

**Goal**: Enable users to modify existing tasks and mark completed tasks as done to keep track of their progress.

**Independent Test**: Can be tested by updating task details and toggling completion status, delivering the value of maintaining accurate and up-to-date task information.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [x] T018 [P] [US2] Unit test for TaskManager update_task method in tests/test_todo.py
- [x] T019 [P] [US2] Unit test for TaskManager toggle_completion method in tests/test_todo.py
- [x] T020 [P] [US2] Integration test for updating tasks in tests/test_todo.py
- [x] T021 [P] [US2] Integration test for toggling completion status in tests/test_todo.py

### Implementation for User Story 2

- [x] T022 [US2] Implement update_task method in src/todo.py
- [x] T023 [US2] Implement toggle_completion method in src/todo.py
- [x] T024 [US2] Implement update_task CLI function in src/cli.py (depends on T022)
- [x] T025 [US2] Implement toggle_completion CLI function in src/cli.py (depends on T023)
- [x] T026 [US2] Add update and completion options to main menu in src/main.py (depends on T024, T025)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Delete Tasks (Priority: P3)

**Goal**: Enable users to remove tasks that are no longer needed to keep their task list manageable and relevant.

**Independent Test**: Can be tested by deleting specific tasks and verifying they no longer appear in the task list, delivering the value of maintaining a clean and organized task inventory.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [x] T027 [P] [US3] Unit test for TaskManager delete_task method in tests/test_todo.py
- [x] T028 [P] [US3] Integration test for deleting tasks in tests/test_todo.py

### Implementation for User Story 3

- [x] T029 [US3] Implement delete_task method in src/todo.py
- [x] T030 [US3] Implement delete_task CLI function in src/cli.py (depends on T029)
- [x] T031 [US3] Add delete option to main menu in src/main.py (depends on T030)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T032 [P] Add comprehensive error handling and user feedback across all operations in src/cli.py
- [x] T033 [P] Implement input validation for all user inputs across all modules
- [x] T034 [P] Add help/usage command as specified in FR-100 in src/cli.py
- [x] T035 [P] Improve output formatting with tabulate library if available in src/cli.py
- [x] T036 [P] Add README.md with setup and usage instructions
- [x] T037 [P] Add docstrings to all public functions and classes
- [x] T038 [P] Run quickstart.md validation to ensure all features work correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Unit test for Task model validation in tests/test_models.py"
Task: "Unit test for TaskManager add_task method in tests/test_todo.py"
Task: "Unit test for TaskManager get_all_tasks method in tests/test_todo.py"
Task: "Integration test for adding and viewing tasks in tests/test_todo.py"

# Launch all models for User Story 1 together:
Task: "Implement Task dataclass with all required fields in src/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
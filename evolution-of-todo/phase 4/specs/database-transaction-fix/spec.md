# Database Transaction Commit Fix Specification

## Problem Statement
Database split confirmed: `add_task` inserts rows but `list_tasks` immediately after returns 0 rows. This proves INSERT and SELECT are hitting different database states due to uncommitted transactions.

**Evidence:**
- add_task inserts: owner_id = aj02MZpu47L1qwUfHFXc0Ch04Y8HfhzO, task_id 112, 113
- list_tasks(user_id=aj02MZpu47L1qwUfHFXc0Ch04Y8HfhzO) returns 0 rows immediately after

**Root Cause:**
The `_SessionContext` class in `mcp_server.py` uses `session.flush()` but never calls `session.commit()`. The comment incorrectly states that the Session context manager "auto-commits on successful exit" - this is false. SQLModel/SQLAlchemy Session context managers only close the session; they do NOT auto-commit. Transactions are rolled back when the session closes without an explicit commit.

## Requirements

### Functional Requirements
1. **Transaction Commit**: All database writes must be explicitly committed
2. **Data Persistence**: INSERT operations must be visible to subsequent SELECT operations
3. **Rollback on Error**: Exceptions must still trigger rollback
4. **Same Engine**: All operations must use the same SQLAlchemy engine

### Non-Functional Requirements
1. **Data Integrity**: ACID properties must be maintained
2. **Performance**: No degradation in database operations
3. **Reliability**: 100% commit success rate for successful operations

## Solution Approach

### Fix
Replace `session.flush()` with `session.commit()` in the `_SessionContext.__exit__` method to ensure transactions are committed before the session closes.

### Components
- `backend/src/mcp/mcp_server.py`: Fix `_SessionContext` to explicitly commit transactions

## Acceptance Criteria
- [ ] add_task commits transactions successfully
- [ ] list_tasks sees rows inserted by add_task immediately
- [ ] All MCP tools (add_task, list_tasks, complete_task, update_task, delete_task) work correctly
- [ ] Exceptions still trigger rollback
- [ ] No data loss or corruption

## Constraints
- Must maintain backward compatibility
- Cannot change tool signatures
- Must work with both SQLite and PostgreSQL

## Risks
- Potential data corruption if commit logic is incorrect
- Performance impact if commits are too frequent
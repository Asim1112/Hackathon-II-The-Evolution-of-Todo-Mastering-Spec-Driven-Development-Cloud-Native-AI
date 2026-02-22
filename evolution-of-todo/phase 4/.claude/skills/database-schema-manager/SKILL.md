name: "database-schema-manager"
  description: "Define, evolve, and manage database models for chat and task systems. Use when creating data persistence layers, handling schema migrations, or ensuring data
  integrity."
  version: "1.0.0"

  When to Use This Skill

  - Defining new database models for chat features
  - Managing schema evolution and migrations
  - Ensuring referential integrity and constraints
  - Optimizing queries and indexes for chat workloads

  How This Skill Works

  1. Define models: Create SQLModel classes with fields, types, and relationships
  2. Add constraints: Define foreign keys, unique constraints, and indexes
  3. Plan migrations: Generate migration scripts for schema changes
  4. Validate integrity: Ensure referential integrity and cascade rules
  5. Optimize queries: Add indexes for common query patterns

  Output Format

  Provide:
  - Model Definitions: SQLModel classes with all fields and types
  - Relationships: Foreign key definitions and cascade behaviors
  - Constraints: Unique constraints, check constraints, and defaults
  - Indexes: Index definitions for query optimization
  - Migration Script: Alembic migration for schema changes

  Quality Criteria

  Schema is ready when:
  - All models have proper primary keys and timestamps
  - Foreign keys enforce referential integrity
  - Indexes cover common query patterns (user_id, conversation_id)
  - Cascade rules prevent orphaned records
  - Migration is reversible and tested

  Example

  Input: "Create Conversation and Message models for chat history with user isolation"

  Output:
  - Models: Conversation(id, user_id, created_at, updated_at), Message(id, conversation_id, user_id, role, content, created_at)
  - Relationships: Message.conversation_id → Conversation.id (CASCADE DELETE)
  - Indexes: idx_conversation_user, idx_message_conversation, idx_message_user
  - Migration: Alembic script to create tables with constraints

  ---
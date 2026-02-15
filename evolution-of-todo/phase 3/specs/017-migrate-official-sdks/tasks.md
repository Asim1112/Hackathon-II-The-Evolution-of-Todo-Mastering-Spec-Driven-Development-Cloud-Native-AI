# Tasks: Migrate to Official OpenAI SDKs for Phase III Compliance

**Input**: Design documents from `/specs/017-migrate-official-sdks/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Manual validation checklist approach (no automated tests in this phase per hackathon/MVP context)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- All paths are absolute from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Verify Python 3.11+ and Node.js 18+ installed per quickstart.md
- [x] T002 Install OpenAI Agents SDK (openai-agents-python==0.7.0) in backend/
- [x] T003 [P] Install ChatKit Python SDK (openai-chatkit) in backend/
- [x] T004 [P] Install ChatKit React SDK (@openai/chatkit-react) in frontend/
- [x] T005 [P] Verify MCP server running on http://localhost:8001/mcp
- [x] T006 Configure environment variables (MCP_SERVER_URL, existing vars preserved)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T007 Create RequestContext dataclass in backend/src/agents/store_adapter.py
- [x] T008 [P] Implement ThreadItem serialization helpers (serialize_thread_item, deserialize_thread_item) in backend/src/agents/store_adapter.py
- [x] T009 [P] Implement ThreadMetadata conversion helpers (conversation_to_thread_metadata, thread_metadata_to_conversation) in backend/src/agents/store_adapter.py
- [x] T010 Create PostgresStoreAdapter class skeleton (13 method stubs) in backend/src/agents/store_adapter.py
- [x] T011 Implement Store.load_thread() method in backend/src/agents/store_adapter.py
- [x] T012 [P] Implement Store.save_thread() method in backend/src/agents/store_adapter.py
- [x] T013 [P] Implement Store.load_threads() method with cursor pagination in backend/src/agents/store_adapter.py
- [x] T014 Implement Store.load_thread_items() method with cursor pagination in backend/src/agents/store_adapter.py
- [x] T015 [P] Implement Store.add_thread_item() method in backend/src/agents/store_adapter.py
- [x] T016 [P] Implement Store.save_item() method in backend/src/agents/store_adapter.py
- [x] T017 [P] Implement Store.load_item() method in backend/src/agents/store_adapter.py
- [x] T018 [P] Implement Store.delete_thread() method in backend/src/agents/store_adapter.py
- [x] T019 [P] Implement Store.delete_thread_item() method in backend/src/agents/store_adapter.py
- [x] T020 [P] Implement Store attachment methods (save_attachment, load_attachment, delete_attachment) as stubs in backend/src/agents/store_adapter.py
- [x] T021 [P] Implement Store.generate_item_id() method in backend/src/agents/store_adapter.py
- [x] T022 Create create_agent() async function with MCPServerStreamableHttp in backend/src/agents/chatkit_server.py
- [x] T023 Create TodoChatKitServer class skeleton in backend/src/agents/chatkit_server.py
- [x] T024 Implement TodoChatKitServer.respond() method (~20 lines) in backend/src/agents/chatkit_server.py
- [x] T025 Create /chatkit FastAPI endpoint in backend/src/api/routes/chatkit.py
- [x] T026 Register /chatkit route in backend/src/main.py (or equivalent app initialization)
- [x] T027 Create ChatKitChat component in frontend/src/components/ChatKitChat.tsx
- [x] T028 Update chat page to use ChatKitChat in frontend/src/app/chat/page.tsx

**Checkpoint**: Foundation ready - user story validation can now begin

---

## Phase 3: User Story 1 - Phase III Compliance Verification (Priority: P1) 🎯 MVP

**Goal**: Verify that the Todo AI Chatbot uses the official OpenAI Agents SDK and ChatKit SDK as required by Phase III specification

**Independent Test**: Inspect codebase for Agent/Runner usage (backend) and ChatKit component (frontend), run Phase III compliance audit

### Manual Validation for User Story 1

- [ ] T029 [US1] Verify Agent class imported and used in backend/src/agents/chatkit_server.py
- [ ] T030 [US1] Verify Runner.run_streamed() called in backend/src/agents/chatkit_server.py
- [ ] T031 [US1] Verify MCPServerStreamableHttp used with cache_tools_list=True in backend/src/agents/chatkit_server.py
- [ ] T032 [US1] Verify ChatKit React component imported in frontend/src/components/ChatKitChat.tsx
- [ ] T033 [US1] Verify no manual OpenAI client usage (grep for "OpenAI()" should find nothing in backend/src/agents/)
- [ ] T034 [US1] Verify orchestrator.py removed from backend/src/agents/
- [ ] T035 [US1] Verify ChatInterface.tsx removed from frontend/src/components/
- [ ] T036 [US1] Run Phase III compliance audit script (python scripts/audit_phase3_compliance.py)
- [ ] T037 [US1] Verify audit shows PASS on all 6 requirements

**Checkpoint**: Phase III compliance verified - project meets all mandatory technical requirements

---

## Phase 4: User Story 2 - Functional Parity Verification (Priority: P1)

**Goal**: Verify that all existing chatbot functionality works identically after the SDK migration

**Independent Test**: Execute same test scenarios before and after migration, compare results for identical behavior

### Manual Validation for User Story 2

- [ ] T038 [US2] Test NLU-001: "Add a task to buy milk" → verify add_task called, task created
- [ ] T039 [US2] Test NLU-002: "Remember to call dentist" → verify add_task called
- [ ] T040 [US2] Test NLU-003: "I need to finish the report" → verify add_task called
- [ ] T041 [US2] Test NLU-004: "Show my tasks" → verify list_tasks called, tasks displayed
- [ ] T042 [US2] Test NLU-005: "What's pending?" → verify list_tasks with status filter
- [ ] T043 [US2] Test NLU-006: "What have I completed?" → verify list_tasks with status filter
- [ ] T044 [US2] Test NLU-007: "Mark task 123 as done" → verify complete_task called
- [ ] T045 [US2] Test NLU-008: "I finished buying milk" → verify complete_task called
- [ ] T046 [US2] Test NLU-009: "Delete task 456" → verify delete_task called
- [ ] T047 [US2] Test NLU-010: "Remove the dentist task" → verify delete_task called
- [ ] T048 [US2] Test NLU-011: "Update task 789 to 'Buy groceries'" → verify update_task called
- [ ] T049 [US2] Test NLU-012: "Change the report task to 'Finish Q4 report'" → verify update_task called
- [ ] T050 [US2] Test multi-turn conversation: Add task → Show tasks → verify context maintained
- [ ] T051 [US2] Test multi-turn: Add 3 tasks → Delete one → verify correct task deleted
- [ ] T052 [US2] Test multi-turn: "What's my first task?" → "Mark it as done" → verify context used
- [ ] T053 [US2] Test state verification: Delete 3 tasks → verify agent queries before/after
- [ ] T054 [US2] Test error handling: MCP server down → verify graceful error message

**Checkpoint**: 100% functional parity verified - all existing features work identically

---

## Phase 5: User Story 3 - Architecture Preservation Verification (Priority: P2)

**Goal**: Verify that the SDK migration preserves all existing architectural decisions (MCP Server, stateless API, database schema, authentication)

**Independent Test**: Verify MCP server, database models, API contracts, and auth logic remain byte-for-byte identical to pre-migration code

### Manual Validation for User Story 3

- [ ] T055 [US3] Verify backend/src/mcp/mcp_server.py unchanged (diff against baseline)
- [ ] T056 [US3] Verify all 5 MCP tool definitions unchanged (add_task, list_tasks, complete_task, delete_task, update_task)
- [ ] T057 [US3] Verify backend/src/models/conversation.py unchanged (schema preserved)
- [ ] T058 [US3] Verify backend/src/models/message.py unchanged (schema preserved)
- [ ] T059 [US3] Verify database schema unchanged (run schema inspection query)
- [ ] T060 [US3] Verify Better Auth integration unchanged (auth flows work identically)
- [ ] T061 [US3] Verify stateless API design preserved (no server-side session state)
- [ ] T062 [US3] Verify user_id injection works via RequestContext in Store methods
- [ ] T063 [US3] Test /chatkit endpoint with different user_ids → verify isolation

**Checkpoint**: Architecture integrity verified - all design decisions preserved

---

## Phase 6: User Story 4 - Developer Experience Verification (Priority: P3)

**Goal**: Verify that the SDK migration reduces code complexity and improves maintainability

**Independent Test**: Measure code metrics (lines of code, cyclomatic complexity) and compare pre/post migration

### Manual Validation for User Story 4

- [ ] T064 [US4] Count lines in old orchestrator.py (baseline: ~100 lines)
- [ ] T065 [US4] Count lines in new chatkit_server.py respond() method (target: ~20 lines)
- [ ] T066 [US4] Calculate code reduction percentage (target: 80%+)
- [ ] T067 [US4] Verify Agent initialization follows official SDK pattern from research.md
- [ ] T068 [US4] Verify Store adapter follows official SDK pattern from research.md
- [ ] T069 [US4] Verify all code references knowledge base files (OpenAI-Agents-SDK-Knowledge.md, Chatkit-SDK-Documentation.md)
- [ ] T070 [US4] Review code readability with new developer perspective
- [ ] T071 [US4] Verify adding new MCP tool would be simpler with SDK integration

**Checkpoint**: Developer experience improved - code is simpler and more maintainable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and documentation

- [ ] T072 [P] Remove deprecated orchestrator.py from backend/src/agents/
- [ ] T073 [P] Remove deprecated ChatInterface.tsx from frontend/src/components/
- [ ] T074 [P] Update imports in any files that referenced orchestrator.py
- [ ] T075 [P] Update imports in any files that referenced ChatInterface.tsx
- [ ] T076 Run full regression test suite (all 25 test cases from plan.md)
- [ ] T077 [P] Measure response latency and compare with baseline (target: within 10%)
- [ ] T078 [P] Run load test with 10 concurrent users
- [ ] T079 Create migration summary document in specs/017-migrate-official-sdks/MIGRATION_SUMMARY.md
- [ ] T080 [P] Update CHANGELOG.md with migration details
- [ ] T081 Run quickstart.md validation (all 9 steps)
- [ ] T082 Final Phase III compliance audit (verify PASS on all 6 requirements)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) or sequentially in priority order
  - US1 (P1) and US2 (P1) are highest priority (MVP scope)
  - US3 (P2) and US4 (P3) can be deferred if needed
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Compliance)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - Functional Parity)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2 - Architecture)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P3 - Developer Experience)**: Can start after Foundational (Phase 2) - No dependencies on other stories

**All user stories are independently testable and can be validated in parallel**

### Within Each Phase

**Phase 2 (Foundational)**:
- T007-T009: Serialization helpers (can run in parallel)
- T010: Store skeleton (depends on T007)
- T011-T021: Store methods (can run in parallel after T010)
- T022-T024: ChatKitServer (can run in parallel with Store methods)
- T025-T026: /chatkit endpoint (depends on T024)
- T027-T028: Frontend (can run in parallel with backend)

**Phase 3-6 (User Stories)**:
- All validation tasks within a story can run in parallel
- Stories can be validated in any order after Foundational complete

**Phase 7 (Polish)**:
- Most tasks can run in parallel (marked with [P])
- T076-T082 should run sequentially for final validation

### Parallel Opportunities

- **Setup (Phase 1)**: T002-T005 can run in parallel
- **Foundational (Phase 2)**:
  - T008-T009 in parallel
  - T011-T021 in parallel (after T010)
  - T022-T024 in parallel with Store methods
  - T027-T028 in parallel with backend
- **User Stories (Phase 3-6)**: All 4 stories can be validated in parallel
- **Polish (Phase 7)**: T072-T075, T077-T078, T080 can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# After T010 (Store skeleton) completes, launch all Store methods together:
Task: "Implement Store.load_thread() in backend/src/agents/store_adapter.py"
Task: "Implement Store.save_thread() in backend/src/agents/store_adapter.py"
Task: "Implement Store.load_threads() in backend/src/agents/store_adapter.py"
Task: "Implement Store.load_thread_items() in backend/src/agents/store_adapter.py"
# ... (all 13 methods can be implemented in parallel)

# While Store methods are being implemented, also launch:
Task: "Create create_agent() function in backend/src/agents/chatkit_server.py"
Task: "Create TodoChatKitServer class in backend/src/agents/chatkit_server.py"
Task: "Create ChatKitChat component in frontend/src/components/ChatKitChat.tsx"
```

---

## Parallel Example: User Story Validation

```bash
# After Foundational phase completes, launch all user story validations together:
Task: "Verify Agent class imported (US1)"
Task: "Test NLU-001: Add task (US2)"
Task: "Verify MCP server unchanged (US3)"
Task: "Count lines in orchestrator.py (US4)"

# Each story can be validated independently by different team members
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T028) - CRITICAL
3. Complete Phase 3: User Story 1 - Compliance (T029-T037)
4. Complete Phase 4: User Story 2 - Functional Parity (T038-T054)
5. **STOP and VALIDATE**: Test both stories independently
6. Run Phase III compliance audit
7. Deploy/demo if ready

**This is the MINIMUM VIABLE MIGRATION** - achieves Phase III compliance with functional parity

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T028)
2. Add User Story 1 → Test independently → Compliance verified (T029-T037)
3. Add User Story 2 → Test independently → Functional parity verified (T038-T054)
4. **MVP COMPLETE** - Can deploy at this point
5. Add User Story 3 → Test independently → Architecture verified (T055-T063)
6. Add User Story 4 → Test independently → Developer experience verified (T064-T071)
7. Polish phase → Final cleanup (T072-T082)

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T028)
2. Once Foundational is done:
   - Developer A: User Story 1 (T029-T037)
   - Developer B: User Story 2 (T038-T054)
   - Developer C: User Story 3 (T055-T063)
   - Developer D: User Story 4 (T064-T071)
3. Stories complete and validate independently
4. Team completes Polish phase together (T072-T082)

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 22 tasks (CRITICAL - blocks all stories)
- **Phase 3 (US1 - Compliance)**: 9 tasks
- **Phase 4 (US2 - Functional Parity)**: 17 tasks
- **Phase 5 (US3 - Architecture)**: 9 tasks
- **Phase 6 (US4 - Developer Experience)**: 8 tasks
- **Phase 7 (Polish)**: 11 tasks

**Total: 82 tasks**

**MVP Scope (US1 + US2)**: 54 tasks (Setup + Foundational + US1 + US2)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Manual validation approach (no automated tests per hackathon/MVP context)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP = Phase 1 + Phase 2 + Phase 3 + Phase 4 (54 tasks)
- Full migration = All 82 tasks

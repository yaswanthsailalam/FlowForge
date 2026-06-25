# plan.md

## 1) Objectives
- Prove the **core**: catalogue → workflow definition → validation → publish → run → tasks/approvals → audit, backed by **MongoDB + FastAPI**.
- Add **optional GPT-4o** assistance (recommendations/summaries/explanations) without blocking deterministic UX.
- Deliver an MVP web app (React) with real workspace data, multi-tenant boundaries, and a seeded **full department catalogue** (80–100+ models).

---

## 2) Implementation Steps (Phased)

### Phase 1 — Core POC (Isolation) 
Goal: validate the hardest parts before UI/auth.

**User stories**
1. As a builder, I can load a seeded process model and generate a draft workflow definition from its template.
2. As a builder, I can run validation and get a clear list of errors/warnings.
3. As a publisher, I can publish an immutable workflow version.
4. As an operator, I can start a workflow run and see step state advance deterministically.
5. As an approver, I can approve/reject a step and see the run transition and audit log update.

**Steps**
- Websearch best practices: DB-backed workflow engines (state machine patterns), Mongo indexing for multi-tenant, append-only audit.
- Create minimal Mongo schema + indexes for: process_models, templates, workflows, workflow_versions, runs, step_runs, tasks, approvals, audit_events.
- Implement FastAPI POC endpoints (no auth):
  - Seed loader (idempotent)
  - Create workflow from template
  - Validate workflow (subset of the 30+ checks, focusing on reachability, roles, transitions, required fields)
  - Publish version (immutability enforced)
  - Start run → create step_runs/tasks/approvals
  - Action endpoints: complete task, approve/reject, auto-step execution loop
  - Audit event append for every action
- Add GPT-4o POC script (standalone Python):
  - Model recommendation given keywords/department
  - Validation explanation for a validation error list
  - Ensure strict JSON output + cost/rate-limit handling
- POC acceptance: run a single happy-path workflow with 1 approval + 1 manual task + 1 condition branch; verify end state + audit trail.
- **Do not proceed** until POC is stable and repeatable.

---

### Phase 2 — V1 App Development (MVP around proven core)
Goal: build working end-to-end product UX with minimal breadth, maximum reliability.

**User stories**
1. As a workspace user, I can browse the process catalogue by department/family and search by keywords/tags.
2. As a process architect, I can select a model variant + template and configure it in a guided wizard.
3. As a workflow owner, I can preview the workflow graph and validate before publishing.
4. As an operator, I can launch a run and complete assigned tasks from a task inbox.
5. As an approver, I can handle approval requests (approve/reject/request-info) and see decisions reflected in the run.

**Backend (FastAPI)**
- Convert POC into API modules: catalogue, workflow_builder, validation, publishing, execution, tasks, approvals, notifications, audit.
- Implement workspace scoping (initially via `X-Workspace-Id` header for MVP; auth deferred).
- Implement validation expansion (prioritize: schema, trigger, steps, transitions, reachability, role refs, approval config, mappings).
- Implement run engine loop:
  - Auto steps execute synchronously (notification/data-write/condition)
  - Human steps create tasks/approvals and pause
  - Retries/failures recorded; cancellation supported
- Implement internal notifications collection + simple polling endpoints.

**Frontend (React)**
- Pages (MVP subset):
  - Dashboard (real counts: active runs/tasks/approvals/recent activity)
  - Catalogue (filters + model details)
  - Template → Guided Config Wizard (16 sections condensed to MVP but structured to expand)
  - Workflow Preview + Validation results
  - Publish screen + version list
  - Run detail (timeline + current step)
  - Task Center
  - Approval Center
  - Audit Log viewer
- UX requirements: clear empty states, deterministic actions, pagination, error handling.

**Data seeding**
- Seed full departments (7+) + 80–100+ models with:
  - healthcare-first tags + cross-industry global models
  - variants/templates for at least key flows per department
  - realistic roles/approval points

**End of phase testing**
- One round of end-to-end test of the V1 journey (create workflow → validate → publish → execute with tasks/approvals → completion → audit review).

---

### Phase 3 — Add More Features (Production hardening + breadth)
Goal: multi-tenancy, RBAC, version lifecycle, richer validation, AI assistance in UI.

**User stories**
1. As an admin, I can invite users to a workspace and assign roles with least privilege.
2. As a department manager, I can limit catalogue visibility to my department/team.
3. As a workflow owner, I can pause/deprecate workflows and view immutable published versions.
4. As an auditor, I can filter/export audit logs by actor/action/date/run.
5. As a builder, I can request GPT-4o help to summarize a workflow and explain validation failures.

**Steps**
- Auth + RBAC (JWT): signup/login, sessions, password reset; server-side permission checks on every endpoint.
- True multi-tenancy enforcement: workspace_id required; indexed; query-scoped everywhere.
- Workflow lifecycle: Draft → Validated → Published → Paused/Deprecated/Archived; immutability guarantees.
- Validation: expand toward full 30+ checks (dead ends, unreachable steps, missing mappings, invalid conditions, role coverage, completion rules).
- Manual builder (basic): edit steps/transitions; reorder; diff against template.
- AI assistance endpoints + UI:
  - model recommendations
  - role suggestions
  - workflow summary
  - validation explanation
  - always user-triggered, never auto-publish/execute
- Notifications UX: read/unread, linking to task/approval/run.

**End of phase testing**
- E2E tests for role-scoped access + multi-user task/approval flows.

---

### Phase 4 — Integrations, Observability, Scale
Goal: adapter architecture + resilience.

**User stories**
1. As an admin, I can connect an integration (webhook/email) and validate credentials.
2. As a workflow owner, I can simulate an integration step safely in a dry-run.
3. As an operator, I can see integration failures and retry or route to manual fallback.
4. As a builder, I can configure escalations/timeouts and see them enforced.
5. As an auditor, I can trace every external call via correlated audit events.

**Steps**
- Integration adapters: connect/disconnect/validate/execute/simulate; store secrets securely.
- Rate limiting + idempotency keys for run actions.
- Observability: structured logs, correlation IDs, metrics endpoints.
- Performance: indexes, pagination everywhere, seed data loading optimizations.

---

## 3) Next Actions
1. Implement Phase 1 POC schemas + indexes in MongoDB.
2. Build Phase 1 FastAPI endpoints + deterministic state-machine execution loop.
3. Write the standalone GPT-4o Python script (JSON-only outputs) and verify cost/limits.
4. Run the POC happy path repeatedly until stable.
5. Only then start Phase 2 UI + API consolidation.

---

## 4) Success Criteria
- POC: A seeded template can become a validated, published workflow; a run completes through task + approval steps with a complete audit trail.
- V1: Users can browse seeded catalogue, configure a workflow via wizard, validate, publish, execute, and manage tasks/approvals in the UI.
- Security (post-Phase 3): workspace isolation + RBAC enforced server-side; audit is append-only and searchable.
- AI: GPT-4o assistance is optional, user-triggered, labeled, returns structured output, and never performs actions without confirmation.

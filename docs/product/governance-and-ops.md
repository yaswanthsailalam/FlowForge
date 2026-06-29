# FlowForge AI - Product Foundation Guide

## 1. Governance Lifecycle
FlowForge implements a strict governance lifecycle for all process model blueprints:
*   **Draft:** Editable by any architect.
*   **In Review:** Locked for editing; pending approval.
*   **Changes Requested:** Returned to author for corrections. Resaving resets to Draft.
*   **Approved:** Validated and ready for publication.
*   **Published:** Immutable. Read-only for all users.
*   **Deprecated:** Visible but not recommended for new workflows.
*   **Archived:** Hidden from standard catalogue views.

## 2. Extension Policies
Every global model defines an Extension Policy that governs how it can be adapted into an **Organisation Variant**:
*   **Locked Stages:** Mandatory steps that cannot be removed.
*   **Activity Controls:** Prohibits removal of core activities.
*   **Input Gating:** Ensures required data points are always captured.

## 3. Platform Owner Bootstrap
To establish the first Platform Owner (Side A access):
1.  Register a standard user via the UI/API.
2.  Run: `python scripts/bootstrap_owner.py <email>`
3.  This user now has access to `/owner` routes and platform-management APIs.

## 4. Onboarding Flows
*   **Self-Service:** Register -> Onboarding Wizard -> Workspace.
*   **Platform-Provisioned:** Owner creates Client Org -> Owner assigns Plan -> Client receives Invite -> Finalize Setup.

## 5. Entitlement Model
Features are gated by Plan.
*   **Plans** contain included products, modules, and feature keys.
*   **Overrides** can be applied per Client Organisation by platform admins.
*   **Enforcement:** Evaluated on the backend via the `verify_entitlement` dependency.

## 6. Support Access (Governance)
Platform owners can request time-limited access to client workspaces.
*   **Audit:** Every access request and approval is logged.
*   **Transparency:** A high-visibility banner appears in the client shell during active sessions.
*   **Revocation:** Clients can revoke access at any time.

## 7. Technical Deployment (Render)
*   **Backend:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
*   **Frontend:** `yarn build` -> Static hosting.
*   **CORS:** Configure `BACKEND_CORS_ORIGINS` with the frontend URL.

# Architecture

High-level system design for Meerkit.

## System Topology

```text
Vue 3 frontend (Vite)
  -> HTTP /api/*
Flask app (meerkit/app.py)
  -> routes + service layer
  -> SQLite persistence (per-user DB files)
  -> background workers (scan/prediction/automation/download)
  -> filesystem caches (data/cache, data/image_cache, data/diffs)
  -> Instagram API via insta_interface wrappers
```

## Backend Layers

1. Routes (`meerkit/routes`)
- HTTP contracts and validation.
- Scope resolution via session and active Instagram account.

2. Services (`meerkit/services`)
- Business logic for auth, scan, prediction, automation, cache, persistence.

3. DB Layer (`meerkit/db`, `meerkit/services/db_service.py`)
- Schema creation/migrations for new columns.
- Thread-local connection handling.

4. Workers (`meerkit/workers`)
- Queue consumers for image, prediction, automation workloads.

## Route Domains

- Auth + account management (`/api/auth/*`)
- Scan lifecycle + history + diffs (`/api/scan*`, `/api/history`, `/api/diff/*`, `/api/summary`)
- Predictions (`/api/predictions/*`, `/api/prediction-tasks/*`, target relationship-cache endpoints)
- Automation (`/api/automation/*`)
- Unified task board (`/api/tasks`)
- Image serving (`/api/image/<pk_id>`)

## Core Data Flows

!!! warning "⚠️ Instagram Rate Limits Apply"
    Keep follow/unfollow actions under **150–200/day** (new accounts: **under 100/day**). Spread actions gradually throughout the day. [Monitor your API usage →](showcase.md#5-api-monitoring-and-limits)

### 1) Scan Flow

1. Frontend calls `POST /api/scan`.
2. `scan_runner.start_scan()` acquires per-scope lock and starts thread.
3. `meerkit/scan_worker.py` runs follower scan with explicit credentials.
4. Scan records + diff metadata are stored.
5. Frontend polls `GET /api/scan/status` and refreshes summary/diff/history when done.

### 2) Prediction Flow

1. Frontend calls `POST /api/predictions/follow-back`.
2. Immediate result may be returned, or background task is queued.
3. Worker refreshes prediction and marks task progress/status.
4. Frontend polls prediction task endpoints and can submit feedback.

### 3) Automation Flow

1. Frontend stages action via prepare endpoint.
2. User confirms action (`/actions/<id>/confirm`).
3. Worker executes item-by-item with heartbeat + rate-aware delay.
4. Status transitions persist in `automation_actions` + `automation_action_items`.

## Scope + Session Design

- Flask session stores app user and active Instagram account.
- Every scoped request resolves context with `get_active_context()`.
- Query override allows selecting explicit profile scope when needed.

## Cache Strategy

- Instagram gateway read-cache envelopes in `data/cache`.
- Optional legacy user detail cache writes controlled by feature flag.
- Relationship cache snapshots for followers/following lists.
- Image cache metadata in DB + files in `data/image_cache`.

## Reliability Patterns

- Stale scan/prediction/automation task detection and error marking.
- Worker thread startup guarded against duplicate startup under Flask reload.
- Background cancellation support for scan, prediction tasks, automation actions.

## Frontend Architecture Notes

- Router-based views in `frontend/src/router/index.ts`.
- TanStack Query for API state, polling, and cache invalidation.
- Dedicated workflows for dashboard, history, discovery, prediction history, tasks, and automation suites.

See [Backend API](backend.md), [Frontend](frontend.md), [Database](database.md), and [API Reference](api-reference.md).

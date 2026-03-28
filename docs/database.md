# Database

The backend uses SQLite with schemas defined in `meerkit/db/schemas.py` and runtime initialization in `meerkit/db/db_handler.py`.

## Storage Model

- SQLite DB is opened through `meerkit/services/db_service.py`.
- DB path is resolved by `meerkit.config.app_user_db()`.
- Data and caches are stored under `data/`.

## Core Tables

### Scan + Diff

- `scan_history`
- `scanned_data`
- `diff_records`
- `image_cache`

Used for scan snapshots, per-scan follower rows, diff metadata, and profile-image cache references.

### Account + Legacy

- `accounts`
- `profile_audience_events`

### Target Profile + Relationship Cache

- `target_profiles`
- `target_profile_relationships`
- `target_profile_list_cache_entries`

Used by prediction and automation features to track fetched metadata and relationship lists.

### Prediction Domain

- `predictions`
- `prediction_tasks`
- `prediction_assessments`

Supports prediction sessions, background refresh tasks, and user feedback/assessment.

### API Usage Metrics

- `instagram_api_usage_events`

Tracks API calls and cache-hit events by category/service/method.

### Automation Domain

- `automation_actions`
- `automation_action_items`
- `automation_safelists`
- `automation_alt_account_links`
- `automation_primary_accounts`

Supports staged/queued/running automation workflows, exclusion lists, and linked-account registry.

## Indexes

The schema includes indexes for high-use access patterns, including:

- prediction scope/session queries
- automation scope queries
- relationship cache scope queries
- API usage aggregation queries

See index definitions in `meerkit/db/schemas.py`.

## Schema Evolution

`SqliteDBHandler` performs startup-safe schema updates:

- ensures required tables exist
- backfills newer columns where needed (for example `last_heartbeat_at`, `prediction_session_id`)
- creates missing indexes

## Common Query Patterns

- latest scan metadata for active profile
- latest diff and diff lookup by ID
- active prediction tasks by scope
- active/recoverable automation actions
- grouped API usage summary per account/category

## Operational Notes

- SQLite is suitable for local/single-node operation.
- Thread-local DB handlers are used for concurrent worker threads.
- Background workers initialize and close DB handlers per thread lifecycle.

For endpoint-level behavior, see [API Reference](api-reference.md).

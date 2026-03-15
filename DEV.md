# Development Guide

## Prerequisites

- Python ≥ 3.12 with `uv` installed
- Node.js ≥ 20 with `npm`
- A valid `.env` file in the repo root (see `.env.example` if present) containing:
    ```
    CSRF_TOKEN=<your Instagram csrftoken cookie>
    SESSION_ID=<your Instagram sessionid cookie>
    USER_ID=<your Instagram numeric user ID>
    ```

## Backend (Flask)

```bash
# From the repo root, activate the venv
source .venv/bin/activate

# Run the Flask dev server on port 5000
flask --app backend.app run --debug --port 5000
```

The API is available at `http://localhost:5000/api/`.

| Method | Path                 | Description                                              |
| ------ | -------------------- | -------------------------------------------------------- |
| POST   | `/api/scan`          | Start a new scan (202 Accepted; 409 if already running)  |
| GET    | `/api/scan/status`   | Scan state: `idle \| running \| error`                   |
| GET    | `/api/summary`       | Latest scan metadata + diff counts                       |
| GET    | `/api/diff/latest`   | Full latest diff (new followers + unfollowers)           |
| GET    | `/api/diff/<id>`     | Specific diff by ID                                      |
| GET    | `/api/history`       | All scan metadata, newest first                          |
| GET    | `/api/image/<pk_id>` | Cached profile picture (served with 7-day Cache-Control) |

Scan snapshots, diffs, and the image cache are stored under `data/` in the repo root.

## Frontend (Vue 3 + Vite)

```bash
cd frontend
npm install        # first time only
npm run dev        # dev server on http://localhost:5173
```

Vite proxies all `/api/*` requests to `http://localhost:5000`, so both servers can run simultaneously without CORS issues.

### Production build

```bash
cd frontend
npm run build      # outputs to frontend/dist/
```

Serve the built assets from Flask (or any static host). To serve from Flask, copy `frontend/dist/` into a `static/` folder or configure Flask to serve at the root:

```python
app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
```

## Data layout

```
data/
├── scans/          # one .jsonl snapshot per scan
├── diffs/          # one .json diff file per consecutive scan pair
├── image_cache/    # profile pictures cached by pk_id
└── scan_index.jsonl  # one-line JSON metadata per scan (append-only)
```

## Editing rules

- **`insta_interface.py`** — read-only; never modify.
- **`get_current_followers.py`** — editable; contains the new `run_scan_for_api()` helper called by the Flask backend.
- All new backend logic lives in `backend/`.
- All new frontend logic lives in `frontend/src/`.

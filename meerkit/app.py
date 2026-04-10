import os
import sys
from pathlib import Path

# Ensure workspace root is on sys.path so get_current_followers and insta_interface
# are importable regardless of the working directory Flask is launched from.
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from flask_cors import CORS

from meerkit.exceptions import ConfigurationError


def _is_dev_or_test_environment() -> bool:
    return (
        os.environ.get("FLASK_ENV") in {"development", "testing"}
        or os.environ.get("FLASK_DEBUG") == "1"
        or bool(os.environ.get("PYTEST_CURRENT_TEST"))
    )


def _resolve_secret_key() -> str:
    secret_key = os.environ.get("APP_SECRET_KEY")
    if secret_key:
        return secret_key
    if os.environ.get("FLASK_ENV") == "production":
        raise ConfigurationError(
            "APP_SECRET_KEY environment variable is required",
            error_code="missing_app_secret_key",
            env_var="APP_SECRET_KEY",
        )
    if _is_dev_or_test_environment():
        return "dev-secret-change-me"
    return "dev-secret-change-me"


def _resolve_cors_origins() -> list[str]:
    raw_origins = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:4173"
    )
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:5173", "http://localhost:4173"]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = _resolve_secret_key()

    # Allow Vite dev server (5173) and preview server (4173) in development
    CORS(
        app,
        resources={r"/api/*": {"origins": _resolve_cors_origins()}},
    )

    from meerkit.routes.auth import bp as auth_bp
    from meerkit.routes.automation import bp as automation_bp
    from meerkit.routes.history import bp as history_bp
    from meerkit.routes.images import bp as images_bp
    from meerkit.routes.predict import bp as predict_bp
    from meerkit.routes.scan import bp as scan_bp
    from meerkit.routes.tasks import bp as tasks_bp
    from meerkit.workers import automation_worker, download_worker, prediction_worker

    is_debug = (
        os.environ.get("FLASK_DEBUG") == "1"
        or os.environ.get("FLASK_ENV") == "development"
    )
    # In debug/reload mode, Werkzeug starts a parent + child process.
    # Start the worker only in the reloader child process.
    if (is_debug and os.environ.get("WERKZEUG_RUN_MAIN") == "true") or (not is_debug):
        download_worker.start_download_worker()
        prediction_worker.start_prediction_worker()
        automation_worker.start_automation_worker()

    app.register_blueprint(auth_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(images_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(automation_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        port=int(os.environ.get("PORT", "5000")),
    )

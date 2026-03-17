import os
import sys
from pathlib import Path

# Ensure workspace root is on sys.path so get_current_followers and insta_interface
# are importable regardless of the working directory Flask is launched from.
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", "dev-secret-change-me")

    # Allow Vite dev server (5173) and preview server (4173) in development
    CORS(
        app,
        resources={
            r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:4173"]}
        },
    )

    from backend.routes.auth import bp as auth_bp
    from backend.routes.history import bp as history_bp
    from backend.routes.images import bp as images_bp
    from backend.routes.scan import bp as scan_bp
    from backend.workers import download_worker

    # # in debug mode, flask runs 2 processes. We only want to start the download worker in one of them to avoid duplicate workers.
    # if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    #     download_worker.start_download_worker()

    app.register_blueprint(auth_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(images_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)

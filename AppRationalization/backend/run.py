# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: AppRationalization — backend (run.py)
# Date: 2026-05-05
# ---------------------------------------------------------------------------
import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()

app = create_app()

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true', 'yes')
    app_host = os.getenv('FLASK_HOST', '127.0.0.1')
    # Port 5000 is reserved by Neo4j discovery on this host. Keep the
    # fallback Flask runner aligned with IIS and the watchdog on 5001.
    app_port = int(os.getenv('FLASK_PORT', '5001'))
    app.run(debug=debug_mode, host=app_host, port=app_port, use_reloader=debug_mode)

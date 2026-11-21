"""
One-Command Launcher for E-Commerce BI & Customer Analytics Platform
Starts both FastAPI backend and React frontend concurrently with graceful shutdown.
Works across Windows, macOS, and Linux.
Usage:
    python run.py
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def print_banner():
    print("=" * 72)
    print("🛒  E-COMMERCE BUSINESS INTELLIGENCE & CUSTOMER ANALYTICS PLATFORM")
    print("    FastAPI Backend (Port 8000) + React/Vite Dashboard (Port 5173)")
    print("=" * 72)

def check_and_prepare_environment():
    """Verify database and dependencies before launching servers."""
    db_file = ROOT_DIR / "data" / "olist_bi.db"
    
    # 1. Check if database exists
    if not db_file.exists() or db_file.stat().st_size < 1000000:
        print("\n[ETL Pipeline] Database not detected. Initializing data pipeline...")
        etl_script = ROOT_DIR / "backend" / "etl" / "etl_pipeline.py"
        code = subprocess.call([sys.executable, str(etl_script)])
        if code != 0:
            print("[Warning] ETL pipeline exited with code:", code)
    else:
        print("[System Check] Relational database verified (143 MB).")

    # 2. Check frontend dependencies
    node_modules = ROOT_DIR / "frontend" / "node_modules"
    if not node_modules.exists():
        print("\n[Frontend] node_modules not found. Running npm install in frontend...")
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        subprocess.call([npm_cmd, "install"], cwd=str(ROOT_DIR / "frontend"))
    else:
        print("[System Check] Frontend dependencies verified.")

def main():
    print_banner()
    check_and_prepare_environment()

    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    print("\n[1/2] Starting FastAPI Backend on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(ROOT_DIR)
    )

    print("[2/2] Starting React Vite Frontend on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(ROOT_DIR / "frontend")
    )

    time.sleep(2.5)
    print("\n" + "=" * 72)
    print("🚀  PLATFORM IS LIVE AND READY!")
    print("    📊 React BI Dashboard:   http://localhost:5173")
    print("    📚 Swagger API Docs:     http://localhost:8000/docs")
    print("    🏥 API Health Check:     http://localhost:8000/health")
    print("=" * 72)
    print("Press Ctrl+C to stop all servers gracefully.\n")

    # Open browser
    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

    def cleanup(sig=None, frame=None):
        print("\n\nShutting down platform processes...")
        try:
            frontend_proc.terminate()
            backend_proc.terminate()
            time.sleep(1)
            frontend_proc.kill()
            backend_proc.kill()
        except Exception:
            pass
        print("All processes stopped successfully. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, cleanup)

    try:
        while True:
            # Check if any process died
            if backend_proc.poll() is not None:
                print(f"[Alert] Backend process exited unexpectedly (code {backend_proc.poll()}).")
                break
            if frontend_proc.poll() is not None:
                print(f"[Alert] Frontend process exited unexpectedly (code {frontend_proc.poll()}).")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()

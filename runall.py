"""Convenience script to launch both ArtificialShield backend and Streamlit dashboard together."""
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

from config import settings


def wait_for_backend(url: str, timeout: int = 60) -> bool:
    """Wait until backend /health endpoint responds."""
    print(f"[*] Waiting for backend to become ready at {url} ...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main() -> None:
    backend_host = "127.0.0.1" if settings.host in {"0.0.0.0", ""} else settings.host
    backend_health_url = f"http://{backend_host}:{settings.port}/health"

    print("=" * 60)
    print("  Starting ArtificialShield Guardrail & Dashboard")
    print("=" * 60)

    # 1. Start the FastAPI backend
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.gateway:app",
        "--host",
        settings.host,
        "--port",
        str(settings.port),
    ]
    print(f"[*] Launching Backend: {' '.join(backend_cmd)}")
    backend_proc = subprocess.Popen(backend_cmd)

    # 2. Wait for backend to be healthy before launching dashboard
    healthy = wait_for_backend(backend_health_url, timeout=60)
    if not healthy:
        print("[!] Backend failed to start within 60 seconds.")
        backend_proc.terminate()
        sys.exit(1)

    print("[+] Backend is online and ready!")

    # 3. Start the Streamlit dashboard
    dashboard_file = os.path.join("dashboard", "streamlit_app.py")
    dashboard_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        dashboard_file,
    ]
    print(f"[*] Launching Streamlit: {' '.join(dashboard_cmd)}")
    dashboard_proc = subprocess.Popen(dashboard_cmd)

    print("\n" + "=" * 60)
    print(f"  Backend running at:   http://localhost:{settings.port}")
    print(f"  Dashboard running at: http://localhost:8501")
    print("  Press Ctrl+C to stop all services.")
    print("=" * 60 + "\n")

    def shutdown(signum=None, frame=None):
        print("\n[*] Shutting down ArtificialShield processes...")
        for name, proc in [("Dashboard", dashboard_proc), ("Backend", backend_proc)]:
            if proc.poll() is None:
                print(f"[*] Terminating {name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        print("[+] All services stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            # Check if either process terminated unexpectedly
            if backend_proc.poll() is not None:
                print("[!] Backend process exited unexpectedly.")
                shutdown()
            if dashboard_proc.poll() is not None:
                print("[!] Dashboard process exited.")
                shutdown()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()

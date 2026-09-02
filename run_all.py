"""
SmartFix Local Services Runner for Windows/macOS/Linux.

Starts all 8 microservices in background processes and monitors their status.
Press Ctrl+C to stop all services simultaneously.
"""

import os
import signal
import subprocess
import sys
import time

SERVICES = [
    ("Orchestrator", "services.orchestrator.main:app", 8000),
    ("RAG Service", "services.rag.main:app", 8001),
    ("Equipment", "services.equipment.main:app", 8002),
    ("Safety Engine", "services.safety.main:app", 8003),
    ("History", "services.history.main:app", 8004),
    ("Spare Parts", "services.spare_parts.main:app", 8005),
    ("Tickets", "services.tickets.main:app", 8006),
    ("LLM Gateway", "services.llm.main:app", 8007),
]

def main():
    print("=" * 65)
    print("   Starting SmartFix Microservices Platform")
    print("=" * 65)

    processes = []
    python_exe = sys.executable

    for name, app_module, port in SERVICES:
        cmd = [python_exe, "-m", "uvicorn", app_module, "--host", "127.0.0.1", "--port", str(port)]
        print(f"[*] Starting {name:15} on http://127.0.0.1:{port}")
        proc = subprocess.Popen(cmd)
        processes.append((name, proc))

    print("=" * 65)
    print("All microservices are starting up.")
    print("Main Orchestrator Entrypoint: http://127.0.0.1:8000")
    print("Press Ctrl+C at any time to shut down all services.")
    print("=" * 65)

    try:
        while True:
            time.sleep(1)
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"[!] Warning: {name} exited with code {proc.returncode}")
    except KeyboardInterrupt:
        print("\n[!] Shutting down all SmartFix microservices...")
        for name, proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        print("[*] All services stopped successfully.")

if __name__ == "__main__":
    main()

import subprocess
import time

def inject(duration_seconds=60):
    print(f"[CPU Starvation] Injecting high CPU load for {duration_seconds}s...")
    # Use stress-ng to create CPU load on all available cores
    proc = subprocess.Popen(["stress-ng", "--cpu", "0", "--timeout", str(duration_seconds)])
    proc.wait()
    print("[CPU Starvation] Injection finished.")
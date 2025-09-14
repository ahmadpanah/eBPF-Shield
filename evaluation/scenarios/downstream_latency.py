import subprocess
import time
import sys

def run_cmd(cmd):
    """Executes a command and handles errors."""
    try:
        subprocess.run(cmd, check=True, shell=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e.cmd}\nStderr: {e.stderr}\nStdout: {e.stdout}", file=sys.stderr)
        raise

def inject(duration_seconds=60, delay_ms=700, interface="eth0"):
    """
    Injects network latency using tc.
    This requires root privileges.
    """
    print(f"[Downstream Latency] Injecting {delay_ms}ms delay on {interface} for {duration_seconds}s...")
    
    # Add a qdisc (queueing discipline) to the interface if it doesn't exist
    # This is a prerequisite for adding delay rules.
    try:
        run_cmd(f"tc qdisc add dev {interface} root netem")
    except subprocess.CalledProcessError:
        print(f"Netem qdisc already exists on {interface}. Changing rule.")
        
    # Apply the delay rule
    run_cmd(f"tc qdisc change dev {interface} root netem delay {delay_ms}ms")
    
    # Wait for the duration of the fault
    time.sleep(duration_seconds)
    
    # Clean up by deleting the rule
    print("[Downstream Latency] Cleaning up latency rule.")
    run_cmd(f"tc qdisc del dev {interface} root netem")
    print("[Downstream Latency] Injection finished.")

if __name__ == '__main__':
    # Example of how to run it standalone
    inject(duration_seconds=30)
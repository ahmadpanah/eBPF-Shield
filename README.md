# eBPF-Shield: Autonomous Anomaly Detection and Remediation

This repository contains the implementation of eBPF-Shield, a framework for autonomous, in-kernel self-healing of cloud-native systems, as described in our research paper.

eBPF-Shield uses eBPF to perform holistic, multi-modal health monitoring (network, CPU, memory, I/O) and executes proactive, real-time remediation to protect services from "gray failures."

## Architecture
The system consists of two main parts:
1.  **eBPF Probes (`bpf/probes.c`):** C programs that run in the Linux kernel to collect metrics and perform actions like packet dropping.
2.  **User-space Agent (`agent/shield_agent.py`):** A Python agent that orchestrates the probes, learns performance baselines, calculates health scores, and updates the remediation policy in the kernel.

## Setup

1.  **Prerequisites:**
    *   Linux kernel >= 4.14
    *   BCC (BPF Compiler Collection) installed. See [BCC installation guide](https://github.com/iovisor/bcc/blob/master/INSTALL.md).
    *   Python 3.8+
    *   Docker and Kubernetes (or a single-node setup like Minikube)

2.  **Installation:**
    ```bash
    git clone https://github.com/ahmadpanah/eBPF-Shield.git
    cd eBPF-Shield
    pip install -r requirements.txt
    ```

## Usage

### Running the Agent
The agent must be run with root privileges to load eBPF programs. It will automatically discover and monitor running Docker containers.

```bash
sudo python3 agent/shield_agent.py
```

### Running the Evaluation
The evaluation script simulates the fault scenarios from the paper.

1.  **Deploy a Target Application:** Deploy a test application (e.g., Online Boutique) to your Kubernetes cluster.

2.  **Start the Load Generator:**
    ```bash
    locust -f evaluation/locust/locustfile.py --host=http://<your-app-service-ip>
    ```

3.  **Run a Scenario:**
    ```bash
    # Run the CPU starvation scenario against a container named 'productcatalog'
    sudo python3 evaluation/run_evaluation.py --scenario cpu_starvation --container_name productcatalog
    ```

4.  **Visualize Results:**
    After running the evaluation, a `summary.csv` is generated. Create plots with:
    ```bash
    python3 results/plot_results.py
    ```
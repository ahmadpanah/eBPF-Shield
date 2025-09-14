import time
import yaml
from bcc import BPF
from agent.baseliner import AdaptiveBaseliner
from agent.health_scorer import HealthScorer
from agent.container_utils import get_running_containers

# --- Main Agent Logic ---
class ShieldAgent:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Load BPF program
        with open("bpf/probes.c", "r") as f:
            bpf_text = f.read()
        self.bpf = BPF(text=bpf_text)
        
        # Attach probes (simplified)
        self.bpf.attach_tracepoint(tp="sched:sched_switch", fn_name="sched_switch")
        self.bpf.attach_tracepoint(tp="exceptions:page_fault_user", fn_name="page_fault_user")
        # TC attachment is more complex, this is a placeholder
        # self.bpf.attach_tc("eth0", "tc_ingress_remediator")

        self.baseliner = AdaptiveBaseliner(self.config['baseliner']['ewma_alpha'])
        self.scorer = HealthScorer(self.config['health_scorer'])
        self.containers = {}

    def run(self):
        print("eBPF-Shield Agent is running...")
        while True:
            # Discover running containers periodically
            self.containers = get_running_containers()
            print(f"Monitoring containers: {list(self.containers.values())}")
            
            # Main monitoring loop
            self.monitor_and_remediate()
            time.sleep(self.config['agent']['poll_interval_seconds'])
            
    def monitor_and_remediate(self):
        metrics_map = self.bpf["metrics_map"]
        health_map = self.bpf["health_scores_map"]

        for cgroup_id_str, name in self.containers.items():
            # In a real system, you'd convert the string ID to a u64
            # Here we just iterate and assume keys match
            cgroup_id = int(cgroup_id_str, 16) # Placeholder conversion
            
            # Read metrics from BPF map
            raw_metrics = metrics_map.get(cgroup_id)
            if not raw_metrics:
                continue

            # This is a placeholder for real metric processing
            current_metrics = {
                "net_latency": raw_metrics.net_latency_ns,
                "net_errors": raw_metrics.net_error_count,
                "cpu_latency": raw_metrics.cpu_sched_latency_ns,
                "mem_faults": raw_metrics.mem_page_faults,
            }

            # Update baselines
            for name, value in current_metrics.items():
                self.baseliner.update(cgroup_id, name, value)

            # Calculate health score
            score = self.scorer.calculate_score(current_metrics, self.baseliner, cgroup_id)
            
            # Write health score back to BPF map (scaled 0-1000)
            health_map[cgroup_id] = int(score * 1000)
            
            print(f"Container: {name}, Health Score: {score:.3f}")
            
            # Clear the metrics for the next interval
            metrics_map.delete(cgroup_id)

if __name__ == "__main__":
    agent = ShieldAgent("config/agent_config.yaml")
    agent.run()
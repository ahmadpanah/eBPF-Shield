#include <uapi/linux/ptrace.h>
#include <uapi/linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <linux/sched.h>
#include <net/sock.h>
#include <linux/pkt_cls.h>

// --- Data Structures ---
// A universal struct to hold collected metrics
struct metric_data {
    u64 net_latency_ns;
    u64 net_error_count;
    u64 cpu_sched_latency_ns;
    u64 mem_page_faults;
};

// --- BPF Maps ---
// 1. Stores raw metrics per container (identified by cgroup ID)
BPF_HASH(metrics_map, u64, struct metric_data);

// 2. Stores the agent-calculated health score (0-1000, scaled from 0.0-1.0)
BPF_HASH(health_scores_map, u64, u32);

// --- Probes ---

// 1. CPU Scheduler Latency Probe
TRACEPOINT_PROBE(sched, sched_switch) {
    // This tracepoint fires when a task is switched out. We can use it to
    // calculate how long a task was waiting to run.
    // (Simplified logic for demonstration)
    u64 cgroup_id = bpf_get_current_cgroup_id();
    struct metric_data *data = metrics_map.lookup(&cgroup_id);
    if (data) {
        // A real implementation would track process start/end times.
        // For simplicity, we just increment a value here.
        __sync_fetch_and_add(&data->cpu_sched_latency_ns, 1);
    }
    return 0;
}

// 2. Memory Page Fault Probe
TRACEPOINT_PROBE(exceptions, page_fault_user) {
    u64 cgroup_id = bpf_get_current_cgroup_id();
    struct metric_data *data = metrics_map.lookup(&cgroup_id);
    if (data) {
        __sync_fetch_and_add(&data->mem_page_faults, 1);
    }
    return 0;
}


// 3. Network TC Ingress Probe for Remediation
int tc_ingress_remediator(struct __sk_buff *skb) {
    u64 cgroup_id = bpf_get_current_cgroup_id();
    if (cgroup_id == 0) {
        return TC_ACT_OK; // Ignore host traffic
    }

    u32 *health_score_ptr = health_scores_map.lookup(&cgroup_id);
    if (!health_score_ptr) {
        return TC_ACT_OK; // No score yet, allow traffic
    }

    u32 health_score = *health_score_ptr; // Score is 0-1000

    if (health_score >= 990) { // If health is near perfect, skip random number generation
        return TC_ACT_OK;
    }

    // Calculate drop probability based on health score.
    // P_drop = (1 - S)^gamma, where S is 0.0-1.0
    // Here, we do integer math. If score is 700 (0.7), drop_threshold is 300 (0.3).
    u32 drop_threshold = 1000 - health_score;

    // A real implementation would use the gamma factor.
    // For simplicity, we use a linear probability.
    u32 random_val = bpf_get_prandom_u32() % 1000;

    if (random_val < drop_threshold) {
        return TC_ACT_SHOT; // Drop the packet
    }

    return TC_ACT_OK; // Allow the packet
}
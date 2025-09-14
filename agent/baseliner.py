# agent/baseliner.py
import numpy as np
from collections import defaultdict

class AdaptiveBaseliner:
    """
    Manages the adaptive statistical baseline for container metrics using an
    Exponentially Weighted Moving Average (EWMA).

    This class is responsible for learning the "normal" behavior of a metric
    by tracking its running mean and variance. It gives more weight to recent
    data points, allowing it to adapt to gradual changes in workload or behavior.
    """

    def __init__(self, alpha: float = 0.3):
        """
        Initializes the baseliner.

        Args:
            alpha (float): The smoothing factor for the EWMA, between 0 and 1.
                           A smaller alpha results in smoother, less responsive baselines.
                           A larger alpha makes the baseline more sensitive to recent changes.
        """
        if not 0 < alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1.")
        
        self.alpha = alpha
        
        # Dictionaries to store the running EWMA mean and variance for each metric.
        # The key will be a tuple: (container_id, metric_name)
        self.means = {}
        self.variances = {}

    def update(self, container_id: str, metric_name: str, value: float):
        """
        Updates the baseline for a specific metric with a new observed value.

        This method applies the EWMA update rules for both the mean and variance.
        If a metric is seen for the first time, its baseline is initialized.

        Args:
            container_id (str): The unique identifier for the container.
            metric_name (str): The name of the metric (e.g., 'net_latency').
            value (float): The newly observed value for the metric.
        """
        key = (container_id, metric_name)

        if key not in self.means:
            # First time seeing this metric for this container.
            # Initialize the baseline with the first value.
            self.means[key] = value
            self.variances[key] = 0.0
        else:
            # Get the previous state
            prev_mean = self.means[key]
            prev_variance = self.variances[key]

            # --- EWMA Update Rules ---
            # 1. Update the mean
            new_mean = (1 - self.alpha) * prev_mean + self.alpha * value
            self.means[key] = new_mean

            # 2. Update the variance
            # This is a common and stable way to calculate an EWMA of variance.
            # It weights the squared difference between the new value and the *previous* mean.
            squared_diff = (value - prev_mean) ** 2
            new_variance = (1 - self.alpha) * (prev_variance + self.alpha * squared_diff)
            self.variances[key] = new_variance

    def get_baseline(self, container_id: str, metric_name: str) -> tuple[float, float]:
        """
        Retrieves the current learned baseline (mean and standard deviation) for a metric.

        Args:
            container_id (str): The unique identifier for the container.
            metric_name (str): The name of the metric.

        Returns:
            tuple[float, float]: A tuple containing the current EWMA mean and
                                 EWMA standard deviation. Returns (0.0, 0.0) if no
                                 baseline has been established yet.
        """
        key = (container_id, metric_name)
        
        mean = self.means.get(key, 0.0)
        variance = self.variances.get(key, 0.0)
        
        # Standard deviation is the square root of the variance.
        # Ensure variance is non-negative to avoid math domain errors.
        std_dev = np.sqrt(max(0, variance))
        
        return mean, std_dev

# --- Example Usage and Demonstration ---
if __name__ == "__main__":
    print("--- Demonstrating AdaptiveBaseliner ---")
    
    # Initialize the baseliner with a relatively high alpha to adapt quickly
    baseliner = AdaptiveBaseliner(alpha=0.4)
    container_a = "container_abc123"
    metric_latency = "net_latency_ms"

    # Simulate a period of stable, low-latency traffic
    print("\nPhase 1: Stable Low Latency (Learning Baseline)")
    stable_traffic = [20, 22, 19, 21, 20, 18, 23, 20]
    for latency in stable_traffic:
        baseliner.update(container_a, metric_latency, latency)
        mean, std_dev = baseliner.get_baseline(container_a, metric_latency)
        print(f"  Observed: {latency:<4} -> Learned Baseline: Mean={mean:.2f}, StdDev={std_dev:.2f}")

    print("\nBaseline established.")
    mean, std_dev = baseliner.get_baseline(container_a, metric_latency)
    print(f"Final learned baseline: Mean={mean:.2f}, StdDev={std_dev:.2f}")

    # Simulate a sudden latency spike (anomaly)
    print("\nPhase 2: Sudden Latency Spike (Anomaly)")
    spike_traffic = [22, 21, 150, 165, 25] # A spike and then recovery
    for latency in spike_traffic:
        baseliner.update(container_a, metric_latency, latency)
        mean, std_dev = baseliner.get_baseline(container_a, metric_latency)
        print(f"  Observed: {latency:<4} -> Learned Baseline: Mean={mean:.2f}, StdDev={std_dev:.2f}")

    print("\nNotice how the mean and standard deviation increased to adapt to the spike.")
    mean, std_dev = baseliner.get_baseline(container_a, metric_latency)
    print(f"Final baseline after spike: Mean={mean:.2f}, StdDev={std_dev:.2f}")